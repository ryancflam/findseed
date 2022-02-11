from threading import Thread

from discord import Embed
from discord.ext import commands
from flask import Flask, abort, render_template, request

from config import gitLogChannels, production
from src.utils import funcs
from src.utils.base_cog import BaseCog

SLASH = "/" if "/" in funcs.PATH else "\\"
PATH = funcs.PATH + funcs.RESOURCES_PATH + f"{SLASH}web_server"
HOST = "0.0.0.0"
PORT = 8080 if production else 80
FLASK_APP = Flask(__name__, template_folder=PATH, static_folder=PATH + f"{SLASH}static")
RIDICULOUS_CHANNEL_LIST = []


class WebServer(BaseCog, name="Web Server", command_attrs=dict(hidden=True),
                description="A simple web server which optionally handles GitHub push webhooks."):
    def __init__(self, botInstance, *args, **kwargs):
        super().__init__(botInstance, *args, **kwargs)

    @commands.Cog.listener()
    async def on_ready(self):
        global RIDICULOUS_CHANNEL_LIST
        for channelID in gitLogChannels:
            channel = self.client.get_channel(channelID)
            if channel:
                RIDICULOUS_CHANNEL_LIST.append(channel)
        RIDICULOUS_CHANNEL_LIST.append(self.client)
        Thread(target=FLASK_APP.run, args=(HOST, PORT)).start()

    @staticmethod
    @FLASK_APP.route("/")
    def home():
        return render_template("index.html")

    @staticmethod
    @FLASK_APP.route("/git", methods=["POST"])
    def gitlog():
        if RIDICULOUS_CHANNEL_LIST[:-1]:
            data = request.json
            try:
                headcommit = data['head_commit']
                commits = data["commits"]
                e = Embed(
                    title=f"{len(commits)} New Commit{'' if len(commits) == 1 else 's'}",
                    description=headcommit['url']
                )
                e.set_author(name=data["repository"]["full_name"] + f" ({data['ref']})",
                             icon_url="https://media.discordapp.net/attachments/771698457391136798/927918869702647808/github.png")
                for commit in commits:
                    user = commit['committer']['username']
                    message = commit['message']
                    e.description += f"\n`{commit['id'][:7]}...{commit['id'][-7:]}` " + \
                                     f"{message[:100] + ('...' if len(message) > 100 else '')} " + \
                                     f"- [{user}](https://github.com/{user})"
                e.description = e.description[:2048]
                e.set_footer(text=f"Commit time: {funcs.timeStrToDatetime(headcommit['timestamp'])} UTC")
                RIDICULOUS_CHANNEL_LIST[-1].loop.create_task(funcs.sendEmbedToChannels(e, RIDICULOUS_CHANNEL_LIST[:-1]))
            except:
                pass
            return "success", 200
        abort(400)

    @commands.command(name="gitlogchannels", description="Lists out all visible git log channels from `config.gitLogChannels`.",
                      aliases=["gitlog", "gitchannels", "gitchannel", "gitlogs", "gitlogchannel"])
    @commands.is_owner()
    async def gitlogchannels(self, ctx):
        msg = ""
        for channel in RIDICULOUS_CHANNEL_LIST[:-1]:
            if channel:
                try:
                    name = f"#{channel.name} in {channel.guild.name} [{channel.guild.id}]"
                except:
                    name = "DM"
                msg += f"- {channel.id} ({name})\n"
        await ctx.send(funcs.formatting(msg, limit=2000) if msg else "```None```")


setup = WebServer.setup
