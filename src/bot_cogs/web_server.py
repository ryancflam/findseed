from asyncio import sleep
from os import path
from threading import Thread

from discord import Embed
from discord.ext import commands
from flask import Flask, abort, render_template, request, send_from_directory

from config import gitLogChannels, production
from src.utils import funcs
from src.utils.base_cog import BaseCog

HOST = "0.0.0.0"
PORT = 8080 if production else 80
PATH = funcs.PATH + funcs.RESOURCES_PATH + "/web_server"
CERTIFICATES = "data/web_server_certificates/"
FLASK_APP = Flask(__name__, template_folder=PATH, static_folder=PATH + "/static")
RIDICULOUS_CHANNEL_LIST = []


class WebServer(BaseCog, name="Web Server", command_attrs=dict(hidden=True),
                description="A simple web server which optionally handles GitHub push webhooks."):
    def __init__(self, botInstance, *args, **kwargs):
        super().__init__(botInstance, *args, **kwargs)
        self.active = False

    @staticmethod
    async def __generateJson():
        if not path.exists(funcs.PATH + CERTIFICATES + "default_certificates.json"):
            template = await funcs.readTxt(CERTIFICATES + "default_certificates.json.template", encoding=None)
            await funcs.writeTxt(CERTIFICATES + "default_certificates.json", template)
            print("Generated file: default_certificates.json")

    @commands.Cog.listener()
    async def on_ready(self):
        await self.__generateJson()
        if not self.active:
            await sleep(1)
            global RIDICULOUS_CHANNEL_LIST
            for channelID in gitLogChannels:
                channel = self.client.get_channel(channelID)
                if channel:
                    RIDICULOUS_CHANNEL_LIST.append(channel)
            RIDICULOUS_CHANNEL_LIST.append(self.client)
            kwargs = None
            keys = await funcs.readJson(CERTIFICATES + "default_certificates.json")
            certs = funcs.PATH + CERTIFICATES if not keys["custom_location"] else keys["custom_location"]
            if not certs.endswith("/"):
                certs += "/"
            cert = certs + keys["public_key"]
            key = certs + keys["private_key"]
            if path.exists(cert) and path.exists(key):
                kwargs = dict(ssl_context=(cert, key))
                print(f"{self.name} - Attempting to use HTTPS...")
            try:
                Thread(target=FLASK_APP.run, args=(HOST, PORT), kwargs=kwargs).start()
                self.active = True
                ip = await funcs.getRequest("https://api.ipify.org")
                await (await self.client.application_info()).owner.send(
                    "Web server is running on: <http{}://{}{}/>".format(
                        "s" if kwargs else "",
                        ip.content.decode("utf8"),
                        "" if PORT == 80 else f":{PORT}")
                )
            except Exception as ex:
                print("Error - " + str(ex))
                return funcs.unloadCog(self.client, self, force=True)

    @staticmethod
    @FLASK_APP.route("/")
    def index():
        return render_template("index.html")

    @staticmethod
    @FLASK_APP.route("/robots.txt")
    def robotstxt():
        return send_from_directory(FLASK_APP.template_folder, "robots.txt")

    @staticmethod
    @FLASK_APP.route("/git", methods=["POST"])
    def git():
        if RIDICULOUS_CHANNEL_LIST[:-1]:
            data = request.json
            try:
                headcommit = data["head_commit"]
                commits = data["commits"]
                e = Embed(
                    title=f"{len(commits)} New Commit{'' if len(commits) == 1 else 's'}",
                    description=headcommit['url']
                )
                e.set_author(name=data["repository"]["full_name"] + f" ({data['ref']})",
                             icon_url="https://media.discordapp.net/attachments/771698457391136798/927918869702647808/github.png")
                for commit in commits:
                    user = commit["committer"]["username"]
                    message = commit["message"].replace("_", "\_").replace("*", "\*")
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
