import json
import requests
from httpx import AsyncClient
import asyncio
import aiohttp
import base64
import certifi

from checking_nfts.staking_contracts import check_staking_contract, check_staking_contract_injboys
                    
async def fetch_data(collection_address, staking_contract, owner):
    async with aiohttp.ClientSession() as session:
        try:
            token_ids = []
            last = 0

            data = r'{"tokens":{"owner":"<owner>", "limit":30}}'.replace("<owner>", owner)
            data_decoded = base64.b64encode(data.encode()).decode()
            url = f"https://lcd.injective.network/cosmwasm/wasm/v1/contract/{collection_address}/smart/{data_decoded}"
            async with session.get(url, ssl=False) as resp:
                nft_ids = await resp.json()
            try:
                if len(nft_ids["data"]["ids"]) > 0:
                    token_ids.extend(nft_ids["data"]["ids"])
                    last = nft_ids["data"]["ids"][-1]
            except:  
                if len(nft_ids["data"]["tokens"]) > 0:
                    token_ids.extend(nft_ids["data"]["tokens"])
                    last = nft_ids["data"]["tokens"][-1]
            finally:
                for i in range(1000):
                    data = r'{"tokens":{"owner":"<owner>", "limit":30, "start_after": "<last>"}}'.replace("<owner>", owner).replace("<last>", str(last))
                    data_decoded = base64.b64encode(data.encode()).decode()
                    url = f"https://lcd.injective.network/cosmwasm/wasm/v1/contract/{collection_address}/smart/{data_decoded}"
                    async with session.get(url, ssl=False) as resp:
                        nft_ids = await resp.json()
                    try:
                        if len(nft_ids["data"]["ids"]) > 0:
                            token_ids.extend(nft_ids["data"]["ids"])
                            last = nft_ids["data"]["ids"][-1]
                        elif len(nft_ids["data"]["ids"]) <= 0:
                            break
                    except:  
                        if len(nft_ids["data"]["tokens"]) > 0:
                            token_ids.extend(nft_ids["data"]["tokens"])
                            last = nft_ids["data"]["tokens"][-1]
                        elif len(nft_ids["data"]["tokens"]) <= 0:
                            break

            if staking_contract != "None":
                if staking_contract == "inj13zmkfd9v8fcj94tzfyay9u7fmk5w35u4358qek":
                    staking_token_ids = await check_staking_contract_injboys(staking_contract, owner)
                else:
                    staking_token_ids = await check_staking_contract(staking_contract, owner)

                if staking_token_ids:
                    token_ids.extend(staking_token_ids)
                
            return token_ids
        except Exception as e:
            print(e)