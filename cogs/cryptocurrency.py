from os import path, remove
from time import time
from asyncio import TimeoutError
from datetime import datetime
from mplfinance import plot
from pandas import DataFrame, DatetimeIndex

from discord import Embed, Colour, File
from discord.ext import commands

import config
from other_utils import funcs
from other_utils.bitcoin_address import BitcoinAddress

COINGECKO_URL = "https://api.coingecko.com/api/v3/"
BITCOIN_LOGO = "https://s2.coinmarketcap.com/static/img/coins/128x128/1.png"
ETHEREUM_LOGO = "https://s2.coinmarketcap.com/static/img/coins/128x128/1027.png"
BLOCKCYPHER_PARAMS = {"token": config.blockCypherKey}


class Cryptocurrency(commands.Cog, name="Cryptocurrency"):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="cryptoprice", description="Finds the current price of a cryptocurrency.",
                      aliases=["cp", "cmc", "coin", "coingecko", "cg"],
                      usage="[cryptocurrency ticker] [to currency]")
    async def cryptoprice(self, ctx, coin: str="btc", fiat: str="usd"):
        await ctx.send("Getting cryptocurrency market information. Please wait...")
        imgName = f"{time()}.png"
        fiat = fiat.upper()
        image = None
        try:
            res = await funcs.getRequest(
                COINGECKO_URL + "coins/markets", params={
                    "ids": funcs.TICKERS[coin.casefold()],
                    "vs_currency": fiat,
                    "price_change_percentage": "1h,24h,7d"
                }
            )
            data = res.json()[0]
            if res.status_code == 200:
                percent1h = round(data["price_change_percentage_1h_in_currency"], 2)
                percent1d = round(data["price_change_percentage_24h_in_currency"], 2)
                percent7d = round(data["price_change_percentage_7d_in_currency"], 2)
                e = Embed(
                    description=f"https://www.coingecko.com/en/coins/{data['name'].casefold().replace(' ', '-')}",
                    colour=Colour.red() if percent1d < 0 else Colour.green() if percent1d > 0 else Colour.light_grey()
                )
                e.set_author(name=f"{data['name']} ({data['symbol'].upper()})", icon_url=data["image"])
                e.add_field(name="Market Price", value=f"`{data['current_price']} {fiat}`")
                e.add_field(name="All-Time High", value=f"`{data['ath']} {fiat}`")
                e.add_field(name="Market Cap", value=f"`{data['market_cap']} {fiat}`")
                e.add_field(name="Max Supply", value=f"`{data['total_supply']}`")
                e.add_field(name="Circulating", value=f"`{data['circulating_supply']}`")
                e.add_field(name="Market Cap Rank", value=f"`{data['market_cap_rank']}`")
                e.add_field(name="Price Change (1h)", value=f"`{percent1h}%`")
                e.add_field(name="Price Change (24h)", value=f"`{percent1d}%`")
                e.add_field(name="Price Change (7d)", value=f"`{percent7d}%`")
                e.set_footer(text=f"Last updated: {funcs.timeStrToDatetime(data['last_updated'])} UTC")
                try:
                    res = await funcs.getRequest(
                        COINGECKO_URL + f"coins/{funcs.TICKERS[coin.casefold()]}/ohlc",
                        params={"vs_currency": fiat.casefold(), "days": "1"}
                    )
                    ohlcData = res.json()
                    df = DataFrame(
                        [date[1:] for date in ohlcData],
                        index=DatetimeIndex([datetime.utcfromtimestamp(date[0] / 1000) for date in ohlcData]),
                        columns=["Open", "High", "Low", "Close"]
                    )
                    plot(df, type="candle", savefig=imgName,
                         style="binance", ylabel=f"Price ({fiat})", title="24h Chart")
                    image = File(imgName)
                    e.set_image(url=f"attachment://{imgName}")
                except:
                    pass
            elif res.status_code == 400:
                e = funcs.errorEmbed(
                    "Invalid argument(s) and/or invalid currency!", "Be sure to use the ticker. (e.g. `btc`)"
                )
            else:
                e = funcs.errorEmbed(None, "Possible server error.")
        except Exception:
            e = funcs.errorEmbed(
                "Invalid argument(s) and/or invalid currency!", "Be sure to use the ticker. (e.g. `btc`)"
            )
        await ctx.send(embed=e, file=image)
        if path.exists(imgName):
            remove(imgName)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="topcoins", aliases=["tc", "topcrypto", "topcoin", "topcryptos"],
                      description="Returns the top 10 cryptocurrencies by market cap " + \
                                  "and how much of the cryptocurrency market each one dominates.")
    async def topcoins(self, ctx):
        image = None
        try:
            res = await funcs.getRequest(COINGECKO_URL + "global")
            data = res.json()["data"]
            lastUpdated = data["updated_at"]
            data = data["market_cap_percentage"]
            e = Embed(title="Top 10 Cryptocurrencies + Market Dominance",
                      description="https://www.coingecko.com/en/coins/all")
            counter = 1
            for coin in data.keys():
                e.add_field(name=f"{counter}) {coin.upper()}", value=f"`{round(data[coin], 5)}%`")
                counter += 1
            e.add_field(name="Last Updated (UTC)", value=f"`{datetime.utcfromtimestamp(lastUpdated)}`")
            e.set_footer(
                text=f"Use {self.client.command_prefix}coinprice <coin ticker> [vs currency] for more information."
            )
        except Exception:
            e = funcs.errorEmbed(None, "Possible server error, please try again later.")
        await ctx.send(embed=e, file=image)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="btcnetwork", description="Gets current information about the Bitcoin network.",
                      aliases=["btc", "bitcoinnetwork", "bn", "bitcoin"])
    async def btcnetwork(self, ctx):
        await ctx.send("Getting Bitcoin network information. Please wait...")
        try:
            data = await funcs.getRequest("https://blockchain.info/stats", params={"format": "json"})
            blockchain = data.json()
            data = await funcs.getRequest("https://api.blockcypher.com/v1/btc/main", params=BLOCKCYPHER_PARAMS)
            blockchain2 = data.json()
            data = await funcs.getRequest("https://bitnodes.io/api/v1/snapshots/latest/")
            blockchain3 = data.json()
            e = Embed(title="Bitcoin Network", description="https://www.blockchain.com/stats", colour=Colour.orange())
            height = blockchain2["height"]
            blockreward = 50
            halvingheight = 210000
            while height >= halvingheight:
                halvingheight += 210000
                blockreward /= 2
            bl = halvingheight - height
            e.set_thumbnail(url=BITCOIN_LOGO)
            e.add_field(name="Market Price", value=f"`{blockchain['market_price_usd']} USD`")
            e.add_field(name="Minutes Between Blocks", value=f"`{blockchain['minutes_between_blocks']}`")
            e.add_field(name="Mining Difficulty", value=f"`{blockchain['difficulty']}`")
            e.add_field(name="Hash Rate", value=f"`{int(int(blockchain['hash_rate']) / 1000)} TH/s`")
            e.add_field(name="Trade Volume (24h)", value=f"`{blockchain['trade_volume_btc']} BTC`")
            e.add_field(name="Total Transactions (24h)", value=f"`{blockchain['n_tx']}`")
            e.add_field(name="Block Height", value=f"`{height}`")
            e.add_field(name="Next Halving Height", value=f"`{halvingheight} ({bl} block{'' if bl == 1 else 's'} left)`")
            e.add_field(name="Block Reward", value=f"`{blockreward} BTC`")
            e.add_field(name="Unconfirmed Transactions", value=f"`{blockchain2['unconfirmed_count']}`")
            e.add_field(name="Full Nodes", value=f"`{blockchain3['total_nodes']}`")
            e.add_field(
                name="Total Transaction Fees (24h)", value=f"`{round(blockchain['total_fees_btc'] * 0.00000001, 8)} BTC`"
            )
        except Exception:
            e = funcs.errorEmbed(None, "Possible server error, please try again later.")
        await ctx.send(embed=e)

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
                e = Embed(
                    title="Ethereum Transaction",
                    description=f"https://live.blockcypher.com/eth/tx/{hashstr}",
                    colour=Colour.light_grey()
                )
                blockHeight = data["block_height"]
                total = data["total"] / 1000000000000000000
                fees = data["fees"] / 1000000000000000000
                try:
                    relayed = data["relayed_by"]
                except:
                    relayed = "N/A"
                e.set_thumbnail(url=ETHEREUM_LOGO)
                e.add_field(name="Date (UTC)", value=f"`{funcs.timeStrToDatetime(data['received'])}`")
                e.add_field(name="Hash", value=f"`{data['hash']}`")
                e.add_field(name="Block Height", value=f"`{blockHeight if blockHeight != -1 else 'Unconfirmed'}`")
                e.add_field(name="Size", value=f"`{data['size']} bytes`")
                e.add_field(name="Total", value=f"`{total if total else 0} ETH`")
                e.add_field(name="Fees", value=f"`{fees if fees else 0} ETH`")
                e.add_field(name="Confirmations", value=f"`{data['confirmations']}`")
                e.add_field(name="Version", value=f"`{data['ver']}`")
                e.add_field(name="Relayed By", value=f"`{relayed}`")
                e.add_field(name="Input Address", value=f"`{'0x' + data['inputs'][0]['addresses'][0]}`")
                e.add_field(name="Output Address", value=f"`{'0x' + data['outputs'][0]['addresses'][0]}`")
            except Exception:
                e = funcs.errorEmbed(None, "Unknown transaction hash or server error?")
        await ctx.send(embed=e)

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
                e = Embed(
                    title="Bitcoin Transaction",
                    description=f"https://live.blockcypher.com/btc/tx/{hashstr}",
                    colour=Colour.orange()
                )
                e.set_thumbnail(url=BITCOIN_LOGO)
                e.add_field(name="Date (UTC)", value=f"`{str(datetime.utcfromtimestamp(txinfo['time']))}`")
                e.add_field(name="Hash", value=f"`{txinfo['hash']}`")
                try:
                    e.add_field(name="Block Height", value=f"`{txinfo['block_height']}`")
                except:
                    e.add_field(name="Block Height", value="`Unconfirmed`")
                e.add_field(name="Size",value=f"`{txinfo['size']} bytes`")
                e.add_field(name="Weight",value=f"`{txinfo['weight']} WU`")
                e.add_field(
                    name="Total", value=f"`{txinfo2['total']} sat.`" if txinfo2["total"] < 10000
                    else f"`{round(int(txinfo2['total']) * 0.00000001, 8)} BTC`"
                )
                e.add_field(
                    name="Fees", value=f"`{txinfo2['fees']} sat.`" if txinfo2["fees"] < 10000
                    else f"`{round(int(txinfo2['fees']) * 0.00000001, 8)} BTC`"
                )
                e.add_field(name="Confirmations", value=f"`{txinfo2['confirmations']}`")
                try:
                    e.add_field(name="Relayed By", value=f"`{txinfo2['relayed_by']}`")
                except:
                    e.add_field(name="Relayed By", value="`N/A`")
                value = ""
                for i in range(len(txinfo["inputs"])):
                    if i == 20:
                        break
                    if txinfo2["inputs"][i]["output_index"] == -1:
                        value = "Newly generated coins"
                        break
                    if txinfo["inputs"][i]["prev_out"]["value"] < 10000:
                        value += txinfo2["inputs"][i]["addresses"][0] + \
                                 f" ({txinfo['inputs'][i]['prev_out']['value']} sat.)\n\n"
                    else:
                        value += txinfo2["inputs"][i]["addresses"][0] + \
                                 f" ({round(int(txinfo['inputs'][i]['prev_out']['value']) * 0.00000001, 8)} BTC)\n\n"
                newvalue = value[:500]
                if newvalue != value:
                    newvalue += "..."
                e.add_field(name=f"Inputs ({txinfo['vin_sz']})", value=f"```{newvalue}```")
                value = ""
                for i in range(len(txinfo["out"])):
                    if i == 20 or not txinfo2["outputs"][i]["addresses"]:
                        break
                    if txinfo["out"][i]["value"] < 10000:
                        value += txinfo2["outputs"][i]["addresses"][0] + \
                               f" ({txinfo['out'][i]['value']} sat.)\n\n"
                    else:
                        value += txinfo2["outputs"][i]["addresses"][0] + \
                                 f" ({round(int(txinfo['out'][i]['value']) * 0.00000001, 8)} BTC)\n\n"
                newvalue = value[:500]
                if newvalue != value:
                    newvalue += "..."
                e.add_field(name=f"Outputs ({txinfo['vout_sz']})", value=f"```{newvalue}```")
                e.set_footer(text="1 satoshi = 0.00000001 BTC")
            except Exception:
                e = funcs.errorEmbed(None, "Unknown transaction hash or server error?")
        await ctx.send(embed=e)

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
                finalBalance = data["final_balance"] / 1000000000000000000
                unconfirmed = data["unconfirmed_balance"] / 1000000000000000000
                totalSent = data["total_sent"] / 1000000000000000000
                totalReceived =  data["total_received"] / 1000000000000000000
                transactions = data["n_tx"]
                e = Embed(
                    title="Ethereum Address",
                    description=f"https://live.blockcypher.com/eth/address/{inphash}",
                    colour=Colour.light_grey()
                )
                e.set_thumbnail(url=f"https://api.qrserver.com/v1/create-qr-code/?data={'0x' + inphash}")
                e.add_field(name="Address", value=f"`{'0x' + data['address']}`")
                e.add_field(name="Final Balance", value=f"`{finalBalance if finalBalance else 0} ETH`")
                e.add_field(name="Unconfirmed Balance", value=f"`{unconfirmed if unconfirmed else 0} ETH`")
                e.add_field(name="Total Sent", value=f"`{totalSent if totalSent else 0} ETH`")
                e.add_field(name="Total Received", value=f"`{totalReceived if totalReceived else 0} ETH`")
                e.add_field(name="Transactions", value=f"`{transactions}`")
                if transactions:
                    latestTx = data["txrefs"][0]
                    value = latestTx["value"] / 1000000000000000000
                    e.add_field(
                        name=f"Last Transaction ({funcs.timeStrToDatetime(latestTx['confirmed'])})",
                        value=f"`{'-' if latestTx['tx_output_n'] == -1 and value else '+'}{value if value else 0} ETH`"
                    )
                    e.add_field(name="Last Transaction Hash", value=f"`{latestTx['tx_hash']}`")
            except Exception:
                e = funcs.errorEmbed(None, "Unknown address or server error?")
        await ctx.send(embed=e)

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
                e.add_field(
                    name="Final Balance", value=f"`{round(data['balance'] * 0.00000001, 8)} BTC`"
                    if data["balance"] > 9999 else f"`{data['balance']} sat.`"
                )
                e.add_field(
                    name="Unconfirmed Balance", value=f"`{round(data['unconfirmed_balance'] * 0.00000001, 8)} BTC`"
                    if (data["unconfirmed_balance"] > 9999 or data["unconfirmed_balance"] < -9999)
                    else f"`{data['unconfirmed_balance']} sat.`"
                )
                e.add_field(
                    name="Total Sent", value=f"`{round(data['total_sent'] * 0.00000001, 8)} BTC`"
                    if data["total_sent"] > 9999 else f"`{data['total_sent']} sat.`"
                )
                e.add_field(
                    name="Total Received", value=f"`{round(data['total_received'] * 0.00000001, 8)} BTC`"
                    if data["total_received"] > 9999 else f"`{data['total_received']} sat.`"
                )
                e.add_field(name="Transactions", value=f"`{data['n_tx']}`")
                try:
                    output = "-" if data["txrefs"][0]["tx_output_n"] == -1 else "+"
                    tran = (str(data["txrefs"][0]["value"]) + " sat.") if -9999 < data["txrefs"][0]["value"] < 10000 \
                        else (str(round(data["txrefs"][0]["value"] * 0.00000001, 8)) + " BTC")
                    e.add_field(
                        name=f"Last Transaction ({funcs.timeStrToDatetime(data['txrefs'][0]['confirmed'])})",
                        value=f"`{output}{tran}`"
                    )
                    e.add_field(name="Last Transaction Hash", value=f"`{data['txrefs'][0]['tx_hash']}`")
                except:
                    pass
                e.set_footer(text="1 satoshi = 0.00000001 BTC")
            except Exception:
                e = funcs.errorEmbed(None, "Unknown address or server error?")
        await ctx.send(embed=e)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="ethblock", description="Gets information about an Ethereum block.",
                      aliases=["eblock", "eb", "ethheight"], usage="<block hash/height>")
    async def ethblock(self, ctx, *, hashstr: str=""):
        await ctx.send("Getting Ethereum block information. Please wait...")
        hashget = await funcs.getRequest("https://api.blockcypher.com/v1/eth/main", params=BLOCKCYPHER_PARAMS)
        hashjson = hashget.json()
        latestHeight = hashjson["height"]
        hashstr = hashstr or latestHeight
        hashstr = str(hashstr).casefold().replace("`", "").replace(" ", "")
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
                title=f"Ethereum Block {height}",
                description=f"https://live.blockcypher.com/eth/block/{h}",
                colour=Colour.light_grey()
            )
            e.set_thumbnail(url=ETHEREUM_LOGO)
            e.add_field(name="Date (UTC)", value=f"`{date}`")
            e.add_field(name="Hash", value=f"`{h}`")
            e.add_field(name="Merkle Root", value=f"`{data['mrkl_root']}`")
            e.add_field(name="Transactions", value=f"`{data['n_tx']}`")
            e.add_field(name="Total Transacted", value=f"`{data['total'] / 1000000000000000000} ETH`")
            e.add_field(name="Fees", value=f"`{data['fees'] / 1000000000000000000} ETH`")
            e.add_field(name="Size", value=f"`{data['size']} bytes`")
            e.add_field(name="Depth", value=f"`{data['depth']}`")
            e.add_field(name="Version", value=f"`{data['ver']}`")
            if relayed:
                e.add_field(name="Relayed By", value=f"`{relayed}`")
            if height != 0:
                e.add_field(name=f"Previous Block ({height - 1})", value=f"`{data['prev_block']}`")
            if height != latestHeight:
                nextHeight = height + 1
                res = await funcs.getRequest(
                    f"https://api.blockcypher.com/v1/eth/main/blocks/{nextHeight}", params=BLOCKCYPHER_PARAMS
                )
                nextHash = res.json()["hash"]
                e.add_field(name=f"Next Block ({nextHeight})", value=f"`{nextHash}`")
        except Exception:
            e = funcs.errorEmbed(None, "Unknown block or server error?")
        await ctx.send(embed=e)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="btcblock", description="Gets information about a Bitcoin block.",
                      aliases=["bblock", "bb", "btcheight"], usage="<block hash/height>")
    async def btcblock(self, ctx, *, hashstr: str=""):
        await ctx.send("Getting Bitcoin block information. Please wait...")
        if hashstr == "":
            hashget = await funcs.getRequest("https://blockchain.info/latestblock")
            hashjson = hashget.json()
            hashstr = hashjson["hash"]
        hashstr = hashstr.casefold().replace("`", "").replace(" ", "")
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
            e = Embed(
                title=f"Bitcoin Block {height}",
                description=f"https://live.blockcypher.com/btc/block/{hashstr}",
                colour=Colour.orange()
            )
            e.set_thumbnail(url=BITCOIN_LOGO)
            e.add_field(name="Date (UTC)", value=f"`{str(datetime.utcfromtimestamp(blockinfo['time']))}`")
            e.add_field(name="Hash", value=f"`{blockinfo['hash']}`")
            e.add_field(name="Merkle Root", value=f"`{blockinfo['mrkl_root']}`")
            e.add_field(name="Bits", value=f"`{blockinfo['bits']}`")
            e.add_field(name="Transactions", value=f"`{blockinfo['n_tx']}`")
            e.add_field(name="Size", value=f"`{blockinfo['size']} bytes`")
            e.add_field(name="Weight", value=f"`{weight} WU`")
            e.add_field(
                name="Block Reward",
                value=f"`{(int(list(blockinfo['tx'])[0]['out'][0]['value']) - int(blockinfo['fee'])) * 0.00000001} BTC`"
            )
            e.add_field(name="Fees", value=f"`{round(int(blockinfo['fee']) * 0.00000001, 8)} BTC`")
            if height != 0:
                e.add_field(name=f"Previous Block ({height - 1})", value=f"`{blockinfo['prev_block']}`")
            if nextblock:
                e.add_field(name=f"Next Block ({height + 1})", value=f"`{nextblock[0]}`")
        except Exception:
            e = funcs.errorEmbed(None, "Unknown block or server error?")
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="ethcontract", aliases=["ec", "econtract", "smartcontract"],
                      description="Shows information about an Ethereum smart contract.", usage="<contract address>")
    async def ethcontract(self, ctx, *, hashstr: str=""):
        inphash = hashstr.replace("`", "").replace(" ", "").casefold()
        if inphash == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            if not inphash.startswith("0x"):
                inphash = "0x" + inphash
            try:
                res = await funcs.getRequest(COINGECKO_URL + f"coins/ethereum/contract/{inphash}")
                data = res.json()
                e = Embed(
                    title=data["name"], description=f"https://etherscan.io/address/{inphash}"
                )
                e.set_thumbnail(url=data["image"]["large"])
                e.add_field(name="Contract Address", value=f"`{data['contract_address']}`")
                e.add_field(name="Symbol", value=f"`{data['symbol'].upper() or 'None'}`")
                e.add_field(name="Genesis Date", value=f"`{data['genesis_date']}`")
                e.add_field(name="Market Cap Rank", value=f"`{data['market_cap_rank'] or 'None'}`")
                e.add_field(name="Approval Rate", value=f"`{data['sentiment_votes_up_percentage']}%`")
                e.add_field(name="Hashing Algorithm", value=f"`{data['hashing_algorithm'] or 'None'}`")
                e.add_field(name="Max Supply", value=f"`{data['market_data']['total_supply'] or 'None'}`")
                e.add_field(name="Circulating", value=f"`{data['market_data']['circulating_supply'] or 'None'}`")
                e.set_footer(text=data["ico_data"]["description"])
            except Exception:
                e = funcs.errorEmbed(None, "Unknown contract or server error?")
        await ctx.send(embed=e)

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
        await ctx.send("```WARNING: It is recommended that you do NOT use any Bitcoin address generated via this " + \
                       "bot due to security reasons; this command was simply made for fun to demonstrate the " + \
                       "capabilities of the Python programming language. If you wish to generate a new Bitcoin " + \
                       "address for actual use, please use proper wallets like Electrum instead.```", embed=e)

    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.command(name="bitmix", aliases=["bm"],
                      description="Creates a BitMix.biz order for you to mix your BTC, LTC, or DASH.")
    @commands.dm_only()
    async def bitmix(self, ctx):
        url = "https://bitmix.biz/api/order/create"
        try:
            await ctx.send("For maximum anonymity, please connect to the Tor network and use the service's .onion link: h"
                + "ttp://bitmixbizymuphkc.onion\n\nWould you like to mix Bitcoin, Litecoin, or Dash? Enter `!c` to cancel."
            )
            while True:
                coin = await self.client.wait_for(
                    "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                    timeout=30
                )
                if coin.content.casefold() == "!c":
                    return await ctx.send("Cancelling BitMix.biz order.")
                if coin.content.casefold()[0] not in ["b", "l", "d"]:
                    await ctx.send(embed=funcs.errorEmbed(None, "Invalid coin. Please try again."))
                    continue
                break
            await ctx.send("Enter your wallet address. Enter `!c` to cancel.")
            while True:
                address = await self.client.wait_for(
                    "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                    timeout=100
                )
                if address.content.casefold() == "!c":
                    return await ctx.send("Cancelling BitMix.biz order.")
                break
            tax, delay = 0.4, 0
            taxmin = 2 if coin.content.casefold()[0] == "l" else 0.4
            taxmax = 20 if coin.content.casefold()[0] == "l" else 4
            await ctx.send(f"Select a fee from {taxmin}% to {taxmax}%. Enter `!c` to cancel.")
            while True:
                fee = await self.client.wait_for(
                    "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                    timeout=60
                )
                if fee.content.casefold() == "!c":
                    return await ctx.send("Cancelling BitMix.biz order.")
                try:
                    tax = float(fee.content.replace("%", ""))
                    if not taxmin <= tax <= taxmax:
                        await ctx.send(
                            embed=funcs.errorEmbed(None, f"Fee must be {taxmin} to {taxmax} inclusive. Please try again.")
                        )
                        continue
                except ValueError:
                    await ctx.send(embed=funcs.errorEmbed(None, "Invalid input. Please try again."))
                    continue
                break
            await ctx.send("Enter your desired transaction delay in minutes between 0 to 4320. Enter `!c` to cancel.")
            while True:
                minutes = await self.client.wait_for(
                    "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                    timeout=60
                )
                if minutes.content.casefold() == "!c":
                    return await ctx.send("Cancelling BitMix.biz order.")
                try:
                    delay = int(minutes.content)
                    if not -1 < delay < 4321:
                        await ctx.send(
                            embed=funcs.errorEmbed(None, "Delay must be 0 to 4320 inclusive. Please try again.")
                        )
                        continue
                except ValueError:
                    await ctx.send(embed=funcs.errorEmbed(None, "Invalid input. Please try again."))
                    continue
                break
            await ctx.send("Enter anonymity code, or enter `!n` if n/a. Enter `!c` to cancel.")
            while True:
                anon = await self.client.wait_for(
                    "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                    timeout=100
                )
                code = anon.content
                if code.casefold() == "!c":
                    return await ctx.send("Cancelling BitMix.biz order.")
                break
        except TimeoutError:
            return await ctx.send("Cancelling BitMix.biz order.")
        params = {
            "tax": tax,
            "delay": [delay],
            "code": code if code != "!n" else "",
            "coin": "bitcoin" if coin.content.casefold().startswith("b")
            else "litecoin" if coin.content.casefold().startswith("l") else "dash",
            "address": [address.content],
            "ref": config.bitmixRef
        }
        res = await funcs.postRequest(url, json=params, headers={"Accept": "application/json"})
        data = res.json()
        if res.status_code != 200:
            e = funcs.errorEmbed("Invalid data given!", "\n".join(i[0] for i in data["errors"].values()))
        else:
            e = Embed(title="BitMix.biz Order", description=f"https://bitmix.biz/en/order/view/{data['id']}")
            e.add_field(name="Input Address", value=f"`{data['input_address']}`")
            e.add_field(name="Order ID", value=f"`{data['id']}`")
            e.add_field(name="Anonymity Code", value=f"`{data['code']}`")
            e.set_thumbnail(url=f"https://api.qrserver.com/v1/create-qr-code/?data={data['input_address']}")
            e.set_footer(
                text="Note: The QR code is that of the input address. Your order will only be valid for 72 hours."
            )
        await ctx.send(embed=e)


def setup(client: commands.Bot):
    client.add_cog(Cryptocurrency(client))
