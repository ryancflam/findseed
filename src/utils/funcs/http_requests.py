from asyncio import sleep
from io import BytesIO
from json import JSONDecodeError

from httpx import AsyncClient


async def getTickers():
    while True:
        try:
            tickers = {}
            cgres = await getRequest("https://api.coingecko.com/api/v3/coins/list")
            cgdata = cgres.json()
            for coin in cgdata:
                if coin["symbol"] not in tickers:
                    tickers[coin["symbol"]] = coin["id"]
            return tickers
        except JSONDecodeError:
            await sleep(30)


async def getRequest(url, headers=None, params=None, timeout=None, verify=True):
    async with AsyncClient(verify=verify) as session:
        res = await session.get(url, headers=headers, params=params, timeout=timeout)
    return res


async def postRequest(url, data=None, headers=None, timeout=None, verify=True, json=None):
    async with AsyncClient(verify=verify) as session:
        res = await session.post(url, data=data, headers=headers, timeout=timeout, json=json)
    return res


async def getImage(url, headers=None, params=None, timeout=None, verify=True):
    async with AsyncClient(verify=verify) as session:
        res = await session.get(url, headers=headers, params=params, timeout=timeout)
    return BytesIO(res.content)


async def decodeQR(link):
    res = await getRequest("http://api.qrserver.com/v1/read-qr-code", params={"fileurl": link})
    return res.json()[0]["symbol"][0]["data"]