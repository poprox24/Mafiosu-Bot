import discord

from flask import Flask, render_template, request, make_response
import asyncio
import base64

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


# Verify 

# Flask Web Server Setup
app = Flask(__name__, template_folder='./websites/')
app2 = Flask(__name__, template_folder='./webserver/')
server = auth_server.AuthServer(bot, 1141730722189672518, server_id, asyncio.get_event_loop())

@app.route('/')
def index():
    return server.index()

@app.route('/console')
def console():
    if ('Authorization' in request.headers):
      authorization = request.headers['Authorization'].replace("Basic ","")
      authorization = base64.b64decode(authorization.encode("ascii")).decode("ascii")

      name = "Mafiosu"
      password = "bigchungus"

      if (authorization == f"{name}:{password}"):
         return render_template('success.html')
      
    response = make_response(render_template('potato.html'), 401)
    response.headers['WWW-Authenticate'] = 'Basic realm=Console'
    return response

@app2.route('/')
def uwu():
    return 'Hi, this page is not done yet, consider it an easter egg'

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



@bot.event
async def on_message(ctx):
  if (ctx.channel.id == 1141718898622861424 and ctx.author.id != 1123922917231710249 and ctx.content != "/verify"):
    await ctx.delete()


@bot.event
async def on_ready():
  print(f"Logged in.")
  restriction_manager.timedRestriction.start()
  #   await bot.get_channel(1141718898622861424).send("Click the button to verify!", view=Button())
  bot.add_view(Button())

if __name__ == '__main__':
    import threading
    threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 25249}).start()
    threading.Thread(target=app2.run, kwargs={'host': '0.0.0.0', 'port': 25208}).start()
    
    # Run the Discord bot
    bot.run(TOKEN)