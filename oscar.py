'''
	Obscure Speedruns Club Advertising Robot (O.S.C.A.R.)
	  by mat1jaczyyy for Obscure Speedruns Club Discord
'''

debug = True  # Print debug (verbose) messages to stdout
dSend = True  # Send messages on Discord (set to False when testing responses locally to reduce spam in channels)

import os, time  # We need time anyways for Twitch cooldowns, also used for verbose output (runtime) so import right away

start = time.time()

if debug:
	os.system("clear")  # Clear the shell - probably doesn't work on Windows (script usually runs on Linux)
	
def timeSince(x):
	r = str(time.time() - x) + "0000"
	return r[:r.index('.') + 4]  # Dirty hack to round to 3 decimals in any case, including trailing zeros (because floats are bad and Decimal rounding doesn't work well)
	
def log(service, level, message):
	global start
	print("  [" + timeSince(start) + "|" + level + "]", service, ">>>", message)
	
if debug:
	log("Core", "I", "Obscure Speedruns Club Advertising Robot (O.S.C.A.R.)")

import aiohttp, asyncio, discord, re, sys  # Import the rest

if debug:
	log("Core", "OK", "Loaded modules")

# Read API token from file
def getToken(x):
	x = '~/.oscar/' + x + '.key'  # Use UNIX home folder - again probably doesn't work on Windows
	
	try:
		f = open(os.path.expanduser(x), "r")  # Open the file with expanding user/home path
		
		if debug:
			log("Token", "OK", "Successfully read " + x)
		
		r = f.read()
		f.close()
		
		return r
	
	# Custom error message
	except FileNotFoundError:
		log("Token", "E", "Can't read file '" + x + "'. Please verify that the file exists and contains a valid API token.")
		sys.exit()

# Tokens, channel IDs, SRC game IDs, etc
keys = {
	'discord': getToken('discord'),
	'twitch': getToken('twitch'),
	'community': 'b70126ca-59d9-4f19-afc6-92477a0e00e2',
	'streams': '398462254603042819',
	'records': '398657127675068417',
	'games': [
		'm1zjjpm6',  # Aurora Trail
		'76rko4d8',  # Dungeon of Zolthan
		'm1zn0210',  # Pokémon Pinball: Ruby & Sapphire
		'pdv4n4dw',  # Super Mario Sunshine 64
	],
	'twitch-games': [
		'501598',  # Aurora Trail
		'503569',  # Dungeon of Zolthan
		'8075'     # Pokémon Pinball: Ruby & Sapphire
		           # Super Mario Sunshine 64 is not supported by Twitch (GiantBomb)'s database - fangames not allowed
	],
	'submissions': '402277478183337987',
	'submissions_open': False,
	'regexLink': '((?:https?://)?(?:www\.)?[A-Za-z0-9]{1,}\.(?:(?:com)|(?:net)|(?:org)|(?:tv))(?:/[A-Z|a-z|-|_|=|?|0-9]*))'  # Thanks Tiln ;)
}

def sms64(x):  # SMS64 is not supported by Twitch because it is a fangame
	x = x.lower()
	return ("sms" in x or ("super" in x and "mario" in x and "sunshine" in x)) and "64" in x  # Dirty hardcode

if debug:
	log("Core", "OK", "Loaded keys")

