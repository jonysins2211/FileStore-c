from bot import Bot
import pyrogram.utils
import threading
from masked_server import run_server

pyrogram.utils.MIN_CHANNEL_ID = -1009147483647

if __name__ == "__main__":

    # start masked link server
    threading.Thread(target=run_server).start()

    # start telegram bot
    Bot().run()
