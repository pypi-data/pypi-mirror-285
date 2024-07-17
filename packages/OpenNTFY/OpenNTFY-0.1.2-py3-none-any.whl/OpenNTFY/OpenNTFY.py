import sys
import os
import asyncio
import subprocess
import argparse
from datetime import datetime, timedelta
import re
import json
import pyte
import time
import threading
import platform
from telegram import Bot
from ._telegram_config import run as telegram_config

parser = argparse.ArgumentParser(description='Telegram notifier')
parser.add_argument('message', nargs='?', default='Notification from {N}', type=str, help='The message to send')
parser.add_argument('-p', '--periodic', nargs=2, metavar=('period', 'command'), help='Execute a command getting periodical updates')
parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')
parser.add_argument('-f', '--file', type=str, help='File to send with relative path')
parser.add_argument('--config', action='store_true', help='Config telegram bot')

config_path = os.path.expanduser('~/.config/OpenNTFY/config.json') if platform.system() == 'Linux' else os.path.expanduser('~/AppData/Roaming/OpenNTFY/config.json')

loop = asyncio.get_event_loop()
screen = pyte.Screen(80, 24)
config = {}

def send(message, bot):
    loop.run_until_complete(bot.send_message(chat_id=config['TELEGRAM_CHAT_ID'], text=message))

def parse_screen():
    return '\n'.join(screen.display) if screen.display else ''

def periodic_send(period, bot):
    time.sleep(1)
    while True:
        message_p = parse_screen()
        if message_p:
            send(message_p, bot)
        time.sleep(period.total_seconds())

def parse_time_string(time_str):
    parts = re.findall(r'.*?[smhd]', time_str)
    total_seconds = 0

    for part in parts:
        value = int(part[:-1])
        unit = part[-1]

        if unit == 's':
            total_seconds += value
        elif unit == 'm':
            total_seconds += value * 60
        elif unit == 'h':
            total_seconds += value * 3600
        elif unit == 'd':
            total_seconds += value * 86400
        else:
            raise ValueError(f"Time unit not recognized: {unit}")

    return timedelta(seconds=total_seconds)

def main():
    try:
        args = parser.parse_args()

        if args.config:
            telegram_config(config_path)
            sys.exit(0)

        verboseprint = print if args.verbose else lambda *a: None

        try:
            with open(config_path) as f:
                global config
                config = json.load(f)
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            print("Please run OpenNTFY.py --config")
            sys.exit(1)

        bot = Bot(config['TELEGRAM_TOKEN'])

        dt = datetime.now()
        fields = {
            'N': platform.uname()[1],
            'T': dt.strftime("%H:%M:%S"),
            'D': dt.strftime("%d/%m/ %Y")
        }
        message = args.message.format(**fields) + '\n'

        if args.periodic:
            period = parse_time_string(args.periodic[0])
            command = args.periodic[1]
            verboseprint(f"Periodic execution of {command} every {period}")

            send_thread = threading.Thread(target=lambda: periodic_send(period, bot))
            send_thread.daemon = True
            send_thread.start()

            actual_screen = os.get_terminal_size()
            global screen
            screen = pyte.Screen(actual_screen.columns, actual_screen.lines)
            stream = pyte.Stream(screen)

            process = subprocess.Popen(
                f'stdbuf -oL {command}',
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            for c in iter(lambda: process.stdout.read(1), ''):
                print(c, end='', flush=True)
                stream.feed(c)

        if not os.isatty(0):
            cmd = sys.stdin.read()
            message += cmd

        if args.file:
            verboseprint(f"Sending file: {args.file}")
            try:
                loop.run_until_complete(bot.send_document(chat_id=config['TELEGRAM_CHAT_ID'], document=open(args.file, 'rb'), caption=message))
                verboseprint("File sent")
            except Exception as e:
                print(f"Error during file sending: {str(e)}")
                sys.exit(1)
        else:
            verboseprint(f"Sending message: {message}")
            try:
                send(message, bot)
                verboseprint("Message sent")
            except Exception as e:
                print(f"Error during message sending: {str(e)}")
                sys.exit(1)

    except KeyboardInterrupt:
        sys.exit(1)

if __name__ == '__main__':
    main()
