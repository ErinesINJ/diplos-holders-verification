import certifi
import discord
from discord.ext import commands
import discord.ui
import time
import aiohttp

from pymongo import MongoClient

from database.collection import  get_guild_information, get_all_tokens_by_id
from database.user_db import find_user_wallet_in_db
from modules.checking import async_while_true
from checking_nfts.check_holder import fetch_data

mongo_key = ""
discord_token = ""

instruction = """1. Connect your wallet and discord account 
Website: https://diplosverification.vercel.app/
2. Click Verify Button

⚠️⚠️⚠️ **Warning** ⚠️⚠️⚠️

We are experiencing some issues with Discord Connect. Connect wallet and try to connect your discord account until Address and Discord appear (check image below), usually up to 4 tries."""

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print('Bot connected')
        
class verification_ui(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label='Verify', style=discord.ButtonStyle.green)
    async def one(self, interaction: discord.Interaction, _: discord.ui.Button):
        try:
            await interaction.response.defer()
            guild = interaction.guild

            guild_settings = await get_guild_information(mongo_client, guild.id)

            if not guild_settings['paid']:
                await interaction.followup.send('Holder verification is unavailable for this guild due to subscription payment issues.', ephemeral=True)
            
            user = interaction.user

            wallets = await asyncio.wait_for(find_user_wallet_in_db(mongo_client, str(user.id)), timeout=30)

            if not wallets:
                await interaction.followup.send('**Your address is not verified**\n\nPlease go to https://diplosverification.vercel.app/ and connect your discord account with wallet address ', ephemeral=True)
            else:
                await interaction.followup.send('Bot is checking NFTs ownership right now...', ephemeral=True)
                holder_roles = guild_settings['roles_amount']
                holder_trait_roles = guild_settings['roles_traits']
                collection_id = guild_settings['collection_id']
                collection_address = guild_settings['collection_address']
                staking_contract = guild_settings['staking_contract']

                result = []
                for wallet in wallets:
                    try:
                        nfts = await asyncio.wait_for(fetch_data(str(collection_address), staking_contract, str(wallet)), timeout=30)
                        if nfts:
                            result.extend(nfts)
                    except:
                        pass

                roles_to_add = []

                # token_traits = await get_all_tokens_by_id(mongo_client, collection_id, result)

                # if holder_trait_roles:
                #     for trait_role in holder_trait_roles:
                #         found_match = False
                #         for token in token_traits:
                #             for trait in token['traits']:
                #                 if trait.get('Type') == trait_role.get('Type') and trait.get('Value') == trait_role.get('Value'):
                #                     discord_role = discord.utils.get(guild.roles, id=trait_role['id'])
                #                     if discord_role not in user.roles:
                #                         await user.add_roles(discord_role)
                #                     found_match = True
                #                     break
                #             if found_match:
                #                 break
                #         if not found_match:
                #             discord_role = discord.utils.get(guild.roles, id=trait_role['id'])
                #             if discord_role in user.roles:
                #                 await user.remove_roles(discord_role)
                    
                for role in holder_roles:
                    await asyncio.sleep(0.02)

                    if len(result) >= role["min"]:
                        discord_role = discord.utils.get(guild.roles, id=role['id'])
                        if discord_role not in user.roles:
                            roles_to_add.append(discord_role)
                            await user.add_roles(discord_role)

                if roles_to_add:
                    assigned_roles_text = ', '.join('@' + role.name for role in roles_to_add)
                    await interaction.followup.send(f'Assigned roles: {assigned_roles_text}', ephemeral=True)
                else:
                    await interaction.followup.send('No roles were assigned. All eligible roles already assigned. ', ephemeral=True)
        except Exception as e:
            print(f'Error tms: {e}')

    @discord.ui.button(label='Check Wallets', style=discord.ButtonStyle.blurple)
    async def check_wallets(self, interaction: discord.Interaction, _: discord.ui.Button):

        await interaction.response.defer()

        user = interaction.user
        wallets = await asyncio.wait_for(find_user_wallet_in_db(mongo_client, str(user.id)), timeout=30)
        wallets_text = '\n'.join(wallets)

        await interaction.followup.send(f'**Your Verified Wallets:**\n{wallets_text}', ephemeral=True)

    @discord.ui.button(label='📙HELP', style=discord.ButtonStyle.blurple)
    async def help(self, interaction: discord.Interaction, _: discord.ui.Button):

        await interaction.response.defer()

        await interaction.followup.send(f'Make Sure to read Instruction and Warning message. In case you can not verify join support server and open ticket\nSupport Server: https://discord.gg/PWRm4YYJev', ephemeral=True)
       
@bot.command()
@commands.is_owner()
async def hv_stp(ctx: commands.Context, eligible_role_id: str, old_channel: str, run_checker: str):
    guild = ctx.guild
    guild_settings = await get_guild_information(mongo_client, guild.id)
        
    if old_channel != 'None':
        channel = bot.get_channel(int(old_channel))
        if channel:
            await channel.purge()
            print("[+] All messages in the channel have been deleted.")
            support_channel = channel
        else:
            print("[-] Channel not found.")

    else:
        eligible_role = ctx.guild.get_role(int(eligible_role_id))

        eligible_role_perms = discord.PermissionOverwrite(
            view_channel=True,
            send_messages=False,
            read_message_history=True,
        )

        bot_perms = discord.PermissionOverwrite(
            view_channel=True,
            manage_channels=True,
            send_messages=True,
            manage_messages=True,
            read_message_history=True,
        )

        everyone_perms = discord.PermissionOverwrite(
            view_channel=False,
        )

        bot_member = ctx.guild.get_member(bot.user.id)

        everyone_role = None
        for role in guild.roles:
            if role.name == "@everyone":
                everyone_role = role

        support_category_overwrites = {
            bot_member: bot_perms,
            everyone_role: everyone_perms,
            eligible_role: eligible_role_perms
        }

        support_channel = await guild.create_text_channel("🦕│Holders Verification", overwrites=support_category_overwrites)
    
    view = verification_ui()
    view.timeout = None
    embed = discord.Embed(title='Holders Verification 🦕\n\nInstruction', description=instruction, color=discord.Color.blue())
    embed.set_image(url='https://cdn.discordapp.com/attachments/1165677634919858316/1183444405512835123/image.png')
    embed.set_footer(text='Developed by Injective Diplos', icon_url='https://cdn.discordapp.com/attachments/1165677634919858316/1183477800494186578/noR3gLwJ_400x400_2.jpg')
    await support_channel.send(embed=embed, view=view)

    if run_checker.lower() == "true":
        print("[+] Launching Checker")
        asyncio.create_task(async_while_true(guild))


async def main():
    global mongo_client

    try:    
        mongo_client = MongoClient(mongo_key, tlsCAFile=certifi.where())
        print("[+] Connected to MongoDB")
    except:
        print("[-] MongoDB connection failed")
        return
    await bot.start(discord_token)
    print("[+] Started holder verification bot")

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
