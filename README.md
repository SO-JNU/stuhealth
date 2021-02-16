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

推荐使用 [Crontab](https://linuxtools-rst.readthedocs.io/zh_CN/latest/tool/crontab.html)（Linux）或[计划任务](https://juejin.cn/post/6844903939930865677)（Windows）实现自动化的每日打卡工作。

```bash
59 13 * * * python3 /path/to/stuhealth-cli.py -u 2017233333 -p p@SsW0Rd
```

> 对于未安装 Python 的 Windows 用户：
>
> 可以在[这里](https://nightly.link/SO-JNU/stuhealth/workflows/build/master/stuhealth-cli)直接下载使用 PyInstaller 打包的可执行文件。
>
> 因为是命令行工具，所以需要在终端中运行（提示：在空白处按住 <kbd>Shift</kbd> 点击右键，选择“在此处打开 Powershell 窗口”可以打开终端），而不是直接双击。
>
> ```powershell
> PS C:\path\to> .\stuhealth-cli -u 2017233333 -p p@SsW0Rd
> ```

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
| `--no-update-check` |  | 不在运行程序时检查是否有更新。 |
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
