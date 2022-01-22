from datetime import datetime
from time import time

from discord import Colour, Embed, File
from discord.ext import commands
from pandas import DataFrame, DatetimeIndex
from plotly import express, graph_objects

import config
from other_utils import funcs
from other_utils.bitcoin_address import BitcoinAddress

GAS_HODL = 0.00088
GAS_GOVN = 0.03504
COINGECKO_URL = "https://api.coingecko.com/api/v3/"
BITCOIN_LOGO = "https://s2.coinmarketcap.com/static/img/coins/128x128/1.png"
ETHEREUM_LOGO = "https://s2.coinmarketcap.com/static/img/coins/128x128/1027.png"
BLOCKCYPHER_PARAMS = {"token": config.blockCypherKey}


class Cryptocurrency(commands.Cog, name="Cryptocurrency", description="Cryptocurrency-related commands."):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.tickers = funcs.getTickers()

    def getCoinGeckoID(self, coin):
        joke = "neo" if coin.casefold() == "neo" \
               or coin.casefold().startswith(("noeo", "ronneo", "neoo", "n*", "neoe", "noee", "ronnoe")) else coin
        try:
            return self.tickers[joke]
        except KeyError:
            return joke

    @staticmethod
    def weiToETH(value):
        return value / 1000000000000000000

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(description="Returns the prices and market capitalisations of NEO and GAS with GAS-to-NEO ratio.",
                      aliases=["n3", "n3o", "noe", "n30", "n", "n**"], usage="[amount of NEO or GAS]", name="neo", hidden=True)
    async def neo(self, ctx, amount="1"):
        try:
            gasamount = float(amount)
            amount = int(gasamount)
        except ValueError:
            amount, gasamount = 1, 1
        if amount < 1:
            amount = 1
        if gasamount <= 0:
            gasamount = 1
        try:
            res = await funcs.getRequest(COINGECKO_URL + "coins/markets", params={"vs_currency": "usd", "ids": "bitcoin,neo,gas"})
            tickers = res.json()
            btcprice = None
            neobtc, neousd, gasbtc, gasusd = None, None, None, None
            neorank, gasrank, neomc, gasmc = None, None, None, None
            for ticker in tickers:
                if ticker["symbol"] == "btc":
                    btcprice = ticker["current_price"]
                if ticker["symbol"] == "neo":
                    neousd = ticker["current_price"]
                    neobtc = neousd / btcprice
                    neorank = ticker["market_cap_rank"]
                    neomc = ticker["market_cap"]
                if ticker["symbol"] == "gas":
                    gasusd = ticker["current_price"]
                    gasbtc = gasusd / btcprice
                    gasrank = ticker["market_cap_rank"]
                    gasmc = ticker["market_cap"]
            e = Embed(colour=Colour.green())
            e.set_author(name="NEO and GAS Prices",
                         icon_url="https://assets.coingecko.com/coins/images/480/large/NEO_512_512.png")
            e.add_field(name="{}NEO".format("" if amount == 1 else str(amount) + " "),
                        value="`{:,} BTC | {:,} USD | {:,} GAS`".format(
                            round(neobtc * amount, 6), round(neousd * amount, 2), round(neousd / gasusd * amount, 3)
                        ), inline=False)
            e.add_field(name="NEO Market Cap", value="`{:,} USD (Rank #{:,})`".format(neomc, neorank))
            e.add_field(name="{}GAS".format("" if gasamount == 1 else funcs.removeDotZero(gasamount) + " "),
                        value="`{:,} BTC | {:,} USD | {:,} NEO`".format(
                            round(gasbtc * gasamount, 6), round(gasusd * gasamount, 2), int(gasusd / neousd * gasamount)
                        ), inline=False)
            e.add_field(name="GAS Market Cap", value="`{:,} USD (Rank #{:,})`".format(gasmc, gasrank))
            e.set_footer(text=f"GAS to NEO ratio: ~{round(gasusd / neousd * 100, 2)}%")
        except Exception as ex:
            funcs.printError(ctx, ex)
            e = funcs.errorEmbed(None, "Server error.")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="gas", description="Calculates N3 GAS earnings based on the amount of NEO you hold.",
                      usage="[amount of NEO]", aliases=["gc", "gascalc", "calcgas", "g"], hidden=True)
    async def gas(self, ctx, amount="1"):
        try:
            amount = int(amount.rsplit(".")[0])
        except ValueError:
            amount = 1
        if amount < 1:
            amount = 1
        hodl, governance = GAS_HODL * amount, GAS_GOVN * amount
        try:
            res = await funcs.getRequest(COINGECKO_URL + "exchanges/binance/tickers", params={"coin_ids": "gas"})
            gasusd = res.json()["tickers"][0]["converted_last"]["usd"]
            gasbtc = res.json()["tickers"][0]["converted_last"]["btc"]
            e = Embed(colour=Colour.green())
            e.set_author(name="GAS Earnings for {:,} NEO".format(amount),
                         icon_url="https://assets.coingecko.com/coins/images/858/large/GAS_512_512.png")
            e.set_footer(text="GAS price: {:,} BTC | {:,} USD".format(gasbtc, gasusd))
            e.add_field(name="Monthly Holding Reward", inline=False,
                        value="`~{:,} GAS ({:,} USD)`".format(round(hodl, 5), round(gasusd * hodl, 5)))
            e.add_field(name="Monthly Governance Participation Reward", inline=False,
                        value="`~{:,} GAS ({:,} USD)`".format(round(governance, 5), round(gasusd * governance, 5)))
        except Exception as ex:
            funcs.printError(ctx, ex)
            e = funcs.errorEmbed(None, "Server error.")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="cryptovs", aliases=["cvs", "vs", "coinvs", "vscoin", "vscrypto", "vsc", "cap", "coincap"],
                      description="Compares the prices of two cryptocurrencies if they had the same market capitalisation.",
                      usage="[coin symbol OR CoinGecko ID] [coin symbol OR CoinGecko ID]")
    async def cryptovs(self, ctx, coin1: str="eth", coin2: str="btc"):
        coinID1, coinID2 = self.getCoinGeckoID(coin1), self.getCoinGeckoID(coin2)
        if coinID1 == coinID2:
            return await ctx.reply(embed=funcs.errorEmbed(None, "Both cryptocurrencies are the same."))
        try:
            res = await funcs.getRequest(
                COINGECKO_URL + "coins/markets", params={"ids": f"{coinID1},{coinID2}", "vs_currency": "usd"}
            )
            data = res.json()
            coin1name = data[0]["name"]
            coin1symb = data[0]["symbol"].upper()
            coin1cap = data[0]["market_cap"]
            coin1price = data[0]["current_price"]
            coin2name = data[1]["name"]
            coin2symb = data[1]["symbol"].upper()
            coin2cap = data[1]["market_cap"]
            coin2price = data[1]["current_price"]
            newvalue = coin1cap / coin2cap
            newvalue2 = coin2cap / coin1cap
            await ctx.reply(f"If **{coin2name} ({coin2symb})** had the market cap of **{coin1name} ({coin1symb})**:\n\n`" + \
                           "{:,} USD` per {} **(+{:,}%)**\n\n".format(
                               round(newvalue * coin2price, 4), coin2symb, round((newvalue - 1) * 100, 2)
                           ) + f"If **{coin1name} ({coin1symb})** had the market cap of **{coin2name} ({coin2symb})**:\n\n`" + \
                           "{:,} USD` per {} **({:,}%)**\n\n".format(
                               round(newvalue2 * coin1price, 4), coin1symb, round((newvalue2 - 1) * 100, 2)
                           ) + "{} price: `{:,} USD` | {} market cap: `{:,} USD` (Rank #{:,})".format(
                               coin1symb, coin1price, coin1symb, coin1cap, data[0]["market_cap_rank"]
                           ) + "\n{} price: `{:,} USD` | {} market cap: `{:,} USD` (Rank #{:,})".format(
                               coin2symb, coin2price, coin2symb, coin2cap, data[1]["market_cap_rank"]
                           ))
        except Exception as ex:
            funcs.printError(ctx, ex)
            return await ctx.reply(embed=funcs.errorEmbed(
                "Invalid argument(s) and/or invalid currency!",
                "Be sure to use the correct symbol or CoinGecko ID. (e.g. `etc` or `ethereum-classic`)"
            ))

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="cryptoprice", description="Shows the current price of a cryptocurrency with a price chart.",
                      aliases=["cp", "cmc", "price", "coingecko", "cg", "coinprice", "coinchart", "chart", "cryptochart", "co"],
                      usage="[coin symbol OR CoinGecko ID] [chart option(s) separated with space]\n\n" +
                            "Valid options:\n\nTime intervals - d, w, 2w, m, 3m, 6m, y, max\n\nOther - " +
                            "Xma (moving average, replace X with number of days), line (line graph)" +
                            "\n\nAny other option will be counted as a comparing currency (e.g. GBP, EUR...)")
    async def cryptoprice(self, ctx, coin: str="btc", *args):
        await ctx.send("Getting cryptocurrency market information. Please wait...")
        imgName = f"{time()}.png"
        days = "1"
        fiat = "USD"
        image = None
        data = []
        count = 0
        noma = True
        mad = 7
        line = False
        for arg in args:
            try:
                days = "1" if int(arg) not in [1, 2, 3, 6, 7, 12, 14, 30, 90, 180, 365] else arg
                days = "14" if days == "2" else "90" if days == "3" else "180" if days == "6" else "365" if days == "12" else days
            except ValueError:
                arg = arg.casefold()
                if arg == "d" or arg.startswith("1d"):
                    days = "1"
                elif arg == "w" or arg.startswith(("1w", "7d")):
                    days = "7"
                elif arg.startswith(("2w", "14d")):
                    days = "14"
                elif arg == "m" or arg.startswith("30d"):
                    days = "30"
                elif arg.startswith(("3m", "90d")) and arg != "3ma":
                    days = "90"
                elif arg.startswith(("6m", "180d")) and arg != "6ma":
                    days = "180"
                elif arg == "y" or arg.startswith(("365d", "12m", "1y")) and arg != "12ma":
                    days = "365"
                elif arg.startswith("max"):
                    days = "max"
                elif arg.endswith("ma"):
                    try:
                        mad = int(arg[:-2])
                        noma = False
                    except:
                        pass
                elif arg == "line":
                    line = True
                else:
                    fiat = arg.upper()
        coinID = self.getCoinGeckoID(coin.casefold())
        try:
            while not data:
                res = await funcs.getRequest(
                    COINGECKO_URL + "coins/markets", params={
                        "ids": coinID,
                        "vs_currency": fiat,
                        "price_change_percentage": "1h,24h,7d,1y"
                    }
                )
                data = res.json()
                if count == 1:
                    break
                count += 1
                if not data:
                    coinID = coinID.replace("-", "")
            if data:
                data = data[0]
                try:
                    res = await funcs.getRequest(COINGECKO_URL + f"coins/{data['id']}/ohlc",
                                                 params={"vs_currency": fiat.casefold(), "days": days}
                    )
                    ohlcData = res.json()
                    difference = ohlcData[-1][4] - ohlcData[0][1]
                    chartData = True
                except:
                    ohlcData = []
                    difference = None
                    chartData = False
                percent1h = data["price_change_percentage_1h_in_currency"] or 0
                percent1d = data["price_change_percentage_24h_in_currency"] or 0
                percent7d = data["price_change_percentage_7d_in_currency"] or 0
                percent1y = data["price_change_percentage_1y_in_currency"] or 0
                if chartData:
                    colour = Colour.red() if difference < 0 else Colour.green() if difference > 0 else Colour.light_grey()
                else:
                    colour = Colour.red() if percent1d < 0 else Colour.green() if percent1d > 0 else Colour.light_grey()
                totalSupply = data["total_supply"]
                circulating = data["circulating_supply"]
                currentPrice = data["current_price"]
                if currentPrice:
                    ath = currentPrice if currentPrice >= data["ath"] else data["ath"]
                else:
                    ath = data["ath"]
                if ath:
                    athDate = funcs.timeStrToDatetime(data["ath_date"]) if ath > currentPrice else "Now! 🎉"
                else:
                    athDate = "N/A"
                e = Embed(
                    colour=colour, description="https://www.coingecko.com/en/coins/" + \
                                               f"{data['name'].casefold().replace(' ', '-').replace('.', '-').replace('τ', 't-')}",
                )
                e.set_author(name=f"{data['name']} ({data['symbol'].upper()})", icon_url=data["image"])
                e.add_field(name="Market Price", value=f"`{'None' if not currentPrice else '{:,} {}'.format(currentPrice, fiat)}`")
                if data["symbol"].upper() != fiat:
                    e.add_field(name=f"All-Time High ({athDate})", value=f"`{'None' if not ath else '{:,} {}'.format(ath, fiat)}`")
                    e.add_field(name="Market Cap", value="`{:,} {}`".format(data['market_cap'], fiat))
                    e.add_field(name="Max Supply",
                                value="`None`" if not totalSupply else "`{:,}`".format(
                                    int(totalSupply) if int(totalSupply) == totalSupply else totalSupply
                                ))
                    e.add_field(name="Circulating",
                                value="`None`" if not circulating else "`{:,}`".format(
                                    int(circulating) if int(circulating) == circulating else circulating
                                ))
                    e.add_field(
                        name="Market Cap Rank",
                        value=f"`{'None' if not data['market_cap_rank'] else '{:,}'.format(data['market_cap_rank'])}`"
                    )
                    e.add_field(name="Price Change (1h)",
                                value=f"`{'None' if not percent1h else '{:,}%'.format(round(percent1h, 2))}`")
                    e.add_field(name="Price Change (24h)",
                                value=f"`{'None' if not percent1d else '{:,}%'.format(round(percent1d, 2))}`")
                    e.add_field(name="Price Change (7d)",
                                value=f"`{'None' if not percent7d else '{:,}%'.format(round(percent7d, 2))}`")
                    e.add_field(name="Price Change (1y)",
                                value=f"`{'None' if not percent1y else '{:,}%'.format(round(percent1y, 2))}`")
                    e.add_field(name="24h High",
                                value="`{:,} {}`".format(data["high_24h"], fiat))
                    e.add_field(name="24h Low",
                                value="`{:,} {}`".format(data["low_24h"], fiat))
                    e.add_field(name="Trading Volume (24h)",
                                value="`{:,} {}`".format(data["total_volume"], fiat))
                    if totalSupply:
                        e.add_field(name="Fully Diluted Valuation",
                                    value="`{:,} {}`".format(int(totalSupply * currentPrice), fiat))
                    e.set_footer(text=f"Last updated: {funcs.timeStrToDatetime(data['last_updated'])} UTC\nChart " +
                                      f"options: {self.client.command_prefix}help cp",
                                 icon_url="https://static.coingecko.com/s/thumbnail-007177f3eca19695592f0b" +
                                          "8b0eabbdae282b54154e1be912285c9034ea6cbaf2.png")
                else:
                    e.set_footer(text="What were you expecting?")
                if chartData:
                    try:
                        df = DataFrame(
                            [date[1:] for date in ohlcData], columns=["Open", "High", "Low", "Close"],
                            index=DatetimeIndex([datetime.utcfromtimestamp(date[0] / 1000) for date in ohlcData])
                        )
                        if line:
                            fig = express.line(x=df.index, y=df["Open"], title="Price")
                        else:
                            fig = graph_objects.Figure(
                                data=[graph_objects.Candlestick(
                                    x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="Price"
                                )]
                            )
                        if not noma:
                            df["ma"] = df["Close"].rolling(window=mad).mean()
                            fig.add_trace(
                                graph_objects.Scatter(
                                    x=df.index, y=df["ma"], line=dict(color="#e0e0e0"), name="{:,}d MA".format(mad)
                                )
                            )
                        fig.update_layout(title=f"{days.title()}{'d' if days != 'max' else ''} Chart ({data['name']})",
                                          yaxis_title=f"Price ({fiat})",
                                          xaxis_rangeslider_visible=False,
                                          xaxis_title="Date",
                                          template="plotly_dark")
                        fig.write_image(f"{funcs.getPath()}/temp/{imgName}")
                        image = File(f"{funcs.getPath()}/temp/{imgName}")
                        e.set_image(url=f"attachment://{imgName}")
                    except Exception as ex:
                        funcs.printError(ctx, ex)
            elif not data:
                e = funcs.errorEmbed(
                    "Invalid argument(s) and/or invalid currency!",
                    "Be sure to use the correct symbol or CoinGecko ID. (e.g. `etc` or `ethereum-classic`)"
                )
            else:
                e = funcs.errorEmbed(None, "Possible server error.")
        except Exception as ex:
            funcs.printError(ctx, ex)
            e = funcs.errorEmbed(
                "Invalid argument(s) and/or invalid currency!",
                "Be sure to use the correct symbol or CoinGecko ID. (e.g. `etc` or `ethereum-classic`)"
            )
        await ctx.reply(embed=e, file=image)
        funcs.deleteTempFile(imgName)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="topcoins", aliases=["tc", "topcrypto", "topcoin", "topcryptos", "top"],
                      description="Returns the top 25 cryptocurrencies by market capitalisation.")
    async def topcoins(self, ctx):
        image = None
        try:
            res = await funcs.getRequest(COINGECKO_URL + "coins")
            data = res.json()
            e = Embed(title="Top 25 Cryptocurrencies by Market Cap",
                      description="https://www.coingecko.com/en/coins/all")
            for counter in range(len(data)):
                coinData = data[counter]
                e.add_field(
                    name=f"{counter + 1}) {coinData['name']} ({coinData['symbol'].upper()})",
                    value="`{:,} USD`".format(coinData['market_data']['market_cap']['usd'])
                )
                if counter == 24:
                    break
            e.set_footer(
                text=f"Use {self.client.command_prefix}coinprice <coin symbol> [vs currency] for more information."
            )
        except Exception as ex:
            funcs.printError(ctx, ex)
            e = funcs.errorEmbed(None, "Possible server error, please try again later.")
        await ctx.reply(embed=e, file=image)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="ethgas", description="Shows the recommended gas prices for Ethereum transactions.",
                      aliases=["eg", "ef", "ethfee", "ethfees", "egas", "efee", "efees", "gasprice", "gasfee"])
    async def ethgas(self, ctx):
        try:
            res = await funcs.getRequest(
                f"https://ethgasstation.info/api/ethgasAPI.json?api-key={config.ethGasStationKey}"
            )
            data = res.json()
            bt = round(data['block_time'])
            e = Embed(colour=Colour.light_grey())
            e.set_author(name="Recommended Ethereum Gas Prices", icon_url=ETHEREUM_LOGO)
            e.add_field(name="Fastest (<30s)", value="`{:,} gwei`".format(int(data['fastest'] / 10)))
            e.add_field(name="Fast (<2m)", value="`{:,} gwei`".format(int(data['fast'] / 10)))
            e.add_field(name="Average (<5m)", value="`{:,} gwei`".format(int(data['average'] / 10)))
            e.add_field(name="Safe Low (<30m)", value="`{:,} gwei`".format(int(data['safeLow'] / 10)))
            e.add_field(name="Block Time", value="`{:,} second{}`".format(bt, "" if bt == 1 else "s"))
            e.set_footer(text="1 gwei = 0.000000001 ETH")
        except Exception as ex:
            funcs.printError(ctx, ex)
            e = funcs.errorEmbed(None, "Server error.")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="btcnetwork", description="Gets current information about the Bitcoin network.",
                      aliases=["btc", "bitcoinnetwork", "bn", "bitcoin", "btcfee", "btcfees"])
    async def btcnetwork(self, ctx):
        await ctx.send("Getting Bitcoin network information. Please wait...")
        try:
            data = await funcs.getRequest("https://blockchain.info/stats", params={"format": "json"})
            blockchain = data.json()
            try:
                data = await funcs.getRequest("https://api.blockcypher.com/v1/btc/main", params=BLOCKCYPHER_PARAMS)
                blockchain2 = data.json()
            except:
                blockchain2 = None
            try:
                data = await funcs.getRequest("https://bitnodes.io/api/v1/snapshots/latest/")
                blockchain3 = data.json()
            except:
                blockchain3 = None
            try:
                data = await funcs.getRequest("https://mempool.space/api/v1/fees/recommended")
                fees = data.json()
            except:
                fees = None
            e = Embed(description="https://www.blockchain.com/stats", colour=Colour.orange())
            height = blockchain2["height"]
            blockreward = 50
            halvingheight = 210000
            while height >= halvingheight:
                halvingheight += 210000
                blockreward /= 2
            bl = halvingheight - height
            blocktime = blockchain['minutes_between_blocks']
            e.set_author(name="Bitcoin Network", icon_url=BITCOIN_LOGO)
            e.add_field(name="Block Time", value="`{:,} minute{}`".format(blocktime, "" if blocktime == 1 else "s"))
            e.add_field(name="Mining Difficulty", value="`{:,}`".format(blockchain['difficulty']))
            e.add_field(name="Hash Rate", value="`{:,} TH/s`".format(int(int(blockchain['hash_rate']) / 1000)))
            e.add_field(name="Trading Volume (24h)", value="`{:,} BTC`".format(blockchain['trade_volume_btc']))
            e.add_field(name="Block Height", value="`{:,}`".format(height))
            e.add_field(name="Next Halving Height",
                        value="`{:,} ({:,} ".format(halvingheight, bl) + f"block{'' if bl == 1 else 's'} left)`")
            e.add_field(name="Block Reward", value=f"`{funcs.btcOrSat(blockreward / 0.00000001)}`")
            if blockchain3:
                e.add_field(name="Full Nodes", value="`{:,}`".format(blockchain3['total_nodes']))
            e.add_field(name="Total Transactions (24h)", value="`{:,}`".format(blockchain['n_tx']))
            if blockchain2:
                e.add_field(name="Unconfirmed Transactions", value="`{:,}`".format(blockchain2['unconfirmed_count']))
            e.add_field(name="Total Transaction Fees (24h)", value=f"`{funcs.btcOrSat(abs(blockchain['total_fees_btc']))}`")
            if fees:
                e.add_field(name="High Priority Fee (~10m)", value="`{:,} sats/vB`".format(fees['fastestFee']))
                e.add_field(name="Medium Priority Fee (~3h)", value="`{:,} sats/vB`".format(fees['halfHourFee']))
                e.add_field(name="Low Priority Fee (~1d)", value="`{:,} sats/vB`".format(fees['hourFee']))
                e.add_field(name="Minimum Fee", value="`{:,} sats/vB`".format(fees['minimumFee']))
        except Exception as ex:
            funcs.printError(ctx, ex)
            e = funcs.errorEmbed(None, "Possible server error, please try again later.")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="ethtx", description="Gets information about an Ethereum transaction.",
                      aliases=["etx", "ethtransaction"], usage="<transaction hash>")
    async def ethtx(self, ctx, *, hashstr: str=""):
        if hashstr == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            await ctx.send("Getting Ethereum transaction information. Please wait...")
            hashstr = hashstr.casefold().replace("`", "").replace(" ", "")
            if hashstr.casefold().startswith("0x"):
                hashstr = hashstr[2:]
            try:
                res = await funcs.getRequest(
                    f"https://api.blockcypher.com/v1/eth/main/txs/{hashstr}", params=BLOCKCYPHER_PARAMS
                )
                data = res.json()
                e = Embed(description=f"https://live.blockcypher.com/eth/tx/{hashstr}", colour=Colour.light_grey())
                blockHeight = data["block_height"]
                total = self.weiToETH(data["total"])
                fees = self.weiToETH(data["fees"])
                try:
                    relayed = data["relayed_by"]
                except:
                    relayed = "N/A"
                e.set_author(name="Ethereum Transaction", icon_url=ETHEREUM_LOGO)
                e.add_field(name="Date (UTC)", value=f"`{funcs.timeStrToDatetime(data['received'])}`")
                e.add_field(name="Hash", value=f"`{data['hash']}`")
                e.add_field(name="Block Height",
                            value=f"`{'{:,}'.format(blockHeight) if blockHeight != -1 else 'Unconfirmed'}`")
                e.add_field(name="Size", value="`{:,} bytes`".format(data['size']))
                e.add_field(name="Total", value=f"`{'{:,}'.format(total) if total else 0} ETH`")
                e.add_field(name="Fees", value=f"`{'{:,}'.format(fees) if fees else 0} ETH`")
                e.add_field(name="Confirmations", value="`{:,}`".format(data['confirmations']))
                e.add_field(name="Version", value=f"`{data['ver']}`")
                e.add_field(name="Relayed By", value=f"`{relayed}`")
                e.add_field(name="Input Address", value=f"`{'0x' + data['inputs'][0]['addresses'][0]}`")
                e.add_field(name="Output Address", value=f"`{'0x' + data['outputs'][0]['addresses'][0]}`")
            except Exception as ex:
                funcs.printError(ctx, ex)
                e = funcs.errorEmbed(None, "Unknown transaction hash or server error?")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="btctx", description="Gets information about a Bitcoin transaction.",
                      aliases=["btx", "btctransaction"], usage="<transaction hash>")
    async def btctx(self, ctx, *, hashstr: str=""):
        if hashstr == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            await ctx.send("Getting Bitcoin transaction information. Please wait...")
            hashstr = hashstr.casefold().replace("`", "").replace(" ", "")
            try:
                res = await funcs.getRequest(f"https://blockchain.info/rawtx/{hashstr}")
                txinfo = res.json()
                res = await funcs.getRequest(
                    f"https://api.blockcypher.com/v1/btc/main/txs/{hashstr}", params=BLOCKCYPHER_PARAMS
                )
                txinfo2 = res.json()
                e = Embed(description=f"https://live.blockcypher.com/btc/tx/{hashstr}", colour=Colour.orange())
                e.set_author(name="Bitcoin Transaction", icon_url=BITCOIN_LOGO)
                e.add_field(name="Date (UTC)", value=f"`{str(datetime.utcfromtimestamp(txinfo['time']))}`")
                e.add_field(name="Hash", value=f"`{txinfo['hash']}`")
                try:
                    e.add_field(name="Block Height", value="`{:,}`".format(txinfo['block_height']))
                except:
                    e.add_field(name="Block Height", value="`Unconfirmed`")
                size = txinfo["size"]
                fee = txinfo2["fees"]
                e.add_field(name="Size",value="`{:,} bytes`".format(size))
                e.add_field(name="Weight",value="`{:,} WU`".format(txinfo['weight']))
                e.add_field(name="Total", value=f"`{funcs.btcOrSat(txinfo2['total'])}`")
                e.add_field(name="Fees", value=f"`{funcs.btcOrSat(fee)}" + f" ({round(fee / size, 2)} sat/byte)`"
                )
                e.add_field(name="Confirmations", value="`{:,}`".format(txinfo2['confirmations']))
                try:
                    e.add_field(name="Relayed By", value=f"`{txinfo2['relayed_by']}`")
                except:
                    e.add_field(name="Relayed By", value="`N/A`")
                value = ""
                for i in range(len(txinfo["inputs"][:20])):
                    if txinfo2["inputs"][i]["output_index"] == -1:
                        value = "Newly generated coins"
                        break
                    value += txinfo2["inputs"][i]["addresses"][0] \
                             + f" ({funcs.btcOrSat(txinfo['inputs'][i]['prev_out']['value'])})\n\n"
                newvalue = value[:500]
                if newvalue != value:
                    newvalue += "..."
                e.add_field(name="Inputs ({:,})".format(txinfo['vin_sz']), value=f"```{newvalue}```")
                value = ""
                for i in range(len(txinfo["out"][:20])):
                    if not txinfo2["outputs"][i]["addresses"]:
                        break
                    value += txinfo2["outputs"][i]["addresses"][0] \
                             + f" ({funcs.btcOrSat(txinfo['out'][i]['value'])})\n\n"
                newvalue = value[:500]
                if newvalue != value:
                    newvalue += "..."
                e.add_field(name="Outputs ({:,})".format(txinfo['vout_sz']), value=f"```{newvalue}```")
                e.set_footer(text="1 satoshi = 0.00000001 BTC")
            except Exception as ex:
                funcs.printError(ctx, ex)
                e = funcs.errorEmbed(None, "Unknown transaction hash or server error?")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="ethaddr", description="Gets information about an Ethereum address.",
                      aliases=["eaddr", "ethaddress", "ea"], usage="<address>")
    async def ethaddr(self, ctx, *, hashstr: str=""):
        inphash = hashstr.replace("`", "").replace(" ", "").casefold()
        if inphash == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            if inphash.startswith("0x"):
                inphash = inphash[2:]
            try:
                await ctx.send("Getting Ethereum address information. Please wait...")
                res = await funcs.getRequest(
                    f"https://api.blockcypher.com/v1/eth/main/addrs/{inphash}", params=BLOCKCYPHER_PARAMS
                )
                data = res.json()
                finalBalance = self.weiToETH(data["final_balance"])
                unconfirmed = self.weiToETH(data["unconfirmed_balance"])
                totalSent = self.weiToETH(data["total_sent"])
                totalReceived = self.weiToETH(data["total_received"])
                transactions = data["n_tx"]
                e = Embed(
                    title="Ethereum Address",
                    description=f"https://live.blockcypher.com/eth/address/{inphash}",
                    colour=Colour.light_grey()
                )
                e.set_thumbnail(url=f"https://api.qrserver.com/v1/create-qr-code/?data={'0x' + inphash}")
                e.add_field(name="Address", value=f"`{'0x' + data['address']}`")
                e.add_field(name="Final Balance", value=f"`{'{:,}'.format(finalBalance) if finalBalance else 0} ETH`")
                e.add_field(name="Unconfirmed Balance", value=f"`{'{:,}'.format(unconfirmed) if unconfirmed else 0} ETH`")
                e.add_field(name="Total Sent", value=f"`{'{:,}'.format(totalSent) if totalSent else 0} ETH`")
                e.add_field(name="Total Received", value=f"`{'{:,}'.format(totalReceived) if totalReceived else 0} ETH`")
                e.add_field(name="Transactions", value="`{:,}`".format(transactions))
                if transactions:
                    latestTx = data["txrefs"][0]
                    value = self.weiToETH(latestTx["value"])
                    e.add_field(
                        name=f"Last Transaction ({funcs.timeStrToDatetime(latestTx['confirmed'])})",
                        value=f"`{'-' if latestTx['tx_output_n'] == -1 and value else '+'}" + \
                              f"{'{:,}'.format(value) if value else 0} ETH`"
                    )
                    e.add_field(name="Last Transaction Hash", value=f"`{latestTx['tx_hash']}`")
            except Exception as ex:
                funcs.printError(ctx, ex)
                e = funcs.errorEmbed(None, "Unknown address or server error?")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="btcaddr", description="Gets information about a Bitcoin address.",
                      aliases=["baddr", "btcaddress", "address", "addr", "ba"], usage="<address>")
    async def btcaddr(self, ctx, *, hashstr: str=""):
        inphash = hashstr.replace("`", "").replace(" ", "")
        if inphash == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            try:
                await ctx.send("Getting Bitcoin address information. Please wait...")
                res = await funcs.getRequest(
                    f"https://api.blockcypher.com/v1/btc/main/addrs/{inphash}", params=BLOCKCYPHER_PARAMS
                )
                data = res.json()
                e = Embed(
                    title="Bitcoin Address",
                    description=f"https://live.blockcypher.com/btc/address/{inphash}",
                    colour=Colour.orange()
                )
                e.set_thumbnail(url=f"https://api.qrserver.com/v1/create-qr-code/?data={inphash}")
                e.add_field(name="Address", value=f"`{inphash}`")
                e.add_field(name="Final Balance", value=f"`{funcs.btcOrSat(data['balance'])}`")
                e.add_field(name="Unconfirmed Balance", value=f"`{funcs.btcOrSat(data['unconfirmed_balance'])}`")
                e.add_field(name="Total Sent", value=f"`{funcs.btcOrSat(data['total_sent'])}`")
                e.add_field(name="Total Received", value=f"`{funcs.btcOrSat(data['total_received'])}`")
                e.add_field(name="Transactions", value="`{:,}`".format(data['n_tx']))
                try:
                    output = "-" if data["txrefs"][0]["tx_output_n"] == -1 else "+"
                    e.add_field(
                        name=f"Last Transaction ({funcs.timeStrToDatetime(data['txrefs'][0]['confirmed'])})",
                        value=f"`{output}{funcs.btcOrSat(data['txrefs'][0]['value'])}`"
                    )
                    e.add_field(name="Last Transaction Hash", value=f"`{data['txrefs'][0]['tx_hash']}`")
                except:
                    pass
                e.set_footer(text="1 satoshi = 0.00000001 BTC")
            except Exception as ex:
                funcs.printError(ctx, ex)
                e = funcs.errorEmbed(None, "Unknown address or server error?")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="ethblock", description="Gets information about an Ethereum block.",
                      aliases=["eblock", "eb", "ethheight"], usage="<block hash OR height>")
    async def ethblock(self, ctx, *, hashstr: str=""):
        await ctx.send("Getting Ethereum block information. Please wait...")
        hashget = await funcs.getRequest("https://api.blockcypher.com/v1/eth/main", params=BLOCKCYPHER_PARAMS)
        hashjson = hashget.json()
        latestHeight = hashjson["height"]
        hashstr = hashstr or latestHeight
        hashstr = funcs.replaceCharacters(str(hashstr).casefold(), ["`", " ", ","])
        if hashstr.casefold().startswith("0x"):
            hashstr = hashstr[2:]
        try:
            res = await funcs.getRequest(
                f"https://api.blockcypher.com/v1/eth/main/blocks/{hashstr}", params=BLOCKCYPHER_PARAMS
            )
            data = res.json()
            date = funcs.timeStrToDatetime(data["time"])
            height = data["height"]
            h = data["hash"]
            relayed = data["relayed_by"]
            e = Embed(
                description=f"https://live.blockcypher.com/eth/block/{h}",
                colour=Colour.light_grey()
            )
            e.set_author(name="Ethereum Block {:,}".format(height), icon_url=ETHEREUM_LOGO)
            e.add_field(name="Date (UTC)", value=f"`{date}`")
            e.add_field(name="Hash", value=f"`{h}`")
            e.add_field(name="Merkle Root", value=f"`{data['mrkl_root']}`")
            e.add_field(name="Transactions", value="`{:,}`".format(data['n_tx']))
            e.add_field(name="Total Transacted", value="`{:,} ETH`".format(self.weiToETH(data['total'])))
            e.add_field(name="Fees", value="`{:,} ETH`".format(self.weiToETH(data['fees'])))
            e.add_field(name="Size", value="`{:,} bytes`".format(data['size']))
            e.add_field(name="Depth", value="`{:,}`".format(data['depth']))
            e.add_field(name="Version", value=f"`{data['ver']}`")
            if relayed:
                e.add_field(name="Relayed By", value=f"`{relayed}`")
            if height != 0:
                e.add_field(name="Previous Block ({:,})".format(height - 1), value=f"`{data['prev_block']}`")
            if height != latestHeight:
                nextHeight = height + 1
                res = await funcs.getRequest(
                    f"https://api.blockcypher.com/v1/eth/main/blocks/{nextHeight}", params=BLOCKCYPHER_PARAMS
                )
                nextHash = res.json()["hash"]
                e.add_field(name="Next Block ({:,})".format(nextHeight), value=f"`{nextHash}`")
        except Exception as ex:
            funcs.printError(ctx, ex)
            e = funcs.errorEmbed(None, "Unknown block or server error?")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="btcblock", description="Gets information about a Bitcoin block.",
                      aliases=["bblock", "bb", "btcheight"], usage="<block hash OR height>")
    async def btcblock(self, ctx, *, hashstr: str=""):
        await ctx.send("Getting Bitcoin block information. Please wait...")
        if hashstr == "":
            hashget = await funcs.getRequest("https://blockchain.info/latestblock")
            hashjson = hashget.json()
            hashstr = hashjson["hash"]
        hashstr = funcs.replaceCharacters(str(hashstr).casefold(), ["`", " ", ","])
        try:
            try:
                hashstr = int(hashstr)
                hashget = await funcs.getRequest(
                    f"https://blockchain.info/block-height/{hashstr}",
                    params={"format": "json"}
                )
                blockinfo = hashget.json()
                blockinfo = blockinfo["blocks"][0]
                nextblock = blockinfo["next_block"]
                hashstr = blockinfo["hash"]
                hashget = await funcs.getRequest(f"https://blockchain.info/rawblock/{hashstr}")
                blockinfo = hashget.json()
                weight = blockinfo["weight"]
            except ValueError:
                if hashstr.casefold().startswith("0x"):
                    hashstr = hashstr[2:]
                hashget = await funcs.getRequest(f"https://blockchain.info/rawblock/{hashstr}")
                blockinfo = hashget.json()
                weight = blockinfo["weight"]
                hashget = await funcs.getRequest(
                    f"https://blockchain.info/block-height/{blockinfo['height']}",
                    params={"format": "json"}
                )
                blockinfo = hashget.json()
                blockinfo = blockinfo["blocks"][0]
                nextblock = blockinfo["next_block"]
            height = blockinfo["height"]
            e = Embed(description=f"https://live.blockcypher.com/btc/block/{hashstr}", colour=Colour.orange())
            e.set_author(name="Bitcoin Block {:,}".format(height), icon_url=BITCOIN_LOGO)
            e.add_field(name="Date (UTC)", value=f"`{str(datetime.utcfromtimestamp(blockinfo['time']))}`")
            e.add_field(name="Hash", value=f"`{blockinfo['hash']}`")
            e.add_field(name="Merkle Root", value=f"`{blockinfo['mrkl_root']}`")
            e.add_field(name="Bits", value="`{:,}`".format(blockinfo['bits']))
            e.add_field(name="Transactions", value="`{:,}`".format(blockinfo['n_tx']))
            e.add_field(name="Size", value="`{:,} bytes`".format(blockinfo['size']))
            e.add_field(name="Weight", value="`{:,} WU`".format(weight))
            e.add_field(
                name="Block Reward",
                value=f"`{(int(list(blockinfo['tx'])[0]['out'][0]['value']) - int(blockinfo['fee'])) * 0.00000001} BTC`"
            )
            e.add_field(name="Fees", value="`{:,} BTC`".format(round(int(blockinfo['fee']) * 0.00000001, 8)))
            if height != 0:
                e.add_field(name="Previous Block ({:,})".format(height - 1), value=f"`{blockinfo['prev_block']}`")
            if nextblock:
                e.add_field(name="Next Block ({:,})".format(height + 1), value=f"`{nextblock[0]}`")
        except Exception as ex:
            funcs.printError(ctx, ex)
            e = funcs.errorEmbed(None, "Unknown block or server error?")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="ethcontract", aliases=["ec", "econtract", "smartcontract"],
                      description="Gets information about an Ethereum smart contract.", usage="<contract address>")
    async def ethcontract(self, ctx, *, hashstr: str=""):
        inphash = funcs.replaceCharacters(str(hashstr).casefold(), ["`", " ", ","])
        if inphash == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            if not inphash.startswith("0x"):
                inphash = "0x" + inphash
            try:
                res = await funcs.getRequest(COINGECKO_URL + f"coins/ethereum/contract/{inphash}")
                data = res.json()
                e = Embed(description=f"https://etherscan.io/address/{inphash}")
                e.set_author(name=data["name"], icon_url=data["image"]["large"])
                e.add_field(name="Contract Address", value=f"`{data['contract_address']}`")
                e.add_field(name="Symbol", value=f"`{data['symbol'].upper() or 'None'}`")
                e.add_field(name="Genesis Date", value=f"`{data['genesis_date']}`")
                e.add_field(name="Market Cap Rank", value=f"`{'{:,}'.format(data['market_cap_rank']) or 'None'}`")
                e.add_field(name="Approval Rate", value=f"`{data['sentiment_votes_up_percentage']}%`")
                e.add_field(name="Hashing Algorithm", value=f"`{data['hashing_algorithm'] or 'None'}`")
                e.add_field(name="Max Supply",
                            value=f"`{'{:,}'.format(data['market_data']['total_supply']) or 'None'}`")
                e.add_field(name="Circulating",
                            value=f"`{'{:,}'.format(data['market_data']['circulating_supply']) or 'None'}`")
                e.set_footer(text=data["ico_data"]["description"])
            except Exception as ex:
                funcs.printError(ctx, ex)
                e = funcs.errorEmbed(None, "Unknown contract or server error?")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="btcaddrgen", aliases=["baddrg", "bgenaddr", "btcgenaddr"],
                      description="Generates a Bitcoin address. This command should only be used purely for fun.")
    async def btcaddrgen(self, ctx):
        address = BitcoinAddress()
        pk, swif, shex = address.getAddr()
        e = Embed(
            title="New Bitcoin Address",
            description=f"https://live.blockcypher.com/btc/address/{pk}",
            colour=Colour.orange()
        )
        e.add_field(name="Public Address",value=f"```{pk}```")
        e.add_field(name="Private Key",value=f"```{swif}```")
        e.add_field(name="Private Key in Hex",value=f"```{shex}```")
        e.set_footer(text=f"Requested by: {ctx.author.name}")
        await ctx.reply("```WARNING: It is recommended that you do NOT use any Bitcoin address generated via this " + \
                       "bot due to security reasons; this command was simply made for fun to demonstrate the " + \
                       "capabilities of the Python programming language. If you wish to generate a new Bitcoin " + \
                       "address for actual use, please use proper wallets like Electrum instead.```", embed=e)


def setup(client: commands.Bot):
    client.add_cog(Cryptocurrency(client))
