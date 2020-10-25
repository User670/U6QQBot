# U6QQBot 
It is a QQ bot by User670. It has limited features,~~but per the Mirai framework licensing, I have to open-source this project if I want to provide features to other people. I don't have much choices.~~ 

# Discontinued
***This project is no longer open-source, due to Mirai actually does not require this project to be open-source. (See https://github.com/mamoe/mirai/issues/657 ). This repository is for archival purposes only.***

# Deprecation
***This GitHub repository will no longer be used, due to unstable connection from China. Please use https://gitee.com/user670/U6QQBot instead.***

# WARNING
The SUPERUSER permission in Nonebot is a **very dangerous permission in U6QQBot, as they can run arbitrary Python and JavaScript code via commands.** Make sure you trust all SUPERUSERS.

# Usage
- Setup Mirai ( https://github.com/mamoe/mirai ) following its instructions. You also need the HTTP API.
- Setup Nonebot ( https://github.com/nonebot/nonebot ) following its instructions. Make sure you install `pip install "nonebot[scheduler]"` when you install the dependencies.
- Place `User670` folder in your Nonebot directory, the same level as your `bot.py`.
- Run `bot.py`.

There might be other dependencies that I forgot I used. Make sure to install them as you see it throw errors. If it somehow prompts a lack of a `JSCTK` module, please replace it with the following three lines:

```py
import json as JSON
JSON.stringify=JSON.dumps
JSON.parse=JSON.loads
```

In order to use the `jsace` command, you also need to install Node.js and make sure it can be accessed on the command line with `node`.

# Licensing
This project **does not have a public license.**
