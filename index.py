import discord
from discord.utils import get

from flask import Flask, render_template, request, make_response
import asyncio
import base64
import json
# Import .py files
import auth_server

from discord.ext import tasks
import typing
from datetime import datetime, timedelta

TOKEN = 'MTEyMzkyMjkxNzIzMTcxMDI0OQ.GSJInG.UeyiV60GpywsX4kza8RKcFu_uwldy4Yzs75qFI'

intents = discord.Intents.all()
intents.members = True

bot = discord.Bot(intents=intents)

server_id = 1141718152946925679 


#restrict
@bot.slash_command(guild_id=1141718152946925679,
                   name="restrict",
                   description="Restricts user")
async def restrict(ctx,
                   name: discord.Member,
                   duration,
                   restriction,
                   reason: typing.Optional[str] = None):

  moderator = discord.utils.get(ctx.guild.roles, name="Moderator")
  head = discord.utils.get(ctx.guild.roles, name="Head")
  host = discord.utils.get(ctx.guild.roles, name="Host")
  if moderator in ctx.author.roles or head in ctx.author.roles or host in ctx.author.roles:

    currenttime = datetime.now().strftime("%d/%m %H:%M")
    time = datetime.now().strptime(currenttime, "%d/%m %H:%M")

    timetype = duration[-1]
    if (timetype == "m"):
      duration = duration.replace("m", "")
      durationtype = " minutes"
    elif (timetype == "h"):
      duration = duration.replace("h", "")
      durationtype = " hours"
    elif (timetype == "d"):
      duration = duration.replace("d", "")
      durationtype = " days"

    if timetype == "m":
      unrestrict_time = datetime.strptime(
        currenttime, "%d/%m %H:%M") + timedelta(minutes=int(duration))
    elif timetype == "h":
      unrestrict_time = datetime.strptime(
        currenttime, "%d/%m %H:%M") + timedelta(hours=int(duration))
    elif timetype == "d":
      unrestrict_time = datetime.strptime(
        currenttime, "%d/%m %H:%M") + timedelta(days=int(duration))

    if (restriction == "1"):
      restrictedtype = "Restricted"
    else:
      restrictedtype = "Restricted +"

    await ctx.respond(
      f"User: <@{name.id}>\nTime: `{duration}{durationtype}`\nType of Restricted: `{restrictedtype}`\nReason: `{reason}`",
      ephemeral=True)

    message = discord.Embed(title="User Restricted",
                            color=discord.Color.blue())
    message.add_field(
      name=f"User was restricted",
      value=
      f"<@{name.id}> Was restricted\n\nRestricted At: **{time.strftime('%d/%m %H:%M')}**\nWhen Unrestricted: **{unrestrict_time.strftime('%d/%m %H:%M')}**\n\nType: **{restrictedtype}**\n\nReason: **{reason}**"
    )
    await bot.get_channel(1141730974636458037).send(embed=message)

    if (restriction == "1"):
      await name.add_roles(
        discord.utils.get(ctx.guild.roles, name="Restricted"))
      await name.remove_roles(
        discord.utils.get(ctx.guild.roles, name="Member"))
    else:
      await name.add_roles(
        discord.utils.get(ctx.guild.roles, name="Restricted +"))
      await name.remove_roles(
        discord.utils.get(ctx.guild.roles, name="Member"))
      await name.remove_roles(
        discord.utils.get(ctx.guild.roles, name="Player"))
      if discord.utils.get(ctx.guild.roles,
                           name="Restricted [+]") in name.roles:
        await name.remove_roles(
          discord.utils.get(ctx.guild.roles, name="Restricted"))

    dictionary = {
      "name": f"{name}",
      "id": f"{name.id}",
      "restricttime": time.strftime("%d/%m %H:%M"),
      "time": unrestrict_time.strftime("%d/%m %H:%M"),
      "type": restriction,
      "reason": reason,
    }

    def write_json(new_data, filename='restriction.json'):
      with open(filename, 'r+') as file:
        file_data = json.load(file)
        file_data["restricted_users"].append(new_data)
        file.seek(0)
        json.dump(file_data, file, indent=4)

    write_json(dictionary)

    def write_json_log(new_data, filename='restrictedlog.json'):
      with open(filename, 'r+') as file:
        file_data = json.load(file)
        file_data["restricted_users"].append(new_data)
        file.seek(0)
        json.dump(file_data, file, indent=4)

    write_json_log(dictionary)

  else:
    await ctx.respond("You don't have rights to use this command.",
                      ephemeral=True)


