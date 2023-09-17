import discord
import json
import typing
from datetime import datetime, timedelta
from discord.ext import tasks
from index import server_id, bot

restriction_channel = bot.get_channel(1141730974636458037)

#restrict
@bot.slash_command(guild_id=server_id,
                   name="restrict",
                   description="Restricts user.")
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
    await restriction_channel.send(embed=message)

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
    await restriction_channel.send(embed=message)

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