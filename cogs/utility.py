from time import time
from datetime import datetime
from urllib.parse import quote
from asyncio import TimeoutError, sleep
from googletrans import Translator, constants

from discord import Embed
from discord.ext import commands

import info
from other_utils import funcs


class Utility(commands.Cog, name="Utility"):
    def __init__(self, client:commands.Bot):
        self.client = client

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="covid", description="Gathers COVID-19 data.",
                      aliases=["coronavirus", "corona", "covid19", "cv", "c19", "cv19"], usage="[location]")
    async def covid(self, ctx, *, searchtype:str=""):
        headers = {
            "x-rapidapi-host": "corona-virus-world-and-india-data.p.rapidapi.com",
            "x-rapidapi-key": info.rapidApiKey
        }
        try:
            res = await funcs.getRequest("https://corona-virus-world-and-india-data.p.rapidapi.com/api", headers=headers)
            data = res.json()
            total = data["countries_stat"]
            found = False
            i = None
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
                        break
                if not found:
                    total = data["world_total"]
                else:
                    total = i
            e = Embed(
                title=f"COVID-19 Stats ({total['country_name'] if found else 'Global'})",
                description="Statistics taken at: `" + data["statistic_taken_at"] + " UTC`"
            )
            e.set_thumbnail(
                url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/" + \
                    "SARS-CoV-2_without_background.png/220px-SARS-CoV-2_without_background.png"
            )
            if found:
                e.add_field(name="Country", value=f"`{total['country_name']}`")
                e.add_field(name="Total Cases", value=f"`{total['cases']}`")
                e.add_field(name="Total Deaths", value=f"`{total['deaths']}" + \
                                                       "\n({}%)`".format(round(int(total['deaths'].replace(',',
                                                           '').replace('N/A', '0'))/int(total['cases'].replace(',',
                                                           '').replace('N/A', '0'))*100, 2)))
                e.add_field(name="Total Recovered", value=f"`{total['total_recovered']}" + \
                                                          "\n({}%)`".format(round(int(total['total_recovered'].replace(',',
                                                              '').replace('N/A', '0'))/int(total['cases'].replace(',',
                                                              '').replace('N/A', '0'))*100, 2)))
                e.add_field(name="Active Cases", value=f"`{total['active_cases']}" + \
                                                       "\n({}%)`".format(round(int(total['active_cases'].replace(',',
                                                           '').replace('N/A', '0'))/int(total['cases'].replace(',',
                                                           '').replace('N/A', '0'))*100, 2)))
                e.add_field(name="Critical Cases", value=f"`{total['serious_critical']}`")
                e.add_field(name="Total Tests", value=f"`{total['total_tests']}`")
            else:
                e.add_field(name="Total Cases", value=f"`{total['total_cases']}`")
                e.add_field(name="Total Deaths", value=f"`{total['total_deaths']}" + \
                                                       "\n({}%)`".format(round(int(total['total_deaths'].replace(',',
                                                           '').replace('N/A', '0'))/int(total['total_cases'].replace(',',
                                                           '').replace('N/A', '0'))*100, 2)))
                e.add_field(name="Total Recovered", value=f"`{total['total_recovered']}" + \
                                                          "\n({}%)`".format(round(int(total['total_recovered'].replace(',',
                                                              '').replace('N/A', '0'))/int(total['total_cases'].replace(',',
                                                              '').replace('N/A', '0'))*100, 2)))
                e.add_field(name="Active Cases", value=f"`{total['active_cases']}" + \
                                                       "\n({}%)`".format(round(int(total['active_cases'].replace(',',
                                                           '').replace('N/A', '0'))/int(total['total_cases'].replace(',',
                                                           '').replace('N/A', '0'))*100, 2)))
            e.add_field(name="New Cases Today", value=f"`{total['new_cases']}`")
            e.add_field(name="New Deaths Today", value=f"`{total['new_deaths']}`")
            e.set_footer(text="Note: The data provided may not be 100% accurate.")
        except Exception:
            e = funcs.errorEmbed(None, "Invalid input or server error.")
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="flight", description="Gets information about a flight",
                      aliases=["flightinfo", "flightradar"], usage="<flight number>")
    async def flight(self, ctx, *, flightstr:str=""):
        if flightstr == "":
            await ctx.send("Error: Empty input.")
            return
        ph = "Unknown"
        flightstr = flightstr.upper().replace(" ", "")
        url = "https://api.flightradar24.com/common/v1/flight/list.json?" + \
              f"&fetchBy=flight&page=1&limit=25&query={flightstr}"
        try:
            res = await funcs.getRequest(url, headers={"User-agent":"*"})
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
                if originname is None:
                    continue
                originiata = data["airport"]["origin"]["code"]["iata"]
                originicao = data["airport"]["origin"]["code"]["icao"]
                destname = data["airport"]["destination"]["name"]
                if destname is None:
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
                thumbnail = list(image["images"]["thumbnails"])[0]["src"][:-4].replace("_tb", "").replace("com/200/", "com/full/")
            e = Embed(title=f"Flight {flightstr}", description=flighturl)
            e.set_image(url=thumbnail)
            e.add_field(name="Date", value=f"`{flightdate}`")
            e.add_field(name="Callsign", value=f"`{callsign}`")
            e.add_field(name="Status", value=f"`{status}`")
            e.add_field(name="Aircraft", value=f"`{aircraft}`")
            e.add_field(name="Registration", value=f"`{reg} ({data['aircraft']['country']['name']})`")
            e.add_field(name="Airline", value=f"`{airline} ({data['airline']['code']['iata']}/{data['airline']['code']['icao']})`")
            e.add_field(name="Origin", value=f"`{originname} ({originiata}/{originicao})`")
            e.add_field(name="Destination", value=f"`{destname} ({destiata}/{desticao})`")
            e.add_field(name=depart, value=f"`{realdepart}`")
            if dago != "":
                e.add_field(name=dago, value=f"`{ft}`")
            e.add_field(name=arrive, value=f"`{realarrive}`")
            if eta != "":
                e.add_field(name=eta, value=f"`{duration}`")
            e.set_footer(text="Note: Flight data provided by Flightradar24 may not be 100% accurate.")
        except Exception:
            e = funcs.errorEmbed(None, "Unknown flight or server error.")
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="weather", description="Finds the current weather of a location.",
                      aliases=["w"], usage="<location>")
    async def weather(self, ctx, *, location:str=""):
        zero = -273.15
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location.casefold().replace(' ', '%20')}" + \
              f"&APPID={info.owmKey}"
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
            e.add_field(name="Wind Direction", value="`{}° ({})`".format(int(winddegrees), funcs.degreesToDirection(winddegrees)))
            e.add_field(name="Local Time", value=f"`{timenow}`")
            e.add_field(name="Last Updated (Local time)", value=f"`{lastupdate}`")
            e.set_footer(text="Note: Weather data provided by OpenWeatherMap may not be 100% accurate.")
            e.set_thumbnail(url=f"http://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png")
        except:
            e = funcs.errorEmbed(None, "Unknown location or server error.")
        await ctx.send(embed=e)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="translate", description="Translates text to a different language.",
                      aliases=["t", "translator", "trans", "tr"], usage="<language code to translate to> <input>")
    async def translate(self, ctx, dest=None, *, text:str=""):
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
                      aliases=["fiat"], usage="<amount> <from currency> <to currency>")
    async def currency(self, ctx, amount=None, fromC=None, toC=None):
        try:
            output = [amount, fromC.upper(), toC.upper()]
        except:
            await ctx.send(
                embed=funcs.errorEmbed(
                    "Invalid usage!", f"Use `{self.client.command_prefix}help currency` to see the correct usage.")
            )
            return
        url = f"http://data.fixer.io/api/latest?access_key={info.fixerKey}"
        try:
            res = await funcs.getRequest(url)
            data = res.json()
            amount = float(output[0])
            initialamount = amount
            if output[1] != "EUR":
                amount = amount / data["rates"][output[1]]
            if output[2] != "EUR":
                amount *= data["rates"][output[2]]
            await ctx.send(f"The current price of **{initialamount} {output[1]}** in **{output[2]}**: `{amount}`")
        except:
            await ctx.send(embed=funcs.errorEmbed(None, "Invalid input or unknown currency."))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="wiki", description="Returns a Wikipedia article.",
                      aliases=["wikipedia"], usage="<article>")
    async def wiki(self, ctx, *, page:str=""):
        if page == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            wikiurl = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&redirects=1&titles="
            try:
                res = await funcs.getRequest(f"{wikiurl}{page.replace(' ','_')}")
                data = res.json()
                wikipage = data["query"]
                if list(wikipage["pages"])[0] == "-1":
                    res = await funcs.getRequest(f"{wikiurl}{page.replace(' ','_').title()}")
                    data = res.json()
                    wikipage = data["query"]
                    if list(wikipage["pages"])[0] == "-1":
                        await ctx.send(embed=funcs.errorEmbed(None, "Invalid article."))
                        return
                if wikipage["pages"][list(wikipage["pages"])[0]]["extract"].casefold().startswith(f"{page} may refer to:\n\n"):
                    try:
                        splitthing = f"may refer to:\n\n"
                        page = wikipage["pages"][list(wikipage["pages"])[0]]["extract"].split(
                            splitthing, 1
                        )[1].split("\n", 1)[1].split(",", 1)[0]
                        res = await funcs.getRequest(f"{wikiurl}{page.replace(' ','_')}")
                        data = res.json()
                        wikipage = data["query"]
                        if wikipage["pages"][list(wikipage["pages"])[0]] == "-1":
                            await ctx.send(embed=funcs.errorEmbed(None, "Invalid article."))
                            return
                    except IndexError:
                        pass
                summary = wikipage["pages"][list(wikipage["pages"])[0]]["extract"]
                if len(summary) != len(wikipage["pages"][list(wikipage["pages"])[0]]["extract"][:1000]):
                    summary = wikipage["pages"][list(wikipage["pages"])[0]]["extract"][:1000] + "..."
                e = Embed(
                    title=wikipage["pages"][list(wikipage["pages"])[0]]["title"],
                    description=f"https://en.wikipedia.org/wiki/{wikipage['pages'][list(wikipage['pages'])[0]]['title'].replace(' ', '_')}"
                )
                e.add_field(name="Extract", value=f"```{summary}```")
                logo = "https://cdn.discordapp.com/attachments/659771291858894849/677853982718165001/1122px-Wikipedia-logo-v2.png"
                e.set_thumbnail(url=logo)
            except Exception:
                e = funcs.errorEmbed(None, "Invalid input or server error.")
        await ctx.send(embed=e)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="lyrics", description="Gets the lyrics of a song.",
                      aliases=["lyric"], usage="<song keywords>")
    async def lyrics(self, ctx, *, keywords:str=""):
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
                e.add_field(name="Genius Link",value=link)
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
                            await msg.remove_reaction("⏮", self.client.user)
                            await msg.remove_reaction("⏭", self.client.user)
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
    async def qrgen(self, ctx, *, text:str=""):
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
        if ctx.message.attachments == []:
            await sleep(3)
        if ctx.message.attachments != [] or ctx.message.embeds != []:
            try:
                if ctx.message.attachments:
                    qrlink = ctx.message.attachments[0].url
                else:
                    qrlink = ctx.message.embeds[0].thumbnail.url
                qr = await funcs.decodeQR(qrlink)
                if not qr:
                    e = funcs.errorEmbed(None, "Cannot detect QR code. Maybe try making the image clearer?")
                else:
                    e = Embed(title="QR Code Message", description=funcs.formatting(qr))
            except Exception as ex:
                e = funcs.errorEmbed(None, str(ex))
        else:
            e = funcs.errorEmbed(None, "No attachment or URL detected, please try again.")
        await ctx.send(embed=e)


def setup(client:commands.Bot):
    client.add_cog(Utility(client))
