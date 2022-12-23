import var
import asyncio
import sys
import importlib
import bot

from time import sleep
# restart = False
# main()
# print(var.restart0)
if sys.platform == 'win32':
    loop = asyncio.ProactorEventLoop()  # needed for subprocesses
    asyncio.set_event_loop(loop)

while True:
    importlib.reload(bot)
    importlib.reload(var)
    var.restart = False
    bot.main()
    # print(var.restart)
    if not var.restart:
        break
    else:
        asyncio.set_event_loop(asyncio.new_event_loop())
        sleep(5)
