from flask import Flask, render_template, request
from ossapi import Ossapi
import requests
import json
import discord
import asyncio

names = ["Tournament not started","No players yet"]

class AuthServer:

    def __init__(self, bot: discord.Bot, verifyUpdateChannel, serverId, loop) -> None:
        self._bot = bot
        self._verify_update_channel_id = verifyUpdateChannel
        self._server_id = serverId
        self._loop = loop

    def index(self):
        return render_template('index.html', names=names)

    async def oauth_callback(self):
        authorization_code = request.args.get('code')
        discord_id = request.args.get('state')

        oauth_response = self._get_oauth_response(authorization_code)

        self._load_users

        if oauth_response.status_code != 200:
            return render_template('error.html', title="Mafiosu! Verify")

        access_token = oauth_response.json()['access_token']

        osu_id = str(self._get_osu_id(access_token))

        verify_update_channel = self._bot.get_channel(self._verify_update_channel_id)
        guild = self._bot.get_guild(self._server_id)
        member = guild.get_member(int(discord_id))
        

        if self._is_user_verified(discord_id, osu_id):
            asyncio.run_coroutine_threadsafe(verify_update_channel.send(f"User has tried to verify, but has already been verified before. <@{discord_id}> https://osu.ppy.sh/users/{osu_id}"), self._loop)
            asyncio.run_coroutine_threadsafe(member.send("You have already been verified before\nIf this is an alt account, go away\nIf this is a mistake, contact <@509028328947056693> in DMs"), self._loop)

            return render_template('already.html', title="Mafiosu! Verify")
        
        dictionary = {
            "discord_name": f"{member.name}",
            "discord_id": f"{discord_id}",
            "osu_id": f"{osu_id}"
        }

        await self._add_roles(member, osu_id, guild, verify_update_channel)

        self._write_json(dictionary)

        return render_template('complete.html', title="Mafiosu! Verify")

    def _write_json(self, new_data, filename='verified.json'):
        with open(filename, 'r+') as file:
            self._users = json.load(file)
            self._users["verified_users"].append(new_data)
            file.seek(0)

            json.dump(self._users, file, indent=4)

    def _is_user_verified(self, discord_id, osu_id) -> bool:
        for user in self._users['verified_users']:
            if discord_id == user['discord_id'] or osu_id == user['osu_id']:
                return True
        
        return False
    
    def _load_users(self, filename='verified.json'):
        with open(filename) as file:
            self._users = json.load(file)

    async def _add_roles(self, member: discord.Member, osu_id, guild: discord.Guild, update_channel: discord.TextChannel):
        asyncio.run_coroutine_threadsafe(member.add_roles(discord.utils.get(guild.roles, name="Member")), self._loop)
        asyncio.run_coroutine_threadsafe(update_channel.send(f"<@{member.id}> Has successfully verified their account. https://osu.ppy.sh/users/{osu_id}"), self._loop)
        asyncio.run_coroutine_threadsafe(member.send("Successfully verified\nEnjoy the server!"), self._loop)

    def _get_osu_id(self, access_token) -> int:
        return Ossapi(
            client_id='24127',
            client_secret='qJHR0ejwuxdJQGwaD5JKlLvoMvfIAahiU6vcmPDT',
            redirect_uri='https://verify.mafiosu.net/oauth-callback',
            scopes=["identify"],
            access_token=access_token
        ).get_me().id
    
    def _get_oauth_response(self, authorization_code) -> requests.Response:
        post_data = {
            'client_id': '24127',
            'client_secret': 'qJHR0ejwuxdJQGwaD5JKlLvoMvfIAahiU6vcmPDT',
            'code': authorization_code,
            'grant_type': 'authorization_code',
            'redirect_uri': 'https://verify.mafiosu.net/oauth-callback'
        }

        return requests.post('https://osu.ppy.sh/oauth/token', data=post_data)