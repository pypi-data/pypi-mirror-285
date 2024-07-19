#solcana_client_manager
import os
import json
import base64
import base58
from solana.rpc.api import Client
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.signature import Signature
from solana.rpc.commitment import Commitment
from solana.rpc.types import TokenAccountOpts
from abstract_security.envy_it import get_env_value
from abstract_utilities import read_from_file,make_list
from abstract_utilities import write_to_file,safe_dump_to_file,safe_read_from_json
def get_jupiter_quote_url():
    return "https://quote-api.jup.ag/v6/quote"
def get_jupiter_api_swap_url():
    return "https://quote-api.jup.ag/v6/swap"
def get_raydium_liquidity_pool_wallet():
    return "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"
def get_wsol_mint_address():
    return "So11111111111111111111111111111111111111112"
def get_usdc_mint_address():
    return "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
def get_client_rpc(net_type="main",protocol='https'):
    net_type = {"main":"mainnet-beta","dev":"devnet","test":"testnet","default":"http://192.168.1.88:8899"}.get(net_type,"mainnet-beta")
    return f"{protocol}://api.{net_type}.solana.com"
def get_custom_rpc(key=None,domain="rpc.ankr.com",network="solana"):
    if key:
        return f"https://{domain}/{network}/{key}"
    return get_client_rpc()
def get_custom_wss(key=None,domain="rpc.ankr.com",network="solana"):
    if key:
        return f"wss://{domain}/{network}/ws/{key}"
    return get_client_rpc(net_type="main",protocol='ws')
def deserialize_data(data):
    # Example of deserializing data. This needs to be tailored to the specific serialization format.
    # For instance, if it's base58 encoded, you can use base58 library to decode it.
    # If it's Borsh serialized, you'd use a Borsh deserialization process.
    try:
        decoded_data = base58.b58decode(data)
        return decoded_data
    except Exception as e:
        print(f" could not get base58 from {data}:\n{e}")
        return data
def deserialize_base64_data(data):
    # This function is for deserializing data encoded in base64.
    try:
        # Decode the base64 data
        decoded_data = base64.b64decode(data)
        return decoded_data
    except Exception as e:
        print(f"Could not decode base64 data from {data}:\n{e}")
        return None
def correct_and_decode_base64(data):
    try:
        # Corrects any padding issues by adding the necessary padding
        padding = 4 - (len(data) % 4)
        data += "=" * padding
        return base64.b64decode(data)
    except Exception as e:
        print(f"Could not decode base64 data: {e}")
        return None

def load_from_private_key(env_key='AMM_P'):
    env_value = get_env_value(key=env_key)
    if env_value:
        return Keypair.from_base58_string(env_value)
    
def get_user_pub_key():
    return load_from_private_key('AMM_P').pubkey()

def load_keypair_from_file(filename):
    curr = os.path.join(sys.path[0], 'data',  filename)
    with open(curr, 'r') as file:
        secret = json.load(file)
        secret_key = bytes(secret)
        # print(base58.b58encode(secret_key))
        return Keypair.from_bytes(secret_key)
    
def get_pub_key(address):
    if pubkey_type() != type(address):
        try:
            tokenPk = Pubkey.from_string(address)
            return tokenPk
        except Exception as e:
            print("public key could not be derived: {e}")
            return None
    return address

def pubkey_type():
    return type(Pubkey.from_string("6fvys6PkSCgZcrDCCkYp56BjLMKZ41ySZK6qtgzX49Hg"))

def is_valid_solana_address(address):
    try:
        # This will throw an exception if the address is not valid
        Pubkey(address)
        return True
    except:
        return False
def check_and_reserialize_solana_address(address):
    try:
        # Attempt to create a PublicKey instance
        pubkey = Pubkey(address)
        # Re-serialize the address (This step is typically not necessary for Solana addresses)
        reserialized_address = str(pubkey)
        return reserialized_address
    except Exception as e:
        print(f"Invalid Solana address: {e}")
        return address

def get_all_imports(keyword, case_sensitive=False, include_imports=True):
    directory = "/home/joben/Desktop/txns_sol/solana-py-master"
    keywords = make_list(keyword)
    all_imports = set()
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        line_processed = line if case_sensitive else line.lower()
                        if any((kw.lower() if not case_sensitive else kw) in line_processed for kw in keywords):
                            if include_imports and (line_processed.startswith('import ') or line_processed.startswith('from ')):
                                all_imports.add(line_processed.strip())
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

    for each in sorted(all_imports):
        print(each)
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
def get_ctx(net_type=None,rpc_url=None,key=None,domain="rpc.ankr.com",network="solana",commitment="confirmed",timeout=30,blockhash_cache=True):
    rpc_url = rpc_url or get_custom_rpc(key=key,domain=domain,network=network)
    cli=Client(rpc_url, commitment=Commitment(commitment), timeout=30)
    #print("about to check connection")
    #print("here is the connection: ", cli.is_connected())
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
    if os.path.isfile(wallet_keypair):
        wallet_keypair = load_keypair_from_file(wallet_keypair)

    # Convert the mint address to a Pubkey object
    mint_pubkey = pubkey_from_mint(mint)

    # Get the associated token address for the wallet and the mint
    associated_token_address = await get_associated_token_address(
        wallet_keypair.public_key,  # The wallet public key
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
