# Hidden category

from asyncio import new_event_loop, set_event_loop
from threading import Thread

from discord import Embed
from discord.ext import commands
from flask import Flask, abort, request

import config
from other_utils import funcs

APP = Flask("")


class GitHubWebhooks(commands.Cog, name="GitHub Webhooks", command_attrs=dict(hidden=True),
                     description="Receive webhooks about your GitHub repository push activity."):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.host = "0.0.0.0"
        self.port = 8080
        if config.githubWebhooks:
            self.startServer()

    @commands.command(name="gitlogchannels", description="Lists out all visible git log channels from `config.githubWebhooks`.",
                      aliases=["gitlog", "gitchannels", "gitchannel"])
    @commands.is_owner()
    async def gitlogchannels(self, ctx):
        msg = ""
        for channelID in config.githubWebhooks:
            channel = self.client.get_channel(channelID)
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
            for channelID in config.githubWebhooks:
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
                    print(e)
                    loop = new_event_loop()
                    print(1)
                    set_event_loop(loop)
                    print(2)
                    loop.run_until_complete(funcs.sendEmbedToChannel(channelID, e))
                    print(3)
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
    client.add_cog(GitHubWebhooks(client))
