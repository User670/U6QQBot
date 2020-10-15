# U6QQBot 
It is a QQ bot by User670. It has limited features, but per the Mirai framework licensing, I have to open-source this project if I want to provide features to other people. I don't have much choices.

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

# Licensing
This project is licensed with the most strict license legally acceptable, and if there are no legal restrictions, then no license at all. I would not explicitly and manually pick a license.

Mirai, a dependency of this project, uses the GNU Affero General Public License. It is unclear whether this project falls in the scope of said license's limitations and is forced to apply the same license. This is also the reason why I did not pick a license in order to not risk over-licensing past necessity. For safety's sake, before you use this project, you might want to consider open-sourcing your project or consulting your lawyer.