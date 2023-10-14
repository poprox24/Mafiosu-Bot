import discord

from flask import Flask, render_template, request, make_response
import asyncio
import base64
import json
# Import .py files
import auth_server

import restriction_manager


TOKEN = 'MTEyMzkyMjkxNzIzMTcxMDI0OQ.GSJInG.UeyiV60GpywsX4kza8RKcFu_uwldy4Yzs75qFI'

intents = discord.Intents.all()
intents.members = True

bot = discord.Bot(intents=intents)

server_id = 1141718152946925679 

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
async def message(ctx):
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






@bot.event
async def on_message(ctx):
  if (ctx.channel.id == 1141718898622861424 and ctx.author.id != 1123922917231710249 and ctx.content != "/verify"):
    await ctx.delete()




@bot.event
async def on_ready():
  print(f"Logged in.")
  restriction_manager.timedRestriction.start()
  bot.add_view(Button())

if __name__ == '__main__':
    import threading
    threading.Thread(target=app2.run, kwargs={'host': '0.0.0.0', 'port': 25250}).start() # Main app
    threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 25249}).start()
    
    # Run the Discord bot
    bot.run(TOKEN)