#unrestrict
@bot.slash_command(
  guild_id=server_id,
  name="unrestrict",
  description="Unrestricts user and removes them from Restricted logs")
async def clearrestrict(ctx,
                        name: discord.Member,
                        reason: typing.Optional[str] = None):
  moderator = discord.utils.get(ctx.guild.roles, name="Moderator")
  head = discord.utils.get(ctx.guild.roles, name="Head")
  host = discord.utils.get(ctx.guild.roles, name="Host")
  if moderator in ctx.author.roles or head in ctx.author.roles or host in ctx.author.roles:
    file = open("restriction.json")

    data = json.load(file)
    for i in data["restricted_users"]:
      if i["name"] == str(name):
        unrestricttime = i["time"]
        id = i["id"]
        unrestrictedtime = i["restricttime"]
        restrictedtype = i["type"]
        restrictreason = i["reason"]

    server = bot.get_guild(int(server_id))

    if (restrictedtype == "1"):
      await name.add_roles(discord.utils.get(ctx.guild.roles,name="Member"))
      await name.remove_roles(discord.utils.get(ctx.guild.roles, name="Restricted"))
      await name.add_roles(discord.utils.get(server.roles, name="Had Restriction"))
    else:
      await name.add_roles(discord.utils.get(ctx.guild.roles,name="Member"))
      await name.remove_roles(discord.utils.get(ctx.guild.roles, name="Restricted +"))
      await name.add_roles(discord.utils.get(server.roles, name="Had Restriction +"))

    if (restrictedtype == "1"):
      restrictedtype = "Restricted"
    else:
      restrictedtype = "Restricted +"

    await ctx.respond(f"User: <@{id}> Unrestricted!\nReason: `{reason}`",
                      ephemeral=True)

    currenttime = datetime.now().strftime("%d/%m %H:%M")
    time = datetime.now().strptime(currenttime, "%d/%m %H:%M")
    currentunrestricttime = time.strftime("%d/%m %H:%M")

    message = discord.Embed(title="User Manually Unestricted",
                            color=discord.Color.blue())
    message.add_field(
      name=f"User was manually unrestricted",
      value=
      f"<@{id}> Was Unrestricted\n\nWhen Restricted: **{unrestrictedtime}**\nWhen Supposed To Be Unrestricted: **{unrestricttime}**\n\nType: **{restrictedtype}**\n\nReason For Restricted: **{restrictreason}**\n\n\nWhen Unrestricted: **{currentunrestricttime}**\nUnrestrict Reason: **{reason}**"
    )
    await bot.get_channel(1141730974636458037).send(embed=message)

    with open('restriction.json') as file:
      data = json.load(file)

    restricted_users = data["restricted_users"]
    filtered_users = [
      user for user in restricted_users if user["name"] != str(name)
    ]
    data["restricted_users"] = filtered_users

    with open("restriction.json", "w") as file:
      json.dump(data, file, indent=4)

@tasks.loop(seconds=60.0)
async def timedRestriction():

  currenttime = datetime.now().strftime("%d/%m %H:%M")
  time = datetime.now().strptime(currenttime, "%d/%m %H:%M")
  print(time.strftime("%d/%m %H:%M") + " Current time")

  print("Restricted Users:")

  file = open("restriction.json")

  data = json.load(file)

  for i in data["restricted_users"]:

    unrestricttime = i["time"]
    id = i["id"]
    name: discord.Member = i["name"]
    unrestrictedtime = i["restricttime"]
    restrictedtype = i["type"]
    reason = i["reason"]

    server = bot.get_guild(int(server_id))

    print(name)

    name = name.replace("#", "")
    name = name.replace("0", "")

    member = server.get_member_named(name)


    if time.strftime("%d/%m %H:%M") >= unrestricttime:

      if (restrictedtype == "1"):
        await member.add_roles(discord.utils.get(server.roles, name="Member"))
        await member.add_roles(discord.utils.get(server.roles, name="Had Restriction"))
        await member.remove_roles(discord.utils.get(server.roles, name="Restricted"))
      elif (restrictedtype == "2"):
        await member.add_roles(discord.utils.get(server.roles, name="Member"))
        await member.add_roles(discord.utils.get(server.roles, name="Had Restriction +"))
        await member.remove_roles(discord.utils.get(server.roles, name="Restricted +"))

      if (restrictedtype == "1"):
        restrictedtype = "Restricted"
      else:
        restrictedtype = "Restricted +"

      message = discord.Embed(title="User UNestricted",
                              color=discord.Color.blue())
      message.add_field(
        name=f"User was unrestricted",
        value=
        f"<@{id}> Was Unrestricted\n\nWhen Restricted: **{unrestrictedtime}**\nWhen Unrestricted: **{unrestricttime}**\n\nType: **{restrictedtype}**\n\nReason: **{reason}**"
      )
      await restriction_channel.send(embed=message)

      restricted_users = data['restricted_users']
      filtered_users = [user for user in restricted_users if user != i]
      data['restricted_users'] = filtered_users

      with open('restriction.json', 'w') as file:
        json.dump(data, file, indent=4)


