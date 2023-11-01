from asyncio import sleep
from io import BytesIO
from json import JSONDecodeError

from discord import File
from httpx import AsyncClient


async def getTickers():
    while True:
        try:
            tickers = {}
            print("Getting CoinGecko tickers...")
            res = await getRequest("https://api.coingecko.com/api/v3/coins/list")
            for coin in res.json():
                tickers[coin["symbol"]] = coin["id"]
            print("Retrieved CoinGecko tickers")
            return tickers
        except JSONDecodeError as ex:
            print(f"Error - Failed to get CoinGecko tickers ({ex}). Retrying in 30 seconds...")
            await sleep(30)


async def getRequest(url, headers=None, params=None, timeout=60, verify=True):
    async with AsyncClient(verify=verify) as session:
        res = await session.get(url, headers=headers, params=params, timeout=timeout)
    return res


async def postRequest(url, data=None, headers=None, timeout=60, verify=True, json=None):
    async with AsyncClient(verify=verify) as session:
        res = await session.post(url, data=data, headers=headers, timeout=timeout, json=json)
    return res


async def getImageFile(url, headers=None, params=None, timeout=60, verify=True, name="image.png", file=True):
    async with AsyncClient(verify=verify) as session:
        res = await session.get(url, headers=headers, params=params, timeout=timeout)
    return File(BytesIO(res.content), name) if file else BytesIO(res.content)
