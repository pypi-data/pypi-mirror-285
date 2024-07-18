from .bot_functions import get_any_value,exponential
from .abstract_rpcs import rpcCallManager
rpc_mgr = rpcCallManager()
def get_supply_from_raw(raw_supply):
    value = get_any_value(raw_supply,'value')
    amount = get_any_value(value,'uiAmount')
    return amount or value or raw_supply
def get_amount_dict(amount,decimals=9):
    if amount!= None:
        if isinstance(amount,dict):
            amount_dict = get_any_value(amount,'uiTokenAmount')
            amount = get_any_value(amount_dict,'amount')
            decimals = get_any_value(amount_dict,'decimals')
        return exponential(amount,decimals,-1)
def get_decimals(mint):
    return get_any_value(get_account_info_dict(mint),'decimals')
def get_account_info_dict(mint):
    return rpc_mgr.get_account_info(mint)
def get_token_supply_dict(mint):
    return rpc_mgr.get_token_supply(mint)
def get_lamports_from_amount(amount,mint):
    return int(exponential(amount,exp=get_decimals(mint),num=1))
def get_lamports_per_token(mint):
    return int(exponential(1,exp=get_decimals(mint),num=1))
def get_amount_from_lamports(lamports,mint):
    return exponential(lamports,exp=get_decimals(mint),num=-1)
