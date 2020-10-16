import nonebot
from nonebot import on_request,RequestSession
import time
import config as nbconfig

bot = nonebot.get_bot()

@bot.on_message()
async def handle_triggers(ctx: nonebot.typing.Context_T):
	"""This used to be where I put conditional notifications. It's been
	removed since."""
	def handle_ctx(ctx):
		"""This formats the message context in a human-readable-ish format.
		Seems to have broken for Mirai."""
		t=""
		if ctx["post_type"]=="message" and ctx["message_type"]=="group":
			c=get_config(str(ctx["group_id"]))
			try:
				gpname=" ("+c["name"]+")"
			except:
				gpname=""
			t="Group message at "+str(ctx["group_id"])+gpname+"\n"
			t+="From "+ctx["sender"]["nickname"]
			try:
				t+="("+(ctx["sender"]["card"]+" / " if ctx["sender"]["card"]!="" else "")+str(ctx["sender"]["user_id"])+")\n"
			except:
				t+="\n"
			t+="Time: "+time.ctime(ctx["time"])+"\n"
			t+=str(list(ctx["message"]))
		else:
			t+=str(ctx)
		return t
	
	
		
@on_request("group")
async def join_group(session: RequestSession):
	if session.ctx["sub_type"]!="invite":return
	if session.ctx["user_id"] not in nbconfig.SUPERUSERS: return
	await session.approve()	