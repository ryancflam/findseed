from asyncio import TimeoutError
from datetime import datetime

from discord import Embed, Colour
from discord.ext import commands

import config
from other_utils import funcs
from other_utils.bitcoin_address import BitcoinAddress

BITCOIN_LOGO = "https://s2.coinmarketcap.com/static/img/coins/128x128/1.png"
BLOCKCYPHER_PARAMS = {"token": config.blockCypherKey}


class Cryptocurrency(commands.Cog, name="Cryptocurrency"):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="cryptoprice", description="Finds the current price of a cryptocurrency.",
                      aliases=["cp", "cmc", "coinmarketcap", "coin"], usage="[coin ticker]")
    async def cryptoprice(self, ctx, coin: str="btc"):
        coin = coin.upper()
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "deflate,gzip",
            "X-CMC_PRO_API_KEY": config.cmcKey
        }
        try:
            r = await funcs.getRequest(url, headers=headers, params={"symbol": coin, "convert": "USD"})
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
            elif r.status_code == 429:
                e = funcs.errorEmbed(None, "Too many requests.")
            elif r.status_code == 400:
                e = funcs.errorEmbed("Invalid argument(s) and/or invalid coin!", "Be sure to use the ticker. (e.g. `btc`)")
            else:
                e = funcs.errorEmbed(None, "Possible server error.")
        except Exception:
            e = funcs.errorEmbed("Invalid argument(s) and/or invalid coin!", "Be sure to use the ticker. (e.g. `btc`)")
        await ctx.send(embed=e)

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
                    description=f"https://www.blockchain.com/btc/tx/{hashstr}",
                    colour=Colour.orange()
                )
                e.set_thumbnail(url=BITCOIN_LOGO)
                e.add_field(name="Date (UTC)", value=f"`{str(datetime.fromtimestamp(txinfo['time']))}`")
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
    @commands.command(name="btcaddr", description="Gets information about a Bitcoin address.",
                      aliases=["baddr", "btcaddress", "address", "addr"], usage="<address>")
    async def btcaddr(self, ctx, *, hashstr: str=""):
        inphash = hashstr.replace("`", "").replace(" ", "")
        if inphash == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            try:
                await ctx.send("Getting Bitcoin address information. Please wait...")
                data = await funcs.getRequest(f"https://blockchain.info/rawaddr/{inphash}")
                txinfo = data.json()
                data = await funcs.getRequest(
                    f"https://api.blockcypher.com/v1/btc/main/addrs/{inphash}", params=BLOCKCYPHER_PARAMS
                )
                txinfo2 = data.json()
                e = Embed(
                    title="Bitcoin Address",
                    description=f"https://www.blockchain.com/btc/address/{inphash}",
                    colour=Colour.orange()
                )
                e.set_thumbnail(url=f"https://api.qrserver.com/v1/create-qr-code/?data={inphash}")
                e.add_field(name="Address", value=f"`{inphash}`")
                e.add_field(name="Hash160", value=f"`{txinfo['hash160']}`")
                e.add_field(
                    name="Final Balance", value=f"`{round(txinfo2['balance'] * 0.00000001, 8)} BTC`"
                    if txinfo2["balance"] > 9999 else f"`{txinfo2['balance']} sat.`"
                )
                e.add_field(
                    name="Unconfirmed Balance", value=f"`{round(txinfo2['unconfirmed_balance'] * 0.00000001, 8)} BTC`"
                    if (txinfo2["unconfirmed_balance"] > 9999 or txinfo2["unconfirmed_balance"] < -9999)
                    else f"`{txinfo2['unconfirmed_balance']} sat.`"
                )
                e.add_field(
                    name="Total Sent", value=f"`{round(txinfo2['total_sent'] * 0.00000001, 8)} BTC`"
                    if txinfo2["total_sent"] > 9999 else f"`{txinfo2['total_sent']} sat.`"
                )
                e.add_field(
                    name="Total Received", value=f"`{round(txinfo2['total_received'] * 0.00000001, 8)} BTC`"
                    if txinfo2["total_received"] > 9999 else f"`{txinfo2['total_received']} sat.`"
                )
                e.add_field(name="Transactions", value=f"`{txinfo['n_tx']}`")
                try:
                    output = "" if round(txinfo["txs"][0]["result"] * 0.00000001, 8) < 0 else "+"
                    tran = (str(txinfo["txs"][0]["result"]) + " sat.") if -9999 < txinfo["txs"][0]["result"] < 10000 \
                        else (str(round(txinfo["txs"][0]["result"] * 0.00000001, 8)) + " BTC")
                    e.add_field(
                        name=f"Last Transaction ({str(datetime.fromtimestamp(txinfo['txs'][0]['time']))})",
                        value=f"`{output}{tran}`"
                    )
                    e.add_field(name="Last Transaction Hash", value=f"`{txinfo['txs'][0]['hash']}`")
                except:
                    pass
                e.set_footer(text="1 satoshi = 0.00000001 BTC")
            except Exception:
                e = funcs.errorEmbed(
                    None, "Unknown address or server error?\n\nNote: Bitcoin addresses are case sensitive. " + \
                          "Addresses that start with `bc1` are not supported."
                )
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
                description=f"https://www.blockchain.com/btc/block/{hashstr}",
                colour=Colour.orange()
            )
            e.set_thumbnail(url=BITCOIN_LOGO)
            e.add_field(name="Date (UTC)", value=f"`{str(datetime.fromtimestamp(blockinfo['time']))}`")
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
            e.add_field(name="Fee Reward", value=f"`{round(int(blockinfo['fee']) * 0.00000001, 8)} BTC`")
            if height != 0:
                e.add_field(name=f"Previous Block ({height - 1})", value=f"`{blockinfo['prev_block']}`")
            if nextblock:
                e.add_field(name=f"Next Block ({height + 1})", value=f"`{nextblock[0]}`")
        except Exception:
            e = funcs.errorEmbed(None, "Unknown block or server error?")
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="btcaddrgen", aliases=["baddrg", "bgenaddr", "btcgenaddr"],
                      description="Generates a Bitcoin address. This command should only be used purely for fun.")
    async def btcaddrgen(self, ctx):
        address = BitcoinAddress()
        pk, swif, shex = address.getAddr()
        e = Embed(
            title="New Bitcoin Address",
            description=f"https://www.blockchain.com/btc/address/{pk}",
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
            await ctx.send("Would you like to mix Bitcoin, Litecoin, or Dash? Enter `!c` to cancel.")
            while True:
                coin = await self.client.wait_for(
                    "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                    timeout=30
                )
                if coin.content.casefold() == "!c":
                    return await ctx.send("Cancelling BitMix.biz order.")
                if coin.content.casefold()[0] not in ["b", "l", "d"]:
                    await ctx.send(embed=funcs.errorEmbed(None, "Invalid coin."))
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
                        await ctx.send(embed=funcs.errorEmbed(None, f"Fee must be {taxmin} to {taxmax} inclusive."))
                        continue
                except ValueError:
                    await ctx.send(embed=funcs.errorEmbed(None, "Invalid input."))
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
                        await ctx.send(embed=funcs.errorEmbed(None, "Delay must be 0 to 4320 inclusive."))
                        continue
                except ValueError:
                    await ctx.send(embed=funcs.errorEmbed(None, "Invalid input."))
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
            e.set_footer(text=f"Requested by: {ctx.author.name}")
        await ctx.send(embed=e)


def setup(client: commands.Bot):
    client.add_cog(Cryptocurrency(client))
