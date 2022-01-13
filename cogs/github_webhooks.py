# Hidden category

from asyncio import new_event_loop, set_event_loop
from threading import Thread

from discord import Embed
from discord.ext import commands
from flask import Flask, abort, request

from config import githubWebhooks
from other_utils import funcs

APP = Flask("")
CHANNEL_LIST = []


class GitHubWebhooks(commands.Cog, name="GitHub Webhooks", command_attrs=dict(hidden=True),
                     description="Receive webhooks about your GitHub repository push activity."):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.host = "0.0.0.0"
        self.port = 8080
        if CHANNEL_LIST:
            self.startServer()

    @commands.command(name="gitlogchannels", description="Lists out all visible git log channels from `config.githubWebhooks`.",
                      aliases=["gitlog", "gitchannels", "gitchannel"])
    @commands.is_owner()
    async def gitlogchannels(self, ctx):
        msg = ""
        for channel in CHANNEL_LIST:
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
        global CHANNEL_LIST
        if request.method == "POST":
            data = request.json
            print(CHANNEL_LIST)
            for channel in CHANNEL_LIST:
                if channel:
                    try:
                        headcommit = data['head_commit']
                        commits = data["commits"]
                        e = Embed(
                            title=f"[{len(commits)} New Commit{'' if len(commits) == 1 else 's'}]({headcommit['url']})",
                            description=""
                        )
                        for commit in commits:
                            user = commit['committer']['username']
                            e.description += f"`{commit['id'][:7]}` {commit['message']} - [{user}](https://github.com/{user})\n"
                        e.set_footer(text=f"Date: {funcs.timeStrToDatetime(headcommit['timestamp'])} UTC")
                        loop = new_event_loop()
                        set_event_loop(loop)
                        loop.run_until_complete(funcs.sendEmbedToChannel(channel, e))
                    except Exception as ex:
                        print(ex)
                        pass
            return "success", 200
        abort(400)

    def run(self):
        APP.run(host=self.host, port=self.port)

    def startServer(self):
        Thread(target=self.run).start()


def setup(client: commands.Bot):
    global CHANNEL_LIST
    for channelID in githubWebhooks:
        CHANNEL_LIST.append(client.get_channel(channelID))
    client.add_cog(GitHubWebhooks(client))
