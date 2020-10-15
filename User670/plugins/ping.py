from nonebot import on_command, CommandSession
import config as nbconfig

@on_command('ping',only_to_me=False)
async def ping(session: CommandSession):
	"""Replies ``Pong!`` to the command call.
	"""
	if session.ctx["user_id"] not in nbconfig.SUPERUSERS: return
	await session.send("Pong!")