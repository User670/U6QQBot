from nonebot import on_command, CommandSession
import os
import config as nbconfig

@on_command('jsace',aliases=["js","node"],only_to_me=False)
async def arbitrary_code_execution_javascript(session: CommandSession):
	"""Runs arbitrary JavaScript code from the command, and send any
	output or errors to the chat.
	For example, (if your command prefix is `u!`)
	
	u!jsace console.log(1);
	
	will send a `1` to the chat.
	This is a very dangerous command, since bad code can wreck the bot
	or even your machine. Also note that endless loops *may* hang the
	bot and require a manual reboot. MAKE SURE THAT YOU TRUST ALL YOUR
	SUPERUSERS!!
	
	Requires Node.js that can be accessed in command line via `node`.
	If your Node.js requires some other command to access, change that
	in the line with `os.popen`.
	"""
	if session.ctx["user_id"] not in nbconfig.SUPERUSERS: return
	t=""
	try:
		snippit1='''try{\n'''
		snippit2='''\n}catch(err){console.log(err);}'''
		f=open("./User670/data/jsace.js","w",encoding="utf-8")
		f.write(snippit1+session.current_arg_text+"\n"+snippit2)
		f.close()
		ff=os.popen("node ./User670/data/jsace.js")
		t=ff.read()
		ff.close()
	except Exception as err:
		t=str(err)
	await session.send(t)
	
	