from nonebot import on_command, CommandSession
import time
import config as nbconfig

@on_command('time',only_to_me=False)
async def report_time(session: CommandSession):
	"""Sends current date and time to the chat.
	Why? You decide.
	"""
	if session.ctx["user_id"] not in nbconfig.SUPERUSERS: return
	await session.send("当前时间："+time.ctime())