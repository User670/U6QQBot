from nonebot import on_command, CommandSession
import config as nbconfig

@on_command('leave',only_to_me=False)
async def leave_group(session: CommandSession):
	"""Leaves the group.
	MAKE SURE YOU TRUST YOUR SUPERUSERS!
	"""
	if session.ctx["user_id"] not in nbconfig.SUPERUSERS: return
	try:
		grpid=int(session.ctx["group_id"])
	except:
		await session.send("退群：无法获取群号。也许这里不是一个群？")
		return
	try:
		await session.bot.set_group_leave(group_id=grpid)
	except Exception as e:
		await session.send("退群：失败，错误代码"+str(e.retcode))