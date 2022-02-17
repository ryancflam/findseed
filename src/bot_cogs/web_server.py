from asyncio import sleep
from os import path

from discord.ext import commands
from flask import Flask, abort, redirect, render_template, request, send_from_directory
from numpy import append, array

from config import gitLogRoute, webServerPort
from src.utils import funcs, github_embeds
from src.utils.base_cog import BaseCog
from src.utils.base_thread import BaseThread

PATH = funcs.PATH + funcs.RESOURCES_PATH + "/web_server"
CERTIFICATES = "data/web_server_certificates/"

app = Flask(__name__, template_folder=PATH, static_folder=PATH + "/static")
client = None
https = False


def _getChannelObjects(bot, channelIDs):
    channelList = array([])
    for i in channelIDs:
        channel = bot.get_channel(i)
        if channel:
            append(channelList, channel)
            print(channelList)
    return channelList


class WebServer(BaseCog, name="Web Server", command_attrs=dict(hidden=True),
                description="A simple web server which also handles push webhooks from the bot's GitHub repository."):
    def __init__(self, botInstance, *args, **kwargs):
        super().__init__(botInstance, *args, **kwargs)
        self.client.loop.create_task(self.__readFiles())
        self.active = False

    @staticmethod
    async def __readFiles():
        if not path.exists(funcs.PATH + CERTIFICATES + "default_certificates.json"):
            template = await funcs.readTxt(CERTIFICATES + "default_certificates.json.template", encoding=None)
            await funcs.writeTxt(CERTIFICATES + "default_certificates.json", template)
            print("Generated file: default_certificates.json")

    @commands.Cog.listener()
    async def on_ready(self):
        global client, https
        if not self.active:
            await sleep(1)
            client = self.client
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
            t = BaseThread(target=app.run, args=("0.0.0.0", webServerPort), kwargs=kwargs)
            try:
                await t.start()
            except Exception as ex:
                print("Error - " + str(ex))
                return funcs.unloadCog(self.client, self, force=True)
            self.active = True
            ip = await funcs.getRequest("https://api.ipify.org")
            await (await self.client.application_info()).owner.send(
                "Web server is running on: <http{}://{}{}/>".format(
                    "s" if kwargs else "",
                    ip.content.decode("utf8"),
                    "" if webServerPort == 80 else f":{webServerPort}")
            )

    @staticmethod
    @app.before_request
    async def ssl():
        if https and not request.is_secure:
            url = request.url.replace("http://", "https://", 1)
            return redirect(url, code=301)

    @staticmethod
    @app.route("/")
    async def index():
        return render_template("index.html")

    @staticmethod
    @app.route("/robots.txt")
    async def robotstxt():
        return send_from_directory(app.template_folder, "robots.txt")

    @staticmethod
    @app.route(gitLogRoute, methods=["POST"])
    async def git():
        try:
            channels = array(list((await funcs.readJson("data/channels_following_repo.json"))["channels"]))
            if channels and request.method == "POST":
                data = request.json
                e = github_embeds.push(data)
                client.loop.create_task(funcs.sendEmbedToChannels(e, _getChannelObjects(client, channels)))
                return "success", 200
            raise
        except Exception as ex:
            print(ex)
            abort(400)


setup = WebServer.setup
