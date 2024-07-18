import os
import sys
import json
import requests
from solders.pubkey import Pubkey
from solana.rpc.api import Client,RPCException
from spl.token.client import Token
from solders.keypair import Keypair
from construct import Struct as cStruct
from solana.transaction import AccountMeta,Transaction
from solders.instruction import Instruction
from spl.token.instructions import close_account, CloseAccountParams
from abstract_security import get_env_value
from solana.rpc.types import TokenAccountOpts
from abstract_utilities import read_from_file,make_list,safe_dump_to_file,safe_read_from_json
from construct import Bytes, Int8ul, Int64ul, BytesInteger
from solders.system_program import TransferParams, transfer
from spl.token.core import _TokenCore
from solana.rpc.commitment import Commitment
from spl.token.instructions import create_associated_token_account, get_associated_token_address
from .abstract_keypair import load_from_private_key,load_keypair_from_file
from .abstract_rpcs import directory_mgr
def get_lamports_per_sol():
    return 1000000000

SERUM_PROGRAM_ID = Pubkey.from_string('srmqPvymJeFKQ4zGQed1GFppgkRHL9kaELCbyksJtPX')
def get_account_params(base_public_key,new_public_key,fee,PublicKey,space=8):
        return sp.CreateAccountParams(
            from_pubkey=base_public_key,
            new_account_pubkey=new_public_key,
            lamports=fee,
            space=space,
            program_id=PublicKey(1),
        )

def get_keypair(key_pair_file):
    with open (key_pair_file) as kpf:
        keypair = kpf.read()
        keypair = keypair.replace('[', '').replace(']','')
        keypair = list(keypair.split(','))
        keypair = [int(i) for i in keypair]
    return Account(keypair[:32])

def get_account_info(client, public_key):
    account_info = client.get_account_info(public_key)
    print("--> Account Info: {}".format(account_info))
    balance = client.get_balance(public_key)
    print("--> Balance: {}".format(balance))
def get_ctx(rpc_url="https://api.mainnet-beta.solana.com",commitment="confirmed",timeout=30,blockhash_cache=True):
    cli=Client(rpc_url, commitment=Commitment(commitment), timeout=30)
    print("about to check connection")
    print("here is the connection: ", cli.is_connected())
    return cli
def pubkey_from_mint(mint):
    return Pubkey.from_string(mint)
def get_account_program_id_from_mint(mint,ctx=get_ctx()):
    pubkey = pubkey_from_mint(mint)
    return ctx.get_account_info_json_parsed(pubkey)

def get_owner(obj):
    return obj.value.owner
def get_program_id_from_mint(mint):
    pubkey = pubkey_from_mint(mint)
    program_id = get_program_id_from_pubkey(pubkey)
    return program_id

def get_account_program_id(pubkey,ctx=get_ctx()):
    return ctx.get_account_info_json_parsed(pubkey)

def get_program_id_from_pubkey(pubkey):
    accountProgramId=get_account_program_id(pubkey)
    return accountProgramId.value.owner

def get_accounts(payer,programid,ctx=get_ctx()):
    return ctx.get_token_accounts_by_owner_json_parsed(payer.pubkey()  ,TokenAccountOpts(program_id=programid)).value

def get_token_balance_lamports_from_account(account):
    return int(account.account.data.parsed['info']['tokenAmount']['amount'])

def get_mint_from_account(account):
    return account.account.data.parsed['info']['mint']

async def send_transaction(tx, signers, ctx):
    try:
        response = await ctx.send_transaction(tx, *signers)
        return response
    except Exception as e:
        print(f"Error sending transaction: {e}")
        return None

def get_recent_blockhash(ctx):
    return ctx.get_recent_blockhash()['result']['value']['blockhash']

def get_token_supply(mint_pubkey, ctx):
    return ctx.get_token_supply(mint_pubkey)['result']['value']['amount']

def get_token_account_balance(account_pubkey, ctx):
    return ctx.get_token_account_balance(account_pubkey)['result']['value']['amount']

async def get_associated_token_account_from_mint_keypair_file(mint,wallet_keypair):
    #if os.path.isfile(wallet_keypair):
    #    wallet_keypair = load_keypair_from_file(wallet_keypair)

    # Convert the mint address to a Pubkey object
    mint_pubkey = pubkey_from_mint(mint)

    # Get the associated token address for the wallet and the mint
    associated_token_address = await get_associated_token_address(
        wallet_keypair.pubkey(),  # The wallet public key
        mint_pubkey                 # The mint public key
    )
    return associated_token_address
"""
Check balance of the token in your wallet
"""
def checkB(TOKEN_TO_SWAP_SELL, payer, ctx):
    tokenPk = pubkey_from_mint(TOKEN_TO_SWAP_SELL)
    accountProgramId = get_account_program_id(tokenPk)
    programid = get_program_id_from_pubkey(tokenPk)
    accounts = get_accounts(payer,programid,ctx=get_ctx())
    for account in accounts:
        tokenBalanceLamports = get_token_balance_lamports_from_account(account)
        mint = get_mint_from_account(account)
        if tokenBalanceLamports > 0 and mint == TOKEN_TO_SWAP_SELL:
            return True
    return False
