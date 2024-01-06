import aiohttp
import base64
import json

async def check_staking_contract(staking_contract, owner):
    token_ids = []
    async with aiohttp.ClientSession() as session:
        data = r'{"get_staked_nfts":{"address":"<owner>"}'.replace("<owner>", owner)
        data_decoded = base64.b64encode(data.encode()).decode()
        url = f"https://lcd.injective.network/cosmwasm/wasm/v1/contract/{staking_contract}/smart/{data_decoded}"
        async with session.get(url, ssl=False) as resp:
            response_text = await resp.text()

        if response_text:
            response_data = json.loads(response_text)
            if "code" in response_data and response_data["code"] == 2:  
                pass
            else:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}")
                json_string = response_text[json_start:json_end + 1]
                json_data = json.loads(json_string)

                for item in json_data['data']['nft_maps']:
                    token_ids.append(item['nft_id'])

    return token_ids

async def check_staking_contract_injboys(staking_contract, owner):
    token_ids = []
    async with aiohttp.ClientSession() as session:
        data = r'{"get_staked_nfts":{"collection_address":"inj16m9n05n80uylxaafk32qyha38fmwcfpssnpfak","address":"<owner>"}}'.replace("<owner>", owner)
        data_decoded = base64.b64encode(data.encode()).decode()
        url = f"https://lcd.injective.network/cosmwasm/wasm/v1/contract/{staking_contract}/smart/{data_decoded}"
        async with session.get(url, ssl=False) as resp:
            response_text = await resp.text()

        if response_text:
            response_data = json.loads(response_text)
            if "code" in response_data and response_data["code"] == 2:  
                pass
            else:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}")
                json_string = response_text[json_start:json_end + 1]
                json_data = json.loads(json_string)

                for item in json_data['data']['nft_maps']:
                    token_ids.append(item['nft_id'])

    return token_ids
