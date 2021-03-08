# stuhealth

[![build](https://github.com/SO-JNU/stuhealth/workflows/build/badge.svg)](https://github.com/SO-JNU/stuhealth/actions)

使用 Python 编写的每日健康打卡命令行工具。

## 快速上手

```bash
# 首次使用需要安装依赖
$ pip3 install -r requirements.txt

# 输入学号和密码进行打卡
$ python3 stuhealth-cli.py -u 2017233333 -p p@SsW0Rd
```

推荐使用云服务器，设置 [Crontab](https://linuxtools-rst.readthedocs.io/zh_CN/latest/tool/crontab.html)（Linux）或[计划任务](https://juejin.cn/post/6844903939930865677)（Windows）实现自动化的每日打卡工作。

```bash
59 13 * * * python3 /path/to/stuhealth-cli.py -u 2017233333 -p p@SsW0Rd
```

> 对于未安装 Python 的 Windows 用户，可以在[这里](https://nightly.link/SO-JNU/stuhealth/workflows/build/master/stuhealth-cli)直接下载使用 PyInstaller 打包的可执行文件。
>
> 因为是命令行工具，所以需要在终端中运行（提示：在空白处按住 <kbd>Shift</kbd> 点击右键，选择“在此处打开 Powershell 窗口”可以打开终端），而不是直接双击。
>
> ```powershell
> PS C:\path\to> .\stuhealth-cli -u 2017233333 -p p@SsW0Rd
> ```

如果没有云服务器，也可以使用 GitHub Actions 实现自动打卡。（后述）

## 参数说明

| 参数 | 简写 | 说明 |
| - | - | - |
| `--jnuid` | `-j` | 打卡者的 JNUID，填写后即可跳过登录过程直接打卡。<br>留空则尝试使用用户名和密码登录。<br>登录成功后也会在终端中输出对应的 JNUID。 |
| `--username` | `-u` | 用户名，如果填写了 JNUID 则会被忽略。 |
| `--password` | `-p` | 密码，如果填写了 JNUID 则会被忽略。 |
| `--batch` | `-b` | 批量打卡的用户列表文件（参见[“批量打卡”](#批量打卡)部分）。<br>如果不需要批量打卡则可以留空。 |
| `--log` | `-l` | 将日志输出到指定的文件。 |
| `--silent` | `-s` | 不在终端中输出任何信息。 |
| `--multithread` | `-m` | 使用多线程执行批量打卡（实验性功能）。 |
| `--thread` | `-t` | 设置多线程时使用的线程数，默认为 8。 |
| `--no-print-jnuid` |  | 不在运行程序时输出 JNUID。 |
| `--no-update-check` |  | 不在运行程序时检查是否有更新（仅可在 Windows 打包版中使用）。 |
| `--help` | `-h` | 显示参数说明。 |

## 批量打卡

将需要打卡的用户信息按照以下格式示例保存为 JSON 文件（可以使用用户名和密码，也可以直接使用 JNUID）：

```json
[
    {"username": "2017233333", "password": "p@SsW0Rd"},
    {"username": "2018666666", "password": "An0+h3r_U$3r"},
    {"jnuid": "YXBwbGljYXRpb24vanNvbg**"}
]
```

假定保存的文件名为 `batch.json`，在终端中执行以下命令即可按顺序逐个为上面的三位用户执行打卡：

```bash
$ python3 stuhealth-cli.py -b batch.json
```

也可以使用多线程同时打卡。由于多线程可能会引起终端的输出混乱，此时建议将日志保存下来：

```bash
$ python3 stuhealth-cli.py -b batch.json -m -l result.log
```

## 使用 GitHub Actions 自动打卡

新建一个任意名称的 repository，设为 public 或 private 都可以。然后点击 Actions 选项卡创建一个新任务，输入以下配置：

<details>

```yaml
name: stuhealth-checkin

on:
  workflow_dispatch:
  schedule:
    # * is a special character in YAML so you have to quote this string
    - cron: '0 0 * * *'

jobs:
  stuhealth-checkin:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Clone stuhealth repository
        run: git clone https://github.com/SO-JNU/stuhealth.git
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.x
          architecture: x64
      - name: Cache pip dependencies
        uses: actions/cache@v2
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
      - name: Install pip dependencies
        working-directory: stuhealth
        run: pip install -r requirements.txt
      - name: Run stuhealth
        working-directory: stuhealth
        run: python stuhealth-cli.py -u ${{ secrets.username }} -p ${{ secrets.password }} --no-print-jnuid
```

</details>

根据需要自行修改 cron 表达式来改变执行时间。配置文件中使用的时区为 UTC，所以上面的表达式 `0 0 * * *` 表示在每天的 UTC 时间 0:00 即北京时间 8:00 执行。可以使用[这个在线工具](https://tool.lu/crontab/)来预览 cron 表达式指定的执行时间。

![](https://img20.360buyimg.com/myjd/jfs/t1/160304/2/11226/43567/6045b463Ec9175d2c/3ca97ae8413b2798.png)

在 Settings 选项卡中的 Secrets 部分添加 `username` 和 `password` 两项，内容分别为自己的用户名和密码。Secrets 保存后便无法再次查看，可以在 Actions 中使用但是也不会在执行结果中显示。

![](https://img20.360buyimg.com/myjd/jfs/t1/159718/28/11336/30002/6045b470E9a94b02d/d0547851b07f1b23.png)

设置完成后，在指定时间 GitHub Actions 就会自动帮你启动打卡机了。你可以在 Actions 选项卡中查看每次运行的结果。

![](https://img20.360buyimg.com/myjd/jfs/t1/140991/34/13332/31473/6045b473E62883ca1/557a90fa0e6b0100.png)

> 注意：GitHub Actions 不能保证任务一定可以准时按照 cron 表达式指定的时间运行，**实际执行时间可能会有数分钟的延迟**，可以参见[这里](https://upptime.js.org/blog/2021/01/22/github-actions-schedule-not-working/)的说明。