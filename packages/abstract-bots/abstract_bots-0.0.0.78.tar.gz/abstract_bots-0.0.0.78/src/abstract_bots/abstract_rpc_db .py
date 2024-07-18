from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv
Base = declarative_base()
# Load environment variables

class ResponseData(Base):
    __tablename__ = 'response_data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    slot = Column(Integer)
    signature = Column(String, nullable=False)
    call_type = Column(String, nullable=False)
    response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)\
                
class dbCoinfig(metaclass=SingletonMeta):
    def __init__(self,dbUrl=None):
        # Create an engine and session
        self.dbUrl= dbUrl
        self.engine = create_engine()
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        return 

def save_response_data(slot, signature, call_type, response):
    session = dbConfig().session
    response_json = json.dumps(response)
    response_data = ResponseData(
        slot=slot,
        signature=signature,
        call_type=call_type,
        response=response_json
    )
    session.add(response_data)
    try:
        session.commit()
        print("Response data saved successfully.")
    except Exception as e:
        print("Error saving response data:", e)
        session.rollback()
def preSave_response(call_type,params,response):
    data = {"call_type": call_type, "params": params, "response": response}
    slot = params[0] if isinstance(params[0], int) else None
    save_response_data(slot, signature, call_type, data)
def fetch_response_data(signature, call_type):
    existing_entry = dbConfig().session.query(ResponseData).filter_by(signature=signature, call_type=call_type).first()
    if existing_entry:
        print(f"Found existing entry for signature: {signature} and call type: {call_type}.")
        return json.loads(existing_entry.response)
    return None
def get_solana_rpc(typ='mainnet'):
    for each in ['mainnet-beta','devnet','testnet']:
        if typ in each:
            return f'https://api.{each}.solana.com'
    return rpc
class rpcCallDbManager(metaclass=SingletonMeta):
    def __init__(self,rpc=None, dbUrl=None, dbMgr=None, directory_mgr=None, price_mgr=None):
        if not hasattr(self, 'initialized'):  # Prevent reinitialization
            self.dbUrl=dbUrl
            self.dbMgr = dbMgr or dbConfig(self.dbUrl)
            self.initialized = True
            self.rpc=get_solana_rpc(typ=rpc)
            self.price_mgr = price_mgr
            self.directory_mgr = directory_mgr or directoryStart()
            self.recently_checked_signature_data = {}

    def get_result(self, response):
        try:
            response = response.json()
        except:
            return response.text
        if isinstance(response, dict) and 'result' in response:
            return response['result']
        return response

    def get_conditions(self, conditions):
        return {k: v for k, v in conditions.items() if v is not None}

    def get_response(self, call_type, params):
        signature = params[0] if isinstance(params[0], str) else None
        existing_response = fetch_response_data(signature, call_type)
        if existing_response:
            return existing_response

        response = self.rpc_call(call_type, params)
        if isinstance(response, dict) and response.get('error') is not None:
            return response

        preSave_response(call_type,params,response)
        return response

    def rpc_call(self, method, params):
        rpc_url = self.rpc
  # Replace with your actual RPC URL
        headers = {"Content-Type": "application/json"}
        request_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params,
        }
        return self.await_statuse(rpc_url, headers, request_data)

    def await_statuse(self, rpc_url, headers, request_data):
        for i in range(3):
            response = requests.post(url=rpc_url, data=json.dumps(request_data), headers=headers)
            if i > 1:
                print(f"response loop has gone for {i} iterations; the current response is: {response}")
            if response.status_code == 200:
                return self.get_result(response)
            elif response.status_code == 429:
                wait_time = int(response.headers.get("Retry-After", 5))
                time.sleep(wait_time)
        return response

    def get_transaction(self, slot, signature):
        return self.get_response("getTransaction", [signature, {"maxSupportedTransactionVersion": 0}])

    def fetch_account_data(self, account):
        return self.json_rpc_call("AddressLookupTableAccount", [account, {"maxSupportedTransactionVersion": 0}])

    def get_signature_for_address(self, account=None, address=None, limit=10, until=None, after=None, finalized=True):
        account = account or address
        conditions = self.get_conditions({
            "limit": limit,
            "until": until,
            "after": after,
            "finalized": finalized,
        })
        return self.json_rpc_call("getSignaturesForAddress", [account, conditions])

    def get_account_info(self, account=None, address=None, encoding='jsonParsed'):
        account = account or address
        conditions = self.get_conditions({"encoding": encoding})
        return self.json_rpc_call("getAccountInfo", [account, conditions])

    def get_token_account_balance(self, account=None, address=None, mint=None):
        account = account or address
        conditions = self.get_conditions({"mint": mint, "commitment": 0})
        return self.json_rpc_call("getTokenAccountBalance", [account, conditions])

    def get_token_accounts_by_delegate(self, account=None, address=None, programId=None, encoding='jsonParsed'):
        account = account or address
        conditions = self.get_conditions({"programId": programId, "encoding": encoding})
        return self.json_rpc_call("getTokenAccountsByDelegate", [account, conditions])

    def get_token_accounts_by_owner(self, account=None, address=None, mint=None, encoding='jsonParsed'):
        account = account or address
        conditions = self.get_conditions({"mint": mint, "encoding": encoding})
        return self.json_rpc_call("getTokenAccountsByOwner", [account, conditions])

    def get_all_signatures(self, address, before=None, after=None, blockTime=None, slot=None, get_any=False, limit=1000):
        n_sig = 0 if after else -1
        direction = [after, before]
        last_signature = direction[n_sig]
        all_valid_signatures = []
        while True:
            signatures = self.get_signature_for_address(address, limit=limit, before=direction[0], after=direction[-1])
            if get_any or not is_full_call(signatures, limit) or is_last_signature_the_comp(signatures, direction[n_sig]) or check_before_and_after(signatures, blockTime=blockTime, slot=slot):
                if (is_last_signature_the_comp(signatures, direction[n_sig]) or check_before_and_after(signatures, blockTime=blockTime, slot=slot)) or not is_full_call(signatures, limit):
                    all_valid_signatures = combine_signatures(all_valid_signatures, signatures, n_sig)
                if all_valid_signatures or not is_full_call(signatures, limit):
                    return all_valid_signatures
            all_valid_signatures = combine_signatures(all_valid_signatures, signatures, n_sig)
            direction[n_sig] = signatures[n_sig]['signature']

    def get_token_supply(self, token):
        return self.json_rpc_call("getTokenSupply", [token])

    def get_block_time_from_slot(self, slot):
        return self.json_rpc_call("getBlockTime", [int(slot)])

    def json_rpc_call(self, call_type, params):
        signature = params[0] if isinstance(params[0], str) else None
        existing_response = fetch_response_data(signature, call_type)
        if existing_response:
            return existing_response

        response = self.rpc_call(call_type, params)
        if isinstance(response, dict) and response.get('error') is not None:
            return response

        preSave_response(call_type,params,response)
        return response
