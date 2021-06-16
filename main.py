import discord
from discord.ext import commands
from discord.utils import get
import math
import random
import json
import asyncio
import aiohttp
from io import BytesIO
from keep_alive import keep_alive
from datetime import datetime, timedelta
from platform import python_version
from time import time
from discord import __version__ as discord_version
import aiofiles
from asyncio import sleep
from discord import user
import discord.utils
import giphy_client
from giphy_client.rest import ApiException
from discord.ext.commands import command, cooldown, BucketType
from discord.ext.commands import (CommandOnCooldown)
import aiosqlite
from PIL import Image, ImageDraw, ImageFont
from prsaw import RandomStuff 
import DiscordUtils
import bs4
import akinator
import requests

with open('reports.json', encoding='utf-8') as f:
  try:
    report = json.load(f)
  except ValueError:
    report = {}
    report['users'] = []
  if not report:
    report['users'] = []

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=commands.when_mentioned_or('>>>'),intents = intents)

tracker = DiscordUtils.InviteTracker(client)

api_key = "3PCCNujbl6QM"
rs = RandomStuff(async_mode = True, api_key = api_key, ai_language="hi")




client.remove_command("help")
mainshop = [{"name":"Watch","price":1000,"description":"Time"},
            {"name":"Laptop","price":15000,"description":"PostMemes"},
            {"name":"CellPhone","price":8000,"description":"Calling"},
            {"name":"FishingPole","price":20000,"description":"Fishing"},
            {"name":"Rifle","price":30000,"description":"Hunting"},
            {"name":"Trophy","price":10000000000,"description":"Show Off"},
            {"name":"GoldMedal","price":1000000000,"description":"Show Off"},
            {"name":"Banknote","price":100000,"description":"Upgrade Your Bank Space"}]

client.ticket_configs = {}

@client.event
async def on_ready():
  
  async with aiofiles.open("ticket_configs.txt", mode="a") as temp:
    pass

  async with aiofiles.open("ticket_configs.txt", mode="r") as file:
        lines = await file.readlines()
        for line in lines:
            data = line.split(" ")
            client.ticket_configs[int(data[0])] = [int(data[1]), int(data[2]), int(data[3])]

print("we have logged in as {0.user}".format(client))

@client.event
async def on_raw_reaction_add(payload):
  if payload.member.id != client.user.id and str(payload.emoji) == u"\U0001F3AB":
    msg_id, channel_id, category_id = client.ticket_configs[payload.guild_id]

  if payload.message_id == msg_id:
    guild = client.get_guild(payload.guild_id)

    for category in guild.categories:
      if category.id == category_id:
        break

    channel = guild.get_channel(channel_id)

    ticket_channel = await category.create_text_channel(f"ticket-{payload.member.display_name}", topic=f"A ticket for {payload.member.display_name}.", permission_synced=True)
            
    await ticket_channel.set_permissions(payload.member, read_messages=True, send_messages=True)
    
    await ticket_channel.set_permissions(ticket_channel.guild.default_role, read_messages=False)

    
    message = await channel.fetch_message(msg_id)
    await message.remove_reaction(payload.emoji, payload.member)

    await ticket_channel.send(f"{payload.member.mention} Thank you for creating a ticket! Use **'-close'** to close your ticket.")

    try:
        await client.wait_for("message", check=lambda m: m.channel == ticket_channel and m.author == payload.member and m.content == "-close", timeout=3600)

    except asyncio.TimeoutError:
        await ticket_channel.delete()

    else:
            await ticket_channel.delete()
            

@client.command()
async def configure_ticket(ctx, msg: discord.Message=None, category: discord.CategoryChannel=None):
    if msg is None or category is None:
        await ctx.channel.send("Failed to configure the ticket as an argument was not given or was invalid.")
        return

    client.ticket_configs[ctx.guild.id] = [msg.id, msg.channel.id, category.id] # this resets the configuration

    async with aiofiles.open("ticket_configs.txt", mode="r") as file:
        data = await file.readlines()

    async with aiofiles.open("ticket_configs.txt", mode="w") as file:
        await file.write(f"{ctx.guild.id} {msg.id} {msg.channel.id} {category.id}\n")

        for line in data:
            if int(line.split(" ")[0]) != ctx.guild.id:
                await file.write(line)
                
    await msg.add_reaction(u"\U0001F3AB")
    await ctx.channel.send("Succesfully configured the ticket system.")


player1 = ""
player2 = ""
turn = ""
gameOver = True

board = []

winningConditions = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6]
]

@client.command()
async def tictactoe(ctx, p1: discord.Member, p2: discord.Member):
    global count
    global player1
    global player2
    global turn
    global gameOver

    if gameOver:
        global board
        board = [":white_large_square:", ":white_large_square:", ":white_large_square:",
                 ":white_large_square:", ":white_large_square:", ":white_large_square:",
                 ":white_large_square:", ":white_large_square:", ":white_large_square:"]
        turn = ""
        gameOver = False
        count = 0

        player1 = p1
        player2 = p2

        # print the board
        line = ""
        for x in range(len(board)):
            if x == 2 or x == 5 or x == 8:
                line += " " + board[x]
                await ctx.send(line)
                line = ""
            else:
                line += " " + board[x]

        # determine who goes first
        num = random.randint(1, 2)
        if num == 1:
            turn = player1
            await ctx.send("It is <@" + str(player1.id) + ">'s turn.")
        elif num == 2:
            turn = player2
            await ctx.send("It is <@" + str(player2.id) + ">'s turn.")
    else:
        await ctx.send("A game is already in progress! Finish it before starting a new one.")

@client.command()
async def place(ctx, pos: int):
    global turn
    global player1
    global player2
    global board
    global count
    global gameOver

    if not gameOver:
        mark = ""
        if turn == ctx.author:
            if turn == player1:
                mark = ":regional_indicator_x:"
            elif turn == player2:
                mark = ":o2:"
            if 0 < pos < 10 and board[pos - 1] == ":white_large_square:" :
                board[pos - 1] = mark
                count += 1

                # print the board
                line = ""
                for x in range(len(board)):
                    if x == 2 or x == 5 or x == 8:
                        line += " " + board[x]
                        await ctx.send(line)
                        line = ""
                    else:
                        line += " " + board[x]

                checkWinner(winningConditions, mark)
                print(count)
                if gameOver == True:
                    await ctx.send(mark + " wins!")
                elif count >= 9:
                    gameOver = True
                    await ctx.send("It's a tie!")

                # switch turns
                if turn == player1:
                    turn = player2
                elif turn == player2:
                    turn = player1
            else:
                await ctx.send("Be sure to choose an integer between 1 and 9 (inclusive) and an unmarked tile.")
        else:
            await ctx.send("It is not your turn.")
    else:
        await ctx.send("Please start a new game using the >>>tictactoe command.")


def checkWinner(winningConditions, mark):
    global gameOver
    for condition in winningConditions:
        if board[condition[0]] == mark and board[condition[1]] == mark and board[condition[2]] == mark:
            gameOver = True

@client.command()
@commands.has_permissions(manage_guild=True)
async def toggle(ctx, command):
    c = client.get_command(command)
    if not c:
        return await ctx.send("Could not find the command...")
    check = getattr(c, 'toggled', True)
    c.toggled = not check
    message = "Command Disabled!" if check else "Command Enabled!"
    await ctx.send(message)

@client.check
def toggled(ctx):
    c = ctx.command
    check  = getattr(c, 'toggled', True)
    return check

@client.event
async def on_member_join(member):
	await sleep(60*10)
	for channel in member.guild.channels: 
		if channel.name.startswith("Members"):
			await channel.edit(name=f"Members :{member.guild.member_count}")
			break

@client.event
async def on_message(message):
  if client.user == message.author:
    return

  if message.channel.id == 845687753370370069:
    response = await rs.get_ai_response(message.content)
    await message.reply(response)

  await client.process_commands(message)
  

@client.command()
async def nsfw(ctx):
  embed = discord.Embed(colour=discord.Colour.random())

  async with aiohttp.ClientSession() as cs:
    async with cs.get('https://www.reddit.com/r/nsfw/new.json?sort=hot') as r:
      res = await r.json()
      embed.set_image(url=res['data']['children'] [random.randint(0, 25)]['data']['url'])
      await ctx.send(embed=embed)
      
  



