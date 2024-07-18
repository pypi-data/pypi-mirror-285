from .bot_functions import get_any_value,safe_get,is_number
from .txn_functions import get_account_keys
def get_supply_from_raw(raw_supply):
    value = get_any_value(raw_supply,'value')
    amount = get_any_value(value,'uiAmount')
    return amount or value or raw_supply
def get_token(amount):
    if amount:
        token = 'So11111111111111111111111111111111111111112'
        if isinstance(amount,dict):
            token = safe_get(amount,['mint'])
        return token
def is_within_range(i,value,comp_value):
  if value and is_number(value):
    small_value = float(value)-float(i)
    big_value = float(value)+float(i)
    if comp_value and is_number(comp_value):
      comp_value = float(comp_value)
      if comp_value>=small_value and comp_value<=big_value:
        return True
def get_price_if_avaliable(comp_address,price_data,block_time,time_range=5):
  prices = {}
  for address,values in price_data.items():
    for value in [int(value) for value in list(values["prices"].keys()) if is_within_range(time_range,block_time,value)]:
        if comp_address in values["prices"][str(value)].keys():
          
          if address not in prices:
            prices[address]=[]
          prices[address]+=values["prices"][str(value)][comp_address]["prices"]
  if prices:
    for address,pricing in prices.items():
      pricing = [price for price in prices[address] if float(price) != float(0)]
      if pricing:
        prices[address] = sum(pricing)/len(pricing)
      else:
        prices[address] = pricing
  return prices
def get_names(price_data,mint,knowns):
    if mint in knowns.values() and price_data[mint]["name"] == None:
        for name,value in knowns.items():
          if value == mint:
            price_data[mint]["name"]=name
    return price_data
def get_mint(price_data,mint):
    if mint not in price_data:
        price_data[mint]={"name":None,"chain":"solana","signatures":[],"prices":{}}
    return price_data
def get_block_time(price_data,mint,mint_2,blockTime):
    if blockTime not in price_data[mint]["prices"]:
        price_data[mint]["prices"][blockTime] = {}
    return price_data
def get_block_time_data(price_data,mint,mint_2,blockTime):
    if mint_2 not in price_data[mint]["prices"][blockTime]:
        price_data[mint]["prices"][blockTime][mint_2] = {"price":None,"prices":[]}
    return price_data
def get_signature_price(price_data,mint,mint_2,tokens,blockTime,signature):
    if signature not in price_data[mint]["signatures"]:
        price_data[mint]["prices"][blockTime][mint_2]["prices"].append(abs(float(tokens[-1][mint]['change'])/float(tokens[-1][mint_2]['change'])))
        price_data[mint]["signatures"].append(signature)
    return price_data
def get_prices(mint,blockTime,address):
    return price_data[mint]["prices"][blockTime][address]['price']
def print_token_amt(signature_data,i):
  account_keys = get_account_keys(signature_data)
  preTokens = get_any_value(signature_data,'preTokenBalances')
  postTokens = get_any_value(signature_data,'postTokenBalances')
  postTokens = [index for index in postTokens if index.get('accountIndex') == i]
  preTokens = [index for index in preTokens if index.get('accountIndex') == i]
  if postTokens and preTokens:
    account=None
    postAccount=None
    preAccount=None
    preToken =preTokens[0]
    postToken=postTokens[0]
    pre_balance = get_any_value(preToken,'uiAmount')
    post_balance = get_any_value(postToken,'uiAmount')
    if pre_balance != None and post_balance != None:
      change = post_balance-pre_balance 
      postOwner = postToken.get('owner')
      preOwner = preToken.get('owner')
      postProgramId = postToken.get('programId')
      preProgramId = preToken.get('programId')
      postAccountIndex=postToken.get('accountIndex')
      preAccountIndex=preToken.get('accountIndex')
      postMint=postToken.get('mint')
      preMint=preToken.get('mint')

      if preAccountIndex != None:
        preAccount=account_keys[preAccountIndex]
      if postAccountIndex != None:
        postAccount=account_keys[postAccountIndex]
      
      if change:
        #print(f'\nchange {change}\npostOwner={postOwner}\npostProgramId={postProgramId}\npostAccount={postAccount}\npostMint={postMint}\n')
        #input()
        return [postMint,change]
def get_usd_price(price_data,signature_data,knowns):
    #print(f"\n\nsignature {signature}")
    tokens = [{}]
    account_keys = get_account_keys(signature_data)
    signature = safe_get(get_any_value(signature_data,'signatures'),[0])
    blockTime = get_any_value(signature_data,'blockTime')
    postBalances = get_any_value(signature_data,'postBalances')
    preBalances = get_any_value(signature_data,'preBalances')
    fee = get_any_value(signature_data,'fee')
    #if fee:
    #print(f"fee = {fee*(10**(-9))}")
    for j,preBalance in enumerate(preBalances):
        sol_change = postBalances[j] - preBalance
        token = print_token_amt(signature_data,j)
        if token:
            keys = list(tokens[-1].keys())
            if tokens[0] not in keys:
                tokens[-1][token[0]]={"change":token[1],"price":{},"prices":{}}
            if len(keys) == 2:
                for key_num,key in enumerate(keys):
                    key_now = key_num-1
                    mint = keys[key_num]
                    mint2=keys[key_now]
                    price_data = get_mint(price_data,mint)
                    price_data = get_names(price_data,mint,knowns)
                    price_data = get_block_time(price_data,mint,mint2,blockTime)
                    price_data = get_block_time_data(price_data,mint,mint2,blockTime)
                    price_data = get_signature_price(price_data,mint,mint2,tokens,blockTime,signature)
                    #print(f"{price_data[keys[key_num]]['name'] or keys[key_num]} worth:\n")
                    for address,price in get_price_if_avaliable(keys[key_num],price_data,blockTime).items():
                        #input(price_data[keys[key_num]]["prices"][blockTime])
                        if price:                  
                            if address not in price_data[keys[key_num]]["prices"][blockTime]:
                                price_data[keys[key_num]]["prices"][blockTime][address]={'price':None,'prices':[]}
                            if price_data[keys[key_num]]["prices"][blockTime][address]['price'] == None:
                                price_data[keys[key_num]]["prices"][blockTime][address]['price'] = price
                            else:
                                price_data[keys[key_num]]["prices"][blockTime][address]['price'] = float(price_data[keys[key_now]]["prices"][blockTime][keys[key_num]]['price'] + price)      
    return price_data
