# stuhealth

[![build](https://github.com/SO-JNU/stuhealth/workflows/build/badge.svg)](https://github.com/SO-JNU/stuhealth/actions)

使用 Python 编写的每日健康打卡命令行工具。

2021 年 9 月 14 日起，打卡系统增加了滑动验证码，并且在服务端实装了二次验证，因此：

* 基于抓包和 JavaScript 逆向的打卡机（包括这个 repo 在内）都已经失效了。
* 基于 Selenium、Puppeteer、Playwright 等浏览器自动控制工具的打卡机，需要自行实现模拟拖动滑块的操作来突破滑动验证码。**已实现！**
* ~~这个 repo 将设为 Archived 状态，代码和说明文本仅作为存档，不再更新。~~

## 快速上手

```bash
# 首次使用需要安装依赖
$ pip3 install -r requirements.txt

# 输入学号和密码进行打卡
$ python3 stuhealth.py -u 2017233333 -p p@SsW0Rd -ve https://example.com/ -vp Ap1t0K3N
```

推荐使用云服务器，设置 [Crontab](https://linuxtools-rst.readthedocs.io/zh_CN/latest/tool/crontab.html)（Linux）或[计划任务](https://juejin.cn/post/6844903939930865677)（Windows）实现自动化的每日打卡工作。

```bash
59 13 * * * python3 /path/to/stuhealth.py -u 2017233333 -p p@SsW0Rd -ve https://example.com/ -vp Ap1t0K3N
```

> 对于未安装 Python 的 Windows 用户，可以在[这里](https://nightly.link/SO-JNU/stuhealth/workflows/build/master/stuhealth-cli)直接下载使用 PyInstaller 打包的可执行文件。
>
> 因为是命令行工具，所以需要在终端中运行（提示：在空白处按住 <kbd>Shift</kbd> 点击右键，选择“在此处打开 Powershell 窗口”可以打开终端），而不是直接双击。
>
> ```powershell
> PS C:\path\to> .\stuhealth -u 2017233333 -p p@SsW0Rd -ve https://example.com/ -vp Ap1t0K3N
> ```

如果没有云服务器，也可以使用 GitHub Actions 实现自动打卡。（后述）

## 参数说明

| 参数 | 简写 | 说明 |
| - | - | - |
| `--username` | `-u` | 用户名。 |
| `--password` | `-p` | 密码。 |
| `--validator-endpoint` | `-ve` | 滑动验证码 API 地址。 |
| `--validator-token` | `-vt` | 滑动验证码 API 的鉴权 token。 |
| `--log` | `-l` | 将日志输出到指定的文件。 |
| `--help` | `-h` | 显示参数说明。 |

如果打卡成功或今日已打卡，则进程返回的状态码为 0，出现错误则为非 0。

滑动验证码的自动完成通过另一个 API 服务实现，可以使用以下项目之一部署的实例：

* [原版](https://github.com/SO-JNU/stuhealth-validate-server) 使用 Python、Selenium 和 GeckoDriver 实现。
* [Docker 版](https://github.com/SO-JNU/stuhealth-validator) 基于原版代码封装成 Docker 容器。

部署后，在自动打卡时将 API 地址和 token 填入命令行参数中即可。

<details>

<summary>API 调用规则</summary>

`POST <validator-endpoint>`

通过添加请求头 `Authorization: Bearer <validator-token>` 完成鉴权。

```json
{
    // 可以用于模拟登录的，完成滑动验证码后得到的token
    "validation_token": "...",
    // 错误信息（如果有的话，此时状态码不是200）
    "error": "..."
}
```

</details>

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
          cache: pip
          cache-dependency-path: requirements.txt
      - name: Install pip dependencies
        working-directory: stuhealth
        run: pip install -U -r requirements.txt
      - name: Run stuhealth
        working-directory: stuhealth
        run: python stuhealth.py -u ${{ secrets.username }} -p ${{ secrets.password }} -ve ${{ secrets.validatorEndpoint }} -vt ${{ secrets.validatorToken }}
```

</details>

根据需要自行修改 cron 表达式来改变执行时间。配置文件中使用的时区为 UTC，所以上面的表达式 `0 0 * * *` 表示在每天的 UTC 时间 0:00 即北京时间 8:00 执行。可以使用[这个在线工具](https://tool.lu/crontab/)来预览 cron 表达式指定的执行时间。

![](https://img20.360buyimg.com/myjd/jfs/t1/160304/2/11226/43567/6045b463Ec9175d2c/3ca97ae8413b2798.png)

在 Settings 选项卡中的 Secrets 部分按照命令行参数用途添加 `username`、`password`、`validatorEndpoint`、`validatorToken`。Secrets 保存后便无法再次查看，可以在 Actions 中使用但是也不会在执行结果中显示。

![](https://img20.360buyimg.com/myjd/jfs/t1/159718/28/11336/30002/6045b470E9a94b02d/d0547851b07f1b23.png)

设置完成后，在指定时间 GitHub Actions 就会自动帮你启动打卡机了。你可以在 Actions 选项卡中查看每次运行的结果。

![](https://img20.360buyimg.com/myjd/jfs/t1/140991/34/13332/31473/6045b473E62883ca1/557a90fa0e6b0100.png)

> 注意：GitHub Actions 不能保证任务一定可以准时按照 cron 表达式指定的时间运行，**实际执行时间可能会有数分钟的延迟**，可以参见[这里](https://upptime.js.org/blog/2021/01/22/github-actions-schedule-not-working/)的说明。
