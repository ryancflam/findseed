from discord import Embed
from discord.ext import commands

import info
from other_utils import funcs


class Cryptocurrency(commands.Cog, name="Cryptocurrency"):
    def __init__(self, client:commands.Bot):
        self.client = client

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="cryptoprice", description="Finds the current price of a cryptocurrency.",
                      aliases=["cp", "cmc", "coinmarketcap", "coin"], usage="[coin ticker]")
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
            e = funcs.errorEmbed(None,"Too many requests.")
        elif r.status_code == 400:
            e = funcs.errorEmbed("Invalid argument(s) and/or invalid coin!","Be sure to use the ticker. (e.g. `btc`)")
        else:
            e = funcs.errorEmbed(None,"Possible server error.")
        await ctx.channel.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="bitcoin", description="Gets current information about the Bitcoin network.",
                      aliases=["btc", "bitcoinnetwork", "bn"])
    async def bitcoin(self, ctx):
        await ctx.channel.send("Getting Bitcoin information. Please wait...")
        try:
            data = await funcs.getRequest("https://blockchain.info/stats?format=json")
            blockchain = data.json()
            data = await funcs.getRequest("https://api.blockcypher.com/v1/btc/main")
            blockchain2 = data.json()
            data = await funcs.getRequest("https://bitnodes.io/api/v1/snapshots/latest/")
            blockchain3 = data.json()
            e = Embed(title="Bitcoin Network", description="https://www.blockchain.com/stats")
            height = blockchain2["height"]
            blockreward = 50
            halvingheight = 210000
            while height >= halvingheight:
                halvingheight += 210000
                blockreward /= 2
            bl = halvingheight - height
            e.set_thumbnail(url="https://s2.coinmarketcap.com/static/img/coins/128x128/1.png")
            e.add_field(name="Market Price", value=f"`{blockchain['market_price_usd']} USD`")
            e.add_field(name="Minutes Between Blocks", value=f"`{blockchain['minutes_between_blocks']}`")
            e.add_field(name="Mining Difficulty", value=f"`{blockchain['difficulty']}`")
            e.add_field(name="Hash Rate", value=f"`{int(int(blockchain['hash_rate'])/1000)} TH/s`")
            e.add_field(name="Trade Volume (24h)", value=f"`{blockchain['trade_volume_btc']} BTC`")
            e.add_field(name="Total Transactions (24h)", value=f"`{blockchain['n_tx']}`")
            e.add_field(name="Block Height", value=f"`{height}`")
            e.add_field(name="Next Halving Height", value=f"`{halvingheight} ({bl} block{'' if bl==1 else 's'} left)`")
            e.add_field(name="Block Reward", value=f"`{blockreward} BTC`")
            e.add_field(name="Unconfirmed Transactions", value=f"`{blockchain2['unconfirmed_count']}`")
            e.add_field(name="Full Nodes", value=f"`{blockchain3['total_nodes']}`")
            e.add_field(name="Total Transaction Fees (24h)", value=f"`{round(blockchain['total_fees_btc']*0.00000001, 8)} BTC`")
        except Exception:
            e = funcs.errorEmbed(None,"Possible server error, please try again later.")
        await ctx.channel.send(embed=e)


def setup(client):
    client.add_cog(Cryptocurrency(client))
