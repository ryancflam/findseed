# Hidden category

from threading import Thread

from discord import Embed
from discord.ext import commands
from flask import Flask, abort, request

from config import githubWebhooks
from other_utils import funcs

APP = Flask(__name__)
CHANNEL_LIST = []


class GitHubWebhooks(commands.Cog, name="GitHub Webhooks", command_attrs=dict(hidden=True),
                     description="Receive webhooks about your GitHub repository push activity."):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.host = "0.0.0.0"
        self.port = 8080
        if CHANNEL_LIST[:-1]:
            self.startServer()

    @commands.command(name="gitlogchannels", description="Lists out all visible git log channels from `config.githubWebhooks`.",
                      aliases=["gitlog", "gitchannels", "gitchannel", "gitlogs", "gitlogchannel"])
    @commands.is_owner()
    async def gitlogchannels(self, ctx):
        msg = ""
        for channel in CHANNEL_LIST[:-1]:
            if channel:
                try:
                    name = f"#{channel.name} in {channel.guild.name} [{channel.guild.id}]"
                except:
                    name = "DM"
                msg += f"- {channel.id} ({name})\n"
        await ctx.send(funcs.formatting(msg, limit=2000) if msg else "```None```")

    @staticmethod
    @APP.route("/")
    def home():
        return "GitHub Webhooks cog is active."

    @staticmethod
    @APP.route("/git", methods=["POST"])
    def gitlog():
        if request.method == "POST":
            data = request.json
            try:
                repo = data["repository"]
                headcommit = data['head_commit']
                commits = data["commits"]
                e = Embed(
                    title=f"{len(commits)} New Commit{'' if len(commits) == 1 else 's'} - {headcommit['url']}",
                    description=""
                )
                e.set_author(name=repo["full_name"] + f" ({data['ref']})",
                             icon_url="https://media.discordapp.net/attachments/771698457391136798/927918869702647808/github.png")
                for commit in commits:
                    user = commit['committer']['username']
                    message = commit['message']
                    e.description += f"`{commit['id'][:7]}...` {message[:50] + ('...' if len(message) > 50 else '')} " + \
                                     f"- [{user}](https://github.com/{user})\n"
                e.set_footer(text=f"Commit Time: {funcs.timeStrToDatetime(headcommit['timestamp'])} UTC")
                executeSend(e)
            except:
                pass
            return "success", 200
        abort(400)

    def run(self):
        APP.run(host=self.host, port=self.port)

    def startServer(self):
        Thread(target=self.run).start()


async def sendEmbedToChannels(embed: Embed):
    for channel in CHANNEL_LIST[:-1]:
        if channel:
            try:
                await channel.send(embed=embed)
            except:
                pass


def executeSend(e):
    CHANNEL_LIST[-1].loop.create_task(sendEmbedToChannels(e))


def setup(client: commands.Bot):
    global CHANNEL_LIST
    for channelID in githubWebhooks:
        channel = client.get_channel(channelID)
        if channel:
            CHANNEL_LIST.append(channel)
    CHANNEL_LIST.append(client)
    client.add_cog(GitHubWebhooks(client))
