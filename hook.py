import datetime
import subprocess

GIT_COMMIT_HASH = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip().decode('ascii')
GIT_COMMIT_TIME = datetime.datetime.fromtimestamp(int(subprocess.check_output(['git', '--no-pager', 'show', '-s', '--format=%ct']).strip().decode('ascii'))).strftime('%Y-%m-%d %H:%M:%S')