def load_from_private_key(env_key='AMM_P'):
    env_value = get_env_value(key=env_key)
    if env_value:
        return Keypair.from_base58_string(env_value)

def load_keypair_from_file(filename):
    curr = os.path.join(sys.path[0], 'data',  filename)
    with open(curr, 'r') as file:
        secret = json.load(file)
        secret_key = bytes(secret)
        # print(base58.b58encode(secret_key))
        return Keypair.from_bytes(secret_key)


def make_swap_instruction(amount_in: int, token_account_in: Pubkey.from_string, token_account_out: Pubkey.from_string,
                              accounts: dict, mint, ctx, owner,AMM_PROGRAM_ID=None):
        AMM_PROGRAM_ID = AMM_PROGRAM_ID or Pubkey.from_string('675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8')
        tokenPk = mint
        TOKEN_PROGRAM_ID = get_program_id_from_mint(mint)
        keys = [
            AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
            AccountMeta(pubkey=accounts["amm_id"], is_signer=False, is_writable=True),
            AccountMeta(pubkey=accounts["authority"], is_signer=False, is_writable=False),
            AccountMeta(pubkey=accounts["open_orders"], is_signer=False, is_writable=True),
            AccountMeta(pubkey=accounts["target_orders"], is_signer=False, is_writable=True),
            AccountMeta(pubkey=accounts["base_vault"], is_signer=False, is_writable=True),
            AccountMeta(pubkey=accounts["quote_vault"], is_signer=False, is_writable=True),
            AccountMeta(pubkey=SERUM_PROGRAM_ID, is_signer=False, is_writable=False), 
            AccountMeta(pubkey=accounts["market_id"], is_signer=False, is_writable=True),
            AccountMeta(pubkey=accounts["bids"], is_signer=False, is_writable=True),
            AccountMeta(pubkey=accounts["asks"], is_signer=False, is_writable=True),
            AccountMeta(pubkey=accounts["event_queue"], is_signer=False, is_writable=True),
            AccountMeta(pubkey=accounts["market_base_vault"], is_signer=False, is_writable=True),
            AccountMeta(pubkey=accounts["market_quote_vault"], is_signer=False, is_writable=True),
            AccountMeta(pubkey=accounts["market_authority"], is_signer=False, is_writable=False),
            AccountMeta(pubkey=token_account_in, is_signer=False, is_writable=True),  #UserSourceTokenAccount 
            AccountMeta(pubkey=token_account_out, is_signer=False, is_writable=True), #UserDestTokenAccount 
            AccountMeta(pubkey=owner.pubkey(), is_signer=True, is_writable=False) #UserOwner 
        ]

        data = get_swap_layout().build(
            dict(
                instruction=9,
                amount_in=int(amount_in),
                min_amount_out=0
            )
        )
        return Instruction(AMM_PROGRAM_ID, data, keys)
def get_token_account(ctx, 
                      owner: Pubkey.from_string, 
                      mint: Pubkey.from_string):
    try:
        account_data = ctx.get_token_accounts_by_owner(owner, TokenAccountOpts(mint))
        return account_data.value[0].pubkey, None
    except:
        swap_associated_token_address = get_associated_token_address(owner, mint)
        swap_token_account_Instructions = create_associated_token_account(owner, owner, mint)
        return swap_associated_token_address, swap_token_account_Instructions

def sell_get_token_account(ctx, 
                      owner: Pubkey.from_string, 
                      mint: Pubkey.from_string):
    try:
        account_data = ctx.get_token_accounts_by_owner(owner, TokenAccountOpts(mint))
        return account_data.value[0].pubkey
    except:
        print("Mint Token Not found")
        return None


def extract_pool_info(pools_list: list, mint: str) -> dict:
    for pool in pools_list:
        
        if pool['baseMint'] == mint and pool['quoteMint'] == 'So11111111111111111111111111111111111111112':
            return pool
        elif pool['quoteMint'] == mint and pool['baseMint'] == 'So11111111111111111111111111111111111111112':
            return pool
    raise Exception(f'{mint} pool not found!')

def get_token_account(ctx, 
                      owner: Pubkey.from_string, 
                      mint: Pubkey.from_string):
    try:
        account_data = ctx.get_token_accounts_by_owner(owner, TokenAccountOpts(mint))
        return account_data.value[0].pubkey, None
    except:
        swap_associated_token_address = get_associated_token_address(owner, mint)
        swap_token_account_Instructions = create_associated_token_account(owner, owner, mint)
        return swap_associated_token_address, swap_token_account_Instructions

def reponse_json(response):
    try:
        response = responsse.json()
        return response
    except:
        return None
