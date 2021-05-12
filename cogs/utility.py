from asyncio import sleep, TimeoutError
from datetime import datetime
from json import dumps
from random import choice
from time import time
from urllib.parse import quote

from asyncpraw import Reddit
from discord import channel, Embed
from discord.ext import commands
from googletrans import constants, Translator

import config
from other_utils import funcs
from other_utils.safe_eval import SafeEval


class Utility(commands.Cog, name="Utility"):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.reddit = Reddit(client_id=config.redditClientID,
                             client_secret=config.redditClientSecret,
                             user_agent="*")
        self.tickers = funcs.getTickers()

    @staticmethod
    def degreesToDirection(value):
        if not 11.24 <= value <= 348.75:
            return "N"
        if 11.25 <= value <= 33.74:
            return "NNE"
        if 33.75 <= value <= 56.24:
            return "NE"
        if 56.25 <= value <= 78.74:
            return "ENE"
        if 78.75 <= value <= 101.24:
            return "E"
        if 101.25 <= value <= 123.74:
            return "ESE"
        if 123.75 <= value <= 146.24:
            return "SE"
        if 146.25 <= value <= 168.74:
            return "SSE"
        if 168.75 <= value <= 191.24:
            return "S"
        if 191.25 <= value <= 213.74:
            return "SSW"
        if 213.75 <= value <= 236.24:
            return "SW"
        if 236.25 <= value <= 258.74:
            return "WSW"
        if 258.75 <= value <= 281.24:
            return "W"
        if 281.24 <= value <= 303.74:
            return "WNW"
        if 303.75 <= value <= 326.24:
            return "NW"
        return "NNW"

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
                if searchtype.casefold() == "us" or searchtype.casefold().startswith("united states") \
                        or searchtype.casefold().startswith("america"):
                    searchtype = "usa"
                elif searchtype.casefold().startswith("united kingdom") or searchtype.casefold().startswith("great britain") \
                        or searchtype.casefold().startswith("britain") or searchtype.casefold().startswith("england") \
                        or searchtype.casefold() == "gb":
                    searchtype = "uk"
                elif searchtype.casefold().startswith("hk"):
                    searchtype = "hong kong"
                if searchtype.casefold().startswith("korea") or searchtype.casefold().startswith("south korea") \
                        or searchtype.casefold().startswith("sk"):
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
                                                       "\n({}%)`".format(round(int(total['deaths'].replace(',',
                                                           '').replace('N/A', '0')) / int(total['cases'].replace(',',
                                                           '').replace('N/A', '0')) * 100, 2)))
                e.add_field(name="Total Recovered", value=f"`{total['total_recovered']}" + \
                                                          "\n({}%)`".format(round(int(total['total_recovered'].replace(',',
                                                              '').replace('N/A', '0')) / int(total['cases'].replace(',',
                                                              '').replace('N/A', '0')) * 100, 2)))
                e.add_field(name="Active Cases", value=f"`{total['active_cases']}" + \
                                                       "\n({}%)`".format(round(int(total['active_cases'].replace(',',
                                                           '').replace('N/A', '0')) / int(total['cases'].replace(',',
                                                           '').replace('N/A', '0')) * 100, 2)))
                e.add_field(name="Critical Cases", value=f"`{total['serious_critical']}`")
                e.add_field(name="Total Tests", value=f"`{total['total_tests']}`")
            else:
                e.add_field(name="Total Cases", value=f"`{total['total_cases']}`")
                e.add_field(name="Total Deaths", value=f"`{total['total_deaths']}" + \
                                                       "\n({}%)`".format(round(int(total['total_deaths'].replace(',',
                                                           '').replace('N/A', '0')) / int(total['total_cases'].replace(',',
                                                           '').replace('N/A', '0')) * 100, 2)))
                e.add_field(name="Total Recovered", value=f"`{total['total_recovered']}" + \
                                                          "\n({}%)`".format(round(int(total['total_recovered'].replace(',',
                                                              '').replace('N/A', '0')) / int(total['total_cases'].replace(',',
                                                              '').replace('N/A', '0')) * 100, 2)))
                e.add_field(name="Active Cases", value=f"`{total['active_cases']}" + \
                                                       "\n({}%)`".format(round(int(total['active_cases'].replace(',',
                                                           '').replace('N/A', '0')) / int(total['total_cases'].replace(',',
                                                           '').replace('N/A', '0')) * 100, 2)))
            e.add_field(name="New Cases Today", value=f"`{total['new_cases']}`")
            e.add_field(name="New Deaths Today", value=f"`{total['new_deaths']}`")
            e.set_footer(text="Note: The data provided may not be 100% accurate.")
        except Exception:
            e = funcs.errorEmbed(None, "Invalid input or server error.")
        await ctx.send(embed=e)

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
                    image=imgl[y]
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
                if dago != "":
                    e.add_field(name=dago, value=f"`{ft}`")
                e.add_field(name=arrive, value=f"`{realarrive}`")
                if eta != "":
                    e.add_field(name=eta, value=f"`{duration}`")
                e.set_footer(text="Note: Flight data provided by Flightradar24 may not be 100% accurate.",
                             icon_url="https://i.pinimg.com/564x/8c/90/8f/8c908ff985364bdba5514129d3d4e799.jpg")
            except Exception:
                e = funcs.errorEmbed(None, "Unknown flight or server error.")
        await ctx.send(embed=e)

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
                        value="`{}° ({})`".format(int(winddegrees), self.degreesToDirection(winddegrees)))
            e.add_field(name="Local Time", value=f"`{timenow}`")
            e.add_field(name="Last Updated (Local time)", value=f"`{lastupdate}`")
            e.set_footer(text="Note: Weather data provided by OpenWeatherMap may not be 100% accurate.",
                         icon_url="https://openweathermap.org/themes/openweathermap/assets/img/mobile_app/android_icon.png")
            e.set_thumbnail(url=f"http://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png")
        except:
            e = funcs.errorEmbed(None, "Unknown location or server error.")
        await ctx.send(embed=e)

    # Partially not working
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="translate", description="Translates text to a different language.", hidden=True,
                      aliases=["t", "translator", "trans", "tr"], usage="<language code to translate to> <input>")
    async def translate(self, ctx, dest=None, *, text: str=""):
        if not dest:
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            try:
                if dest.casefold() not in constants.LANGUAGES.keys():
                    e = funcs.errorEmbed(
                        "Invalid language code!",
                        f"See [this](https://github.com/ssut/py-googletrans/blob/master/googletrans/constants.py)" + \
                        " for a list of language codes. (Scroll down for `LANGUAGES`)"
                    )
                else:
                    output = Translator().translate(text.casefold(), dest=dest.casefold()).text
                    e = Embed(title="Translate", description=funcs.formatting(output))
            except Exception:
                e = funcs.errorEmbed(None, "An error occurred. Invalid input?")
        await ctx.send(embed=e)

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
            await ctx.send(
                f"The current price of **{'{:,}'.format(initialamount)} {fromCurrency}** in **{toCurrency}**: " + \
                "`{:,}`".format(amount)
            )
        except:
            await ctx.send(embed=funcs.errorEmbed(None, "Invalid input or unknown currency."))

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
                        return await ctx.send(embed=funcs.errorEmbed(None, "Invalid article."))
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
                            return await ctx.send(embed=funcs.errorEmbed(None, "Invalid article."))
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
        await ctx.send(embed=e)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="lyrics", description="Gets the lyrics of a song.",
                      aliases=["lyric"], usage="<song keywords>")
    async def lyrics(self, ctx, *, keywords: str=""):
        if keywords == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
            await ctx.send(embed=e)
        else:
            try:
                await ctx.send("Getting lyrics. Please wait...")
                url = "https://some-random-api.ml/lyrics"
                res = await funcs.getRequest(url, params={"title": keywords})
                data = res.json()
                thumbnail = data["thumbnail"]["genius"]
                link = data["links"]["genius"]
                originallyric = data["lyrics"].replace("*", "\*").replace("_", "\_")
                lyric2 = originallyric[:2048]
                title = data["title"].replace("*", "\*").replace("_", "\_")
                author = data["author"].replace("*", "\*").replace("_", "\_")
                e = Embed(description=lyric2, title=f"{author} - {title}")
                e.set_thumbnail(url=thumbnail)
                e.add_field(name="Genius Link", value=link)
                page = 1
                allpages = (len(originallyric) - 1) // 2048 + 1
                e.set_footer(text=f"Page {page} of {allpages}")
                msg = await ctx.send(embed=e)
                if originallyric != lyric2:
                    await msg.add_reaction("⏮")
                    await msg.add_reaction("⏭")
                    while True:
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
                            return
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
                        if success:
                            start = 2048 * (page - 1)
                            limit = start + 2048
                            newlyric = originallyric[start:limit]
                            edited = Embed(description=newlyric, title=f"{author} - {title}")
                            edited.set_thumbnail(url=thumbnail)
                            edited.add_field(name="Genius Link", value=link)
                            edited.set_footer(text=f"Page {page} of {allpages}")
                            await msg.edit(embed=edited)
            except Exception:
                e = funcs.errorEmbed(None, "Invalid keywords or server error.")
                await ctx.send(embed=e)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="qrgen", description="Generates a QR code.", aliases=["qrg", "genqr", "qr"],
                      usage="<input>")
    async def qrgen(self, ctx, *, text: str=""):
        if text == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            try:
                e = Embed(title="QR Code").set_image(
                    url=f"http://api.qrserver.com/v1/create-qr-code/?data={quote(text)}&margin=25"
                )
            except Exception:
                e = funcs.errorEmbed(None, "Invalid input or server error?")
        await ctx.send(embed=e)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="qrread", description="Reads a QR code.", aliases=["qrscan", "qrr", "readqr"],
                      usage="<image URL/attachment>")
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
        await ctx.send(embed=e)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="compile", description="Compiles code.", aliases=["comp"])
    async def compile(self, ctx):
        res = await funcs.getRequest("https://run.glot.io/languages", verify=False)
        data = res.json()
        languages = [i["name"] for i in data]
        output = ", ".join(f'`{j}`' for j in languages)
        language = ""
        await ctx.send(embed=Embed(title="Please select a language below or input `quit` to quit...",
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
                    await ctx.send(embed=funcs.errorEmbed(None, "Invalid language."))
            except TimeoutError:
                return await ctx.send("Cancelling compilation...")
        if language == "quit":
            return await ctx.send("Cancelling compilation...")
        versionurl = f"https://run.glot.io/languages/{language}"
        res = await funcs.getRequest(versionurl, verify=False)
        data = res.json()
        url = data["url"]
        await ctx.send("**You have 15 minutes to type out your code. Input `quit` to quit.**")
        code = None
        try:
            option = await self.client.wait_for(
                "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=900
            )
            content = option.content
            try:
                if option.attachments:
                    attachment = option.attachments[0]
                    decoded = await attachment.read()
                    content = decoded.decode("utf-8")
                code = content.replace("```", "").replace('“', '"').replace('”', '"').replace("‘", "'").replace("’", "'")
                if code == "quit":
                    return await ctx.send("Cancelling compilation...")
            except:
                pass
        except TimeoutError:
            return await ctx.send("Cancelling compilation...")
        await ctx.send("**Please enter your desired file name including the extension.** (e.g. `main.py`)")
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
                await ctx.send(embed=Embed(title="Compilation", description=funcs.formatting(data["stdout"] or "None")))
            else:
                await ctx.send(embed=funcs.errorEmbed(data["error"].title(), funcs.formatting(stderr)))
        except AttributeError:
            await ctx.send(embed=funcs.errorEmbed(None, "Code exceeded the maximum allowed running time."))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="dictionary", description="Returns the definition(s) of a word.",
                      aliases=["dict", "word", "def", "definition", "meaning"],
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
        await ctx.send(embed=e)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="poll", description="Makes a poll.", usage="<question>", aliases=["questionnaire"])
    @commands.guild_only()
    async def poll(self, ctx, *, question):
        if len(question) > 200:
            return await ctx.send(embed=funcs.errorEmbed(None, "Question must be 200 characters or less."))
        messages, answers = [ctx.message], []
        count = 0
        while count < 20:
            messages.append(
                await ctx.send("Enter poll choice, `!undo` to delete previous choice, or `!done` to publish poll.")
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
                        await ctx.send(embed=funcs.errorEmbed(None, "No choices."))
                    )
            else:
                answers.append((chr(0x1f1e6 + count), entry.content))
                count += 1
        try:
            await ctx.channel.delete_messages(messages)
        except:
            pass
        if len(answers) <= 1:
            return await ctx.send(embed=funcs.errorEmbed(None, "Not enough choices."))
        answer = "\n".join(f"{keycap}: {content}" for keycap, content in answers)
        e = Embed(title=f"Poll - {question}", description=f"Asked by: {ctx.author.mention}")
        e.add_field(name="Choices", value=answer)
        try:
            poll = await ctx.send(embed=e)
            for emoji, _ in answers:
                await poll.add_reaction(emoji)
        except Exception:
            return await ctx.send(embed=funcs.errorEmbed(None, "Too many choices?"))

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="urban", description="Looks up a term on Urban Dictionary.",
                      aliases=["ud", "urbandictionary"], usage="<term>")
    async def urban(self, ctx, *, term=""):
        if term == "":
            e = funcs.errorEmbed(None, "Empty input.")
        else:
            res = await funcs.getRequest(f"http://api.urbandictionary.com/v0/define", params={"term": term})
            data = res.json()
            terms = data["list"]
            if len(terms) == 0:
                e = funcs.errorEmbed(None, "Unknown term.")
            else:
                example = terms[0]["example"].replace("[", "").replace("]", "")
                definition = terms[0]["definition"].replace("[", "").replace("]", "")
                permalink = terms[0]["permalink"]
                word = terms[0]["word"].replace("*", "\*").replace("_", "\_")
                e = Embed(description=permalink)
                e.set_author(name=f'"{word}"', icon_url="https://cdn.discordapp.com/attachments/659771291858894849/" + \
                                                 "669142387330777115/urban-dictionary-android.png")
                e.add_field(name="Definition", value=funcs.formatting(definition, limit=1000))
                if example:
                    e.add_field(name="Example(s)", value=funcs.formatting(example, limit=1000))
                e.set_footer(
                    text=f"Submitted by {terms[0]['author']} | Approval rate: " + \
                         f"{round(terms[0]['thumbs_up'] / (terms[0]['thumbs_up'] + terms[0]['thumbs_down']) * 100, 2)}" + \
                         f"% ({terms[0]['thumbs_up']} 👍 - {terms[0]['thumbs_down']} 👎)"
                )
        await ctx.send(embed=e)

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
                    e.add_field(name="Created (UTC)", value=f"`{datetime.fromtimestamp(subreddit.created_utc)}`")
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
                        e.add_field(name="Join Date (UTC)", value=f"`{datetime.fromtimestamp(redditor.created_utc)}`")
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
        await ctx.send(embed=e)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="calc", description="Does simple math.",
                      aliases=["calculate", "calculator", "cal", "math", "maths", "safeeval"], usage="<input>")
    async def calc(self, ctx, *, inp):
        inp = inp.casefold().replace("^", "**").replace("x", "*").replace(",", "").replace("%", "/100") \
              .replace("×", "*").replace(" ", "")
        try:
            e = Embed(description=funcs.formatting("{:,}".format(SafeEval(inp).safeEval())))
        except ZeroDivisionError:
            answer = choice([
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
                "You did absolutely **** all to resolve the pandemic, you did close to nothing to " + \
                "prepare yourselves for it, and let alone did you do anything to functionally reso" + \
                "lve problems. You are oppressing our individual liberties because of the shortcom" + \
                "ings of your institutions. You are stifling your economy and, as a consequence, o" + \
                "ur income because of your vices. And last but not least, you seem to be absolutel" + \
                "y stuck into a self-repetitive loop of making the same idiotic mistakes over and over again.",
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
        await ctx.send(embed=e)


def setup(client: commands.Bot):
    client.add_cog(Utility(client))
