import argparse
import base64
import json
import os
import random
import requests
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

def checkin(jnuid, username, password, log, silent):
    key = b'xAt9Ye&SouxCJziN'
    cipher = AES.new(key, AES.MODE_CBC, key)
    success = False
    result = 'Failed to check in: '

    try:
        if not jnuid:
            if not silent:
                print('Trying to login and get JNUID with username and password')
            try:
                jnuid = requests.post(
                    'https://stuhealth.jnu.edu.cn/api/user/login',
                    json.dumps({
                        'username': username,
                        'password': base64.b64encode(cipher.encrypt(pad(password.encode(), 16))).decode(),
                    }),
                    headers={
                        'Content-Type': 'application/json',
                        'X-Forwarded-For': '.'.join(str(random.randint(0, 255)) for x in range(4)),
                    }
                ).json()['data']['jnuid']
            except Exception as ex:
                raise Exception('Failed to get JNUID')
        if not silent:
            print(f'JNUID: {jnuid}')

        checkinInfo = requests.post(
            'https://stuhealth.jnu.edu.cn/api/user/stucheckin',
            json.dumps({
                'jnuid': jnuid,
            }),
            headers={
                'Content-Type': 'application/json',
                'X-Forwarded-For': '.'.join(str(random.randint(0, 255)) for x in range(4)),
            }
        ).json()
        if not checkinInfo['meta']['success']:
            raise Exception('Invalid JNUID')
        for item in checkinInfo['data']['checkinInfo']:
            if item['flag'] == True:
                checkinInfo = item
                break

        if not silent:
            print(f'Fetching last checkin info #{checkinInfo["id"]} ({checkinInfo["date"]})')
        mainTable = requests.post(
            'https://stuhealth.jnu.edu.cn/api/user/review',
            json.dumps({
                'jnuid': jnuid,
                'id': str(checkinInfo["id"]),
            }),
            headers={
                'Content-Type': 'application/json',
                'X-Forwarded-For': '.'.join(str(random.randint(0, 255)) for x in range(4)),
            }
        ).json()['data']['mainTable']

        deleteKey = ['personType', 'createTime', 'del', 'id']
        deleteKey.extend(key for key in mainTable.keys() if mainTable[key] == '')
        for key in deleteKey:
            del mainTable[key]
        mainTable['declareTime'] = time.strftime('%Y-%m-%d', time.localtime())

        submit = requests.post(
            'https://stuhealth.jnu.edu.cn/api/write/main',
            json.dumps({
                'jnuid': jnuid,
                'mainTable': mainTable,
            }),
            headers={
                'Content-Type': 'application/json',
                'X-Forwarded-For': '.'.join(str(random.randint(0, 255)) for x in range(4)),
            }
        ).json()
        success = submit['meta']['success']
        if success:
            result = 'Checkin submitted.'
        else:
            raise Exception(submit['meta']['msg'])
    except Exception as ex:
        result += f'{type(ex).__name__} {ex}'
        raise ex
    finally:
        if log:
            with open(log, 'a+') as f:
                f.write(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}] JNUID: {jnuid} {result}\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        epilog='Source on GitHub: https://github.com/SO-JNU/stuhealth\nLicense: GNU GPLv3',
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
    args = parser.parse_args()

    if not args.jnuid and (not args.username or not args.password):
        parser.print_help()
        exit(0)

    try:
        checkin(args.jnuid, args.username, args.password, args.log, args.silent)
    except Exception as ex:
        if not args.silent:
            print(f'Failed to check in: {type(ex).__name__} {ex}')
        exit(-1)
