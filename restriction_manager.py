import discord
import json
import typing
from datetime import datetime, timedelta
from discord.ext import tasks
from index import server_id, bot

restriction_channel = bot.get_channel(1141730974636458037)




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