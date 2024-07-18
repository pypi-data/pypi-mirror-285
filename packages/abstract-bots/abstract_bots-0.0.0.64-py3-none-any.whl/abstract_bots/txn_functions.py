from .bot_functions import safe_get,get_any_value,exponential
def search_for_account_index(data,index_number):
    for index_data in data:
        if str(safe_get(index_data,['accountIndex'])) == str(index_number):
            return index_data
def get_amount_dict(amount,decimals=9):
    if amount!= None:
        if isinstance(amount,dict):
            amount_dict = get_any_value(amount,'uiTokenAmount')
            amount = get_any_value(amount_dict,'amount')
            decimals = get_any_value(amount_dict,'decimals')
        return exponential(amount,decimals,-1)
def calculate_change(pre,post,decimals=9):
    if pre !=None and post!=None:
        return get_amount_dict(pre,decimals) - get_amount_dict(post,decimals)
def get_acct_index(txn_details,acct_index):
    for each in txn_details:
        if each['accountIndex'] == acct_index:
            return each
def get_account_keys(signature_data):
    accountKeys = get_any_value(signature_data,'accountKeys')
    loaded_addresses = get_any_value(signature_data,'loadedAddresses')
    for key,value in loaded_addresses.items():
        accountKeys+=value
    return accountKeys
def create_token_txns(signature_data):
    preTokenBalances = get_any_value(signature_data,'preTokenBalances')
    postTokenBalances = get_any_value(signature_data,'postTokenBalances')
    account_keys = get_account_keys(signature_data)
    txns=[]
    dont_use = []
    all_txns = {"Address":[],"Owner":[],'Balance Before':[],"Balance After":[],"Change":[],"Token":[]}
    for i,each in enumerate([preTokenBalances,postTokenBalances]):
        for post in each:
            index = post['accountIndex']
            if index not in dont_use:
                dont_use.append(index)
                after = get_amount_dict(get_acct_index(postTokenBalances,index))
                change = get_amount_dict(post)
                if after!=None and change !=None:
                    before = after-change
                    if i == 0:
                        pre_change = change
                        change = before
                        before = pre_change
                    all_txns["Address"].append(safe_get(account_keys,index))
                    all_txns["Owner"].append(safe_get(post,['owner']))
                    all_txns['Balance Before'].append(before)
                    all_txns["Balance After"].append(after)
                    all_txns["Change"].append(change)
                    all_txns["Token"].append(safe_get(post,['mint']))
                    #asset_mgr.return_token_info(address=post['mint'], address_type="token")
    return all_txns
def get_solana_balances(signature_data):
    balance = []
    preBalances = get_any_value(signature_data,'preBalances')
    postBalances = get_any_value(signature_data,'postBalances')
    account_keys = get_account_keys(signature_data)
    all_txns = {"Address":[],'Balance Before':[],"Balance After":[],"Change":[]}
    for i, amt in enumerate(preBalances):
        balance_change = [exponential(amt, 9,-1), -exponential(postBalances[i], 9,-1)]
        balance.append(balance_change)
          
        address = account_keys[i]
        all_txns['Address'].append(address)
        #asset_mgr.return_token_info(address=address, address_type="account")
        all_txns['Balance Before'].append(balance[-1][0])
        all_txns['Balance After'].append(balance[-1][1])
        all_txns['Change'].append(sum(balance[-1]))
    return all_txns
def get_all_txns(signature_data):
    output_js={}
    result = get_solana_balances(signature_data)
    output_js['solana']=result
    result = create_token_txns(signature_data)
    output_js['Token']=result
    return output_js
def parse_pool_data(logMessages):
    log_messages_string = str(get_any_value(logMessages,'logMessages') or logMessages)
    new_js={}
    init_split = log_messages_string.split('InitializeInstruction2 {')[1]
    brac_split = init_split.split('}')[0].replace(' ','')
    for each in brac_split.split(','):
        each=each.split(':')
        new_js[each[0]] = each[1]
    return new_js
