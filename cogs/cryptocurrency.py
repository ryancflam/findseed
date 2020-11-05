from discord import Embed
from discord.ext import commands

import info
import funcs


class Cryptocurrency(commands.Cog, name="Cryptocurrency"):
    def __init__(self, client:commands.Bot):
        self.client = client

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="cryptoprice", description="Finds the current price of a cryptocurrency.",
                      aliases=["cp", "cmc", "coinmarketcap", "btc", "bitcoin", "coin"], usage="[coin ticker]")
    async def cryptoprice(self, ctx, coin:str="btc"):
        coin = coin.upper()
        url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={coin}&convert=USD"
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "deflate,gzip",
            "X-CMC_PRO_API_KEY": info.cmcKey
        }
        r = await funcs.getRequest(url, headers=headers)
        data = r.json()
        if r.status_code == 200:
            value = round(data["data"][coin]["quote"]["USD"]["price"], 8)
            name = data["data"][coin]["name"]
            marketCap = int(data["data"][coin]["quote"]["USD"]["market_cap"])
            try:
                volume = int(data["data"][coin]["quote"]["USD"]["volume_24h"])
            except:
                volume = 0
            try:
                percent1h = round(data["data"][coin]["quote"]["USD"]["percent_change_1h"], 2)
            except:
                percent1h = 0
            try:
                percent1d = round(data["data"][coin]["quote"]["USD"]["percent_change_24h"], 2)
            except:
                percent1d = 0
            try:
                percent7d = round(data["data"][coin]["quote"]["USD"]["percent_change_7d"], 2)
            except:
                percent7d = 0
            rank = data["data"][coin]["cmc_rank"]
            maxSupply = data["data"][coin]["max_supply"]
            circulating = data["data"][coin]["circulating_supply"]
            e = Embed(
                title=name,
                description=f"https://coinmarketcap.com/currencies/{data['data'][coin]['slug']}"
            )
            e.set_thumbnail(
                url=f"https://s2.coinmarketcap.com/static/img/coins/128x128/{data['data'][coin]['id']}.png"
            )
            e.add_field(name="Market Price", value=f"`{value} USD`")
            e.add_field(name="Market Cap", value=f"`{marketCap} USD`")
            e.add_field(name="Max Supply", value=f"`{maxSupply}`")
            e.add_field(name="Circulating", value=f"`{circulating}`")
            e.add_field(name="CoinMarketCap Rank", value=f"`{rank}`")
            e.add_field(name="Volume (24h)", value=f"`{volume} USD`")
            e.add_field(name="Price Change (1h)", value=f"`{percent1h}%`")
            e.add_field(name="Price Change (24h)", value=f"`{percent1d}%`")
            e.add_field(name="Price Change (7d)", value=f"`{percent7d}%`")
            e.set_footer(text="Data provided by: coinmarketcap.com")
        elif r.status_code == 429:
            e = funcs.errorEmbed(None, "Too many requests.")
        elif r.status_code == 400:
            e = funcs.errorEmbed("Invalid argument(s) and/or invalid coin!", "Be sure to use the ticker. (e.g. `btc`)")
        else:
            e = funcs.errorEmbed(None, "Possible server error.")
        await ctx.channel.send(embed=e)


def setup(client):
    client.add_cog(Cryptocurrency(client))
