import argparse
import base64
import json
import sys
import random
import requests
import time

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from urllib import parse

IS_PYINSTALLER = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

if IS_PYINSTALLER:
    from _version import GIT_COMMIT_HASH
    from _version import GIT_COMMIT_TIME

def buildHeader() -> dict[str, str]:
    return {
        'Content-Type': 'application/json',
        'X-Forwarded-For': '.'.join(str(random.randint(0, 255)) for x in range(4)),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko',
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        epilog='Source on GitHub: https://github.com/SO-JNU/stuhealth\nLicense: GNU AGPLv3\nAuthor: Akarin' + (f'\nCommit: {GIT_COMMIT_HASH} ({GIT_COMMIT_TIME})' if IS_PYINSTALLER else ''),
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '-u',
        '--username',
        required=True,
        type=str,
        help='Used for login.'
    )
    parser.add_argument(
        '-p',
        '--password',
        required=True,
        type=str,
        help='Used for login.'
    )
    parser.add_argument(
        '-ve',
        '--validator-endpoint',
        required=True,
        type=str,
        help='Endpoint of captcha validator API.'
    )
    parser.add_argument(
        '-vt',
        '--validator-token',
        required=True,
        type=str,
        help='Token of captcha validator API.'
    )
    parser.add_argument(
        '-l',
        '--log',
        required=False,
        type=str,
        help='Write log to the specified path.'
    )
    parser.add_argument(
        '-dr',
        '--dry-run',
        action='store_true',
        help='Print checkin data but don\'t submit it.'
    )
    args = parser.parse_args()

    username: str = args.username
    password: str = args.password
    validatorEndpoint: str = args.validator_endpoint
    validatorToken: str = args.validator_token
    log: str = args.log

    if not username or not password:
        parser.print_help()
        sys.exit(0)

    try:
        s = requests.Session()
        s.hooks['response'].append(lambda r, *args, **kwargs: r.raise_for_status())
        s.headers['User-Agent'] = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.0.0 Safari/537.36'
        key = b'xAt9Ye&SouxCJziN'
        cipher = AES.new(key, AES.MODE_CBC, key)
        success = False
        result = 'Failed to check in: '

        print('Getting verifyID.')
        r = s.get('https://stuhealth.jnu.edu.cn/', allow_redirects=False)
        verifyID = parse.parse_qs(parse.urlparse(r.headers['Location']).query)['verifyID'][0]
        s.get('https://auth7.jnu.edu.cn/wechat_auth/wechat/wechatScanAsync', params={'verifyID': verifyID})

        try:
            for i in range(3):
                print(f'Fetching captcha validate token. (Attempt #{i + 1}/3)')
                try:
                    validate = s.post(
                        validatorEndpoint,
                        headers={
                            'Authorization': f'Bearer {validatorToken}',
                        },
                    ).json()['validation_token']
                    attemptException = None
                    break
                except Exception as ex:
                    attemptException = ex
            if attemptException:
                raise Exception(f'Failed to get validate token: {type(attemptException).__name__} {attemptException}')
            print(f'Validate token: {validate[:8]}{"*" * min(8, max(0, len(validate) - 16))}{validate[-8:]}')

            print(f'Trying to login and get JNUID with username {username} and password.')
            login = s.post(
                'https://stuhealth.jnu.edu.cn/api/user/login',
                json.dumps({
                    'username': username,
                    'password': base64.b64encode(cipher.encrypt(pad(password.encode(), 16))).decode(),
                    'validate': validate,
                }),
                headers=buildHeader(),
            ).json()
            if not login['meta']['response']:
                raise Exception(f'Failed to get JNUID: {login["meta"]["msg"]}')
            jnuid = login['data']['jnuid']
            idType = login['data']['idtype']
            print(f'JNUID: {jnuid[:8]}{"*" * min(8, max(0, len(jnuid) - 16))}{jnuid[-8:]}')

            if login['meta']['code'] == 201 and not args.dry_run:
                result = 'Checkin already submitted.'
            else:
                stuinfo = s.post(
                    'https://stuhealth.jnu.edu.cn/api/user/stuinfo',
                    json.dumps({
                        'idType': idType,
                        'jnuid': jnuid,
                    }),
                    headers=buildHeader(),
                ).json()
                mainTable = {
                    k: v
                    for k, v in stuinfo['data']['mainTable'].items()
                    if v and k not in {'personType', 'createTime', 'del', 'id', 'other', 'passAreaC2', 'passAreaC3', 'passAreaC4', 'language', 'leaveTransportationOther'}
                }
                mainTable['declareTime'] = time.strftime('%Y-%m-%d', time.localtime())
                mainTable['personName'] = stuinfo['data']['xm']
                mainTable['sex'] = stuinfo['data']['xbm']
                mainTable['professionName'] = stuinfo['data']['zy']
                mainTable['collegeName'] = stuinfo['data']['yxsmc']

                if stuinfo['data']['secondTable'] is None:
                    if 'inChina' not in mainTable:
                        mainTable['inChina'] = '1'
                    for key in {'personC1', 'personC1id', 'personC2', 'personC2id', 'personC3', 'personC3id', 'personC4'}:
                        if key not in mainTable:
                            mainTable[key] = ''
                    if mainTable['inChina'] == '1':
                        secondTable = {
                            'other1': mainTable['inChina'],
                            'other3': mainTable['personC4'],
                            'other4': mainTable['personC1'],
                            'other5': mainTable['personC1id'],
                            'other6': mainTable['personC2'],
                            'other7': mainTable['personC2id'],
                            'other8': mainTable['personC3'],
                            'other9': mainTable['personC3id'],
                        }
                    elif mainTable['inChina'] == '2':
                        secondTable = {
                            'other1': mainTable['inChina'],
                            'other2': mainTable['countryArea'],
                            'other3': mainTable['personC4'],
                        }
                else:
                    secondTable = {
                        k: v
                        for k, v in stuinfo['data']['secondTable'].items()
                        if v and k not in {'mainId', 'id'}
                    }

                if args.dry_run:
                    print('Dry run mode enabled. Checkin data will not be submitted.')
                    print('You can submit it manually with the command:')
                    print('$ curl -X POST -H "Content-Type: application/json" -d ... https://stuhealth.jnu.edu.cn/api/write/main')
                    print('Checkin data:')
                    print(json.dumps(
                        {
                            'jnuid': jnuid,
                            'mainTable': mainTable,
                            'secondTable': secondTable,
                        },
                        ensure_ascii=False,
                        indent=4,
                        separators=(',', ': '),
                    ))
                    result = 'Dry run mode enabled.'
                else:
                    submit = s.post(
                        'https://stuhealth.jnu.edu.cn/api/write/main',
                        json.dumps(
                            {
                                'jnuid': jnuid,
                                'mainTable': mainTable,
                                'secondTable': secondTable,
                            },
                            ensure_ascii=False,
                        ).encode('utf-8'),
                        headers=buildHeader(),
                    ).json()
                    success = submit['meta']['success']

                    if success:
                        result = 'Checkin submitted.'
                    else:
                        raise Exception(submit['meta']['msg'])

            print(result)
        except Exception as ex:
            result += str(ex)
            raise ex
        finally:
            if log:
                with open(log, 'a+') as f:
                    f.write(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}] Username: {username} {result}\n')
    except Exception as ex:
        print(f'Failed to check in: {ex}')
        sys.exit(-1)
