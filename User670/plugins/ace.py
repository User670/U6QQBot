from nonebot import on_command, CommandSession
import sys
import config as nbconfig

@on_command('ace', aliases=["py", "pyace", "python"], only_to_me=False)
async def arbitrary_code_execution(session: CommandSession):
	"""Runs arbitrary Python code from the command, and send any outputs
	or errors back through to the chat.
	For example, (if your command prefix is `u!`)
	
	u!ace print(1)
	
	will send a `1` to the chat.
	This is a very dangerous command, since bad code can wreck the bot
	or even your machine. Also note that endless loops will hang the
	bot and requires a manual reboot. MAKE SURE THAT YOU TRUST ALL YOUR
	SUPERUSERS!!
	"""
	if session.ctx["user_id"] not in nbconfig.SUPERUSERS: return
	
	# def send_message(session, content):
		# session.send(content)
	# print(session.current_arg_text)
	# try:
		# exec(session.current_arg_text)
	# except Exception as err:
		# await session.send(str(err))
	
	#f=open("ace.txt","w")
	snippit1='''import sys
sys.stdout=open("./User670/data/ace.txt","w")
'''
	snippit2='''sys.stdout.close()
'''
	
	
	try:
		exec(snippit1+session.current_arg_text+"\n"+snippit2)
	except Exception as err:
		await session.send(str(err))
	f=open("./User670/data/ace.txt","r")
	t=f.read()
	if t!="":
		await session.send(t)
	f.close()
	
	