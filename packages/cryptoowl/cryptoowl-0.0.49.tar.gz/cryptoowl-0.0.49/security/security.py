import json
from datetime import datetime

import requests

from common.secretmanager import SecretManager
from common_utils.time_utils import convert_timestamp_to_datetime
from db.databases import RDSConnection
from security.constants import HONEYPOT_FINDER_URL, GO_PLUS_URL, INSERT_OR_UPDATE_ETH_SECURITY_DATA_QUERY, \
    UPDATE_OTHER_CHAIN_SECURITY_DATA_QUERY, GET_QUICK_AUDIT_URL, QUICK_INTEL_API_KEY_SECRET_ID, \
    SOCIAL_INTELLIGENCE_DB_SECRET_ID
from common_utils.chain_utils import chain_to_id, id_to_chain

write_db = RDSConnection(db_secret_name=SOCIAL_INTELLIGENCE_DB_SECRET_ID)


class Honeypot:
    def __init__(self):
        self.__aws_secret_manager = SecretManager()
        self.__api_key_values = self.__aws_secret_manager.get_secret_key_value(
            secret_name=QUICK_INTEL_API_KEY_SECRET_ID)
        self.__api_key = self.__api_key_values.get("api-key")

    @classmethod
    def __store_security_data(cls, security_data, chain_id, verbose=False):
        if security_data:
            token_id = security_data.get("token_id")
            honeypot = security_data.get("honeypot")
            buy_tax = security_data.get("buy_tax")
            sell_tax = security_data.get("sell_tax")
            holder_count = security_data.get("holder_count")
            lp_burned = security_data.get("lp_burned")
            is_scam = security_data.get("is_scam")
            can_burn = security_data.get("can_burn")
            can_mint = security_data.get("can_mint")
            can_freeze = security_data.get("can_freeze")
            contract_creator = security_data.get("contract_creator")
            contract_owner = security_data.get("contract_owner")
            lp_lock_percentage = security_data.get("lp_lock_percentage")
            lp_unlock_date = security_data.get("lp_unlock_date")
            filled_by = security_data.get("filled_by") if security_data.get("filled_by") else "no_data"

            if chain_id in (1, "eth", "ether", "ethereums"):
                value = (token_id, honeypot, sell_tax, buy_tax, holder_count, contract_creator, contract_owner,
                         lp_lock_percentage, lp_unlock_date, filled_by)
                query = INSERT_OR_UPDATE_ETH_SECURITY_DATA_QUERY
            else:
                value = (honeypot, sell_tax, buy_tax, lp_burned, is_scam, can_burn, can_mint, can_freeze, holder_count,
                         contract_creator, contract_owner, lp_lock_percentage, lp_unlock_date, datetime.utcnow(),
                         filled_by, token_id)
                query = UPDATE_OTHER_CHAIN_SECURITY_DATA_QUERY

            try:
                write_db.execute_query(query=query, values=value)
                if verbose:
                    print(f"INFO: Data updated for: {token_id}")
            except Exception as error:
                print(f"ERROR: {error}")

    def get_security_data(self, chain_id, token_id):
        if not isinstance(chain_id, int):
            chain_id = chain_to_id.get(chain_id)

        security_data_dict = {"filled_by": "no_data"}
        # if chain is not solana then we go from goplus > quickintel > honeypot
        # else we directly go to quickintel as goplus does not support solana chain as of 19th june 2024
        if chain_id != 69420:
            security_data_dict = self.get_data_from_goplus(chain_id=chain_id, token_id=token_id)

        if not security_data_dict.get("is_filled"):
            security_data_dict = self.get_data_from_quickintel(chain_id=chain_id, token_id=token_id)

            # honeypot.io currently support eth, bsc, and base so we only check for those chains and ignore others
            if not security_data_dict.get("is_filled") and chain_id in (1, 56, 8453):
                security_data_dict = self.get_data_from_honeypot(chain_id=chain_id, token_id=token_id)

        return security_data_dict

    @classmethod
    def _get_lp_locks_data_gp(cls, lp_lock_data):
        lp_lock_percentage = None
        if not lp_lock_data:
            return lp_lock_percentage

        for i in lp_lock_data:
            is_locked = i.get("is_locked")
            if is_locked:
                percentage_locked = float(i.get("percent")) if i.get("percent") else i.get("percent")
                if lp_lock_percentage is None:
                    lp_lock_percentage = percentage_locked
                else:
                    lp_lock_percentage += percentage_locked

        return lp_lock_percentage

    @classmethod
    def get_data_from_goplus(cls, chain_id, token_id):
        if isinstance(chain_id, str):
            chain_id = chain_to_id.get(chain_id)

        token_id = token_id.lower()
        url = GO_PLUS_URL.format(chain_id=chain_id, token_id=token_id)
        response = requests.get(url=url)
        try:
            if response.status_code not in [500, 404]:
                result = response.json().get("result")
                if result:
                    is_honey_pot = result.get(token_id).get('is_honeypot')
                    buy_tax = result.get(token_id).get('buy_tax')
                    sell_tax = result.get(token_id).get('sell_tax')
                    holders_count = result.get(token_id).get("holder_count")
                    is_mintable = result.get(token_id).get('is_mintable')
                    contract_creator = result.get(token_id).get('creator_address')
                    contract_owner = result.get(token_id).get('owner_address')
                    lp_holders = result.get(token_id).get('lp_holders')
                    lp_lock_percentage = cls._get_lp_locks_data_gp(lp_lock_data=lp_holders)

                    security_data_dict = {
                        "token_id": token_id,
                        "honeypot": is_honey_pot,
                        "buy_tax": float(buy_tax) * 100 if buy_tax else buy_tax,
                        "sell_tax": float(sell_tax) * 100 if sell_tax else sell_tax,
                        "holder_count": holders_count,
                        "can_mint": is_mintable,
                        "contract_creator": contract_creator,
                        "contract_owner": contract_owner,
                        "lp_lock_percentage": float(lp_lock_percentage) * 100 if lp_lock_percentage
                        else lp_lock_percentage,
                        "is_filled": True,
                        "filled_by": "goplus"
                    }
                    cls.__store_security_data(security_data=security_data_dict, chain_id=chain_id)
                    return security_data_dict
            else:
                print(f"ERROR: In get_data_from_goplus: {response.text}")
        except Exception as error:
            print(f"ERROR: In get_data_from_goplus {error}")
        return {"filled_by": "no_data"}

    @classmethod
    def get_data_from_honeypot(cls, chain_id, token_id):
        if isinstance(chain_id, int):
            chain_id = id_to_chain.get(chain_id)

        url = HONEYPOT_FINDER_URL.format(token_id=token_id, chain_id=chain_id)
        response = requests.get(url=url)
        try:
            if response.status_code not in [500, 404]:
                data = response.json()
                is_honey_pot = data.get('IsHoneypot')
                buy_tax = round(data.get('BuyTax'))
                sell_tax = round(data.get('SellTax'))

                security_data_dict = {
                    "token_id": token_id,
                    "honeypot": is_honey_pot,
                    "buy_tax": buy_tax,
                    "sell_tax": sell_tax,
                    "is_filled": True,
                    "filled_by": "honeypot.io"
                }
                cls.__store_security_data(security_data=security_data_dict, chain_id=chain_id)
                return security_data_dict
            else:
                print(f"ERROR: In get_data_from_goplus: {response.text}")
        except Exception as error:
            print(f"ERROR: In get_data_from_honeypot {error}")
        return {"filled_by": "no_data"}

    @classmethod
    def _get_lp_locks_data_qi(cls, lp_lock_data):
        lp_lock_percentage = None
        lp_unlock_date = None
        if not lp_lock_data:
            return lp_lock_percentage, lp_unlock_date

        for key, value in lp_lock_data.items():
            if value and isinstance(value, dict):
                if percentage_locked := float(value.get("percentageLocked")) if value.get("percentageLocked") \
                                                                                and value.get("percentageLocked") != "NaN" \
                        else value.get("percentageLocked"):
                    if percentage_locked == "NaN":
                        continue
                    if lp_lock_percentage is None:
                        lp_lock_percentage = percentage_locked
                    else:
                        lp_lock_percentage += percentage_locked

                if unlock_date_timestamp := value.get("unlockDate"):
                    unlock_date = convert_timestamp_to_datetime(timestamp=unlock_date_timestamp)
                    if lp_unlock_date is None:
                        lp_unlock_date = unlock_date
                    else:
                        if lp_unlock_date > unlock_date:
                            lp_unlock_date = unlock_date

        return lp_lock_percentage, lp_unlock_date

    def get_data_from_quickintel(self, chain_id, token_id):
        if isinstance(chain_id, int):
            chain_id = id_to_chain.get(chain_id)

        url = GET_QUICK_AUDIT_URL
        payload = {"chain": chain_id, "tokenAddress": token_id}
        headers = {"X-QKNTL-KEY": self.__api_key, "Content-Type": "application/json"}
        response = requests.post(url=url, data=json.dumps(payload), headers=headers)
        try:
            if response.status_code not in [500, 404]:
                data = response.json()
                token_dynamic_details = data.get("tokenDynamicDetails") if data.get("tokenDynamicDetails") else {}
                quick_audit = data.get("quickiAudit") if data.get("quickiAudit") else {}
                honeypot = token_dynamic_details.get("is_Honeypot")
                buy_tax = token_dynamic_details.get("buy_Tax")
                sell_tax = token_dynamic_details.get("sell_Tax")
                lp_burned = token_dynamic_details.get("lp_Burned_Percent")
                lp_lock = token_dynamic_details.get("lp_Locks")
                lp_lock_percentage, lp_unlock_date = self._get_lp_locks_data_qi(lp_lock_data=lp_lock)

                is_scam = data.get("isScam")
                can_burn = quick_audit.get("can_Burn")
                can_mint = quick_audit.get("can_Mint")
                can_freeze = quick_audit.get("can_Freeze_Trading")
                contract_creator = quick_audit.get("contract_Creator").lower() if quick_audit.get("contract_Creator") \
                    else quick_audit.get("contract_Creator")
                contract_owner = quick_audit.get("contract_Owner").lower() if quick_audit.get("contract_Owner") \
                    else quick_audit.get("contract_Owner")

                security_data_dict = {
                    "token_id": token_id,
                    "honeypot": honeypot,
                    "buy_tax": buy_tax,
                    "sell_tax": sell_tax,
                    "lp_burned": lp_burned,
                    "is_scam": is_scam,
                    "can_burn": can_burn,
                    "can_mint": can_mint,
                    "can_freeze": can_freeze,
                    "contract_creator": contract_creator,
                    "contract_owner": contract_owner,
                    "lp_lock_percentage": float(lp_lock_percentage) if lp_lock_percentage else lp_lock_percentage,
                    "lp_unlock_date": lp_unlock_date,
                    "is_filled": True,
                    "filled_by": "quick_intel"
                }
                self.__store_security_data(security_data=security_data_dict, chain_id=chain_id)
                return security_data_dict
            else:
                print(f"ERROR: In get_data_from_goplus: {response.text}")
        except Exception as error:
            print(f"ERROR: In get_data_from_quickintel {error}")
        return {"filled_by": "no_data"}
