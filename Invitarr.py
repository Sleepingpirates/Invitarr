#Copyright 2020 Sleepingpirate. 
from os import environ
import discord
from discord.ext import commands
import asyncio
from plexapi.myplex import MyPlexAccount
from discord import Webhook, AsyncWebhookAdapter
import aiohttp

# settings
Discord_bot_token = '' 
roleid =            # Role Id, right click the role and copy id.  
PLEXUSER = ''           # Plex Username
PLEXPASS = ''           # plex password
PLEX_SERVER_NAME = ''   # Name of plex server 
Plex_LIBS = [] #name of the libraries you want the user to have access to.
chan =  #Channel id of the channel you want to log emails and use -plexadd in. 
auto_remove_user = environ.get('autoremoveuser') if environ.get('autoremoveuser') else False # auto remove user from plex and db if removed from the role

if auto_remove_user:
    print("auto remove user = True")
    import db as db

account = MyPlexAccount(PLEXUSER, PLEXPASS)
plex = account.resource(PLEX_SERVER_NAME).connect()  # returns a PlexServer instance

def plexadd(plexname):
    try:
        plex.myPlexAccount().inviteFriend(user=plexname, server=plex, sections=Plex_LIBS, allowSync=False,
                                              allowCameraUpload=False, allowChannels=False, filterMovies=None,
                                              filterTelevision=None, filterMusic=None)

    except Exception as e:
        print(e)
        return False
    else:
        print(plexname +' has been added to plex (☞ຈل͜ຈ)☞')
        return True


def plexremove(plexname):
    try:
        plex.myPlexAccount().removeFriend(user=plexname)
    except Exception as e:
        print(e)
        return False
    else:
        print(plexname +' has been removed from plex (☞ຈل͜ຈ)☞')
        return True

class MyClient(discord.Client):
    async def on_ready(self):
        print('Made by Sleepingpirate https://github.com/Sleepingpirates/')
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def on_member_update(self, before, after):
        role = after.guild.get_role(roleid)
        if (role in after.roles and role not in before.roles):
            await after.send('Welcome To '+ PLEX_SERVER_NAME +'. Just reply with your email so we can add you to Plex!')
            await after.send('I will wait 10 minutes for your message, if you do not send it by then I will cancel the command.')
            def check(m):
                return m.author == after and not m.guild
            try:
                email = await client.wait_for('message', timeout=600, check=check)
            except asyncio.TimeoutError:
                await after.send('Timed Out. Message Server Admin So They Can Add You Manually.')
            else:
                await asyncio.sleep(5)
                await after.send('Got it we will be processing your email shortly')
            print(email.content) #make it go to a log channel
            plexname = str(email.content)
            if plexadd(plexname):
                if auto_remove_user:
                    db.save_user(after.display_name, email.content)
                await asyncio.sleep(20)
                await after.send('You have Been Added To Plex!')
                secure = client.get_channel(chan)
                await secure.send(plexname + ' ' + after.mention + ' was added to plex')
            else:
                await after.send('There was an error adding this email address. Message Server Admin.')
        elif(role not in after.roles and role in before.roles):
            if auto_remove_user:
                try:
                    username = after.display_name
                    email = db.get_useremail(username)
                    plexremove(email)
                    deleted = db.delete_user(username)
                    if deleted:
                        print("Removed {} from db".format(email))
                    else:
                        print("Cannot remove this user from db.")
                except:
                    print("Cannot remove this user from plex.")

    async def on_message(self, message):
        secure = client.get_channel(chan)
        if message.author.id == self.user.id:
            return

        if str(message.channel) == str(secure):
            if message.content.startswith('-plexadd'):
                mgs = message.content.replace('-plexadd ','')
                if plexadd(mgs):
                    await message.channel.send('The email has been added! {0.author.mention}'.format(message))
                else:
                    message.channel.send('Error Check Logs! {0.author.mention}'.format(message))
            if message.content.startswith('-plexrm'):
                mgs = message.content.replace('-plexrm ','')
                if plexremove(mgs):
                    await message.channel.send('The email has been removed! {0.author.mention}'.format(message))
                else:
                    message.channel.send('Error Check Logs! {0.author.mention}'.format(message))
            if message.content.startswith('-adddb'):
                mgs = message.content.replace('-adddb ','')
                try:
                    mgs = mgs.split(' ')
                    email = mgs[0]
                    username = mgs[1].replace('@', '').split('#')[0]
                    db.save_user(username, email)
                    await message.channel.send('The user {} has been added to db!'.format(mgs[1]))
                except:
                    print("Cannot add this user to db.")

client = MyClient()
client.run(Discord_bot_token)
