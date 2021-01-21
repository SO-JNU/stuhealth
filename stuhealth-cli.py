import argparse
import json
import stuhealth
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

IS_PYINSTALLER = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

if IS_PYINSTALLER:
    from _version import GIT_COMMIT_HASH
    from _version import GIT_COMMIT_TIME

parser = argparse.ArgumentParser(
    epilog='Source on GitHub: https://github.com/SO-JNU/stuhealth\nLicense: GNU GPLv3\nAuthor: Akarin' + (f'\nCommit: {GIT_COMMIT_HASH} ({GIT_COMMIT_TIME})' if IS_PYINSTALLER else ''),
    formatter_class=argparse.RawTextHelpFormatter
)
parser.add_argument(
    '-j',
    '--jnuid',
    required=False,
    type=str,
    help='Use JNUID to make a check-in directly, or leave it blank and login with username and password.'
)
parser.add_argument(
    '-u',
    '--username',
    required=False,
    type=str,
    help='Used for login.'
)
parser.add_argument(
    '-p',
    '--password',
    required=False,
    type=str,
    help='Used for login.'
)
parser.add_argument(
    '-b',
    '--batch',
    required=False,
    type=str,
    help='Specify a JSON file to perform batch check-in. See README.md for details.'
)
parser.add_argument(
    '-l',
    '--log',
    required=False,
    type=str,
    help='Write log to the specified path.'
)
parser.add_argument(
    '-s',
    '--silent',
    action='store_true',
    help='Slient mode.'
)
parser.add_argument(
    '-m',
    '--multithread',
    action='store_true',
    help='Use multithreading for batch check-in. This is a experimental feature!'
)
parser.add_argument(
    '-t',
    '--thread',
    required=False,
    default=8,
    type=int,
    help='Number of threads for multithreading.'
)
args = parser.parse_args()

if args.batch:
    checkinList = [{
        'jnuid': None,
        'username': None,
        'password': None,
        **x,
    } for x in json.load(open(args.batch, 'r', encoding='utf-8'))]
else:
    if not args.jnuid and (not args.username or not args.password):
        parser.print_help()
        sys.exit(0)
    checkinList = [vars(args)]

def run(jnuid, username, password, log, silent):
    try:
        stuhealth.checkin(jnuid, username, password, log, silent)
    except Exception as ex:
        if not silent:
            print(f'Failed to check in: {type(ex).__name__} {ex}')

if args.multithread and len(checkinList) > 1:
    if not args.silent:
        print('Warning: multithreading enabled, the output may be messed up.')
    with ThreadPoolExecutor(args.thread) as executor:
        for item in checkinList:
            executor.submit(run, item['jnuid'], item['username'], item['password'], args.log, args.silent)
else:
    for item in checkinList:
        run(item['jnuid'], item['username'], item['password'], args.log, args.silent)