def get_pool_data(lp_mint):
    response = requests.get('https://api.raydium.io/v2/sdk/liquidity/mainnet.json',stream=True)
    if response.status_code == 200:
        safe_dump_to_file(data = response.json(),file_path=directory_mgr.all_pool_info_file)
    for pool_data in safe_read_from_json(directory_mgr.all_pool_info_file)['unOfficial']:
        if pool_data['lpMint'] == lp_mint:
            return pool_data
def get_pool_keys(liquidityPoolAddress=None):
    url='http://solcatcher.io:5000/get_pool_keys'
    headers = {"Content-Type":"application/json"}
    return requests.post(url,json={"liquidityPoolAddress":liquidityPoolAddress},headers=headers).json()

def get_pool_key_info(liquidityPoolAddress):
    amm_info = get_pool_keys(liquidityPoolAddress)
    return {
        'amm_id': Pubkey.from_string(amm_info['id']),
        'authority': Pubkey.from_string(amm_info['authority']),
        'base_mint': Pubkey.from_string(amm_info['baseMint']),
        'base_decimals': amm_info['baseDecimals'],
        'quote_mint': Pubkey.from_string(amm_info['quoteMint']),
        'quote_decimals': amm_info['quoteDecimals'],
        'lp_mint': Pubkey.from_string(amm_info['lpMint']),
        'open_orders': Pubkey.from_string(amm_info['openOrders']),
        'target_orders': Pubkey.from_string(amm_info['targetOrders']),
        'base_vault': Pubkey.from_string(amm_info['baseVault']),
        'quote_vault': Pubkey.from_string(amm_info['quoteVault']),
        'market_id': Pubkey.from_string(amm_info['marketId']),
        'market_base_vault': Pubkey.from_string(amm_info['marketBaseVault']),
        'market_quote_vault': Pubkey.from_string(amm_info['marketQuoteVault']),
        'market_authority': Pubkey.from_string(amm_info['marketAuthority']),
        'bids': Pubkey.from_string(amm_info['marketBids']),
        'asks': Pubkey.from_string(amm_info['marketAsks']),
        'event_queue': Pubkey.from_string(amm_info['marketEventQueue'])
            }

def get_pool_info_layout():
    return cStruct(
    "instruction" / Int8ul,
    "simulate_type" / Int8ul
    )

def get_swap_layout():
    return cStruct(
    "instruction" / Int8ul,
    "amount_in" / Int64ul,
    "min_amount_out" / Int64ul
    )

# Not in use right now, might be useful in future
def get_amm_info_layout_4():
    return cStruct(
    'status' / Int64ul,
    'nonce' / Int64ul,
    'order_num' / Int64ul,
    'depth' / Int64ul,
    'base_decimal' / Int64ul,
    'quote_decimal' / Int64ul,
    'state' / Int64ul,
    'reset_flag' / Int64ul,
    'min_size' / Int64ul,
    'vol_max_cut_ratio' / Int64ul,
    'amount_wave_ratio' / Int64ul,
    'base_lot_size' / Int64ul,
    'quote_lot_size' / Int64ul,
    'min_price_multiplier' / Int64ul,
    'max_price_multiplier' / Int64ul,
    'system_decimal_value' / Int64ul,
    # Fees
    'min_separate_numerator' / Int64ul,
    'min_separate_denominator' / Int64ul,
    'trade_fee_numerator' / Int64ul,
    'trade_fee_denominator' / Int64ul,
    'pnl_numerator' / Int64ul,
    'pnl_denominator' / Int64ul,
    'swap_fee_numerator' / Int64ul,
    'swap_fee_denominator' / Int64ul,
    # OutPutData
    'base_need_take_pnl' / Int64ul,
    'quote_need_take_pnl' / Int64ul,
    'quote_total_pnl' / Int64ul,
    'base_total_pnl' / Int64ul,
    # 128
    'quote_total_deposited' / BytesInteger(16, signed=False, swapped=True),
    'base_total_deposited' / BytesInteger(16, signed=False, swapped=True),
    'swap_base_in_amount' / BytesInteger(16, signed=False, swapped=True),
    'swap_quote_out_amount' / BytesInteger(16, signed=False, swapped=True),

    'swap_base2_quote_fee' / Int64ul,
    # 128
    'swap_quote_in_amount' / BytesInteger(16, signed=False, swapped=True),
    'swap_base_out_amount' / BytesInteger(16, signed=False, swapped=True),

    'swap_quote2_base_fee' / Int64ul,
    # AMM Vault
    'base_vault' / Bytes(32),
    'quote_vault' / Bytes(32),
    # Mint
    'base_mint' / Bytes(32),
    'quote_mint' / Bytes(32),
    'lp_mint' / Bytes(32),
    # Market
    'open_orders' / Bytes(32),
    'market_id' / Bytes(32),
    'serum_program_id' / Bytes(32),
    'target_orders' / Bytes(32),
    'withdraw_queue' / Bytes(32),
    'lp_vault' / Bytes(32),
    'amm_owner' / Bytes(32),

    'lpReserve' / Int64ul,
    )
