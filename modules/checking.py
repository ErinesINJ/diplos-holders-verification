import asyncio
import discord
import certifi
import aiohttp
from pymongo import MongoClient


from checking_nfts.check_holder import fetch_data
from database.user_db import find_user_wallet_in_db, get_all_user_ids
from database.collection import get_guild_information, get_all_tokens_by_id

async def async_while_true(guild: discord.Guild):
    mongo_client = MongoClient(
        "mongodb+srv://deryplos:0AwyF3G51kegwjf8@cluster0.3zzwmsy.mongodb.net/?retryWrites=true&w=majority",
        tlsCAFile=certifi.where())

    while True:
        try:
            guild_settings = await asyncio.wait_for(get_guild_information(mongo_client, guild.id), timeout=30)
            holder_roles = guild_settings['roles_amount']
            holder_trait_roles = guild_settings['roles_traits']
            collection_id = guild_settings['collection']
            collection_address = guild_settings['collection_address']
            staking_contract = guild_settings['staking_contract']
            paid = guild_settings['paid']
            try:
                role_map = {}
                for role in guild.roles:
                    if any(role.id == holder_role['id'] for holder_role in holder_roles):
                        role_map[role.id] = role
                    if any(role.id == holder_trait_role['id'] for holder_trait_role in holder_trait_roles):
                        role_map[role.id] = role
            except Exception as e:
                print(f'[CHECKER] [-] Error creating role map: {e}')
                continue
        except Exception as e:
            print(f'[CHECKER] [-] Failed to fetch guild information: {e}')
            return

        if not paid:
            print(f'[PAYMENT] [{collection_id}] NOT PAID')
            print(f'[PAYMENT] [{collection_id}] NOT PAID')
            print(f'[PAYMENT] [{collection_id}] NOT PAID')
            await asyncio.sleep(600)
            continue

        try:
            await asyncio.sleep(1)
            print("[CHECKER] [?] Checking users and roles...")
            user_ids = await asyncio.wait_for(get_all_user_ids(mongo_client), timeout=30)
            for user_id in user_ids:
                try:
                    member = guild.get_member(int(user_id))
                    if member is None:
                        continue

                    wallets = await asyncio.wait_for(find_user_wallet_in_db(mongo_client, user_id), timeout=30)

                    result = []
                    for wallet in wallets:
                        try:
                            nfts = await asyncio.wait_for(fetch_data(str(collection_address), staking_contract, str(wallet)), timeout=30)
                            if nfts:
                                result.extend(nfts)
                        except:
                            pass

                    # token_traits = await get_all_tokens_by_id(mongo_client, collection_id, result)
                    
                    # if holder_trait_roles:
                    #     for trait_role in holder_trait_roles:
                    #         found_match = False
                    #         for token in token_traits:
                    #             for trait in token['traits']:
                    #                 if trait.get('Type') == trait_role.get('Type') and trait.get('Value') == trait_role.get('Value'):
                    #                     role_id = trait_role['id']
                    #                     discord_role = role_map.get(role_id)
                    #                     if discord_role not in member.roles:
                    #                         await member.add_roles(discord_role)
                    #                         print(f"[CHECKER] [+] Added role {discord_role.name} to {member.name}")
                    #                     found_match = True
                    #                     break
                    #             if found_match:
                    #                 break
                    #         if not found_match:
                    #             role_id = trait_role['id']
                    #             discord_role = role_map.get(role_id)
                    #             if discord_role in member.roles:
                    #                 await member.remove_roles(discord_role)
                    #                 print(f"[CHECKER] [-] Removed role {discord_role.name} from {member.name}")

                    for holder_role in holder_roles:
                        await asyncio.sleep(0.2)
                        role_id = holder_role['id']
                        discord_role = role_map.get(role_id)

                        if len(result) >= holder_role['min']:
                            if discord_role not in member.roles:
                                await member.add_roles(discord_role)
                                print(f"[CHECKER] [+] Added role {discord_role.name} to {member.name}")
                        else:   
                            if discord_role in member.roles:
                                await member.remove_roles(discord_role)
                                print(f"[CHECKER] [+] Removed role {discord_role.name} from {member.name}")
                    print(f"[CHECKER] [{collection_id}] [+] Checked {member.name}")
                    await asyncio.sleep(2)
                except Exception as e:
                    print(f"[CHECKER] [-] Error checking user {user_id}: {e}")
                    continue
        except Exception as e:
            print(f"[CHECKER] [-] Exception in loop: {e}")