# Custom
@bot.slash_command(guild_id=server_id,
                   name="embed",
                   description="Custom Embed")
async def shame(ctx, title, field_name, field_text, footer_text):
  moderator = discord.utils.get(ctx.guild.roles, name="Moderator")
  head = discord.utils.get(ctx.guild.roles, name="Head")
  host = discord.utils.get(ctx.guild.roles, name="Host")
  if moderator in ctx.author.roles or head in ctx.author.roles or host in ctx.author.roles:
    await ctx.respond("Sent!", delete_after=0.05, ephemeral=True)
    shame = discord.Embed(title=f"{title}", color=discord.Color.red())
    shame.add_field(name=f"{field_name}", value=f"{field_text}")
    shame.set_footer(text=f"{footer_text}")
    await ctx.send(embed=shame)
  else:
    await ctx.respond("You don't have rights to use this command.",
                      ephemeral=True)


# Message
@bot.slash_command(guild_id=server_id,
                   name="message",
                   description="Custom Message")
async def message(ctx, message):
  moderator = discord.utils.get(ctx.guild.roles, name="Moderator")
  head = discord.utils.get(ctx.guild.roles, name="Head")
  host = discord.utils.get(ctx.guild.roles, name="Host")
  if moderator in ctx.author.roles or head in ctx.author.roles or host in ctx.author.roles:
    await ctx.respond("Sent!", delete_after=0.05, ephemeral=True)
    await ctx.send(f"{message}")
  else:
    await ctx.respond("You don't have rights to use this command.",
                      ephemeral=True)

# Create verify button
@bot.slash_command(guild_id=server_id,
                   name="verifybutton",
                   description="Creates the verify button, if removed")
async def verifybutton(ctx):
  head = discord.utils.get(ctx.guild.roles, name="Head")
  host = discord.utils.get(ctx.guild.roles, name="Host")
  if head in ctx.author.roles or host in ctx.author.roles:
    await ctx.respond("Sent!", delete_after=0.05, ephemeral=True)
    await bot.get_channel(1141718898622861424).send("Click the button to verify!", view=Button())
  else:
    await ctx.respond("You don't have rights to use this command.",
                      ephemeral=True)
    

# Create screening button
@bot.slash_command(guild_id=server_id,
                   name="screeningbutton",
                   description="Creates the screening button, if removed")
async def verifybutton(ctx):
  head = discord.utils.get(ctx.guild.roles, name="Head")
  host = discord.utils.get(ctx.guild.roles, name="Host")
  if head in ctx.author.roles or host in ctx.author.roles:
    await ctx.respond("Sent!", delete_after=0.05, ephemeral=True)
    await bot.get_channel(1162986847253823518).send("Click the button to open a chat!", view=Button1())
  else:
    await ctx.respond("You don't have rights to use this command.",
                      ephemeral=True)

# Flask Web Server Setup
app = Flask(__name__, template_folder='./websites/')
app2 = Flask(__name__, template_folder='./websites/')
server = auth_server.AuthServer(bot, 1141730722189672518, server_id, asyncio.get_event_loop())

@app.route('/')
def uwu():
    return 'UwU'

