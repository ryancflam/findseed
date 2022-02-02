# Hidden category

from threading import Thread

from discord import Embed
from discord.ext import commands
from flask import Flask, abort, request

from config import githubWebhooks
from src.utils import funcs

FLASK_APP = Flask(__name__)
RIDICULOUS_CHANNEL_LIST = []


class GitHubWebhooks(commands.Cog, name="GitHub Webhooks", command_attrs=dict(hidden=True),
                     description="A cog for handling push webhooks from GitHub."):
    def __init__(self, botInstance):
        self.client = botInstance
        if RIDICULOUS_CHANNEL_LIST[:-1]:
            Thread(target=self.startFlaskApp).start()

    @staticmethod
    def startFlaskApp(host: str="0.0.0.0", port: int=8080):
        FLASK_APP.run(host=host, port=port)

    @staticmethod
    @FLASK_APP.route("/")
    def home():
        return "GitHub Webhooks cog is active."

    @staticmethod
    @FLASK_APP.route("/git", methods=["POST"])
    def gitlog():
        if request.method == "POST":
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

    @commands.command(name="gitlogchannels", description="Lists out all visible git log channels from `config.githubWebhooks`.",
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


def setup(botInstance):
    global RIDICULOUS_CHANNEL_LIST
    for channelID in githubWebhooks:
        channel = botInstance.get_channel(channelID)
        if channel:
            RIDICULOUS_CHANNEL_LIST.append(channel)
    RIDICULOUS_CHANNEL_LIST.append(botInstance)
    botInstance.add_cog(GitHubWebhooks(botInstance))