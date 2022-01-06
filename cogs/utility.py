from asyncio import sleep, TimeoutError
from datetime import datetime, timedelta
from json import dumps, JSONDecodeError
from pathlib import Path
from platform import system
from random import choice
from statistics import mean, median, mode, pstdev, stdev
from string import punctuation
from subprocess import PIPE, Popen, STDOUT
from time import time
from urllib.parse import quote

from asyncpraw import Reddit
from discord import channel, Embed
from discord.ext import commands
from googletrans import constants, Translator

import config
from other_utils import funcs
from other_utils.safe_eval import SafeEval

DEFAULT_REPO = "ryancflam/findseed"
HCF_LIMIT = 1000000


class Utility(commands.Cog, name="Utility", description="Useful commands for getting data or calculating things."):
    COPYPASTA = Path(f"{funcs.getPath()}/assets/copypasta.txt").read_text()

    def __init__(self, client: commands.Bot):
        self.client = client
        self.reddit = Reddit(client_id=config.redditClientID,
                             client_secret=config.redditClientSecret,
                             user_agent="*")
        self.tickers = funcs.getTickers()

    async def waitForReaction(self, ctx, msg, allpages: int, page: int):
        try:
            reaction, user = await self.client.wait_for(
                "reaction_add",
                check=lambda reaction, user: (str(reaction.emoji) == "⏮" or str(
                    reaction.emoji
                ) == "⏭") and user == ctx.author and reaction.message == msg, timeout=300
            )
        except TimeoutError:
            try:
                await msg.clear_reactions()
            except:
                pass
            return None, 0
        success = False
        if str(reaction.emoji) == "⏭":
            await funcs.reactionRemove(reaction, user)
            if page < allpages:
                page += 1
                success = True
        else:
            await funcs.reactionRemove(reaction, user)
            if page > 1:
                page -= 1
                success = True
        return success, page

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="github", description="Returns statistics about a Github repository.",
                      aliases=["loc", "code", "linesofcode", "repository", "repo"], usage='[username/repository]')
    async def repository(self, ctx, *, repo: str=""):
        await ctx.send("Getting repository lines of code statistics. Please wait...")
        try:
            repo = repo.casefold().replace(" ", "") or DEFAULT_REPO
            res = await funcs.getRequest("https://api.codetabs.com/v1/loc/?github=" + repo)
            e = Embed(description=f"https://github.com/{repo}")
            e.set_author(name=repo,
                         icon_url="https://media.discordapp.net/attachments/771698457391136798/927918869702647808/github.png")
            for i in sorted(res.json(), reverse=True, key=lambda x: x["linesOfCode"])[:24]:
                if i["language"] == "Total":
                    e.add_field(name="Total Files", value="`{:,}`".format(i["files"]))
                e.add_field(name=f"{i['language']} Lines", value="`{:,}`".format(i["linesOfCode"]))
            e.set_footer(text="Note: Lines of code do not include comment or blank lines.")
        except Exception:
            e = funcs.errorEmbed(None, "Unknown repository or server error.")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="covid", description="Gathers COVID-19 data.",
                      aliases=["coronavirus", "corona", "covid19", "cv", "c19", "cv19"], usage="[location]")
    async def covid(self, ctx, *, searchtype: str=""):
        headers = {
            "x-rapidapi-host": "corona-virus-world-and-india-data.p.rapidapi.com",
            "x-rapidapi-key": config.rapidApiKey
        }
        try:
            res = await funcs.getRequest("https://corona-virus-world-and-india-data.p.rapidapi.com/api", headers=headers)
            data = res.json()
            total = data["countries_stat"]
            found = False
            if searchtype == "":
                total = data["world_total"]
            else:
                if searchtype.casefold() == "us" or searchtype.casefold().startswith(("united states", "america")):
                    searchtype = "usa"
                elif searchtype.casefold().startswith(("united kingdom", "great britain", "britain", "england")) \
                        or searchtype.casefold() == "gb":
                    searchtype = "uk"
                elif searchtype.casefold().startswith("hk"):
                    searchtype = "hong kong"
                if searchtype.casefold().startswith(("korea", "south korea", "sk")):
                    searchtype = "S. Korea"
                for i in total:
                    if i["country_name"].casefold().replace(".", "") == searchtype.casefold().replace(".", ""):
                        found = True
                        total = i
                        break
                if not found:
                    total = data["world_total"]
            e = Embed(description="Statistics taken at: `" + data["statistic_taken_at"] + " UTC`")
            e.set_author(name=f"COVID-19 Statistics ({total['country_name'] if found else 'Global'})",
                         icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/" + \
                                  "SARS-CoV-2_without_background.png/220px-SARS-CoV-2_without_background.png")
            if found:
                e.add_field(name="Country", value=f"`{total['country_name']}`")
                e.add_field(name="Total Cases", value=f"`{total['cases']}`")
                e.add_field(name="Total Deaths", value=f"`{total['deaths']}" + \
                                                       "\n({}%)`".format(round(int(total['deaths']
                                                           .replace(',', '').replace('N/A', '0')) / int(total['cases']
                                                           .replace(',', '').replace('N/A', '0')) * 100, 2)))
                e.add_field(name="Total Recovered", value=f"`{total['total_recovered']}" + \
                                                          "\n({}%)`".format(round(int(total['total_recovered']
                                                              .replace(',', '').replace('N/A', '0')) / int(total['cases']
                                                              .replace(',', '').replace('N/A', '0')) * 100, 2)))
                e.add_field(name="Active Cases", value=f"`{total['active_cases']}" + \
                                                       "\n({}%)`".format(round(int(total['active_cases']
                                                           .replace(',', '').replace('N/A', '0')) / int(total['cases']
                                                           .replace(',', '').replace('N/A', '0')) * 100, 2)))
                e.add_field(name="Critical Cases", value=f"`{total['serious_critical']}`")
                e.add_field(name="Total Tests", value=f"`{total['total_tests']}`")
            else:
                e.add_field(name="Total Cases", value=f"`{total['total_cases']}`")
                e.add_field(name="Total Deaths", value=f"`{total['total_deaths']}" + \
                                                       "\n({}%)`".format(round(int(total['total_deaths']
                                                           .replace(',', '').replace('N/A', '0')) / int(total['total_cases']
                                                           .replace(',', '').replace('N/A', '0')) * 100, 2)))
                e.add_field(name="Total Recovered", value=f"`{total['total_recovered']}" + \
                                                          "\n({}%)`".format(round(int(total['total_recovered']
                                                              .replace(',', '').replace('N/A', '0')) / int(total['total_cases']
                                                              .replace(',', '').replace('N/A', '0')) * 100, 2)))
                e.add_field(name="Active Cases", value=f"`{total['active_cases']}" + \
                                                       "\n({}%)`".format(round(int(total['active_cases']
                                                           .replace(',', '').replace('N/A', '0')) / int(total['total_cases']
                                                           .replace(',', '').replace('N/A', '0')) * 100, 2)))
                e.add_field(name="Critical Cases", value=f"`{total['serious_critical']}`")
            e.add_field(name="New Cases Today", value=f"`{total['new_cases']}`")
            e.add_field(name="New Deaths Today", value=f"`{total['new_deaths']}`")
            e.set_footer(text="Note: The data provided may not be 100% accurate.")
        except Exception:
            e = funcs.errorEmbed(None, "Invalid input or server error.")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="flight", description="Gets information about a flight",
                      aliases=["flightinfo", "flightradar"], usage="<flight number>")
    async def flight(self, ctx, *, flightstr: str=""):
        if flightstr == "":
            e = funcs.errorEmbed(None, "Empty input.")
        else:
            ph = "Unknown"
            flightstr = flightstr.upper().replace(" ", "")
            url = "https://api.flightradar24.com/common/v1/flight/list.json?"
            params = {"fetchBy": "flight", "page": "1", "limit": "25", "query": flightstr}
            try:
                res = await funcs.getRequest(url, headers={"User-agent": "*"}, params=params)
                allflights = res.json()
                fdd = allflights["result"]["response"]["data"]
                dago, eta = "", ""
                reg, data, arrive, realarrive, depart, realdepart = ph, ph, ph, ph, ph, ph
                ft, duration, originname, originicao, originiata, destname, desticao, destiata = ph, ph, ph, ph, ph, ph, ph, ph
                flighturl = f"https://www.flightradar24.com/data/flights/{flightstr.lower()}"
                status, callsign, aircraft, flightdate, airline = ph, ph, ph, ph, ph
                for i in range(len(fdd)):
                    data = fdd[i]
                    callsign = data["identification"]["callsign"]
                    if callsign is None:
                        callsign = "None"
                    status = str(data["status"]["text"])
                    aircraft = f"{str(data['aircraft']['model']['text'])} ({str(data['aircraft']['model']['code'])})"
                    reg = data["aircraft"]["registration"]
                    airline = data["airline"]["name"]
                    originname = data["airport"]["origin"]["name"]
                    originiata = data["airport"]["origin"]["code"]["iata"]
                    originicao = data["airport"]["origin"]["code"]["icao"]
                    destname = data["airport"]["destination"]["name"]
                    if not originname or not destname:
                        continue
                    destiata = data["airport"]["destination"]["code"]["iata"]
                    desticao = data["airport"]["destination"]["code"]["icao"]
                    realdepart = data["time"]["real"]["departure"]
                    depart = "Local Departure Time"
                    realarrive = data["time"]["real"]["arrival"]
                    arrive = "Local Arrival Time"
                    if realarrive is None:
                        realarrive = data["time"]["estimated"]["arrival"]
                        if realarrive is None:
                            continue
                        arrive = "Estimated Local Arrival Time"
                        duration = str(datetime.fromtimestamp(realarrive) - datetime.utcnow())[:5]
                        if duration[1:2] == ":":
                            duration = "0" + (duration[:4])
                        eta = "Estimated Flight Time Remaining"
                    else:
                        duration = str(datetime.fromtimestamp(realarrive) - datetime.fromtimestamp(realdepart))[:5]
                        if duration[1:2] == ":":
                            duration = "0" + (duration[:4])
                        eta = "Total Flight Duration"
                    if eta.startswith("\nEstimated"):
                        ft = str(datetime.utcnow() - datetime.fromtimestamp(realdepart))[:5]
                        if ft[1:2] == ":":
                            ft = "0" + (ft[:4])
                        dago = "Current Flight Time"
                    realdepart = str(datetime.fromtimestamp(realdepart + data["airport"]["origin"]["timezone"]["offset"]))
                    realarrive = str(datetime.fromtimestamp(realarrive + data["airport"]["destination"]["timezone"]["offset"]))
                    flightdate = realdepart[:10]
                    break
                imgl = res.json()["result"]["response"]["aircraftImages"]
                thumbnail = "https://images.flightradar24.com/opengraph/fr24_logo_twitter.png"
                for y in range(len(imgl)):
                    image = imgl[y]
                    if image["registration"] != reg:
                        continue
                    thumbnail = list(
                        image["images"]["thumbnails"]
                    )[0]["src"][:-4].replace("_tb", "").replace("com/200/", "com/full/")
                e = Embed(title=f"Flight {flightstr}", description=flighturl)
                e.set_image(url=thumbnail)
                e.add_field(name="Date", value=f"`{flightdate}`")
                e.add_field(name="Callsign", value=f"`{callsign}`")
                e.add_field(name="Status", value=f"`{status}`")
                e.add_field(name="Aircraft", value=f"`{aircraft}`")
                e.add_field(name="Registration", value=f"`{reg} ({data['aircraft']['country']['name']})`")
                e.add_field(name="Airline",
                            value=f"`{airline} ({data['airline']['code']['iata']}/{data['airline']['code']['icao']})`")
                e.add_field(name="Origin", value=f"`{originname} ({originiata}/{originicao})`")
                e.add_field(name="Destination", value=f"`{destname} ({destiata}/{desticao})`")
                e.add_field(name=depart, value=f"`{realdepart}`")
                if dago:
                    e.add_field(name=dago, value=f"`{ft}`")
                e.add_field(name=arrive, value=f"`{realarrive}`")
                if eta:
                    e.add_field(name=eta, value=f"`{duration}`")
                e.set_footer(text="Note: Flight data provided by Flightradar24 may not be 100% accurate.",
                             icon_url="https://i.pinimg.com/564x/8c/90/8f/8c908ff985364bdba5514129d3d4e799.jpg")
            except Exception:
                e = funcs.errorEmbed(None, "Unknown flight or server error.")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="weather", description="Finds the current weather of a location.",
                      aliases=["w"], usage="<location>")
    async def weather(self, ctx, *, location: str=""):
        zero = -273.15
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location.casefold().replace(' ', '%20')}" + \
              f"&APPID={config.owmKey}"
        try:
            r = await funcs.getRequest(url)
            data = r.json()
            country = data["sys"]["country"]
            temp = data["main"]["temp"] + zero
            lastupdate = str(datetime.fromtimestamp(int(data["dt"]) + (int(data["timezone"]))))
            timenow = str(datetime.fromtimestamp(int(time()) + int(data["timezone"])))
            temp2 = funcs.celsiusToFahrenheit(temp)
            high = data["main"]["temp_max"] + zero
            low = data["main"]["temp_min"] + zero
            high2 = funcs.celsiusToFahrenheit(high)
            low2 = funcs.celsiusToFahrenheit(low)
            winddegrees = float(data["wind"]["deg"])
            e = Embed(title=f"{data['name']}, {country}", description=f"**{data['weather'][0]['description'].title()}**")
            e.add_field(name="Temperature", value="`{}°F / {}°C`".format(round(temp2, 1), round(temp, 1)))
            e.add_field(name="Temp Range", value="`{}°F - {}°F\n".format(round(low2, 1), round(high2, 1)) + \
                                                 "{}°C - {}°C`".format(round(low, 1), round(high, 1)))
            e.add_field(name="Humidity", value="`{}%`".format(data["main"]["humidity"]))
            e.add_field(name="Wind Speed", value="`{} m/s`".format(data["wind"]["speed"]))
            e.add_field(name="Wind Direction",
                        value="`{}° ({})`".format(int(winddegrees), funcs.degreesToDirection(winddegrees)))
            e.add_field(name="Local Time", value=f"`{timenow}`")
            e.add_field(name="Last Updated (Local Time)", value=f"`{lastupdate}`")
            e.set_footer(text="Note: Weather data provided by OpenWeatherMap may not be 100% accurate.",
                         icon_url="https://openweathermap.org/themes/openweathermap/assets/img/mobile_app/android_icon.png")
            e.set_thumbnail(url=f"http://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png")
        except:
            e = funcs.errorEmbed(None, "Unknown location or server error.")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 15, commands.BucketType.user)
    @commands.command(name="translate", description="Translates text to a different language. " + \
                                                    "Translation may sometimes fail due to rate limit.",
                      aliases=["t", "translator", "trans", "tr", "translation"], usage="<language code to translate to> <input>")
    async def translate(self, ctx, dest=None, *, text):
        try:
            if dest.casefold() not in constants.LANGUAGES.keys():
                e = funcs.errorEmbed(
                    "Invalid language code!",
                    f"Valid options:\n\n{', '.join(f'`{i}`' for i in constants.LANGUAGES.keys())}"
                )
            else:
                output = Translator().translate(text.casefold(), dest=dest.casefold()).text
                e = Embed(title="Translation", description=funcs.formatting(output))
        except Exception:
            e = funcs.errorEmbed(None, "An error occurred. Invalid input?")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="currency", description="Converts the price of one currency to another",
                      aliases=["fiat", "cc", "convertcurrency", "currencyconvert"], usage="<from currency> <to currency> [amount]")
    async def currency(self, ctx, fromC, toC, *, amount: str="1"):
        try:
            output = [fromC.upper(), toC.upper(), amount]
            res = await funcs.getRequest("http://data.fixer.io/api/latest", params={"access_key": config.fixerKey})
            data = res.json()
            amount = float(output[2].replace(",", "").replace(" ", ""))
            initialamount = amount
            fromCurrency = output[0]
            toCurrency = output[1]
            coingecko = "https://api.coingecko.com/api/v3/coins/markets"
            if fromCurrency != "EUR":
                try:
                    amount /= data["rates"][fromCurrency]
                except:
                    res = await funcs.getRequest(
                        coingecko, params={"ids": self.tickers[fromCurrency.casefold()], "vs_currency": "EUR"}
                    )
                    cgData = res.json()
                    amount *= cgData[0]["current_price"]
            if toCurrency != "EUR":
                try:
                    amount *= data["rates"][toCurrency]
                except:
                    res = await funcs.getRequest(
                        coingecko, params={"ids": self.tickers[toCurrency.casefold()], "vs_currency": "EUR"}
                    )
                    cgData = res.json()
                    if fromCurrency.upper() == toCurrency.upper():
                        amount = float(initialamount)
                    else:
                        amount /= cgData[0]["current_price"]
            await ctx.reply(
                f"The current price of **{'{:,}'.format(initialamount)} {fromCurrency}** in **{toCurrency}**: " + \
                "`{:,}`".format(amount)
            )
        except:
            await ctx.reply(embed=funcs.errorEmbed(None, "Invalid input or unknown currency."))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="wiki", description="Returns a Wikipedia article.",
                      aliases=["wikipedia"], usage="<article title (case sensitive)>")
    async def wiki(self, ctx, *, page: str=""):
        if page == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            wikiurl = "https://en.wikipedia.org/w/api.php?format=json&action=query" + \
                      "&prop=extracts&exintro&explaintext&redirects=1&titles="
            try:
                res = await funcs.getRequest(f"{wikiurl}{page.replace(' ', '_')}")
                data = res.json()
                wikipage = data["query"]
                if list(wikipage["pages"])[0] == "-1":
                    res = await funcs.getRequest(f"{wikiurl}{page.replace(' ', '_').title()}")
                    data = res.json()
                    wikipage = data["query"]
                    if list(wikipage["pages"])[0] == "-1":
                        return await ctx.reply(embed=funcs.errorEmbed(None, "Invalid article."))
                if wikipage["pages"][list(wikipage["pages"])[0]]["extract"].casefold().startswith(f"{page} may refer to:\n\n"):
                    try:
                        splitthing = f"may refer to:\n\n"
                        page = wikipage["pages"][list(wikipage["pages"])[0]]["extract"].split(
                            splitthing, 1
                        )[1].split("\n", 1)[1].split(",", 1)[0]
                        res = await funcs.getRequest(f"{wikiurl}{page.replace(' ', '_')}")
                        data = res.json()
                        wikipage = data["query"]
                        if wikipage["pages"][list(wikipage["pages"])[0]] == "-1":
                            return await ctx.reply(embed=funcs.errorEmbed(None, "Invalid article."))
                    except IndexError:
                        pass
                summary = wikipage["pages"][list(wikipage["pages"])[0]]["extract"]
                if len(summary) != len(wikipage["pages"][list(wikipage["pages"])[0]]["extract"][:1000]):
                    summary = wikipage["pages"][list(wikipage["pages"])[0]]["extract"][:1000] + "..."
                e = Embed(description="https://en.wikipedia.org/wiki/" + \
                                      f"{wikipage['pages'][list(wikipage['pages'])[0]]['title'].replace(' ', '_')}"
                )
                e.set_author(name=wikipage["pages"][list(wikipage["pages"])[0]]["title"],
                             icon_url="https://cdn.discordapp.com/attachments/659771291858894849/" + \
                                      "677853982718165001/1122px-Wikipedia-logo-v2.png")
                e.add_field(name="Extract", value=f"```{summary}```")
            except Exception:
                e = funcs.errorEmbed(None, "Invalid input or server error.")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="lyrics", description="Gets the lyrics of a song.",
                      aliases=["lyric"], usage="<song keywords>")
    async def lyrics(self, ctx, *, keywords):
        try:
            await ctx.send("Getting lyrics. Please wait...")
            url = "https://some-random-api.ml/lyrics"
            res = await funcs.getRequest(url, params={"title": keywords})
            data = res.json()
            thumbnail = data["thumbnail"]["genius"]
            link = data["links"]["genius"]
            originallyric = funcs.multiString(data["lyrics"].replace("*", "\*").replace("_", "\_").replace("\n\n", "\n"), n=2048)
            allpages = len(originallyric)
            title = data["title"].replace("*", "\*").replace("_", "\_")
            author = data["author"].replace("*", "\*").replace("_", "\_")
            e = Embed(description=originallyric[0], title=f"{author} - {title}")
            e.set_thumbnail(url=thumbnail)
            e.add_field(name="Genius Link", value=link)
            page = 1
            e.set_footer(text=f"Page {page} of {allpages}")
            msg = await ctx.reply(embed=e)
            if allpages > 1:
                await msg.add_reaction("⏮")
                await msg.add_reaction("⏭")
                while True:
                    success, page = await self.waitForReaction(ctx, msg, allpages, page)
                    if success:
                        edited = Embed(description=originallyric[page - 1], title=f"{author} - {title}")
                        edited.set_thumbnail(url=thumbnail)
                        edited.add_field(name="Genius Link", value=link)
                        edited.set_footer(text=f"Page {page} of {allpages}")
                        await msg.edit(embed=edited)
                    elif success is None:
                        return
        except Exception:
            await ctx.reply(embed=funcs.errorEmbed(None, "Invalid keywords or server error."))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="qrgen", description="Generates a QR code.", aliases=["qrg", "genqr", "qr"],
                      usage="<input>")
    async def qrgen(self, ctx, *, text):
        try:
            e = Embed(title="QR Code").set_image(
                url=f"http://api.qrserver.com/v1/create-qr-code/?data={quote(text)}&margin=25"
            )
        except Exception:
            e = funcs.errorEmbed(None, "Invalid input or server error?")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="qrread", description="Reads a QR code.", aliases=["qrscan", "qrr", "readqr"],
                      usage="<image URL OR image attachment>")
    async def qrread(self, ctx):
        await ctx.send("Reading image. Please wait... " + \
                       "(URL embeds take longer to process than image attachments)")
        if not ctx.message.attachments:
            await sleep(3)
        if ctx.message.attachments or ctx.message.embeds:
            try:
                qrlink = ctx.message.attachments[0].url if ctx.message.attachments else ctx.message.embeds[0].thumbnail.url
                qr = await funcs.decodeQR(qrlink)
                e = Embed(title="QR Code Message", description=funcs.formatting(qr)) if qr \
                    else funcs.errorEmbed(None, "Cannot detect QR code. Maybe try making the image clearer?")
            except Exception as ex:
                e = funcs.errorEmbed(None, str(ex))
        else:
            e = funcs.errorEmbed(None, "No attachment or URL detected, please try again.")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="compile", description="Compiles code.", aliases=["comp"])
    async def compile(self, ctx):
        res = await funcs.getRequest("https://run.glot.io/languages", verify=False)
        data = res.json()
        languages = [i["name"] for i in data]
        output = ", ".join(f'`{j}`' for j in languages)
        language = ""
        option = None
        await ctx.reply(embed=Embed(title="Please select a language below or input `quit` to quit...",
                                   description=output))
        while language not in languages and language != "quit":
            try:
                option = await self.client.wait_for(
                    "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=120
                )
                language = option.content.casefold().replace(" ", "").replace("#", "sharp").replace(
                    "♯", "sharp").replace("++", "pp")
                language = "javascript" if language == "js" else language
                if language not in languages and language != "quit":
                    await option.reply(embed=funcs.errorEmbed(None, "Invalid language."))
            except TimeoutError:
                return await ctx.send("Cancelling compilation...")
        if language == "quit":
            return await option.reply("Cancelling compilation...")
        versionurl = f"https://run.glot.io/languages/{language}"
        res = await funcs.getRequest(versionurl, verify=False)
        data = res.json()
        url = data["url"]
        await option.reply("**You have 15 minutes to type out your code. Input `quit` to quit.**")
        code = None
        try:
            option = await self.client.wait_for(
                "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=900
            )
            content = option.content
            try:
                if option.attachments:
                    content = await funcs.readTxt(option)
                code = content.replace("```", "").replace('“', '"').replace('”', '"').replace("‘", "'").replace("’", "'")
                if code == "quit":
                    return await option.reply("Cancelling compilation...")
            except:
                pass
        except TimeoutError:
            return await ctx.send("Cancelling compilation...")
        await option.reply("**Please enter your desired file name including the extension.** (e.g. `main.py`)")
        try:
            option = await self.client.wait_for(
                "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=120
            )
            filename = option.content
        except TimeoutError:
            return await ctx.send("Cancelling compilation...")
        data = {"files": [{"name": filename, "content": code}]}
        headers = {
            "Authorization": f"Token {config.glotIoKey}",
            "Content-type": "application/json"
        }
        res = await funcs.postRequest(url=url, data=dumps(data), headers=headers, verify=False)
        try:
            data = res.json()
            stderr = data["stderr"]
            if stderr == "":
                await option.reply(embed=Embed(title="Compilation", description=funcs.formatting(data["stdout"] or "None")))
            else:
                await option.reply(embed=funcs.errorEmbed(data["error"].title(), funcs.formatting(stderr)))
        except AttributeError:
            await option.reply(embed=funcs.errorEmbed(None, "Code exceeded the maximum allowed running time."))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="dictionary", description="Returns the definition(s) of a word.",
                      aliases=["dict", "def", "definition", "meaning", "define"],
                      usage="<word> [language code]")
    async def dictionary(self, ctx, word="", lang="en"):
        if word == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            codes = ["en", "hi", "es", "fr", "ja", "ru", "de", "it", "ko", "pt-BR", "ar", "tr"]
            languages = [
                "English", "Hindi", "Spanish", "French", "Japanese", "Russian", "German",
                "Italian", "Korean", "Brazilian Portuguese", "Arabic", "Turkish"
            ]
            if lang not in codes:
                codesList = ", ".join(f"`{code}` ({languages[codes.index(code)]})" for code in codes)
                e = funcs.errorEmbed("Invalid language code!", f"Valid options:\n\n{codesList}")
            else:
                try:
                    url = f"https://api.dictionaryapi.dev/api/v2/entries/{lang}/{word}"
                    res = await funcs.getRequest(url)
                    data = res.json()
                    word = data[0]["word"].title()
                    output = ""
                    for i in data:
                        meanings = i["meanings"]
                        for j in meanings:
                            partOfSpeech = j["partOfSpeech"]
                            definitions = j["definitions"]
                            for k in definitions:
                                definition = k["definition"]
                                output += f"- {definition} [{partOfSpeech}]\n"
                    e = Embed(title=f'"{word}"').add_field(name="Definition(s)", value=funcs.formatting(output[:-1]))
                except Exception:
                    e = funcs.errorEmbed(None, "Unknown word.")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="poll", description="Makes a poll.", usage="<question>", aliases=["questionnaire"])
    @commands.guild_only()
    async def poll(self, ctx, *, question):
        if len(question) > 200:
            return await ctx.reply(embed=funcs.errorEmbed(None, "Question must be 200 characters or less."))
        messages, answers = [ctx.message], []
        count = 0
        while count < 20:
            messages.append(
                await messages[-1].reply("Enter poll choice, `!undo` to delete previous choice, or `!done` to publish poll.")
            )
            try:
                entry = await self.client.wait_for(
                    "message",
                    check=lambda m: m.author == ctx.author and m.channel == ctx.channel and len(m.content) <= 100,
                    timeout=60
                )
            except TimeoutError:
                break
            messages.append(entry)
            if entry.content.casefold() == "!done":
                break
            if entry.content.casefold() == "!undo":
                if answers:
                    answers.pop()
                    count -= 1
                else:
                    messages.append(
                        await entry.reply(embed=funcs.errorEmbed(None, "No choices."))
                    )
            else:
                answers.append((chr(0x1f1e6 + count), entry.content))
                count += 1
        try:
            await ctx.channel.delete_messages(messages)
        except:
            pass
        if len(answers) < 2:
            return await messages[-1].reply(embed=funcs.errorEmbed(None, "Not enough choices."))
        answer = "\n".join(f"{keycap}: {content}" for keycap, content in answers)
        e = Embed(title=f"Poll - {question}", description=f"Asked by: {ctx.author.mention}")
        e.add_field(name="Choices", value=answer)
        try:
            poll = await messages[-1].reply(embed=e)
            for emoji, _ in answers:
                await poll.add_reaction(emoji)
        except Exception:
            return await messages[-1].reply(embed=funcs.errorEmbed(None, "Too many choices?"))

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="urban", description="Looks up a term on Urban Dictionary.",
                      aliases=["ud", "urbandictionary"], usage="<term>")
    async def urban(self, ctx, *, term=""):
        if term == "":
            return await ctx.reply(embed=funcs.errorEmbed(None, "Empty input."))
        else:
            res = await funcs.getRequest("http://api.urbandictionary.com/v0/define", params={"term": term})
            data = res.json()
            terms = data["list"]
            if not terms:
                return await ctx.reply(embed=funcs.errorEmbed(None, "Unknown term."))
            else:
                page = 1
                example = terms[0]["example"].replace("[", "").replace("]", "")
                definition = terms[0]["definition"].replace("[", "").replace("]", "")
                permalink = terms[0]["permalink"]
                word = terms[0]["word"]
                e = Embed(description=permalink)
                e.set_author(name=f'"{word}"', icon_url="https://cdn.discordapp.com/attachments/659771291858894849/" + \
                                                        "669142387330777115/urban-dictionary-android.png")
                e.add_field(name="Definition", value=funcs.formatting(definition, limit=1000))
                if example:
                    e.add_field(name="Example", value=funcs.formatting(example, limit=1000))
                e.add_field(name="Author", value=f"`{terms[0]['author']}`")
                try:
                    e.set_footer(
                        text=f"Approval rate: " + \
                             f"{round(terms[0]['thumbs_up'] / (terms[0]['thumbs_up'] + terms[0]['thumbs_down']) * 100, 2)}" + \
                             f"% ({terms[0]['thumbs_up']} 👍 - {terms[0]['thumbs_down']} 👎) | Page {page} of {len(terms)}"
                    )
                except ZeroDivisionError:
                    e.set_footer(text=f"Approval rate: n/a (0 👍 - 0 👎) | Page {page} of {len(terms)}")
                msg = await ctx.reply(embed=e)
                if len(terms) > 1:
                    await msg.add_reaction("⏮")
                    await msg.add_reaction("⏭")
                    while True:
                        success, page = await self.waitForReaction(ctx, msg, len(terms), page)
                        if success:
                            example = terms[page - 1]["example"].replace("[", "").replace("]", "")
                            definition = terms[page - 1]["definition"].replace("[", "").replace("]", "")
                            permalink = terms[page - 1]["permalink"]
                            word = terms[page - 1]["word"]
                            e = Embed(description=permalink)
                            e.set_author(name=f'"{word}"', icon_url="https://cdn.discordapp.com/attachments/659771291858894849/" + \
                                                                    "669142387330777115/urban-dictionary-android.png")
                            e.add_field(name="Definition", value=funcs.formatting(definition, limit=1000))
                            if example:
                                e.add_field(name="Example", value=funcs.formatting(example, limit=1000))
                            e.add_field(name="Author", value=f"`{terms[page - 1]['author']}`")
                            try:
                                ar = round(
                                    terms[page - 1]['thumbs_up'] / (terms[page - 1]['thumbs_up'] + terms[page - 1]['thumbs_down'])
                                    * 100, 2
                                )
                                e.set_footer(
                                    text=f"Approval rate: {ar}% ({terms[page - 1]['thumbs_up']} 👍 - " + \
                                         f"{terms[page - 1]['thumbs_down']} 👎) | Page {page} of {len(terms)}"
                                )
                            except ZeroDivisionError:
                                e.set_footer(text=f"Approval rate: n/a (0 👍 - 0 👎) | Page {page} of {len(terms)}")
                            await msg.edit(embed=e)
                        elif success is None:
                            return

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="reddit", description="Looks up a community or user on Reddit.",
                      aliases=["subreddit", "r", "redditor"], usage="<r/subreddit OR u/redditor>")
    async def reddit(self, ctx, *, inp=""):
        inp = inp.replace(" ", "/")
        while inp.startswith("/"):
            inp = inp[1:]
        while inp.endswith("/"):
            inp = inp[:-1]
        try:
            icon_url = "https://www.redditinc.com/assets/images/site/reddit-logo.png"
            if inp.casefold().startswith("r") and "/" in inp:
                subreddit = await self.reddit.subreddit(inp.split("/")[-1], fetch=True)
                if subreddit.over18 and not isinstance(ctx.channel, channel.DMChannel) \
                        and not ctx.channel.is_nsfw():
                    e = funcs.errorEmbed("NSFW/Over 18!", "Please view this community in an NSFW channel.")
                else:
                    tags = [
                        i for i in [
                            "Link Flairs" if subreddit.can_assign_link_flair else 0,
                            "User Flairs" if subreddit.can_assign_user_flair else 0,
                            "Spoilers Enabled" if subreddit.spoilers_enabled else 0,
                            "NSFW" if subreddit.over18 else 0
                        ] if i
                    ]
                    e = Embed(description=f"https://www.reddit.com/r/{subreddit.display_name}" + " ([Old Reddit](" + \
                                          f"https://old.reddit.com/r/{subreddit.display_name}))")
                    e.set_author(icon_url=icon_url, name="r/" + subreddit.display_name)
                    if tags:
                        e.add_field(name="Tags", value=", ".join(f"`{i}`" for i in tags))
                    e.set_footer(text=subreddit.public_description)
                    dt = datetime.utcfromtimestamp(subreddit.created_utc)
                    e.add_field(name="Creation Date", value=funcs.dateBirthday(dt.day, dt.month, dt.year))
                    e.add_field(name="Subscribers", value="`{:,}`".format(subreddit.subscribers))
                    async for submission in subreddit.new(limit=1):
                        sauthor = submission.author or "[deleted]"
                        if sauthor != "[deleted]":
                            sauthor = sauthor.name
                        e.add_field(
                            name="Latest Post ({:,} point{}; from u/{})".format(
                                submission.score, "" if submission.score == 1 else "s", sauthor
                            ),
                            value=f"https://www.reddit.com{submission.permalink}" + " ([Old Reddit](" + \
                                  f"https://old.reddit.com{submission.permalink}))",
                            inline=False
                        )
            elif inp.casefold().startswith("u") and "/" in inp:
                redditor = await self.reddit.redditor(inp.split("/")[-1], fetch=True)
                try:
                    suspended = redditor.is_suspended
                    tags = ["Suspended"]
                    nickname = ""
                except:
                    suspended = False
                    tags = [
                        i for i in [
                            "Verified" if redditor.has_verified_email else 0,
                            "Reddit Employee" if redditor.is_employee else 0,
                            "Moderator" if redditor.is_mod else 0,
                            "Gold" if redditor.is_gold else 0,
                            "NSFW" if redditor.subreddit["over_18"] else 0
                        ] if i
                    ]
                    nickname = redditor.subreddit["title"]
                if "NSFW" in tags and not isinstance(ctx.channel, channel.DMChannel) \
                        and not ctx.channel.is_nsfw():
                    e = funcs.errorEmbed("NSFW/Over 18!", "Please view this profile in an NSFW channel.")
                else:
                    e = Embed(description=f"https://www.reddit.com/user/{redditor.name}" + " ([Old Reddit](" + \
                                          f"https://old.reddit.com/user/{redditor.name}))")
                    e.set_author(icon_url=icon_url, name="u/" + redditor.name + (f" ({nickname})" if nickname else ""))
                    if tags:
                        e.add_field(name="Tags", value=", ".join(f"`{i}`" for i in tags))
                    if not suspended:
                        lkarma = redditor.link_karma
                        ckarma = redditor.comment_karma
                        trophies = await redditor.trophies()
                        e.set_thumbnail(url=redditor.icon_img)
                        dt = datetime.utcfromtimestamp(redditor.created_utc)
                        e.add_field(name="Join Date", value=funcs.dateBirthday(dt.day, dt.month, dt.year))
                        e.add_field(name="Total Karma", value="`{:,}`".format(lkarma + ckarma))
                        e.add_field(name="Post Karma", value="`{:,}`".format(lkarma))
                        e.add_field(name="Comment Karma", value="`{:,}`".format(ckarma))
                        if trophies:
                            e.add_field(
                                name="Trophies ({:,})".format(len(trophies)),
                                value=", ".join(f"`{trophy.name}`" for trophy in trophies[:50])
                                      + ("..." if len(trophies) > 50 else ""),
                                inline=False
                            )
                        async for submission in redditor.submissions.new(limit=1):
                            e.add_field(
                                name=f"Latest Post (on r/{submission.subreddit.display_name}; " + \
                                     f"{'{:,}'.format(submission.score)} point{'' if submission.score == 1 else 's'})",
                                value=f"https://www.reddit.com{submission.permalink}" + " ([Old Reddit](" + \
                                      f"https://old.reddit.com{submission.permalink}))",
                                inline=False
                            )
                        async for comment in redditor.comments.new(limit=1):
                            e.add_field(
                                name=f"Latest Comment (on r/{comment.subreddit.display_name}; " + \
                                     f"{'{:,}'.format(comment.score)} point{'' if comment.score == 1 else 's'})",
                                value=funcs.formatting(comment.body, limit=1000),
                                inline=False
                            )
                        e.set_footer(text=redditor.subreddit["public_description"])
                        e.set_image(url=redditor.subreddit["banner_img"])
            else:
                e = funcs.errorEmbed("Invalid input!", 'Please use `r/"subreddit name"` or `u/"username"`.')
        except Exception:
            e = funcs.errorEmbed(None, "Invalid search.")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="calc", description="Does simple math.",
                      aliases=["calculate", "calculator", "cal", "math", "maths", "safeeval"], usage="<input>")
    async def calc(self, ctx, *, inp):
        inp = inp.casefold().replace("^", "**").replace("x", "*").replace(",", "").replace("%", "/100") \
              .replace("×", "*").replace(" ", "")
        try:
            e = Embed(description=funcs.formatting(funcs.removeDotZero("{:,}".format(SafeEval(inp).safeEval()))))
        except ZeroDivisionError:
            answer = choice([
                self.COPYPASTA.replace("\*", "*")[:1994],
                "Stop right there, that's illegal!",
                "Wait hol up...",
                "FBI OPEN UP!!!",
                "LOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOL",
                "You madlad...",
                "God damn you.",
                "......................................................",
                "Why the hell do you exist?",
                "Mate I think you've got issues.",
                "Are you okay?",
                "You tell me the answer.",
                "What is wrong with you?",
                "Disgraceful.",
                "Don't you dare.",
                "HOW DARE YOU?!?",
                "You bloody bastard...",
                "Do that again and I will stick that zero down your throat. Egg for breakfast, anyone?",
                "Get a life.",
                "Dio taxista Ronnosessuale dio animale porca di quella madonna vacca in calore rotta in settecento mila pezzi",
                "Naughty naughty naughty, you filthy old soomaka!",
                "Hey that's my yarbles! Give it back!",
                "*magic portal opens...*", "[magic humming]",
                "Go to the den.",
                "EXXXXXCCCCCCUUUUUSEEEE MEEE",
                "what", "wat", "wut", "Negative nothing", "屌", "No.", "no",
                "Der Mann sprach für seine Rechte\ner ist verstört, er ist ein egoistischer Gör!",
                "ENOUGH! Because of you, I almost lost my way! But everycreature here has reminded me of " + \
                "the true power of friendship! There will always be darkness in the world, but there will " + \
                "also always be those who find the light!",
                "Focusing on our differences keeps us divided! Villains and creatures use that division against us!",
                "SSSSHHHHHAAAAAAAAAAAHHDAAAHHHPPP",
                "YOU! YOU TRIPLE GREASY WALKING SECOND DINING COURSE, YOU'RE JUST A PHONY! YOU'RE A GIANT, MORALIST" + \
                " PHONY WHO CAN'T TAKE CARE OF ANYONE, ESPECIALLY HIMSELF! YOU HAVE YOUR OWN DISCIPLINE UP YOUR OWN" + \
                " ARSE AND YOU DON'T EVEN SEE IT!"
            ])
            e = Embed(description=f"```{answer}```")
        except Exception:
            e = funcs.errorEmbed(None, "Invalid input.")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="wordcount", description="Counts the number of words and characters in an input.",
                      aliases=["lettercount", "countletter", "countchar", "countletters", "char", "chars", "letters",
                               "charcount", "wc", "countword", "word", "words", "countwords", "letter"],
                      usage="<input OR .txt attachment>")
    async def wordcount(self, ctx, *, inp=""):
        if ctx.message.attachments:
            try:
                inp = await funcs.readTxt(ctx.message)
            except:
                inp = inp
        if not inp:
            return await ctx.reply(embed=funcs.errorEmbed(None, "Cannot process empty input."))
        splt = "".join(ch for ch in inp if ch not in set(punctuation)).split()
        e = Embed(title="Word Count")
        e.add_field(name="Characters", value="`{:,}`".format(len(inp.strip())))
        e.add_field(name="Words", value="`{:,}`".format(len(splt)))
        e.add_field(name="Unique Words", value="`{:,}`".format(len(set(splt))))
        e.set_footer(text="Note: This may not be 100% accurate.")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="country", description="Shows information about a country.",
                      aliases=["location", "countries", "place", "nation"], usage="<country name OR code>")
    async def country(self, ctx, *, country):
        msg = ctx.message
        try:
            try:
                res = await funcs.getRequest(
                    "https://restcountries.com/v2/name/" + country.casefold().replace("_", ""), verify=False
                )
                data = res.json()
                if len(data) > 1:
                    await ctx.reply(
                        "`Please select a number: " + \
                        f"{', '.join(str(var) + ' (' + data[var]['name'] + ')' for var in range(len(data)))}`"
                    )
                    try:
                        pchoice = await self.client.wait_for(
                            "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=20
                        )
                        msg = pchoice
                        pchoice = int(pchoice.content) if -1 < int(pchoice.content) < len(data) else 0
                    except (TimeoutError, ValueError):
                        pchoice = 0
                else:
                    pchoice = 0
                data = data[pchoice]
            except Exception:
                res = await funcs.getRequest(
                    "https://restcountries.com/v2/alpha/" + country.casefold().replace("_", ""), verify=False
                )
                data = res.json()
            lat = data['latlng'][0]
            long = data['latlng'][1]
            e = Embed(title=f"{data['name']} ({data['alpha3Code']})")
            e.set_thumbnail(url=data["flags"]["png"])
            e.add_field(name="Native Name", value=f"`{data['nativeName']}`")
            e.add_field(name="Population", value="`{:,}`".format(data["population"]))
            e.add_field(name="Demonym", value=f"`{data['demonym']}`")
            e.add_field(
                name="Local Currency", value=", ".join(f"`{c['name']} ({c['code']} {c['symbol']})`" for c in data["currencies"])
            )
            try:
                if data["gini"]:
                    e.add_field(name="Gini Coefficient", value=f"`{round(data['gini'] / 100, 3)}`")
            except:
                pass
            try:
                if data["capital"]:
                    e.add_field(name="Capital", value=f"`{data['capital']}`")
            except:
                pass
            e.add_field(
                name="Coordinates",
                value=f"`{str(round(lat, 2)).replace('-', '')}°{'N' if lat > 0 else 'S'}, " + \
                      f"{str(round(long, 2)).replace('-', '')}°{'E' if long > 0 else 'W'}`"
            )
            e.add_field(name="Region", value=f"`{data['region']} ({data['subregion']})`")
            e.add_field(name="Land Area", value="`{:,} km² / {:,} mi²`".format(int(data["area"]), int(data["area"] * 0.386102159)))
            e.add_field(name="Calling Code", value=", ".join(f"`+{code}`" for code in data["callingCodes"]))
            e.add_field(name="Top Level Domain", value=", ".join(f"`{dom}`" for dom in data["topLevelDomain"]))
            e.add_field(name="Time Zones", value=", ".join(f"`{tz}`" for tz in data["timezones"]))
            e.set_footer(text="Note: The data provided may not be 100% accurate.")
        except Exception:
            e = funcs.errorEmbed(None, "Invalid input or server error.")
        await msg.reply(embed=e)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="normalbodytemp", description="Shows the normal body temperature range chart.",
                      aliases=["bodytemp", "nbt"])
    async def normalbodytemp(self, ctx):
        await funcs.sendImage(ctx, "https://cdn.discordapp.com/attachments/771404776410972161/851367517241999380/image0.jpg")

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(description="Gets information and generates a citation for an article via DOI number.",
                      aliases=["reference", "ref", "citation", "doi", "cit", "altmetric", "altmetrics", "cite", "art"],
                      usage="<DOI number> [citation style]", name="article")
    async def article(self, ctx, doi, style="apa"):
        await ctx.send("Getting article data. Please wait...")
        doi = f'https://doi.org/{funcs.replaceCharacters(doi, ["https://doi.org/", "doi:", "doi.org/"])}'.casefold()
        while doi.endswith("."):
            doi = doi[:-1]
        style = style.casefold()
        style = "chicago-author-date" if style.startswith("chig") or style.startswith("chic") else style
        style = "multidisciplinary-digital-publishing-institute" if style.startswith("mdpi") else style
        cmd = f'curl -LH "Accept: text/x-bibliography; style={style}" "{doi}"'
        try:
            obj = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=False if system() == "Windows" else True)
            res = obj.stdout.read().decode("utf-8").split("\n")
            if res[-1]:
                res.append("")
            res = "".join(i.replace("\n", "") for i in res[4:-1])
            if res.startswith(("<", " ")) or '{"status"' in res or not res:
                raise Exception("Invalid DOI number or server error.")
            while "  " in res:
                res = res.replace("  ", " ")
            if "java.lang.Thread.run" in res:
                res = "Invalid citation style!"
            doi = doi.replace('"', "")
            desc = doi + "\nhttps://sci-hub.mksa.top/" + doi.replace("https://doi.org/", "") + "\n"
            e = Embed(title="Article", description=desc + funcs.formatting(res))
            obj.kill()
            doi = doi.split("doi.org/")[1]
            try:
                altmetricdata = await funcs.getRequest("https://api.altmetric.com/v1/doi/" + doi, verify=False)
                altmetric = altmetricdata.json()
                desc += altmetric["details_url"] + "\n"
                e.description = desc + funcs.formatting(res)
                if len(altmetric["title"]) < 257:
                    e.title = altmetric["title"]
                e.set_thumbnail(url=altmetric["images"]["large"])
                try:
                    e.add_field(name='Authors ({:,})'.format(len(altmetric["authors"])),
                                value=", ".join(f"`{author}`" for author in altmetric["authors"][:10])
                                      + ("..." if len(altmetric["authors"]) > 10 else ""))
                except:
                    pass
                try:
                    e.add_field(name="Journal",
                                value=f"`{altmetric['journal']} (ISSN: {'/'.join(issn for issn in altmetric['issns'])})`")
                except:
                    pass
                if altmetric["published_on"] < 0:
                    pub = (datetime(1970, 1, 1) + timedelta(seconds=altmetric["published_on"])).date()
                else:
                    pub = datetime.utcfromtimestamp(int(altmetric["published_on"])).date()
                e.add_field(name="Publish Date", value="`%s %s %s`" % (pub.day, funcs.monthNumberToName(pub.month), pub.year))
                try:
                    e.add_field(name="PMID", value=f"`{altmetric['pmid']}`")
                except:
                    pass
                citations = [
                    {"field": "cited_by_msm_count", "name": "News Outlet"},
                    {"field": "cited_by_tweeters_count", "name": "Twitter"},
                    {"field": "cited_by_feeds_count", "name": "Blog"},
                    {"field": "cited_by_wikipedia_count", "name": "Wikipedia"},
                    {"field": "cited_by_videos_count", "name": "Video"},
                    {"field": "cited_by_rdts_count", "name": "Reddit"},
                    {"field": "cited_by_fbwalls_count", "name": "Facebook"},
                    {"field": "cited_by_gplus_count", "name": "Google+"},
                    {"field": "cited_by_qna_count", "name": "Q&A Thread"},
                    {"field": "cited_by_rh_count", "name": "Research Highlight"},
                    {"field": "cited_by_policies_count", "name": "Policy Source"},
                    {"field": "cited_by_book_reviews_count", "name": "Book Review"}
                ]
                for i in citations:
                    try:
                        if altmetric[i["field"]]:
                            e.add_field(name=f"{i['name']} Mentions", value="`{:,}`".format(altmetric[i["field"]]))
                    except:
                        pass
                e.set_footer(text="Last updated: {} UTC".format(str(datetime.utcfromtimestamp(int(altmetric["last_updated"])))),
                             icon_url="https://secure.gravatar.com/avatar/97869aff9f24c5d0e1e44b55a274631a")
            except JSONDecodeError:
                e.set_footer(text="Note: No Altmetric data available for this article.")
            try:
                dimensionsdata = await funcs.getRequest("https://metrics-api.dimensions.ai/doi/" + doi, verify=False)
                dimensions = dimensionsdata.json()
                if dimensions["times_cited"]:
                    e.add_field(name="Citations", value="`{:,}`".format(dimensions["times_cited"]))
                if dimensions["recent_citations"]:
                    e.add_field(name="Citations (2y)", value="`{:,}`".format(dimensions["recent_citations"]))
                if dimensions["times_cited"] or dimensions["recent_citations"]:
                    e.description = f"{desc}https://badge.dimensions.ai/details/doi/{doi}\n{funcs.formatting(res)}"
            except:
                pass
        except Exception as ex:
            e = funcs.errorEmbed(None, str(ex))
        await ctx.reply(embed=e)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="textgen", description="Generates text based on your input.",
                      aliases=["tg", "gentext", "text"], usage="<input>")
    async def textgen(self, ctx, *, text=""):
        try:
            if text:
                await ctx.send("Processing text. Please wait...")
            data = {"text": text}
            res = await funcs.postRequest(
                "https://api.deepai.org/api/text-generator", data=data, headers={"api-key": config.deepAIKey}
            )
            data = res.json()
            e = Embed(title="Text Generation", description=funcs.formatting(data["output"]))
        except Exception:
            e = funcs.errorEmbed(None, "Invalid input or server error.")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="quartile", usage="<numbers separated with ;>",
                      aliases=["avg", "average", "mean", "median", "mode", "q1", "q2", "q3", "range", "sd", "iqr", "quartiles"],
                      description="Computes statistical data from a set of numerical values.")
    async def quartile(self, ctx, *, items):
        try:
            while items.startswith(";"):
                items = items[1:]
            while items.endswith(";"):
                items = items[:-1]
            while "  " in items:
                items = items.replace("  ", " ")
            while "; ;" in items:
                items = items.replace("; ;", ";")
            while ";;" in items:
                items = items.replace(";;", ";")
            itemslist = items.split(";")
            if "" in itemslist:
                raise Exception("Invalid input. Please separate the items with `;`.")
            while " " in itemslist:
                itemslist.remove(" ")
            data = sorted(list(map(float, [i.strip() for i in itemslist])))
            halflist = int(len(data) // 2)
            q3 = median(data[-halflist:])
            q1 = median(data[:halflist])
            e = Embed(title="Quartile Calculator",
                      description=f'Requested by: {ctx.author.mention}\n' + \
                                  f'{funcs.formatting("; ".join(funcs.removeDotZero("{:,}".format(i)) for i in data), limit=2000)}')
            e.add_field(name="Total Values", value="`{:,}`".format(len(data)))
            e.add_field(name="Mean", value=f'`{funcs.removeDotZero("{:,}".format(mean(data)))}`')
            try:
                e.add_field(name="Mode", value=f'`{funcs.removeDotZero("{:,}".format(mode(data)))}`')
            except:
                e.add_field(name="Mode", value="`None`")
            e.add_field(name="Q1", value=f'`{funcs.removeDotZero("{:,}".format(q1))}`')
            e.add_field(name="Median (Q2)", value=f'`{funcs.removeDotZero("{:,}".format(median(data)))}`')
            e.add_field(name="Q3", value=f'`{funcs.removeDotZero("{:,}".format(q3))}`')
            e.add_field(name="Interquartile Range", value=f'`{funcs.removeDotZero("{:,}".format(q3 - q1))}`')
            e.add_field(name="Range", value=f'`{funcs.removeDotZero("{:,}".format(max(data) - min(data)))}`')
            e.add_field(name="Population SD", value=f'`{funcs.removeDotZero("{:,}".format(pstdev(data)))}`')
            e.add_field(name="Sample SD", value=f'`{funcs.removeDotZero("{:,}".format(stdev(data)))}`')
            e.add_field(name="Minimum Value", value=f'`{funcs.removeDotZero("{:,}".format(min(data)))}`')
            e.add_field(name="Maximum Value", value=f'`{funcs.removeDotZero("{:,}".format(max(data)))}`')
            e.add_field(name="Sum", value=f'`{funcs.removeDotZero("{:,}".format(sum(data)))}`')
        except Exception as ex:
            e = funcs.errorEmbed(None, str(ex))
        await ctx.reply(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="hcf", usage="<value #1 up to {:,}> <value #2 up to {:,}>".format(HCF_LIMIT, HCF_LIMIT),
                      aliases=["lcm", "gcf", "gcd", "hcd", "lcf", "hcm"],
                      description="Calculates the highest common factor and lowest common multiple of two values.")
    async def hcf(self, ctx, number1, number2):
        try:
            a = int(float(number1))
            b = int(float(number2))
            if a > HCF_LIMIT or b > HCF_LIMIT:
                raise ValueError
            lst = sorted([a, b])
            a, b = lst[0], lst[1]
            hcf = 1
            for i in range(2, a + 1):
                if not a % i and not b % i:
                    hcf = i
            lcm = int((a * b) / hcf)
            await ctx.reply(f'The HCF of {funcs.removeDotZero("{:,}".format(a))} and ' + \
                           f'{funcs.removeDotZero("{:,}".format(b))} is: **{funcs.removeDotZero("{:,}".format(hcf))}' + \
                           f'**\nThe LCM of {funcs.removeDotZero("{:,}".format(a))} and ' + \
                           f'{funcs.removeDotZero("{:,}".format(b))} is: **{funcs.removeDotZero("{:,}".format(lcm))}**')
        except ValueError:
            await ctx.reply(embed=funcs.errorEmbed(None, "Invalid input. Values must be {:,} or below.".format(HCF_LIMIT)))

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="zodiac", description="Converts a date to its zodiac sign.",
                      aliases=["starsign", "horoscope", "zs"], usage="[month] [day]\n\nAlternative usage(s):\n\n- <zodiac sign>")
    async def zodiac(self, ctx, month: str="", day: str=""):
        try:
            if month and not day:
                try:
                    z = funcs.getZodiacInfo(month)
                    e = Embed(title=z[2] + f" :{z[2].casefold().replace('scorpio', 'scorpius')}:")
                    e.add_field(name="Dates", value=f"`{z[1]}`")
                    e.set_image(url=z[0])
                except Exception as ex:
                    e = funcs.errorEmbed("Invalid zodiac!", str(ex))
            else:
                if not month:
                    month = month or datetime.now().month
                if not day:
                    day = day or datetime.now().day
                try:
                    month = funcs.monthNumberToName(int(month))
                except:
                    month = funcs.monthNumberToName(funcs.monthNameToNumber(month))
                monthint = int(funcs.monthNameToNumber(month))
                try:
                    day = int(day)
                except:
                    day = int(day[:-2])
                date = f"{month} {funcs.valueToOrdinal(day)}"
                if day < 1 or day > 31 and monthint in [1, 3, 5, 7, 8, 10, 12] \
                        or day > 30 and monthint in [4, 6, 9, 11] \
                        or day > 29 and monthint == 2:
                    raise Exception
                z = funcs.dateToZodiac(date)
                e = Embed(title=f"{date} Zodiac Sign :{z.casefold().replace('scorpio', 'scorpius')}:")
                e.set_image(url=funcs.getZodiacInfo(z)[0])
                e.set_footer(text=z)
        except Exception:
            e = funcs.errorEmbed(None, "Invalid input.")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="chinesezodiac", description="Converts a year to its Chinese zodiac sign.", usage="[year]",
                      aliases=["cz", "zodiacchinese", "zc", "year", "yearofthe", "ly", "leap", "leapyear"])
    async def chinesezodiac(self, ctx, year: str=""):
        year = year or datetime.now().year
        try:
            year = int(year)
            e = Embed(
                title=f"{str(year) if year > 1 else str(year * -1 + 1) + ' B.C.'} Chinese Zodiac Sign",
                description=funcs.formatting(funcs.yearToChineseZodiac(year))
            )
            ly = str(funcs.leapYear(year))
            e.add_field(name="Leap Year", value=f"`{ly if ly != 'None' else 'Unknown'}`")
        except Exception:
            e = funcs.errorEmbed(None, "Invalid input.")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(description="Shows how far apart two dates are.", aliases=["weekday", "day", "days", "dates", "age", "today"],
                      usage="[date #1 day] [date #1 month] [date #1 year] [date #2 day] [date #2 month] [date #2 year]\n\n" +
                            "Alternative usage(s):\n\n- <days (+/-) from today OR weeks (+/- ending with w) from today>\n\n" + \
                            "- <date day> <date month> <date year> <days (+/-) from date OR weeks (+/- ending with w) from date>",
                      name="date")
    async def date(self, ctx, day: str="", month: str="", year: str="", day2: str="", month2: str="", year2: str=""):
        today = datetime.today()
        try:
            if day and not month and not year and not day2 and not month2 and not year2:
                try:
                    day1int = int(day)
                except ValueError:
                    day1int = int(day[:-1]) * 7
                neg1 = day1int < 0
                dateobj = datetime.today() + timedelta(days=day1int)
                month2 = month2 or datetime.now().month
                day2 = day2 or datetime.now().day
                year2 = year2 or datetime.now().year
                try:
                    month2 = funcs.monthNumberToName(int(month2))
                except:
                    month2 = funcs.monthNumberToName(funcs.monthNameToNumber(month2))
                dateobj2 = datetime(int(year2), int(funcs.monthNameToNumber(month2)), int(day2))
            else:
                neg1 = False
                month = month or datetime.now().month
                day = day or datetime.now().day
                year = year or datetime.now().year
                try:
                    month = funcs.monthNumberToName(int(month))
                except:
                    month = funcs.monthNumberToName(funcs.monthNameToNumber(month))
                dateobj = datetime(int(year), int(funcs.monthNameToNumber(month)), int(day))
                if day2 and not month2 and not year2:
                    try:
                        day2int = int(day2)
                    except ValueError:
                        day2int = int(day2[:-1]) * 7
                    dateobj2 = dateobj + timedelta(days=day2int)
                else:
                    if not month2:
                        month2 = month2 or datetime.now().month
                    if not day2:
                        day2 = day2 or datetime.now().day
                    if not year2:
                        year2 = year2 or datetime.now().year
                    try:
                        month2 = funcs.monthNumberToName(int(month2))
                    except:
                        month2 = funcs.monthNumberToName(funcs.monthNameToNumber(month2))
                    dateobj2 = datetime(int(year2), int(funcs.monthNameToNumber(month2)), int(day2))
            dateobjs = sorted([dateobj, dateobj2])
            delta = dateobjs[1] - dateobjs[0]
            daysint = delta.days + (1 if neg1 else 0)
            if dateobj.date() != today.date() and dateobj2.date() != today.date():
                e = Embed(title="Two Dates")
                e.add_field(
                    name="Date #1",
                    value="`%s, %s %s %s`" % (
                        funcs.weekdayNumberToName(dateobjs[0].weekday()),
                        dateobjs[0].day,
                        funcs.monthNumberToName(dateobjs[0].month),
                        dateobjs[0].year
                    )
                )
                e.add_field(
                    name="Date #2",
                    value="`%s, %s %s %s`" % (
                        funcs.weekdayNumberToName(dateobjs[1].weekday()),
                        dateobjs[1].day,
                        funcs.monthNumberToName(dateobjs[1].month),
                        dateobjs[1].year
                    )
                )
                hastoday = False
            else:
                hastoday = True
                if today.date() == dateobj.date():
                    e = Embed(
                        title=f"{funcs.weekdayNumberToName(dateobj2.weekday())}, " + \
                              f"{dateobj2.day} {funcs.monthNumberToName(dateobj2.month)} {dateobj2.year}"
                    )
                else:
                    e = Embed(
                        title=f"{funcs.weekdayNumberToName(dateobj.weekday())}, " + \
                              f"{dateobj.day} {funcs.monthNumberToName(dateobj.month)} {dateobj.year}"
                    )
            if daysint:
                years, months, daysfinal, monthsfinal, daysint = funcs.dateDifference(dateobjs[0].date(), dateobjs[1].date())
                res = f"== {'Difference From Today' if hastoday else 'Time Difference'} ==\n\n"
                if years:
                    res += "{:,} year{}, {} month{}, and {} day{}\nor ".format(
                        years, "" if years == 1 else "s", months, "" if months == 1 else "s", daysfinal, "" if daysfinal == 1 else "s"
                    )
                if monthsfinal:
                    res += "{:,} month{} and {} day{}\nor ".format(
                        monthsfinal, "" if monthsfinal == 1 else "s", daysfinal, "" if daysfinal == 1 else "s"
                    )
                res += "{:,} day{}".format(daysint, "" if daysint == 1 else "s")
                e.description = funcs.formatting(res)
            else:
                e.description = funcs.formatting("Today")
        except Exception:
            e = funcs.errorEmbed(None, "Invalid input.")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="iss", description="Gets information about the International Space Station and all humans in space.",
                      aliases=["space"])
    async def iss(self, ctx):
        try:
            issdata = await funcs.getRequest("http://api.open-notify.org/iss-now.json", verify=False)
            iss = issdata.json()["iss_position"]
            hisdata = await funcs.getRequest("http://api.open-notify.org/astros.json", verify=False)
            his = hisdata.json()["people"]
            dt = datetime(1998, 11, 20).date()
            e = Embed(description="https://en.wikipedia.org/wiki/International_Space_Station")
            e.set_author(name="The International Space Station",
                         icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/ISS_emblem.png/195px-ISS_emblem.png")
            e.add_field(name="Location", value=f"`{iss['latitude']}, {iss['longitude']}`")
            e.add_field(name="Launch Date", value=funcs.dateBirthday(dt.day, dt.month, dt.year))
            e.add_field(name="Speed", value="`7.66 km/s (27,600 km/h or 17,100 mph)`")
            if his:
                e.add_field(name="Humans in Space ({:,})".format(len(his)), inline=False,
                            value=", ".join(
                                f"`{i['name']} ({i['craft']})`" for i in sorted(his, key=lambda x: x["craft"])
                            )[:800].rsplit("`, ", 1)[0] + "`")
            e.set_image(url="https://cdn.discordapp.com/attachments/771698457391136798/926876797759537192/unknown.png")
        except Exception:
            e = funcs.errorEmbed(None, "Server error.")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(usage="<note #1 with octave (0 to 9)> <note #2 with octave (0 to 9)>",
                      aliases=["octave", "note", "notes", "semitone", "semitones", "vocalrange", "octaves", "notesrange"],
                      name="noterange", description="Shows the range in octaves and semitones between two given musical notes.")
    async def noterange(self, ctx, *, noterange):
        try:
            note1, note2 = funcs.replaceCharacters(noterange.strip(), ["-", "—"], " ").split(" ")
            notes = sorted([funcs.noteFinder(note1), funcs.noteFinder(note2)], key=lambda x: x[1])
            diff = notes[1][1] - notes[0][1]
            if not diff or notes[0][1] < 0 or notes[1][1] > 119:
                e = funcs.errorEmbed("Invalid note range!", "Notes must be between C0 and B9.")
                e.set_footer(text="Notes: " + ", ".join(i for i in funcs.musicalNotes()))
            else:
                octaves = diff // 12
                semitones = diff % 12
                andsemitones = f" and {semitones} semitone{'' if semitones == 1 else 's'}"
                octavestr = f"{octaves} octave{'' if octaves == 1 else 's'}{andsemitones if semitones else ''}\nor "
                e = Embed(title=f"{notes[0][0]}—{notes[1][0]}",
                          description=funcs.formatting(
                              f"== Note Range ==\n\n{octavestr if octaves else ''}{diff} semitone{'' if diff == 1 else 's'}"
                          ))
        except Exception:
            e = funcs.errorEmbed(None, "Invalid input.")
        await ctx.reply(embed=e)


def setup(client: commands.Bot):
    client.add_cog(Utility(client))