@app2.route('/dashboard')
def dashboard():
    if ('Authorization' in request.headers):
      authorization = request.headers['Authorization'].replace("Basic ","")
      authorization = base64.b64decode(authorization.encode("ascii")).decode("ascii")

      name = "Mafiosu"
      password = "bigchungus"

      if (authorization == f"{name}:{password}"):
         return render_template('success.html', title="Mafiosu! Dashboard")
      
    response = make_response(render_template('potato.html'), 401)
    response.headers['WWW-Authenticate'] = 'Basic realm=Console'
    return response

@app2.route('/results')
def results():
   return render_template('results.html')



@app2.route('/')
def index():
    return server.index()

# Verify

CLIENT_ID = '24127'
CLIENT_SECRET = 'qJHR0ejwuxdJQGwaD5JKlLvoMvfIAahiU6vcmPDT'

@app.route('/oauth-callback', methods=['GET', 'POST'])
async def oauth_callback():
  return await server.oauth_callback()


class Button(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Verify!", style=discord.ButtonStyle.primary, emoji="✅", custom_id="verify_button1")
    async def button_callback(self, button, interaction):
        button.disabled = True
        REDIRECT_URI = f'https://verify.mafiosu.net/oauth-callback&state={interaction.user.id}'
        auth_url = f'https://osu.ppy.sh/oauth/authorize?client_id={CLIENT_ID}&response_type=code&scope=identify&redirect_uri={REDIRECT_URI}'
        await interaction.response.send_message(auth_url, ephemeral=True)



def _write_json(self, new_data, filename='verified.json'):
    with open(filename, 'r+') as file:
        self._users = json.load(file)
        self._users["verified_users"].append(new_data)
        file.seek(0)

        json.dump(self._users, file, indent=4)

# Unverify a User
@bot.slash_command(guild_id=server_id,
                   name="unverify",
                   description="Unverify a user")
async def verifybutton(ctx, name: discord.Member):
  moderator = discord.utils.get(ctx.guild.roles, name="Moderator")
  head = discord.utils.get(ctx.guild.roles, name="Head")
  host = discord.utils.get(ctx.guild.roles, name="Host")
  if moderator in ctx.author.roles or head in ctx.author.roles or host in ctx.author.roles:
    await ctx.respond(f"Unverified! <@{name.id}>", ephemeral=True)
    
    name = str(name)

    name = name.replace("#", "")
    name = name.replace("0", "")

    file = open("verified.json")

    data = json.load(file)

    for i in data["verified_users"]:

      discord_name = i["discord_name"]
      discord_id = i["discord_id"]
      osu_id = i["osu_id"]


    server = bot.get_guild(int(server_id))

    member = server.get_member_named(name)
    await member.remove_roles(discord.utils.get(server.roles, name="Member"))

    verified_users = data['verified_users']
    filtered_users = [name for name in verified_users if name != i]
    data['verified_users'] = filtered_users

    with open('verified.json', 'w') as file:
        json.dump(data, file, indent=4)
        file.close
    file.close

  else:
    await ctx.respond("You don't have rights to use this command.",
                      ephemeral=True)



class Button1(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Create a Ticket!", style=discord.ButtonStyle.primary, emoji="✅", custom_id="screening_button1")
    async def button_callback(self, button, interaction):
        button.disabled = True
        user = interaction.user
        guild = interaction.guild
        head = discord.utils.get(guild.roles, name="Head")
        print(str(head))
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True),
            head: discord.PermissionOverwrite(read_messages=True)
        }
        category = discord.utils.get(interaction.guild.categories, name="screening")
        channel = await category.create_text_channel(user.name, overwrites=overwrites)

        await interaction.response.send_message(f"Ticket Created: {channel.mention}", ephemeral=True)




@bot.event
async def on_message(ctx):
  if (ctx.channel.id == 1141718898622861424 and ctx.author.id != 1123922917231710249 and ctx.content != "/verify"):
    await ctx.delete()




@bot.event
async def on_ready():
  print(f"Logged in.")
  timedRestriction.start()
  bot.add_view(Button())
  bot.add_view(Button1())

if __name__ == '__main__':
    import threading
    threading.Thread(target=app2.run, kwargs={'host': '0.0.0.0', 'port': 25250}).start() # Main app
    threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 25249}).start()
    
    # Run the Discord bot
    bot.run(TOKEN)