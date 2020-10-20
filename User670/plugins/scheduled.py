from datetime import datetime
import time
import json as JSON
JSON.stringify=JSON.dumps
JSON.parse=JSON.loads
import requests
import nonebot
import pytz
from aiocqhttp.exceptions import Error as CQHttpError
import User670.utils.u6logger as u6logger


@nonebot.scheduler.scheduled_job('cron', second='*')
async def scheduled():
	"""All code that run periodically go here!
	It runs every second; if you need things that run every longer
	period, make the code read current time and do conditional
	checks.
	
	If the code here does not finish within a single second, it may
	throw errors into the console. Not sure how that affects the bot
	"""
	def timercheck(lastpull, mode, parameter):
		'''
		A helper function to test if it's time to perform a task.
		Somehow I never ended up using it.
		
		lastpull: a unix timestamp of when you last performed the task.
		mode: string "interval" or "timestamp".
		if mode is "interval":
			Next run will be at least a number of seconds after the
			previous.
			parameter: a single integer, interval in seconds.
		if mode is "timestamp":
			Use a few timestamps to control whether to run the task.
			The difference of this between "current time == timestamp"
			approach is that, if it somehow skips a timestamp (say,
			due to some downtime), it will immediately execute as soon
			as it is able to run again.
			parameter: a list of 6-digit intergers, in the format hhmmss.
		
		Returns True or False of whether it should run.
		
		Example (assuming UTC timezone):
		
		timercheck(0, "interval", 3600)
			it will return True as long as current time >= 1970-01-01
			01:00 (i.e. 3,600 second past 1970-01-01 00:00).
		timercheck(3600, "timestamp", [003000, 013000])
			It will see that it has cleared the 00:30 timestamp, so it
			will return True as long as current time >= 1970-01-01 01:30
			(i.e. the next timestamp).
		timercheck(7200, "timestamp", [003000, 013000])
			It will see that it has cleared both the 00:30 and 01:30
			timestamps of the day, so it will return True as long as
			current time >= 1970-01-02 00:30 (i.e. the first timestamp 
			of the *next* day).		
		'''
		if mode=="interval":
			return int(time.time())-lastpull>=parameter
		
		if mode=="timestamp":
			t=time.localtime(lastpull)
			t=list(t)
			# 0     1      2      3      4      5
			# year  month  day    hour   minute second
			lt=t[3]*10000+t[4]*100+t[5]
			idx=0
			day=0
			for i in parameter:
				if lt>i:
					idx+=1
				else:
					break
			if idx==len(parameter):
				day=1
				idx=0
			nt=parameter[idx]
			h=nt//10000
			m=nt//100%100
			s=nt%100
			t[2]+=day
			t[3]=h
			t[4]=m
			t[5]=s
			t=time.mktime(tuple(t))
			return int(time.time())>=t

	def getjson(url, component=""):
		"""HTTP GET a JSON value. (Didn't test on JSONP; use at your own
		risk)
		Returns the parsed value, or None if an error occurs. Also logs
		if error occurs.
		"""
		headers={"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
		"accept-encoding": "gzip, deflate, br",
		"accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7",
		"cache-control": "max-age=0",
		"cookie": "LIVE_BUVID=AUTO7515618136945152; _uuid=8D45A9BB-3572-83C1-BE52-C7700A36A5A217113infoc; Hm_lvt_8a6e55dbd2870f0f5bc9194cddf32a02=1575749719; buvid3=76E414E5-84AB-4332-B821-B067D8663522190969infoc",
		"dnt": "1",
		"sec-fetch-dest": "document",
		"sec-fetch-mode": "navigate",
		"sec-fetch-site": "none",
		"sec-fetch-user": "?1",
		"upgrade-insecure-requests": "1",
		"user-agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36"}
		try:
			r=requests.get(url,headers=headers)
			return r.json()
		except Exception as err:
			u6logger.log("Scheduled -> getjson: "+("in component "+component+" " if component!="" else "")+"getting this URL throws an error:",url,"(error message:",str(err),")")
			return None
	
	bot = nonebot.get_bot()
	now = int(time.time())
	
	
	# *************************
	#      Streams Watch
	# *************************
	"""Checks live streams on Bilibili.
	Probably TODO: use a newer version of the Bilibili API.
	
	This requires a config file in User670/config, and a log file in
	User670/data.
	"""
	
	f=open("./User670/config/streamwatchconfig.json","r")
	config=JSON.parse(f.read())
	f.close()
	
	verbosemessage=config["global"]["verbosemessage"]
	
	f=open("./User670/data/streamwatchlog.json","r")
	log=JSON.parse(f.read())
	f.close()
	
	count=0
	
	#u6logger.log("StreamsWatch begins")
	
	for i in config["list"]:
		#i={id, mid, groups{id:type}}
		#u6logger.log("Pulling data for streamer with mid",i["mid"])
		
		#0. Does this streamer have a record in log?
		if i["mid"] not in log.keys():
			log[i["mid"]]={
				"name":"",
				"lastquery":[-1,0,0],
					#[0]: 0 (not live), 1 (live), 2 (error), -1 (init)
					#[1]: the last pull
					#[2]: the time it changed to this state
				"nextquery":0,
				"cd":config["global"]["interval"]
			}
		
		#0.1. Should I pull or should I wait?
		if now<log[i["mid"]]["nextquery"]:
			#u6logger.log("Recent pull, skipping")
			continue
		
		
		#1. fetch data about this streamer
		d=getjson("https://api.live.bilibili.com/room/v1/Room/getRoomInfoOld?mid="+str(i["mid"]))
		
		thispull=0
		if d==None:
			# request failed: the request itself is dead
			#u6logger.log("API request is dead. There should be a log detailing the error.")
			#await bot.send_private_msg(user_id=verbosemessage, message=time.ctime()+" - StreamsWatch failed to obtain a JSON data from API request. Check logs for more info.")
			thispull=2
		elif d["code"]!=0:
			u6logger.log("API request gives a non-zero return code ("+str(d["code"])+"). Full response data:",JSON.stringify(d))
			await bot.send_private_msg(user_id=verbosemessage, message=time.ctime()+" - StreamsWatch received a non-zero return code from Bilibili. Check logs for more info.")
			# request failed: Bilibili didn't give data
			thispull=2
		else:
			#2. request successful.
			#u6logger.log("API request successful, with liveStatus",d["data"]["liveStatus"])
			thispull=d["data"]["liveStatus"]
		
		statuspair=[log[i["mid"]]["lastquery"][0],thispull]
		
		if statuspair==[0,1]:
			#stream begins
			dd=getjson("https://api.live.bilibili.com/live_user/v1/UserInfo/get_anchor_in_room?roomid="+str(d["data"]["roomid"]))
			try:
				log[i["mid"]]["name"]=dd["data"]["info"]["uname"]
			except:
				pass
			t=time.ctime()+"\n"
			t+=log[i["mid"]]["name"] if log[i["mid"]]["name"]!="" else "(昵称信息暂无)"
			t+=" 开播了。\n\n"
			t+=d["data"]["title"]+"\n"
			t+=d["data"]["url"]
			
			try:
				await bot.send_private_msg(user_id=verbosemessage, message=t)
			except:
				u6logger.log("Scheduled -> Streamwatch: send info to OP failed.")
			
			if "#测试" not in d["data"]["title"]:			   
				for j in i["groups"].keys():
					try:
						await bot.send_group_msg(group_id=int(j),message=t)
					except:
						u6logger.log("Scheduled -> Streamwatch: send info to groupchat failed:",j)
		if statuspair==[1,0]:
			#stream ends
			dd=getjson("https://api.live.bilibili.com/live_user/v1/UserInfo/get_anchor_in_room?roomid="+str(d["data"]["roomid"]))
			try:
				log[i["mid"]]["name"]=dd["data"]["info"]["uname"]
			except:
				pass
			t=time.ctime()+"\n"
			t+=log[i["mid"]]["name"] if log[i["mid"]]["name"]!="" else "(昵称信息暂无)"
			t+=" 下播了。\n\n"
			t+=d["data"]["url"]
			
			try:
				await bot.send_private_msg(user_id=verbosemessage, message=t)
			except:
				u6logger.log("Scheduled -> Streamwatch: send info to OP failed.")
			
			if "#测试" not in d["data"]["title"]:
				for j in i["groups"].keys():
					if i["groups"][j] in [1]:
						try:
							await bot.send_group_msg(group_id=int(j),message=t)
						except:
							u6logger.log("Scheduled -> Streamwatch: send info to groupchat failed:",j)
			
		if statuspair[0]==-1:
			#stream has just been added
			dd=getjson("https://api.live.bilibili.com/live_user/v1/UserInfo/get_anchor_in_room?roomid="+str(d["data"]["roomid"]))
			try:
				log[i["mid"]]["name"]=dd["data"]["info"]["uname"]
			except:
				pass
			t=time.ctime()+"\n"
			t+=log[i["mid"]]["name"] if log[i["mid"]]["name"]!="" else "(昵称信息暂无)"
			t+=" was added to the database and was scanned for the first time.\n\n"
			t+="Current stream status: "+str(statuspair[1])+"\n"
			t+="Current stream title: "+d["data"]["title"]+"\n"
			t+=d["data"]["url"]
			
			try:
				await bot.send_private_msg(user_id=verbosemessage, message=t)
			except:
				u6logger.log("Scheduled -> Streamwatch: send info to OP failed.")
			
			
		
		
		if thispull==2:
			log[i["mid"]]["lastquery"]=[
				2,
				now,
				now if thispull!=statuspair[0] else log[i["mid"]]["lastquery"][2]
			]
			log[i["mid"]]["cd"]=min(log[i["mid"]]["cd"]*2,config["global"]["maxcd"])
			log[i["mid"]]["nextquery"]=now+log[i["mid"]]["cd"]
		else:
			log[i["mid"]]["lastquery"]=[
				thispull,
				now,
				now if thispull!=statuspair[0] else log[i["mid"]]["lastquery"][2]
			]
			log[i["mid"]]["cd"]=config["global"]["interval"]
			log[i["mid"]]["nextquery"]=now+log[i["mid"]]["cd"]
		
		count+=1
		if count>=config["global"]["persecondlimit"]:
			#u6logger.log("Excceeding per-second pull limit, breaking loop")
			break
	
	
	f=open("./User670/data/streamwatchlog.json","w")
	f.write(JSON.stringify(log))
	f.close()
	
	#u6logger.log("StreamsWatch ended.")
	
	
	# ***********************
	#      Diandian Watch
	# ***********************
	"""This notifies streaming on a website called Diandian Kaihei
	(y.tuwan.com).
	
	This requires a separate program writing files into ../common/dd
	This separate program will not be open source.
	
	This also requires a config file in User670/config, and a log file
	in User670/data.
	
	
	An explanation about the separate program:
	In short:
		- it will connect to Diandian's chat socket,
		- read incoming messages,
		- for every message with `typeid:1`, dump the message into
		  (cid)-host.json, eg `3710-host.json`
		- for every message with `typeid:18`, dump the message into
		  (cid)-room.json, eg `3710-room.json`
		- The files will be in, relative to this bot, ../common/dd
	You can figure out how to connect to the socket by exploring the source
	code of Diandian Kaihei. Some tips:
		- It uses socket.io. Unless you know how to do equivalent tasks in
		  other languages/libraries, I recommend you implement your code
		  in node.js with socket.io-client library imported.
		- Find class `DianDianSocket` in chat0-xxx.js (where xxx are numbers),
		  and `gloabDDSoket` in chat3-xxx.js. You'll see how this is being
		  used to connect to the socket. (tips: the values used in the
		  connect method call ultimately come from a GET request.)
		- After connecting to the socket, you need to send an initlist event
		  to make the socket recognize where you are and who you are.
		  You can find relevant code in chat3.
	"""
	f=open("./User670/config/ddwatchconfig.json","r")
	config=JSON.parse(f.read())
	f.close()
	
	verbosemessage=config["global"]["verbosemessage"]
	
	f=open("./User670/data/ddwatchlog.json","r")
	log=JSON.parse(f.read())
	f.close()
	"""ddwatchlog format
	{
		"uid@channel":{
			"host":[status, since, lastupdated],
			      //^ 0=no, 1=yes
			"room":[status, since, lastupdated]
		          //^ 0=no, 1=yes and open, 2=yes and closed
		}
	}
	"""
	
	
	if timercheck(log["global"]["lastpull"], "interval", config["global"]["interval"]):
		verboselog=""
		ddnotify={}
		for channel in config["list"]:
			cname=config["channelNameOverrides"][channel]
			f=open("../common/dd/"+channel+"-host.json")
			host=JSON.parse(f.read())
			f.close()
			f=open("../common/dd/"+channel+"-room.json")
			room=JSON.parse(f.read())
			f.close()
			for uid in config["list"][channel]:
				logKey=uid+"@"+channel
				if logKey not in log.keys():
					log[logKey]={
						"nick":"",
						"host":[-1, 0, 0],
						"room":[-1, 0, 0]
					}
				# Is this UID on mic in this channel?
				foundHost=0
				for i in host["data"]:
					if i["uid"]!=int(uid):
						continue
					foundHost=1
					log[logKey]["nick"]=i["nickname"]
					break
				nick=log[logKey]["nick"]
				statuspair=[log[logKey]["host"][0], foundHost]
				if statuspair[0]==-1:
					verboselog+="\n"+logKey+"/host was being tracked the first time."
				if statuspair==[0,1]:
					verboselog+="\n"+logKey+" ("+nick+"@"+cname+") is now on mic."
					for group in config["list"][channel][uid]:
						if group not in ddnotify.keys():
							ddnotify[group]=""
						ddnotify[group]+="\n"+nick+" 在 "+cname+" 上麦了。"
				if statuspair==[1,0]:
					verboselog+="\n"+logKey+" ("+nick+"@"+cname+") is no longer on mic."
				
				if statuspair[0]!=statuspair[1]:
					log[logKey]["host"][0]=foundHost
					log[logKey]["host"][1]=now
				log[logKey]["host"][2]=now
				
				# Is this UID hosting a room in this channel?
				foundRoom=0
				roominfo=""
				for i in room["data"]:
					if i["uid"]!=int(uid):
						continue
					foundRoom=i["state"]+1
					log[logKey]["nick"]=i["nickname"]
					roominfo=i["desc"]+" - "+i["area"]+"/"+i["level"]
					break
				nick=log[logKey]["nick"]
				statuspair=[log[logKey]["room"][0], foundRoom]
				if statuspair[0]==-1:
					verboselog+="\n"+logKey+"/room was being tracked the first time."
				if statuspair==[0,1]:
					verboselog+="\n"+logKey+" ("+nick+"@"+cname+") opened a room. ("+roominfo+")"
					for group in config["list"][channel][uid]:
						if group not in ddnotify.keys():
							ddnotify[group]=""
						ddnotify[group]+="\n"+nick+" 在 "+cname+" 开启了车队。（"+roominfo+"）"
				if statuspair==[0,2]:
					verboselog+="\n"+logKey+" ("+nick+"@"+cname+") opened a room and quickly launched it. ("+roominfo+")"
				if statuspair==[1,0]:
					verboselog+="\n"+logKey+" ("+nick+"@"+cname+") closed the room (from not running)."
				if statuspair==[1,2]:
					verboselog+="\n"+logKey+" ("+nick+"@"+cname+") launched the room. ("+roominfo+")"
				if statuspair==[2,0]:
					verboselog+="\n"+logKey+" ("+nick+"@"+cname+") closed the room (from running)."
				if statuspair==[2,1]:
					verboselog+="\n"+logKey+" ("+nick+"@"+cname+") closed and opened a room. ("+roominfo+")"
					for group in config["list"][channel][uid]:
						if group not in ddnotify.keys():
							ddnotify[group]=""
						ddnotify[group]+="\n"+nick+" 在 "+cname+" 开启了车队。（"+roominfo+"）"
				
				if statuspair[0]!=statuspair[1]:
					log[logKey]["host"][0]=foundHost
					log[logKey]["host"][1]=now
				log[logKey]["host"][2]=now
		# I hope this doesn't turn out to be too buggy
		if verboselog!="":
			try:
				await bot.send_private_msg(user_id=verbosemessage, message="Diandian Watch\n"+time.ctime()+"\n"+verboselog)
			except:
				u6logger.log("Scheduled -> DDwatch: send info to OP failed.")
		for group in ddnotify:
			try:
				await bot.send_group_msg(group_id=group,message="点点开黑\n"+time.ctime()+"\n"+ddnotify[group])
			except:
				u6logger.log("Scheduled -> DDwatch: send info to group failed.")
		
		f=open("./User670/data/ddwatchlog.json","w")
		f.write(JSON.stringify(log))
		f.close()