@client.command()
async def prefix(ctx):
  emb = discord.Embed (
    title="**MY PREFIX**",
    description="My Prefix Is >>>",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  await ctx.send(embed=emb)

@client.command()
async def search(ctx, message):
  await ctx.send(f"https://www.google.com/search?q={message}")

@client.command(aliases=["bal"])
async def balance(ctx,user: discord.Member=None):
  
  if user == None:
    user = ctx.author
  
  await open_account(user)


  users = await get_bank_data()
  
  wallet_amt = users[str(user.id)]["wallet"]
  bank_amt = users[str(user.id)]["bank"]
  bankspace = users[str(user.id)]["bankspace"]
  

  embed=discord.Embed(title="{}s balance:".format(user.name), colour=discord.Colour.random())
  embed.add_field(name="Wallet:", value=wallet_amt, inline=False)
  embed.add_field(name="Bank:", value=f"{bank_amt}/{bankspace}", inline=False)

  await ctx.send(embed=embed)

@client.command(aliases=["with"])
async def withdraw(ctx,amount):
  await open_account(ctx.author)
  user=ctx.author

  bal = await update_bank(ctx.author)
  users = await get_bank_data()
  wallet_amt =users[str(user.id)]["wallet"]
  bank_amt =users[str(user.id)]["bank"]
  bankspace =users[str(user.id)]["bankspace"]

  
  if amount == None:
    await ctx.send("Please Insert Amount")
  
  if amount == "all":
    await update_bank(user,1*bank_amt,"wallet")
    await update_bank(user,-1*bank_amt,"bank")
    await ctx.send("You Have Withdrew All Money From Bank")

  amount = int(amount)
  if amount>bal[1]:
    await ctx.send("You Have not Enough Money Poor")
    return

  if amount<0:
    await ctx.send("Amount Must Be Positive.")
    return
      
  await update_bank(user,1*amount,"wallet")
  await update_bank(user,-1*amount,"bank")
  
  await ctx.send(f"You Withdrew {amount} Coins!")

@client.command(aliases=["dep"])
async def deposit(ctx,amount):
  await open_account(ctx.author)
  user=ctx.author

  bal = await update_bank(ctx.author)
  users = await get_bank_data()
  wallet_amt =users[str(user.id)]["wallet"]
  bank_amt =users[str(user.id)]["bank"]
  bankspace =users[str(user.id)]["bankspace"]


  if amount == None:
    await ctx.send("Please Insert Amount")
  
  if bankspace == bank_amt:
    await ctx.send ("your bank is full.")
    return
  
  if amount == "all":
    await update_bank(user,-1*bankspace,"wallet")
    await update_bank(user,1*bankspace,"bank")
    await ctx.send("You Have Deposited Max Money To Bank")
  
  amount = int(amount)
  if amount>bal[0]:
    await ctx.send("You Have not Enough Money Poor")
    return

  if amount>bankspace:
    await ctx.send("You haven't Enough Storage In The Bank")
    return

  if amount<0:
    await ctx.send("Amount Must Be Positive.")
    return

  await update_bank(user,-1*amount,"wallet")
  await update_bank(user,1*amount,"bank")
  
  await ctx.send(f"You Deposited {amount} Coins!")

@client.command()
async def give(ctx,member:discord.Member,amount):
  await open_account(ctx.author)
  await open_account(member)

  user=ctx.author
  bal = await update_bank(ctx.author)
  users = await get_bank_data()
  wallet_amt =users[str(user.id)]["wallet"]
  bank_amt =users[str(user.id)]["bank"]

  
  
  if amount == None:
    await ctx.send("Please Insert Amount")
  
  if amount == "all":
    await update_bank(user,-1*wallet_amt,"wallet")
    await update_bank(member,1*wallet_amt,"wallet")
    await ctx.send(f"You gave Your All Money To {member}.")
  
  amount = int(amount)
  if amount<bal[1]:
    await ctx.send("You Have not Enough Money Poor")
    return

  if amount<0:
    await ctx.send("Amount Must Be Positive.")
    return
  
  await update_bank(ctx.author,-1*amount,"wallet")
  await update_bank(member,1*amount,"wallet")
  
  await ctx.send(f"You Gave {amount} Coins To {member.name}!")

@client.command()
@cooldown(1, 60*5, BucketType.user)
async def rob(ctx,member:discord.Member):
  await open_account(ctx.author)
  await open_account(member)

  bal = await update_bank(member)
  

  if bal[0]<100:
    await ctx.send("It's Not Worth It. He Has Less Than 100 Coins")
    return
  
  earnings = random.randrange(1000)
  
  await update_bank(ctx.author,1*earnings,"wallet")
  await update_bank(member,-1*earnings,"wallet")
  
  await ctx.send(f"You Robbed {member.name} And Got {earnings} Coins!")

@client.command(aliases=["cf","CoinFlip","COINFLIP","Coinflip"])
async def coinflip(ctx, bet:int, msg):
  choices=("Heads", "Tails")
  roll=random.choice(choices)
  
  gg=random.randrange(5)
  
  der=gg*bet

  foo = der+bet
  
  if msg == "Heads":
    if roll == "Heads":
      await update_bank(ctx.author,1*foo,"wallet")
      await ctx.send(f"You Got {foo} Coins")
      
  if msg == "Tails":
    if roll == "Tails":
      await update_bank(ctx.author,1*foo,"wallet")
      await ctx.send(f"You Got {foo} Coins")
      
  if msg == "Heads":
    if roll == "Tails":
      await update_bank(ctx.author,-1*bet,"wallet")
      await ctx.send(f"It's {roll} And You Lose {bet} Coins")

  if msg == "Tails":
    if roll == "Heads":
      await update_bank(ctx.author,-1*bet,"wallet")
      await ctx.send(f"It's {roll} And You Lose {bet} Coins")


@client.command(aliases = ["lb","rich"])
async def leaderboard(ctx,x = 1):
    users = await get_bank_data()
    leader_board = {}
    total = []
    for user in users:
        name = int(user)
        total_amount = users[user]["wallet"] + users[user]["bank"]
        leader_board[total_amount] = name
        total.append(total_amount)

    total = sorted(total,reverse=True)    

    em = discord.Embed(title = f"Top {x} Richest People" , description = "This is decided on the basis of raw money in the bank and wallet",color = discord.Color.random())
    index = 1
    for amt in total:
        id_ = leader_board[amt]
        member = client.get_user(id_)
        name = member.name
        em.add_field(name = f"{index}. {name}" , value = f"{amt}",  inline = False)
        if index == x:
            break
        else:
            index += 1

    await ctx.send(embed = em)

async def open_account(user):
    users = await get_bank_data()

    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["wallet"] = 0
        users[str(user.id)]["bank"] = 0
        users[str(user.id)]["bankspace"] = 10000
        
    with open("mainbank.json", "w") as f:
        json.dump(users, f)
    return True



async def get_bank_data():
    with open("mainbank.json", "r") as f:
        users = json.load(f)
    return users

async def update_bank(user:discord.User,change = 0,mode="wallet"):
  users = await get_bank_data()
  
  users[str(user.id)][mode] += change 
  
  with open ("mainbank.json","w") as f:
    json.dump(users, f)

  bal = users[str(user.id)]["wallet"],users[str(user.id)]["bank"]
  return bal

@client.command()
@cooldown(1, 45, BucketType.user)
async def beg(ctx):

    users = await get_bank_data()
    user = ctx.author

    earnings = random.randrange(500)
    

    if earnings == 0:
        await ctx.send(f"How unlucky... You didn't get anything...")

    elif earnings > 50:
        await ctx.send(f"Nice you got ${earnings} from a cool dude")

    elif earnings > 100:
        await ctx.send(f"Someone felt nice and gave you ${earnings}")

    elif earnings > 500:
        await ctx.send(f"You seem to have a way with people! Someone gave you ${earnings}")

    elif earnings > 800:
        await ctx.send(f"What a lucky day!! Someone gave you ${earnings}")

    elif earnings > 1500:
        await ctx.send(f"A rich man passed by you and felt bad. So ha gave you ${earnings}")

    elif earnings > 2000:
        await ctx.send(f"A shady man walked up to you and said 'I know how tough it can be out here' before giving you ${earnings}")

    users[str(user.id)]["wallet"] += earnings

    with open("mainbank.json", "w") as f:
        users = json.dump(users,f)


@rob.error
async def rob_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send('This command is on a %.2fs cooldown' % error.retry_after)
    raise error  # re-raise the error so all the errors will still show up in console
  

@beg.error
async def beg_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send('This command is on a %.2fs cooldown' % error.retry_after)
    raise error  # re-raise the error so all the errors will still show up in console
  

@client.command()
async def shop(ctx):
    em = discord.Embed(title = "Shop",colour=discord.Colour.random(),timestamp=ctx.message.created_at)

    for item in mainshop:
        name = item["name"]
        price = item["price"]
        desc = item["description"]
        em.add_field(name = name, value = f"${price} | {desc}")

    await ctx.send(embed = em)



@client.command()
async def buy(ctx,item,amount = 1):
    await open_account(ctx.author)

    res = await buy_this(ctx.author,item,amount)

    if not res[0]:
        if res[1]==1:
            await ctx.send("That Object isn't there!")
            return
        if res[1]==2:
            await ctx.send(f"You don't have enough money in your wallet to buy {amount} {item}")
            return


    await ctx.send(f"You just bought {amount} {item}")


@client.command()
async def inv(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []


    em = discord.Embed(title = "Inventory",colour=discord.Colour.random(), timestamp=ctx.message.created_at)
    for item in bag:
        name = item["item"]
        amount = item["amount"]

        em.add_field(name = name, value = amount)    

    await ctx.send(embed = em)    
async def buy_this(user,item_name,amount):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            price = item["price"]
            break

    if name_ == None:
        return [False,1]

    cost = price*amount

    users = await get_bank_data()

    bal = await update_bank(user)

    if bal[0]<cost:
        return [False,2]


    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt + amount
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index+=1 
        if t == None:
            obj = {"item":item_name , "amount" : amount}
            users[str(user.id)]["bag"].append(obj)
    except:
        obj = {"item":item_name , "amount" : amount}
        users[str(user.id)]["bag"] = [obj]        

    with open("mainbank.json","w") as f:
        json.dump(users,f)

    await update_bank(user,cost*-1,"wallet")

    return [True,"Worked"]

@client.command()
async def sell(ctx,item,amount = 1):
    await open_account(ctx.author)

    res = await sell_this(ctx.author,item,amount)

    if not res[0]:
        if res[1]==1:
            await ctx.send("That Object isn't there!")
            return
        if res[1]==2:
            await ctx.send(f"You don't have {amount} {item} in your bag.")
            return
        if res[1]==3:
            await ctx.send(f"You don't have {item} in your bag.")
            return

    await ctx.send(f"You just sold {amount} {item}.")

async def sell_this(user,item_name,amount,price = None):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            if price==None:
                price = 0.9* item["price"]
            break

    if name_ == None:
        return [False,1]

    cost = price*amount

    users = await get_bank_data()

    bal = await update_bank(user)


    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt - amount
                if new_amt < 0:
                    return [False,2]
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index+=1 
        if t == None:
            return [False,3]
    except:
        return [False,3]    

    with open("mainbank.json","w") as f:
        json.dump(users,f)

    await update_bank(user,cost,"wallet")

    return  [True,"Worked"]

@client.group()
async def use(ctx):
  emb = discord.Embed (
    title="Use Items",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**",value="-use item_name")

@use.command()
async def Banknote(ctx):
  users = await get_bank_data()
  
  if users[str(ctx.author.id)]["bag"]["Banknote"]:
    users[str(ctx.author.id)]["bankspace"] += random.randrange(5000, 25000)
    await ctx.send(f"Your Bank Sapce Is Now {bankspace}")
    

@client.command()
async def date(ctx):
    try:
        from datetime import date
        today = date.today()
        await ctx.send(f'```diff\n Current date is: {today}.```')
    except:
        pass


@client.command()
async def subscribe(ctx):
  emb = discord.Embed(
    title="Subscribe My Owner And My Coder",
    description="**These Are The Links**",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  
  emb.add_field(name="My Owner's YouTube Channel", value="[Click Here To Subscribe](https://youtube.com/c/PocketEditionHindi)")
  emb.add_field(name="My Coder's YouTube Channel",value="[Click Here To Subscribe](https://youtube.com/c/AlAoTach)")
  
  await ctx.send(embed=emb)
  
@client.command()
async def afk(ctx, mins):
    current_nick = ctx.author.nick
    member=discord.User
    await ctx.send(f"{ctx.author.mention} has gone afk for {mins} minutes.")
    await ctx.author.edit(nick=f"{ctx.author.name} [AFK]")

    counter = 0
    while counter <= int(mins):
        counter += 1
        await asyncio.sleep(60)

        if counter == int(mins):
            await member.edit(nick=current_nick)
            await ctx.send(f"{ctx.author.mention} is no longer AFK")
            break
 
@client.command(name="role")
async def add_role(ctx, role: discord.Role,member: discord.Member=None):
  if member is None:
    member=ctx.author
  if ctx.author.guild_permissions.manage_roles:
    await member.add_roles(role)
    emb= discord.Embed (
      title="Success",
      description=f"{role} Added To {member}",
      colour=discord.Colour.random(),
      timestamp=ctx.message.created_at)
    await ctx.send(embed=emb)

@client.command()
async def remove_role(ctx, role:discord.Role, member:discord.Member):
  if member is None:
    member=ctx.author
  if ctx.author.guild_permissions.manage_roles:
    await member.remove_roles(role)
    emb= discord.Embed (
      title="Success",
      description=f"{role} Removed From {member}",
      colour=discord.Colour.random(),
      timestamp=ctx.message.created_at)
    await ctx.send(embed=emb)

@client.command()
async def create_role(ctx, *, msg):
  guild = ctx.guild

  if ctx.author.guild_permissions.manage_roles:
    await guild.create_role(name=msg)
    emb= discord.Embed (
      title="Success",
      description=f"{msg} Created",
      colour=discord.Colour.random(),
      timestamp=ctx.message.created_at)
    await ctx.send(embed=emb)

@client.command(name="delete_role", pass_context=True)
async def delete_role(ctx, role:discord.Role):
    if ctx.author.guild_permissions.manage_roles:
      await role.delete()
    emb= discord.Embed (
    title="Success",
    description=f"{role} Deleted",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
    await ctx.send(embed=emb)


@client.command()
async def reminder(ctx,time:int, *,msg):
  if True:
    await sleep(time)
    await ctx.send(f"{msg} {ctx.author.mention}")

@client.command()
async def dal(ctx):
  await ctx.send("🚩 BAJRANG DAL, JAI BAJARANG BALI.")

@client.command()
async def nuke(ctx, amount=99999999):
  if ctx.author.guild_permissions.manage_messages:
    await ctx.channel.purge(limit=amount)
    embe = discord.Embed (
      title="NUKED THIS CHANNEL",
      description="",
      colour=discord.Colour.random(),
      timestamp=ctx.message.created_at
      )
    
    embe.set_image(url="https://c.tenor.com/XRaqIsw6SgcAAAAM/rahul-gandhi-khatam.gif")
    
    embe.set_footer(text= f"{ctx.author}")
    
    await ctx.channel.send(embed=embe)



@client.command(aliases=["b"])
async def ban(ctx, member: discord.Member, *, reason=None):
  if ctx.author.guild_permissions.ban_members:
    await member.ban(reason=reason)
  emb=discord.Embed (
    title=f"Banned {member}",
    description=f"Banned {member} By {ctx.author}",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  
  await ctx.send(embed=emb)



@client.command(aliases=["u"])
async def unban(ctx, id: int):
  user = await client.fetch_user(id)
  await ctx.guild.unban(user)
  emb=discord.Embed (
    title=f"Unnbanned {user}",
    description=f"Unbanned {user} By {ctx.author}",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  await ctx.send(embed=emb)



@client.command(aliases=["k"])
async def kick(ctx, member: discord.Member, *, reason=None):
  if ctx.author.guild_permissions.kick_members:
    await member.kick(reason=reason)
  emb=discord.Embed (
    title=f"KICKED {member}",
    description=f"Kicked {member} by {ctx.author}",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
    
  await ctx.send(embed=emb)



def add(n: float, n2: float):
 return n + n2

def sub(n: float, n2: float):
	return n - n2

def rando(n: int, n2: int):	return random.randint(n, n2)

def div(n: float, n2: float):	return n / n2

def sqrt(n: float):
	return math.sqrt(n)

def mult(n: float, n2: float):
	return n * n2

@client.command(aliases=["ma"])
async def mathadd(ctx, x: float, y: float):
	try:
		result = add(x, y)
		await ctx.send(result)

	except:
		pass

@client.command(aliases=["msub"])
async def mathsub(ctx, x: float, y: float):
	try:
		result = sub(x, y)
		await ctx.send(result)

	except:
		pass

@client.command(aliases=["mr"])
async def mathrando(ctx, x: int, y: int):
	try:
		result = rando(x, y)
		await ctx.send(result)

	except:
		pass

@client.command(aliases=["md"])
async def mathdiv(ctx, x: float, y: float):
	try:
		result = div(x, y)
		await ctx.send(result)
		
	except:
		pass

@client.command(aliases=["mm"])
async def mathmult(ctx, x: float, y: float):
	try:
		result = mult(x, y)
		await ctx.send(result)

	except:
		pass

@client.command(aliases=["ms"])
async def mathsqrt(ctx, x: float):
	try:
		result = sqrt(x)
		await ctx.send(result)

	except:
		pass

@client.command(aliases=["po"])
async def poll(ctx,*,message):
 emb=discord.Embed(title=" 📣POLL", description=f"{message}", colour=discord.Colour.random(), timestamp=ctx.message.created_at)
 
 emb.set_footer(text= f"{ctx.author}")
 
 msg= await ctx.channel.send(embed=emb)
 await msg.add_reaction('👍')
 await msg.add_reaction('👎')
 
@client.command(aliases=["bc"])
async def botcoder(ctx):
  emb=discord.Embed (
    title="My Coder Is 👇👇👇",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at
    )

  emb.set_image(url="https://cdn.discordapp.com/attachments/651744491606114304/792288604507996180/20201226_124033.gif")
  
  emb.set_footer(text= f"{ctx.author}")
  
  await ctx.send(embed=emb)

@client.command(aliases=["bo"]) 
async def botowner(ctx):
  emb=discord.Embed (
    title="**My OWNER Is 👇👇👇**",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at
    )

  emb.set_image(url="https://cdn.discordapp.com/attachments/780391951580135444/834429265440276531/avatar.jpg")
  
  emb.set_footer(text= f"{ctx.author}")
  
  await ctx.send(embed=emb)

@client.command(aliases=["announce"])
async def announcement(ctx, *, message):
  if ctx.author.guild_permissions.administrator:
    await ctx.message.delete()
    emb=discord.Embed (
      title="📢ANNOUNCEMENT📢",
      description=f"{message}",
      colour=discord.Colour.random(),
      timestamp=ctx.message.created_at
)

    emb.set_footer(text= f"{ctx.author}")
    
    await ctx.send(embed=emb)



@client.command(aliases=["n"])
async def nitro(ctx):
  msg = await ctx.send(f"https://discord.gift/2NcrWUVvs2y8m9xhPGEkUyER")

@client.command(aliases=["w"])
async def wanted(ctx, user: discord.Member = None):
  if user == None:
    user = ctx.author
  
    
  wanted = Image.open("wanted.jpeg")
    
  asset = user.avatar_url_as(size = 128)
  data = BytesIO(await asset.read())
  pfp = Image.open(data)
    
  pfp = pfp.resize((200, 200))
    
  wanted.paste(pfp, (110, 200))
    
  wanted.save("profile.jpg")
    
  await ctx.send(file = discord.File("profile.jpg"))
  
@client.command(aliases=["rip","RIP","Rip","rest_in_peace","Rest_in_peace","restinpeace","Restinpeace"])
async def REST_IN_PEACE(ctx, user: discord.Member = None):
  if user == None:
    user = ctx.author
  
    
  rip = Image.open("rip.jpeg")
    
  asset = user.avatar_url_as(size = 128)
  data = BytesIO(await asset.read())
  pfp = Image.open(data)
    
  pfp = pfp.resize((80, 80))
    
  rip.paste(pfp, (260, 220))
    
  rip.save("photo.jpg")
    
  await ctx.send(file = discord.File("photo.jpg"))
  
@client.command(aliases=["userinfo","userInfo","Userinfo"])
async def whois(ctx, member:discord.Member =  None):

  if member is None:
    member = ctx.author
    roles = [role for role in ctx.author.roles]

  else:
    roles = [role for role in member.roles]

  embed = discord.Embed(title=f"{member}", colour=discord.Colour.random(), timestamp=ctx.message.created_at)
  embed.set_footer(text=f"Requested by: {ctx.author}", icon_url=ctx.author.avatar_url)
  embed.set_author(name="User Info: ")
  embed.set_thumbnail(url=member.avatar_url)
  embed.add_field(name="ID:", value=member.id, inline=False)
  embed.add_field(name="User Name:",value=member.display_name, inline=False)
  embed.add_field(name="Discriminator:",value=member.discriminator, inline=False)
  embed.add_field(name="Current Activity:", value=f"{str(member.activity.type).title().split('.')[1]} {member.activity.name}" if member.activity is not None else "None", inline=False)
  embed.add_field(name="Created At:", value=member.created_at.strftime("%a, %d, %B, %Y, %I, %M, %p UTC"), inline=False)
  embed.add_field(name="Joined At:", value=member.joined_at.strftime("%a, %d, %B, %Y, %I, %M, %p UTC"), inline=False)
  embed.add_field(name=f"Roles [{len(roles)}]", value=" **|** ".join([role.mention for role in roles]), inline=False)
  embed.add_field(name="Top Role:", value=member.top_role, inline=False)
  embed.add_field(name="Bot?:", value=member.bot, inline=False)
  await ctx.send(embed=embed)
  return

@client.command(name="serverinfo", aliases=["guildinfo", "si", "gi"])
async def server_info(ctx):
  
  owner = str(ctx.message.guild.owner)
  
  embed = discord.Embed(
    title="Server information",
	  colour=discord.Colour.random(),
		timestamp=datetime.utcnow())

  embed.set_thumbnail(url=ctx.guild.icon_url)
  
  embed.set_footer(text=f"Requested by: {ctx.author}", icon_url=ctx.author.avatar_url)
  
  embed.add_field(name="ID",value=ctx.guild.id,inline=False)
  embed.add_field(name="Owner",value= owner ,inline=False)
  embed.add_field(name="Region",value=ctx.guild.region,inline=False)
  embed.add_field(name="Created At",value=ctx.guild.created_at.strftime("%d/%m/%Y/%H:%M:%S"),inline=False)
  embed.add_field(name="Members",value=ctx.guild.member_count,inline=False)

  await ctx.send(embed=embed)

@client.command(pass_context=True)
async def nick(ctx,nick, member: discord.Member= None):
  if member is None:
    member=ctx.author
    
  if ctx.author.guild_permissions.manage_nicknames:
    try:
      await member.edit(nick=nick)
      await ctx.send(f'Nickname was changed for {member.mention} ')
    except:
      await ctx.send("Missing Permissions")


@client.command(aliases=["av"])
async def avatar(ctx, user: discord.Member = None):
  if user == None:
    user = ctx.author
    
  emb = discord.Embed(
    title = f"{user}",
    colour = discord.Colour.random())
  emb.set_image(url=user.avatar_url)
  await ctx.send(embed=emb)

@client.command(aliases=["mc"])
async def membercount(ctx):
  emb=discord.Embed (
    title="MEMBERS",
    description=f"{ctx.guild.member_count}",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at
  )
    
  emb.set_footer(text= f"{ctx.author}")
    
  await ctx.send(embed=emb)

@client.command(aliases=["ae","announce_everyone","announce_all"])
async def announcement_everyone(ctx, *, message):
  if ctx.author.guild_permissions.administrator:
    await ctx.message.delete()
    emb=discord.Embed (
      title="📢ANNOUNCEMENT📢",
      description=f"{message}",
      colour=discord.Colour.random(),
      timestamp=ctx.message.created_at
)

    emb.set_footer(text= f"{ctx.author}")
    
    await ctx.send(f"@everyone", embed=emb)

@client.command()
async def say(ctx, *, message):
  await ctx.message.delete()
  emb=discord.Embed (
    title="",
    description=f"{message}",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at
    )
    
  emb.set_footer(text= f"{ctx.author}")
    
  await ctx.send(embed=emb)

@client.command()
async def covid(ctx , *, countryName = None):
  try:
    if countryName is None:
      embed=discord.Embed(title="This command is used like this: ```>>>covid [country]```", colour=discord.Colour.random())
      
      await ctx.send(embed=embed)


    else:
      url = f"https://coronavirus-19-api.herokuapp.com/countries/{countryName}"
      stats = requests.get(url)
      json_stats = stats.json()
      country = json_stats["country"]
      totalCases = json_stats["cases"]
      todayCases = json_stats["todayCases"]
      totalDeaths = json_stats["deaths"]
      todayDeaths = json_stats["todayDeaths"]
      recovered = json_stats["recovered"]
      active = json_stats["active"]
      critical = json_stats["critical"]
      casesPerOneMillion = json_stats["casesPerOneMillion"]
      deathsPerOneMillion = json_stats["deathsPerOneMillion"]
      totalTests = json_stats["totalTests"]
      testsPerOneMillion = json_stats["testsPerOneMillion"]

      embed2 = discord.Embed(title=f"**COVID-19 Status Of {country}**!", description="This Information Isn't Live Always, Hence It May Not Be Accurate!", colour=discord.Colour.random(), timestamp=ctx.message.created_at)
      embed2.add_field(name="**Total Cases**", value=totalCases, inline=True)
      embed2.add_field(name="**Today Cases**", value=todayCases, inline=True)
      embed2.add_field(name="**Total Deaths**", value=totalDeaths, inline=True)
      embed2.add_field(name="**Today Deaths**", value=todayDeaths, inline=True)
      embed2.add_field(name="**Recovered**", value=recovered, inline=True)
      embed2.add_field(name="**Active**", value=active, inline=True)
      embed2.add_field(name="**Critical**", value=critical, inline=True)
      embed2.add_field(name="**Cases Per One Million**", value=casesPerOneMillion, inline=True)
      embed2.add_field(name="**Deaths Per One Million**", value=deathsPerOneMillion, inline=True)
      embed2.add_field(name="**Total Tests**", value=totalTests, inline=True)
      embed2.add_field(name="**Tests Per One Million**", value=testsPerOneMillion, inline=True)

      embed2.set_thumbnail(url="https://cdn.discordapp.com/attachments/564520348821749766/701422183217365052/2Q.png")
      await ctx.send(embed=embed2)
  except:
        embed3 = discord.Embed(title="Invalid Country Name Or API Error! Try Again..!", colour=discord.Colour.random(), timestamp=ctx.message.created_at)
        embed3.set_author(name="Error!")
        await ctx.send(embed=embed3)

@client.command(aliases=["ct","cc","create_channel"])
async def create_text(ctx, channelName):
  guild = ctx.guild
  
  emb=discord.Embed (
    title="Success",
    description="{} Is Successfully Created".format(channelName),
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.set_footer(text=f"{ctx.author}")
    
  await guild.create_text_channel(name='{}'.format(channelName))
  await ctx.send(embed=emb)



@client.command(aliases=["dt","delete_channel","dc"])
async def delete_text(ctx, channel: discord.TextChannel):
  
  emb=discord.Embed (
    title = "Success",
    description = f'Channel: {channel} Successfully Deleted',
    colour = discord.Colour.random(),
    timestamp = ctx.message.created_at)
  emb.set_footer(text=f"{ctx.author}")
  
  if ctx.author.guild_permissions.manage_channels:
    await channel.delete()
  await ctx.send(embed=emb)



@client.command(aliases=["create_vc","cv"])
async def create_voice(ctx, channelName):
  guild = ctx.guild
  
  emb=discord.Embed (
    title="Success",
    description="{} Is Successfully Created".format(channelName),
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.set_footer(text=f"{ctx.author}")
    
  await guild.create_voice_channel(name='{}'.format(channelName))
  await ctx.send(embed=emb)



@client.command(aliases=["delete_vc","dv",])
async def delete_voice(ctx, channel: discord.VoiceChannel):
  
  emb=discord.Embed (
    title = "Success",
    description = f'Channel: {channel} Successfully Deleted',
    colour = discord.Colour.random(),
    timestamp = ctx.message.created_at)
  emb.set_footer(text=f"{ctx.author}")
  
  if ctx.author.guild_permissions.manage_channels:
    await channel.delete()
  await ctx.send(embed=emb)



@client.command(aliases=["dm","Dm","dM"])
async def DM(ctx, user: discord.User, *,msg):
  emb=discord.Embed (
    title="Successful",
    description=f"Successfully sended the message to {user}",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
    
  await ctx.message.delete()
  
  embe=discord.Embed(
    title=f"DM BY {ctx.author}",
    description=f"{msg}",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  
  await user.send(embed=embe)
  await ctx.send(embed=emb)

@client.command(aliases=["ce","Ce","cE"])
async def createemoji(ctx, url: str, *, name):
	guild = ctx.guild
	if ctx.author.guild_permissions.manage_emojis:
		async with aiohttp.ClientSession() as ses:
			async with ses.get(url) as r:
				
				try:
					img_or_gif = BytesIO(await r.read())
					b_value = img_or_gif.getvalue()
					if r.status in range(200, 299):
						emoji = await guild.create_custom_emoji(image=b_value, name=name)
						await ctx.send(f'Successfully created emoji: <:{name}:{emoji.id}>')
						await ses.close()
					else:
						await ctx.send(f'Error when making request | {r.status} response.')
						await ses.close()
						
				except discord.HTTPException:
					await ctx.send('File size is too big!')


@client.command(aliases=["de","De","dE"])
async def deleteemoji(ctx, emoji: discord.Emoji):
	guild = ctx.guild
	if ctx.author.guild_permissions.manage_emojis:
		await ctx.send(f'Successfully deleted (or not): {emoji}')
		await emoji.delete()



@client.command(aliases=["clear"])
@commands.has_permissions(manage_messages=True)
async def purge(ctx, limit: int = 50):
  await ctx.message.delete()
  c = await ctx.channel.purge(limit=limit)
  
  embed=discord.Embed (
    title="Cleared",
    description=f"Cleared {len(c)} messages By {ctx.author}",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  
  embed.add_field(name="This Message Will Be Deleted", value="After 10 Seconds")
  
  await ctx.channel.purge(limit=limit)
  await ctx.send(embed=embed, delete_after = 10)
 
@client.command(description="Mutes the specified user.")
@commands.has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member, *,reason=None):
    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="Muted")

    if not mutedRole:
        mutedRole = await guild.create_role(name="Muted")

        for channel in guild.channels:
            await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True, read_messages=True )
    embed = discord.Embed(title="muted", description=f"{member.mention} was muted ", colour=discord.Colour.random(),timestamp=ctx.message.created_at)
    embed.add_field(name="reason:", value=reason, inline=False)
    await ctx.send(embed=embed)
    await member.add_roles(mutedRole, reason=reason)
    await member.send(f" you have been muted from: {guild.name} reason: {reason}")



@client.command(description="Unmutes a specified user.")
@commands.has_permissions(manage_messages=True)
async def unmute(ctx, member: discord.Member):
   mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")

   await member.remove_roles(mutedRole)
   await member.send(f" you have unmutedd from: - {ctx.guild.name}")
   embed = discord.Embed(title="unmute", description=f" unmuted-{member.mention}",colour=discord.Colour.random(),timestamp=ctx.message.created_at)
   await ctx.send(embed=embed)



@client.group(invoke_without_command=True)
async def help(ctx):
  emb=discord.Embed (
    title="Commands",
    description="Help Commands, Use >>>help [command] for more info about a command.",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
    
  emb.add_field(name="**Moderation**", value="Kick, Ban, Unban, Mute, Unmute, Purge, Nuke, create_text, create_voice, createemoji, delete_text, delete_voice, createemoji, deleteemoji, configure_ticket, announcement, announcement_everyone, poll, roll, remove_role, create_role, delete_role, toggle, lock, unlock, warn, warnings, giveaway, reroll")
  emb.add_field(name="**Fun**", value="avatar, covid, membercount, nitro, say, wanted, ping, uptime, DM, search, coinflip, Kiss, Kill, Hug, userinfo, serverinfo, date, afk")
  emb.add_field(name="**Calculator**", value="mathadd, mathsub, mathmult, mathdiv, mathrando, mathsqrt")
  emb.add_field(name="**Bot Information**", value="botcoder, botowner, prefix, subscribe")
  emb.add_field(name="**Music**", value="clip, clips, loop, lyrics, move, np, pause, play, playlist, pruning, queue, remove, resume, skip, skipto, stop, volume")
  emb.add_field(name="**ECONOMY**", value="balance, beg, withdraw, deposit, rob, shop, buy, sell")
  emb.add_field(name="**GAMES**", value = "TicTacToe")
  await ctx.send(embed=emb)



@help.command()
async def toggle(ctx):
  emb=discord.Embed (
    title="toggle",
    description="toggle on or off the given name command",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>toggle commandName")
  await ctx.send(embed=emb)

@help.command()
async def role(ctx):
  emb=discord.Embed (
    title="role",
    description="gives mentioned role to the mentioned user",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>role [roleID/role Mention] [userID/user Mention]")
  await ctx.send(embed=emb)

@help.command()
async def remove_role(ctx):
  emb=discord.Embed (
    title="remove_role",
    description="removes mentioned role to the mentioned user",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>role [roleID/role Mention] [userID/user Mention]")
  await ctx.send(embed=emb)

@help.command()
async def create_role(ctx):
  emb=discord.Embed (
    title="create_role",
    description="creates a role of given name",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>create_role roleName")
  await ctx.send(embed=emb)
  
@help.command()
async def delete_role(ctx):
  emb=discord.Embed (
    title="delete_role",
    description="deletes the mentioned role",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>delete_role [roleId/Role mention]")
  await ctx.send(embed=emb)

@help.command()
async def kick(ctx):
  emb=discord.Embed (
    title="Kick",
    description="Kicks A User From The Server",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>kick [userID/user Mention]")
  await ctx.send(embed=emb)

@help.command()
async def ban(ctx):
  emb=discord.Embed (
    title="Ban",
    description="Bans A User From The Server",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>ban [userID/user Mention]")
  await ctx.send(embed=emb)

@help.command()
async def unban(ctx):
  emb=discord.Embed (
    title="Unban",
    description="Unbans The Banned User From The Server",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>unban [userID/username]")
  await ctx.send(embed=emb)

@help.command()
async def mute(ctx):
  emb=discord.Embed (
    title="Mute",
    description="Mutes A User From The Server",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>mute [userID/user Mention]")
  await ctx.send(embed=emb)

@help.command()
async def unmute(ctx):
  emb=discord.Embed (
    title="Unmute",
    description="Unmutes The Muted User From The Server",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>unmute [userID]")
  await ctx.send(embed=emb)

@help.command()
async def purge(ctx):
  emb=discord.Embed (
    title="Purge",
    description="Deletes The Number Of Messages Which Were Given In Command",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>purge [Number Of Messages You Want To Delete]")
  await ctx.send(embed=emb)

@help.command()
async def nuke(ctx):
  emb=discord.Embed (
    title="Nuke",
    description="Deletes All Messages In A Channel",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>nuke")
  await ctx.send(embed=emb)

@help.command()
async def create_text(ctx):
  emb=discord.Embed (
    title="create_text",
    description="Creates Text Channel",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>create_text [name]")
  await ctx.send(embed=emb)

@help.command()
async def delete_text(ctx):
  emb=discord.Embed (
    title="delete_text",
    description="Deletes The Text Channel",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>delete_text [channelID/channelMention/channelName]")
  await ctx.send(embed=emb)

@help.command()
async def create_voice(ctx):
  emb=discord.Embed (
    title="create_voice",
    description="Creates Voice Channel",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>create_voice [name]")
  await ctx.send(embed=emb)

@help.command()
async def delete_voice(ctx):
  emb=discord.Embed (
    title="delete_voice",
    description="Deletes The Voice Channel",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>delete_voice [channelName/channelID]")
  await ctx.send(embed=emb)

@help.command()
async def deleteemoji(ctx):
  emb=discord.Embed (
    title="deleteemoji",
    description="deletes The Emoji From Server",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>deleteemoji [name]")
  await ctx.send(embed=emb)

@help.command()
async def createemoji(ctx):
  emb=discord.Embed (
    title="createemoji",
    description="Creates The Emoji",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>createemoji [emoji_link]")
  await ctx.send(embed=emb)

@help.command()
async def announcement(ctx):
  emb=discord.Embed (
    title="Announcement",
    description="Announces Your message In Current Channel",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>announcement [msg]")
  await ctx.send(embed=emb)

@help.command()
async def announcement_everyone(ctx):
  emb=discord.Embed (
    title="announcement_everyone",
    description="Announces Your Msg With @everyone ping",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>announcement_everyone [msg]")
  await ctx.send(embed=emb)

@help.command()
async def configure_ticket(ctx):
  emb=discord.Embed (
    title="configure_ticket",
    description="configures ticket system in a msg",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>configure_ticket [msgID] [category ID] msgID will be id of that msg from where all can react and ticket will be opened and categoryID will be the id of that category where all tickets will be opened")
  await ctx.send(embed=emb)

@help.command()
async def poll(ctx):
  emb=discord.Embed (
    title="Poll",
    description="Makes A Poll With Your Question",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>poll [Question]")
  await ctx.send(embed=emb)

@help.command()
async def avatar(ctx):
  emb=discord.Embed (
    title="avatar",
    description="shows a user's pfp",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>avatar [user mention]")
  await ctx.send(embed=emb)

@help.command()
async def covid(ctx):
  emb=discord.Embed (
    title="covid",
    description="Shows Covid Stats Of A Country",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>covid [country]")
  await ctx.send(embed=emb)

@help.command()
async def nitro(ctx):
  emb=discord.Embed (
    title="nitro",
    description="Shows A Nitro Gift Image",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>nitro")
  await ctx.send(embed=emb)

@help.command()
async def membercount(ctx):
  emb=discord.Embed (
    title="membercount",
    description="Shows How Many Members Are There In The Server",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>membercount")
  await ctx.send(embed=emb)

@help.command()
async def say(ctx):
  emb=discord.Embed (
    title="say",
    description="Bot Says Your Msg",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>say [msg]")
  await ctx.send(embed=emb)

@help.command()
async def wanted(ctx):
  emb=discord.Embed (
    title="wanted",
    description="makes mentioned user's wanted poster",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>wanted [userMention]")
  await ctx.send(embed=emb)

@help.command()
async def ping(ctx):
  emb=discord.Embed (
    title="ping",
    description="Shows The Latency Of The Bot",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>ping")
  await ctx.send(embed=emb)

@help.command()
async def DM(ctx):
  emb=discord.Embed (
    title="DM",
    description="DMs Mentioned User with your message",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>DM [usermention/userID] [msg]")
  await ctx.send(embed=emb)

@help.command()
async def uptime(ctx):
  emb=discord.Embed (
    title="upt",
    description="Shows The Since The Bot Is Online",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>uptime")
  await ctx.send(embed=emb)

@help.command()
async def invite(ctx):
  emb=discord.Embed (
    title="Invite" ,
    description="Shows The Invite Link Of The Bot",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>invite")
  await ctx.send(embed=emb)

@help.command()
async def botcoder(ctx):
  emb=discord.Embed (
    title="botcoder",
    description="Tells who is the bot's coder",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>botcoder")
  await ctx.send(embed=emb)

@help.command()
async def botowner(ctx):
  emb=discord.Embed (
    title="botowner",
    description="Shows Who Is The Bot's Owner",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>botowner")
  await ctx.send(embed=emb)

@help.command()
async def mathadd(ctx):
  emb=discord.Embed (
    title="mathadd",
    description="Adds x and y",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>mathadd x y")
  await ctx.send(embed=emb)

@help.command()
async def mathsub(ctx):
  emb=discord.Embed (
    title="mathsub",
    description="Substracts x and y",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>mathsub x y")
  await ctx.send(embed=emb)

@help.command()
async def mathmult(ctx):
  emb=discord.Embed (
    title="mathmult",
    description="multiplies x and y",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>mathmult x y")
  await ctx.send(embed=emb)

@help.command()
async def mathdiv(ctx):
  emb=discord.Embed (
    title="mathdiv",
    description="divides x and y",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntaxrr**", value=">>>mathdiv x y")
  await ctx.send(embed=emb)

@help.command()
async def mathrando(ctx):
  emb=discord.Embed (
    title="mathrando",
    description="shows a random number between x and y",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>mathrando x y")
  await ctx.send(embed=emb)

@help.command()
async def mathsqrt(ctx):
  emb=discord.Embed (
    title="mathsqrt",
    description="Shows The Square Root Of x",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>mathsqrt x")
  await ctx.send(embed=emb)

@help.command()
async def clip(ctx):
  emb=discord.Embed (
    title="clip",
    description="plays a clip sound",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>clip [name]")
  await ctx.send(embed=emb)

@help.command()
async def clips(ctx):
  emb=discord.Embed (
    title="clips",
    description="Shows List Of All Clips",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>clips")
  await ctx.send(embed=emb)

@help.command()
async def loop(ctx):
  emb=discord.Embed (
    title="loop",
    description="Toggle Music Loop",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>loop")
  await ctx.send(embed=emb)

@help.command()
async def lyrics(ctx):
  emb=discord.Embed (
    title="lyrics",
    description="get lyrics of currently playing song",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>lyrics")
  await ctx.send(embed=emb)

@help.command()
async def move(ctx):
  emb=discord.Embed (
    title="move",
    description="move songs in the queue",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>move [queueNumber]")
  await ctx.send(embed=emb)

@help.command()
async def np(ctx):
  emb=discord.Embed (
    title="np",
    description="Shows Now Playing Song",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>np")
  await ctx.send(embed=emb)

@help.command()
async def pause(ctx):
  emb=discord.Embed (
    title="pause",
    description="Pause The Song",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>pause")
  await ctx.send(embed=emb)

@help.command()
async def play(ctx):
  emb=discord.Embed (
    title="play",
    description="plays the song from youtube",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>play [songLink/songName]")
  await ctx.send(embed=emb)

@help.command()
async def playlist(ctx):
  emb=discord.Embed (
    title="playlist",
    description="plays a playlist",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>playlist [link/name]")
  await ctx.send(embed=emb)

@help.command()
async def pruning(ctx):
  emb=discord.Embed (
    title="pruning",
    description="Toggle pruning",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>pruning")
  await ctx.send(embed=emb)

@help.command()
async def queue(ctx):
  emb=discord.Embed (
    title="queue",
    description="shows the song queue",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>queue")
  await ctx.send(embed=emb)

@help.command()
async def remove(ctx):
  emb=discord.Embed (
    title="remove",
    description="remove song from the queue",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>remove [name]")
  await ctx.send(embed=emb)

@help.command()
async def resume(ctx):
  emb=discord.Embed (
    title="resume",
    description="resume song playing",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>resume")
  await ctx.send(embed=emb)

@help.command()
async def skip(ctx):
  emb=discord.Embed (
    title="skip",
    description="skips the song",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>skip")
  await ctx.send(embed=emb)

@help.command()
async def skipto(ctx):
  emb=discord.Embed (
    title="skipto",
    description="skip to the selected queue number",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>skipto [queueNumber]")
  await ctx.send(embed=emb)

@help.command()
async def stop(ctx):
  emb=discord.Embed (
    title="stop",
    description="Stops The Music And left the vc",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>stop")
  await ctx.send(embed=emb)

@help.command()
async def volume(ctx):
  emb=discord.Embed (
    title="volume",
    description="Increase And Decrease Volume Upto 100",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>volume [number]")
  await ctx.send(embed=emb)

@help.command()
async def coinflip(ctx):
  emb=discord.Embed (
    title="**CoinFlip**",
    description="Flips A Coin And Shows It's Heads Or Tails.",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  emb.add_field(name="**Syntax**", value=">>>coinflip")
  await ctx.send(embed=emb)

@client.command()
async def gif(ctx,*,q="random"):

    api_key="eLILjOE4fwooaNXTfwIgw6DlvRY4nE07"
    api_instance = giphy_client.DefaultApi()

    try: 
    # Search Endpoint
        
        api_response = api_instance.gifs_search_get(api_key, q, limit=5, rating='g')
        lst = list(api_response.data)
        giff = random.choice(lst)

        emb = discord.Embed(title=q, description=f"Your {q} Gif Is Here",colour=discord.Colour.random(),timestamp=ctx.message.created_at)
        emb.set_image(url = f'https://media.giphy.com/media/{giff.id}/giphy.gif')

        await ctx.channel.send(embed=emb)
    except ApiException as e:
        print("Exception when calling DefaultApi->gifs_search_get: %s\n" % e)

@client.command()
async def kill(ctx, *, member:discord.Member):
  kill_gifs=("https://media.tenor.com/images/054c0fadb9e3833a7bdcb08e2baf9ed5/tenor.gif", "https://media1.tenor.com/images/900dfb92336966c5f5b9e818289343a4/tenor.gif?itemid=4712383", "https://media1.tenor.com/images/5a5194bcb1919c0f56b96ebfbe433ebd/tenor.gif?itemid=8288451", "https://media1.tenor.com/images/78a8cf1c1fb52d72916bfcdb5d226e1e/tenor.gif?itemid=5336963","https://media1.tenor.com/images/6bcb7579b294a013e1acd7a0c88f30d0/tenor.gif?itemid=4728975","https://media1.tenor.com/images/6c972a21f58d56cf7c82c9db80b9f2d7/tenor.gif?itemid=3460733","https://media1.tenor.com/images/6c840ad80e677a64b4ab478f8afa6b9d/tenor.gif?itemid=11907231","https://media1.tenor.com/images/7f94a71f086af08665d2f2e0393992e5/tenor.gif?itemid=20888227", "https://media1.tenor.com/images/c4b237dbcf676cf49a6d6d11cfbe45c8/tenor.gif?itemid=5336936","https://media.tenor.com/images/5d6fb1ec30fd6a195e3a411a5c34cd89/tenor.gif","https://media1.tenor.com/images/591ff80f58564f2e13750c469a52267b/tenor.gif?itemid=18958002","https://media1.tenor.com/images/05b93aca2ce10967785e22ce887b028b/tenor.gif?itemid=11143657","https://media1.tenor.com/images/c92616f453a940f182b05eaf81ff3b82/tenor.gif?itemid=5336945","https://media1.tenor.com/images/45efa50aa917b47779a1f065645585c8/tenor.gif?itemid=20168211","https://cdn.weeb.sh/images/B1VnoJFDZ.gif","https://cdn.weeb.sh/images/HyXTiyKw-.gif","https://cdn.weeb.sh/images/B1qosktwb.gif","https://cdn.weeb.sh/images/r11as1tvZ.gif","https://cdn.weeb.sh/images/BJO2j1Fv-.gif")
  uwu=random.choice(kill_gifs)
  
  emb=discord.Embed (
    title="",
    description=f"{ctx.message.author.name} Killed {member.name} OH MY GOD!",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  
  emb.set_image(url=f"{uwu}")
  
  await ctx.send(embed=emb)

@client.command()
async def kiss(ctx, *, member:discord.Member):
  kiss_gifs=("https://media1.tenor.com/images/ef9687b36e36605b375b4e9b0cde51db/tenor.gif?itemid=12498627","https://media1.tenor.com/images/31362a548dc7574f80d01a42a637bc93/tenor.gif?itemid=13985240.","https://media1.tenor.com/images/59966642c3fe571ae12fb1d8b13feec5/tenor.gif?itemid=10662832","https://media1.tenor.com/images/896f0159d6605b27c59ef3c3f818d664/tenor.gif?itemid=16490903","https://media1.tenor.com/images/e7036cbfd163f0925f0dc54d2b61dc61/tenor.gif?itemid=13795595","https://media1.tenor.com/images/55a44408c9ec232dc77a73c21de15ca3/tenor.gif?itemid=3544051","https://media1.tenor.com/images/8ccd2d3b29dd37a9d9e3d49e4907c8c5/tenor.gif?itemid=17424018","https://media1.tenor.com/images/d57217aeb7810ab1c619ef0102378285/tenor.gif?itemid=15342216","https://media1.tenor.com/images/23547c466df7d691ae28f0df5e25be2e/tenor.gif?itemid=16018766","https://media1.tenor.com/images/1d133ea3c2d71bcffbf79e3665a65983/tenor.gif?itemid=13519864","https://media1.tenor.com/images/58a6a6621a41811e9e00d3079834c1d9/tenor.gif?itemid=13627208","https://media1.tenor.com/images/5c712c9fc3f17b1735a36b8ec65996ba/tenor.gif?itemid=12535181","https://cdn.weeb.sh/images/B12LhT_Pb.gif","https://cdn.weeb.sh/images/BJSdQRtFZ.gif","https://cdn.weeb.sh/images/Byh57gqkz.gif","https://cdn.weeb.sh/images/S1VEna_v-.gif","https://cdn.weeb.sh/images/B1yv36_PZ.gif","https://cdn.weeb.sh/images/SJn43adDb.gif","https://cdn.weeb.sh/images/SkKL3adPb.gif","https://cdn.weeb.sh/images/ryFdQRtF-.gif","https://cdn.weeb.sh/images/HJYghpOP-.gif","https://cdn.weeb.sh/images/rkv_mRKF-.gif")

  kiss=random.choice(kiss_gifs)
  
  emb=discord.Embed (
    title="",
    description=f"{ctx.message.author.name} Kissed {member.name} Such A Lovely Moment.😘",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  
  emb.set_image(url=f"{kiss}")
  
  await ctx.send(embed=emb)

@client.command()
async def hug(ctx, *, member:discord.Member):
  hug_gifs=("https://media1.tenor.com/images/5ce46aca3246d88b81e99c4a8eaaf84c/tenor.gif?itemid=15965620","https://media1.tenor.com/images/24ac13447f9409d41c1aecb923aedf81/tenor.gif?itemid=5026057","https://media1.tenor.com/images/8ac5ada8524d767b77d3d54239773e48/tenor.gif?itemid=16334628","https://media1.tenor.com/images/491bc8d63f1e40a741f24e30f6ebae62/tenor.gif?itemid=12899882","https://media1.tenor.com/images/1f79b4d18f336fb68f6fe25e583a3668/tenor.gif?itemid=13260206","https://media1.tenor.com/images/ce9dc4b7e715cea12604f8dbdb49141b/tenor.gif?itemid=4451998","https://media1.tenor.com/images/b283b61ae2d891e41b5391ca88c8929f/tenor.gif?itemid=13883173","https://media1.tenor.com/images/e2a4acd737d13ac073822d4cf837ea2b/tenor.gif?itemid=9243716","https://media1.tenor.com/images/b7492c8996b25e613a2ab58a5d801924/tenor.gif?itemid=14227401","https://media1.tenor.com/images/95b41ae72f201a5389a78ccfdf2e6657/tenor.gif?itemid=4911454","https://cdn.weeb.sh/images/r1R3_d7v-.gif","https://cdn.weeb.sh/images/BJ0UovdUM.gif","https://cdn.weeb.sh/images/Bkta0ExOf.gif","https://cdn.weeb.sh/images/H1X6OOmPW.gif","https://cdn.weeb.sh/images/Hk0yFumwW.gif","https://cdn.weeb.sh/images/Sk2gmRZZG.gif","https://cdn.weeb.sh/images/ryPix0Ft-.gif","https://cdn.weeb.sh/images/Bk5haAocG.gif","https://cdn.weeb.sh/images/BJ0UovdUM.gif","https://cdn.weeb.sh/images/SJByY_QwW.gif")

  hug=random.choice(hug_gifs)
  
  emb=discord.Embed (
    title="",
    description=f"{ctx.message.author.name} Hugged {member.name} Awwwwww.🤗",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
  
  emb.set_image(url=f"{hug}")
  
  await ctx.send(embed=emb)


def convert(time):
    pos = ["s","m","h","d"]

    time_dict = {"s" : 1, "m" : 60, "h" : 3600 , "d" : 3600*24}

    unit = time[-1]

    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])
    except:
        return -2


    return val * time_dict[unit]



@client.command()
@commands.has_permissions(administrator=True)
async def giveaway(ctx):
    await ctx.send("Let's start with this giveaway! Answer these questions within 15 seconds!")

    questions = ["Which channel should it be hosted in?", 
                "What should be the duration of the giveaway? (s|m|h|d)",
                "What is the prize of the giveaway?"]

    answers = []

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel 

    for i in questions:
        await ctx.send(i)

        try:
            msg = await client.wait_for('message', timeout=15.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send('You didn\'t answer in time, please be quicker next time!')
            return
        else:
            answers.append(msg.content)
    try:
        c_id = int(answers[0][2:-1])
    except:
        await ctx.send(f"You didn't mention a channel properly. Do it like this {ctx.channel.mention} next time.")
        return

    channel = client.get_channel(c_id)

    time = convert(answers[1])
    if time == -1:
        await ctx.send(f"You didn't answer the time with a proper unit. Use (s|m|h|d) next time!")
        return
    elif time == -2:
        await ctx.send(f"The time must be an integer. Please enter an integer next time")
        return            

    prize = answers[2]

    await ctx.send(f"The Giveaway will be in {channel.mention} and will last {answers[1]}!")


    embed = discord.Embed(title = "Giveaway!", description = f"{prize}", color = ctx.author.color)

    embed.add_field(name = "Hosted by:", value = ctx.author.mention)

    embed.set_footer(text = f"Ends {answers[1]} from now!")

    my_msg = await channel.send(embed = embed)


    await my_msg.add_reaction("🎉")


    await asyncio.sleep(time)


    new_msg = await channel.fetch_message(my_msg.id)


    users = await new_msg.reactions[0].users().flatten()
    users.pop(users.index(client.user))

    winner = random.choice(users)

    await channel.send(f"Congratulations! {winner.mention} won {prize}!")
    
@giveaway.error
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        em = discord.Embed(title="",description="You Do Not Have Permissions To Perform This Command", colour=discord.Colour.random())
        await ctx.send(embed=em)


@client.command()
@commands.has_permissions(administrator=True)
async def reroll(ctx, channel : discord.TextChannel, id_ : int):
    try:
        new_msg = await channel.fetch_message(id_)
    except:
        await ctx.send("The id was entered incorrectly.")
        return
    
    users = await new_msg.reactions[0].users().flatten()
    users.pop(users.index(client.user))

    winner = user

    await channel.send(f"Congratulations! The new winner is {winner.mention}.!")    

@reroll.error
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        em = discord.Embed(title="",description="You Do Not Have Permissions To Perform This Command", colour=discord.Colour.random())
        await ctx.send(embed=em)


@client.command(pass_context = True)
@commands.has_permissions(manage_roles=True, manage_channels=True)
async def warn(ctx,user:discord.User, *,reason:str):
  if not reason:
    await client.say("Please provide a reason")
    return
  reason = ' '.join(reason)
  for current_user in report['users']:
    if current_user['name'] == user.name:
      current_user['reasons'].append(reason)
      break
  else:
    report['users'].append({
      'name':user.name,
      'reasons': [reason,]
    })
  with open('reports.json','w+') as f:
    json.dump(report,f)
    
  emb = discord.Embed (
    title="Warned",
    description=f"Warned {user} By {ctx.author} For {reason}",
    colour=discord.Colour.random(),
    timestamp=ctx.message.created_at)
    
  await user.send(embed=emb)
  await ctx.send(embed=emb)

@warn.error
async def warn_error(error, ctx):
  if isinstance(error, MissingPermissions):
      text = "Sorry {}, you do not have permissions to do that!".format(ctx.message.author)
      await client.send_message(ctx.message.channel, text)   


@client.command(pass_context = True)
async def warnings(ctx,user:discord.User):
  for current_user in report['users']:
    if user.name == current_user['name']:
      await ctx.send(f"{user.name} has been reported {len(current_user['reasons'])} times : {','.join(current_user['reasons'])}")


@client.command(aliases=["lockdown"])
@commands.has_permissions(manage_channels = True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send( ctx.channel.mention + " ***is now in lockdown.***")



@client.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send(ctx.channel.mention + " ***has been unlocked.***")

@unlock.error
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        em = discord.Embed(title="",description="You Do Not Have Permissions To Perform This Command", colour=discord.Colour.random())
        await ctx.send(embed=em)

initial_extensions = [
]

if __name__ == '__main__':
    for extension in initial_extensions:
        client.load_extension(extension)


keep_alive()
client.run("ODM0NDA1MzI4NjI3MDQwMjY2.YIAahA.NapOXsHe81w6XV0dRF3EbLJtOwA")