from nonebot import on_command, CommandSession
import time
import config as nbconfig
import json as JSON
JSON.parse=JSON.loads
JSON.stringify=JSON.dumps

@on_command('swatch',aliases=["streamwatch", "streamswatch", "stream", "streams"], only_to_me=False)
async def report_time(session: CommandSession):
	"""Manipulates the streamswatchconfig.json.
	"""
	def timediff(a,b):
		c=a-b
		sign= 1 if c>=0 else -1
		if sign==-1: c=-c
		d=c//86400
		h=(c%86400)//3600
		m=(c%3600)//60
		s=c%60
		if d!=0: return "{}d{}h".format(d,h)
		if h!=0: return "{}h{}m".format(h,m)
		if m!=0: return "{}m{}s".format(m,s)
		return "{}s".format(s)
	
	now=int(time.time())
	if session.ctx["user_id"] not in nbconfig.SUPERUSERS: return
	args=session.current_arg_text.split(" ")
	try:
		grpid=int(session.ctx["group_id"])
	except:
		grpid=0
	
	f=open("./User670/config/streamwatchconfig.json")
	config=JSON.parse(f.read())
	f.close()
	
	if len(args)==0:
		args=[""]
	
	if args[0]=="global":
		# u!swatch global: show current global settings
		# u!swatch global interval 10: set global settings
		if len(args)==1:
			await session.send("""Current global settings:
interval: {}
maxcd: {}
persecondlimit: {}
verbosemessage: {}""".format(
				config["global"]["interval"],
				config["global"]["maxcd"],
				config["global"]["persecondlimit"],
				config["global"]["verbosemessage"]
			))
			return
		if len(args)<3:
			await session.send("u!swatch global <option> <value>")
			return
		if args[1] not in ["interval","maxcd","persecondlimit","verbosemessage"]:
			await session.send("Invalid option")
			return
		try:
			config["global"][args[1]]=int(args[2])
			f=open("./User670/config/streamwatchconfig.json","w")
			f.write(JSON.stringify(config))
			f.close()
			return
		except:
			await session.send("Invalid value (expecting int)")
			return
	elif args[0]=="list":
		# u!swatch list: list watching streamers
		# u!swatch list 123: list groups being notified for this streamer
		if len(args)==1:
			t="Currently following these streamers: (Note: UID, not stream ID)"
			for i in config["list"]:
				t+="\n"+str(i["mid"])
			await session.send(t)
			return
		for i in config["list"]:
			if args[1]==i["mid"]:
				if len(i["groups"])==0:
					await session.send("Currently no groups are notified of this streamer.\nu!swatch unsub {} to remove this streamer from watchlist, or u!swatch notify here {} to add this group to notification list.".format(args[1], args[1]))
					return
				t="Currently the following groups will receive notification for this streamer:"
				for j in i["groups"]:
					t+="\n"+str(j)
				await session.send(t)
				return
		#Streamer not found:
		await session.send("The specified streamer is not found.")
		return
	elif args[0]=="info":
		# u!swatch info 123: show info from streamswatchlog.
		for i in config["list"]:
			if args[1]==i["mid"]:
				f=open("./User670/data/streamwatchlog.json")
				data=JSON.parse(f.read())
				f.close()
				if args[1] not in data:
					await session.send("While this streamer is being watched, no data of this streamer exist in the logs. Maybe wait until next successful pull.")
					return
				await session.send("""Streamer {}'s info, according to the logs:
Nickname: {}
Status: {} (since {} ago, last updated {} ago)
Next pull: in {} (current interval {})""".format(
					data[args[1]]["name"],
					"Not streaming" if data[args[1]]["lastquery"][0]==0 else ("Streaming" if data[args[1]]["lastquery"][0]==1 else "Error"),
					timediff(now, data[args[1]]["lastquery"][2]),
					timediff(now, data[args[1]]["lastquery"][1]),
					timediff(now, data[args[1]]["nextquery"]),
					timediff(0, data[args[1]]["cd"])
				))
				return
		#Streamer not found:
		await session.send("The specified streamer is not found.")
		return
	else:
		await session.send("""Implemented features:
u!swatch global
u!swatch global <option> <value>
u!swatch list
u!swatch list <uid>
u!swatch info <uid>

Unimplemented featrues:
u!swatch sub <uid>
u!swatch unsub <uid>
u!swatch notify <group|"here"> <uid>
u!swatch unnotify <group|"here"|"all"> <uid>""")
		return