# SRC returns some weird human-like time in the API - a library for this probably exists somewhere
def humanTime(x):
	x = float(x)
	
	s = str(int(x) % 60)
	m = str((int(x) // 60) % 60)
	
	s = ("0" * (2 - len(s))) + s
	m = ("0" * (2 - len(m))) + m
	
	ms = ""
	if x != int(x):
		ms = (str(x - int(x)) + "0000")[1:5]
	
	return ((str(h) + ":") if h > 0 else "") + m + ":" + s + ms

# Asynchronous HTTP requests are required for keeping up the heartbeat of the Discord connection
# If done synchronously, they can sometimes take a long time to return, enough for the heartbeat to time out, killing the bot

# Get JSON data from SRC API
async def src(url):
	base = 'https://www.speedrun.com/api/v1/'
	
	try:
		async with aiohttp.ClientSession() as session:
			async with session.get(base + url) as resp:
				assert resp.status == 200
				return dict(await resp.json())['data']
	
	except AssertionError:  # If we got a status code other than 200 OK
		log("SRC", "E", "Failed to get " + url + " (" + str(resp.status) + "), retrying...")
		
		await asyncio.sleep(5)  # If the site is under load, best to avoid spamming it with even more requests, so let's just wait a bit
		return await src(url)  # Try again recursively

# Get JSON data from Twitch (Helix) API
async def helix(url):
	global keys
	base = 'https://api.twitch.tv/helix/'
	
	try:
		async with aiohttp.ClientSession() as session:
			async with session.get(base + url, headers={'Client-ID': keys['twitch']}) as resp:
				assert resp.status == 200
				return dict(await resp.json())['data']
	
	except AssertionError:
		log("Twitch", "E", "Failed to get " + url + " (" + str(resp.status) + "), retrying...")
		
		await asyncio.sleep(5)
		return await helix(url)

disc = discord.Client()  # Create Discord client instance

# I would have done these inline, but the verbose output would look messy so wrapped it in a nice function
async def send(channel, message):
	global disc, dSend
	
	if debug:
		log("Discord", "D", "Sending message to channel #" + channel.name + " '" + message + "'")
	
	if dSend:
		await disc.send_message(channel, message)
	
	if debug:
		log("Discord", "OK", "Message " + ("sent" if dSend else "skipped"))

async def sendEmbed(channel, embed):
	global disc, dSend
	
	if debug:
		log("Discord", "D", "Sending embed to channel #" + channel.name)  # TO-DO: find a nice way to print embeds
	
	if dSend:
		await disc.send_message(channel, embed=embed)
	
	if debug:
		log("Discord", "OK", "Message " + ("sent" if dSend else "skipped"))

# Read submissions from disk
def getSubmissions():
	try:
		f = open(os.path.expanduser("~/.oscar/submissions.db"), "r")
		
		if debug:
			log("Submit", "OK", "Successfully read submissions.db")
		
		r = f.read().split("\n")
		f.close()
		
		if r == [""]:  # Failsafe for empty file (starting point - 0 submissions)
			r = []
		
		return r
	
	except FileNotFoundError:
		log("Submit", "E", "Can't read file 'submissions.db'. Please verify that the file exists.")
		sys.exit()

# Write submissions to disk
def setSubmissions(x):
	f = open(os.path.expanduser("~/.oscar/submissions.db"), "w")
	f.write('\n'.join(x))  # Separate by newline
	f.close()
	
	if debug:
		log("Submit", "OK", "Successfully wrote submissions.db to disk")

# This function runs when the Discord client has initialized - since calling disc.run() halts the main synchronous thread, all following code must go here
@disc.event
async def on_ready():
	global keys, disc  # These global definitions are probably not required anywhere, but I like to be sure
	
	if debug:
		log("Discord", "OK", "Logged in as " + str(disc.user))
	
	# Get channel objects we'll be sending to from Discord immediately, and keep them in memory
	streams = disc.get_channel(keys['streams'])
	records = disc.get_channel(keys['records'])
	
	if debug:
		log("Discord", "OK", "Channel objects loaded")
	
	cooldown = 7200  # Twitch cooldown in seconds - minimum amount of time before someone's stream is advertised again
	
	streaming = {}  # {streamer's user id: [time of cooldown expiration (Unix timestamp), is currently streaming (bool)]}
	runs = {}  # {game id: {category id: {runner id: run time in seconds}}}
	
	if debug:
		log("SRC", "I", "Initializing run database")
	
	# Initialize database of runs
	# Separate from main loop because here we gather initial data and NOT notify the Discord channel
	for game in keys['games']:
		if debug:
			log("SRC", "D", "Processing game " + game)
		
		runs[game] = {}  # Add game to the dict
		
		for category in await src('games/' + game + '/categories'):  # Get categories and loop through them
			if category['type'] == "per-game":  # Only full-game runs (per-level runs don't give us enough info here)
				if debug:
					log("SRC", "D", "Category " + category['id'])
				
				runs[game][category['id']] = {'_wr': 999999999}  # Add category to the dict and leave placeholder WR in case of an empty leaderboard
				
				for run in (await src('leaderboards/' + game + '/category/' + category['id']))['runs']:  # Get all runs for the category
					player = run['run']['players'][0]['id'] if run['run']['players'][0]['rel'] == "user" else run['run']['players'][0]['name']  # Run submitter can be guest (no SRC account)
					runs[game][category['id']][player] = run['run']['times']['primary_t']  # Save the run
					
					if debug:
						log("SRC", "D", player + " " + str(run['run']['times']['primary_t']))
					
					if run["place"] == 1:  # If WR
						runs[game][category['id']]['_wr'] = run['run']['times']['primary_t']  # Save WR time (used to determine if new WR is tied)
				
				if debug:
					log("SRC", "D", "WR " + str(runs[game][category['id']]['_wr']))
		
		for level in await src('games/' + game + '/levels'):  # Get individual levels (they behave like games)
			if debug:
				log("SRC", "D", "Level " + level['id'])
			
			runs[level['id']] = {}  # Add level to the dict
			
			for category in await src('levels/' + level['id'] + '/categories'):
				if debug:
					log("SRC", "D", "Category " + category['id'])
				
				runs[level['id']][category['id']] = {'_wr': 999999999}
				
				for run in (await src('leaderboards/' + game + '/level/' + level['id'] + '/' + category['id']))['runs']:
					player = run['run']['players'][0]['id'] if run['run']['players'][0]['rel'] == "user" else run['run']['players'][0]['name']
					runs[level['id']][category['id']][player] = run['run']['times']['primary_t']
					
					if debug:
						log("SRC", "D", player + " " + str(run['run']['times']['primary_t']))
					
					if run["place"] == 1:  # If WR
						runs[level['id']][category['id']]['_wr'] = run['run']['times']['primary_t']
				
				if debug:
					log("SRC", "D", "WR " + str(runs[level['id']][category['id']]['_wr']))
	
	if debug:
		log("SRC", "OK", "Run database initialized")
		log("Core", "OK", "Setup complete")
	
	# Main loop
	while True:
		if debug:
			log("Twitch", "I", "Getting OSC livestreams")
		
		osc = await helix('streams?community_id=' + keys['community'])  # Get OSC community livestreams
		
		if debug:
			log("Twitch", "OK", "Received OSC livestreams from server")
		
		now = []  # Clean list of currently live OSC streamers
		
		for live in osc:
			if live["game_id"] in keys["twitch-games"] or sms64(live["title"]):
				now.append(live["user_id"])
				
				if live["user_id"] not in streaming:  # Streamer isn't in the dict if this is the first time we see them streaming
					streaming[live["user_id"]] = [0, False]  # No cooldown and not streaming - will get overridden (need a placeholder)
				
				if int(time.time()) > streaming[live["user_id"]][0] and not streaming[live["user_id"]][1]:  # If the cooldown has expired and the streamer has just started streaming (he wasn't streaming in the previous iteration of the main loop)
					if debug:
						log("Twitch", "I", live["user_id"] + " started streaming outside of cooldown")
					
					channel = (await helix('users?id=' + live["user_id"]))[0]  # Get info about streamer channel (used for profile picture, display name)
					
					# Create the Embed to be sent - https://cog-creators.github.io/discord-embed-sandbox/ helps a lot
					embed=discord.Embed(title=live["title"], description="http://twitch.tv/" + channel["display_name"])
					embed.set_author(name=channel["display_name"] + " is now streaming!", icon_url=channel["profile_image_url"])
					embed.set_thumbnail(url=live["thumbnail_url"].format(width='480', height='480'))

					if sms64(live["title"]):
						embed.set_footer(text="Super Mario Sunshine 64")
					else:
						game = (await helix('games?id=' + live["game_id"]))[0]  # Get info about the game being streamed (used for box art, game name)
						embed.set_footer(text=game["name"], icon_url=game["box_art_url"].format(width='120', height='120'))
					
					await sendEmbed(streams, embed)
					
					streaming[live["user_id"]][0] = int(time.time()) + cooldown  # Set cooldown
				
				streaming[live["user_id"]][1] = True  # Is streaming (if statement checking whether the value needs changing would be redundant)
		
		if debug:
			log("Twitch", "D", "Currently streaming: " + str(now))
		
		for live in streaming:
			if live not in now:
				streaming[live][1] = False  # Anyone not streaming is set to False (if statement checking whether the value needs changing would be redundant)
			
			if debug:
				log("Twitch", "D", "Streamer " + live + " " + str(streaming[live]) + " (" + ((str(streaming[live][0] - int(time.time())) + " until ") if streaming[live][0] - int(time.time()) >= 0 else "") + "expired)")
		
		if debug:
			log("SRC", "I", "Checking for new runs...")
		
		# Check for new PBs - can be optimized further with smarter async calls, but mostly unnecessary
		for game in keys['games']:
			if debug:
				log("SRC", "D", "Processing game " + game)
			
			for category in await src('games/' + game + '/categories'):
				if category['type'] == "per-game":
					if debug:
						log("SRC", "D", "Category " + category['id'])
					
					if category['id'] not in runs[game]:  # It is possible a mod adds another category while we're running the script, make sure the bot doesn't throw an error trying to access it
						runs[game][category['id']] = {'_wr': 999999999}
					
					for run in (await src('leaderboards/' + game + '/category/' + category['id']))["runs"]:
						player = run['run']['players'][0]['id'] if run['run']['players'][0]['rel'] == "user" else run['run']['players'][0]['name']
						
						if debug:
							log("SRC", "D", player + " " + str(run['run']['times']['primary_t']))
						
						if player not in runs[game][category['id']]:  # It is possible a new runner submits their first run
							runs[game][category['id']][player] = 999999999
						
						if run['run']['times']['primary_t'] < runs[game][category['id']][player]:  # If a runner has a better time than before
							runs[game][category['id']][player] = run['run']['times']['primary_t']  # Save new PB
							
							text = " has achieved a new Personal Best!"
							
							if run["place"] == 1:  # If WR
								text = " has set the new World Record!"
								
								if run['run']['times']['primary_t'] == runs[game][category['id']]['_wr']:  # If tied with previous WR
									text = " has tied the current World Record!"
									
									if debug:
										log("SRC", "I", "^ Tied WR")
								
								else:
									runs[game][category['id']]['_wr'] = run['run']['times']['primary_t']  # Save new WR
									
									if debug:
										log("SRC", "I", "^ New WR")
							
							elif debug:
								log("SRC", "I", "^ New PB")
							
							runner = (await src('users/' + player))['names']['international'] if run['run']['players'][0]['rel'] == "user" else player
							gameInfo = await src('games/' + game)
							
							# https://cog-creators.github.io/discord-embed-sandbox/
							embed=discord.Embed(title=humanTime(run['run']['times']['primary_t']) + " in " + gameInfo['names']['international'] + " (" + category['name'] + ")", description=run['run']['weblink'])
							embed.set_author(name=runner + text, icon_url='https://www.speedrun.com/themes/user/' + runner + '/image.png')
							embed.set_footer(text="Congratulations!", icon_url=gameInfo['assets']['cover-medium']['uri'])
							
							await sendEmbed(records, embed)
			
			for level in await src('games/' + game + '/levels'):
				if debug:
					log("SRC", "D", "Level " + level['id'])
				
				if level['id'] not in runs:  # It is possible a mod adds another individual level while we're running the script
					runs[level['id']] = {}
				
				for category in await src('levels/' + level['id'] + '/categories'):
					if debug:
						log("SRC", "D", "Category " + category['id'])
					
					if category['id'] not in runs[level['id']]:
						runs[level['id']][category['id']] = {'_wr': 999999999}
					
					for run in (await src('leaderboards/' + game + '/level/' + level['id'] + '/' + category['id']))['runs']:
						player = run['run']['players'][0]['id'] if run['run']['players'][0]['rel'] == "user" else run['run']['players'][0]['name']
						
						if debug:
							log("SRC", "D", player + " " + str(run['run']['times']['primary_t']))
						
						if player not in runs[level['id']][category['id']]:
							runs[level['id']][category['id']][player] = 999999999
						
						if run['run']['times']['primary_t'] < runs[level['id']][category['id']][player]:
							runs[level['id']][category['id']][player] = run['run']['times']['primary_t']
							
							text = " has achieved a new Personal Best!"
							
							if run["place"] == 1:
								text = " has set the new World Record!"
								
								if run['run']['times']['primary_t'] == runs[level['id']][category['id']]['_wr']:
									text = " has tied the current World Record!"
									
									if debug:
										log("SRC", "I", "^ Tied WR")
								
								else:
									runs[level['id']][category['id']]['_wr'] = run['run']['times']['primary_t']
									
									if debug:
										log("SRC", "I", "^ New WR")
							
							elif debug:
								log("SRC", "I", "^ New PB")
							
							runner = (await src('users/' + player))['names']['international'] if run['run']['players'][0]['rel'] == "user" else player
							gameInfo = await src('games/' + game)
							
							# https://cog-creators.github.io/discord-embed-sandbox/
							embed=discord.Embed(title=humanTime(run['run']['times']['primary_t']) + " in " + gameInfo['names']['international'] + ": " + level['name'] + " (" + category['name'] + ")", description=run['run']['weblink'])
							embed.set_author(name=runner + text, icon_url='https://www.speedrun.com/themes/user/' + runner + '/image.png')
							embed.set_footer(text="Congratulations!", icon_url=gameInfo['assets']['cover-medium']['uri'])
							
							await sendEmbed(records, embed)
				
# Message interactions with the bot (commands)
@disc.event
async def on_message(m):
	global disc, keys
	
	if m.author == disc.user:  # Return if BOT receives its own message (happens basically every time it sends one)
		return
	
	if m.channel.id == keys['submissions'] and key['submissions_open']	:  # Game submissions
		if debug:
			log("Discord", "D", "Received message from " + m.channel.name + " - " + m.author.name + " - " + m.content)
		
		if re.search(keys['regexLink'], m.content) != None:  # If user added a link
			sub = getSubmissions()  # Read submissions
			
			hasSubmitted = -1  # Index of user submission, if they are resubmitting
			for i in range(len(sub)):
				if sub[i].split(" | ")[0] == str(m.author):  # Found old submissiom
					hasSubmitted = i
					break
			
			if hasSubmitted > -1:  # If user is resubmitting
				sub[hasSubmitted] = str(m.author) + " | " + m.content
				await send(m.channel, m.author.name + ", you've submitted a second time, thus your previous submission has been overridden by the new one. Thank you for your submission! :heart:")
				
			else:  # New submission
				sub.append(str(m.author) + " | " + m.content)
				await send(m.channel, m.author.name + ", thank you for your game submission! I've accepted your submission and will keep it safe until voting begins. :heart:")
				
			setSubmissions(sub)  # Save submissions

if debug:
	log("Discord", "I", "Logging in...")

# Run the Discord client and log in (will halt execution of main synchronous thread, so any code after this point would only run after the client logs out, which never happens under perfect circumstances)
disc.run(keys['discord'])
