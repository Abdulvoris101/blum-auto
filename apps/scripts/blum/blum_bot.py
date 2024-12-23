import datetime
import logging
import random
from asyncio import Lock
from typing import Optional

import requests
from fake_useragent import UserAgent
from pydantic import ValidationError

from apps.accounts.models import Proxy
from apps.accounts.scheme import ProxyDetailScheme
from apps.common.exceptions import InternalServerException, InvalidRequestException
from apps.common.settings import settings
from apps.core.scheme import BlumBalanceScheme, FriendBalanceScheme
from pyrogram import Client
from pyrogram.raw.functions.messages import RequestWebView
import asyncio
from urllib.parse import unquote

from bot import logger
from utils import text
import httpx

dbLock = Lock()


class BlumBot:
    def __init__(self, sessionName: str, proxy: Optional[ProxyDetailScheme] = None):
        self.proxy = None

        if proxy is not None:
            self.proxy = f"{proxy.type}://{proxy.user}:{proxy.password}@{proxy.host}:{proxy.port}"

            proxy = {
                "scheme": proxy.type,
                "hostname": proxy.host,
                "port": int(proxy.port),
                "username": proxy.user,
                "password": proxy.password
            }

        self.client = Client(name=sessionName, api_id=settings.API_ID, api_hash=settings.API_HASH,
                             workdir=settings.WORKDIR, proxy=proxy)
        self.webSession = None
        self.refreshToken = ''

    async def initWebSession(self):
        headers = {'User-Agent': UserAgent(os='android').random}
        timeout = httpx.Timeout(timeout=60)
        self.webSession = httpx.AsyncClient(proxies=self.proxy, headers=headers, timeout=timeout)

    async def logout(self):
        """
        Logout by closing the aiohttp session.
        """
        await self.webSession.close()

    async def login(self):
        """
        Login to the game using Telegram mini app authentication.
        """
        json_data = {"query": await self.getTgWebData()}
        resp = await self.webSession.post("https://user-domain.blum.codes/api/v1/auth/provider/PROVIDER_TELEGRAM_MINI_APP",
                                          json=json_data)

        if resp.status_code in range(500, 600):
            logger.error(f"Login error - {resp.text}")
            raise InvalidRequestException(messageText=text.BLUM_NOT_WORKING.value, exceptionText="login")

        responseJson = resp.json()
        errorCode = responseJson.get('code')

        if errorCode is not None and errorCode == 9:
            raise InvalidRequestException(messageText=text.BLUM_NOT_LAUNCHED.value)
        elif errorCode is not None and errorCode == 3:
            raise InvalidRequestException(messageText=text.BLUM_NOT_WORKING.value)

        self.webSession.headers['Authorization'] = "Bearer " + responseJson.get("token").get("access")
        self.refreshToken = responseJson.get("token").get("refresh")
        return True

    async def refresh(self):
        """
        Refresh the authorization token.
        """
        json_data = {'refresh': self.refreshToken}
        response = await self.webSession.post("https://user-domain.blum.codes/api/v1/auth/refresh", json=json_data)

        if response.status_code in range(500, 600):
            logger.error(f"Refresh error - {response.text}")
            raise InvalidRequestException(messageText=text.BLUM_NOT_WORKING.value)

        data = response.json()

        self.webSession.headers['Authorization'] = "Bearer " + data.get('access')
        self.refreshToken = data.get('refresh')

    async def start(self):
        """
        Start the farming process.
        """
        response = await self.webSession.post("https://game-domain.blum.codes/api/v1/farming/start")
        if response.status_code in range(500, 600):
            logger.error(f"Start error - {response.text}")
            raise InvalidRequestException(messageText=text.BLUM_NOT_WORKING.value)

        return response.json()

    async def claim(self):
        """
        Claim the farming rewards.
        """
        response = await self.webSession.post("https://game-domain.blum.codes/api/v1/farming/claim")

        if response.status_code in range(500, 600):
            logger.error(f"Claim error - {response.text}")
            raise InvalidRequestException(messageText=text.BLUM_NOT_WORKING.value)

        data = response.json()

        return data.get("availableBalance")

    async def claimDailyReward(self) -> bool:
        """
        Claim the daily reward.
        """
        response = await self.webSession.post("https://game-domain.blum.codes/api/v1/daily-reward?offset=-180")
        responseText = response.text

        if response.status_code in range(500, 600):
            logger.error(f"Claim daily error - {response.text}")
            raise InvalidRequestException(messageText=text.BLUM_NOT_WORKING.value)

        return True if responseText == 'OK' else False

    async def balance(self) -> BlumBalanceScheme:
        """
        Get the current balance and farming status.
        """
        response = await self.webSession.get("https://game-domain.blum.codes/api/v1/user/balance")

        if response.status_code in range(500, 600) or response.status_code == 401:
            logger.error(f"Balance error - {response.text}")
            raise InvalidRequestException(messageText=text.CANT_GET_BLUM_BALANCE.value)

        data = response.json()
        await asyncio.sleep(2)

        if 'farming' not in data:
            data['farming'] = None
        try:
            data["availableBalance"] = float(data.get("availableBalance"))
            data["playPasses"] = int(data.get("playPasses"))
            balanceScheme = BlumBalanceScheme(**data)
            balanceScheme.timestamp = balanceScheme.timestamp / 1000

            if balanceScheme.farming:
                balanceScheme.farming.startTime = balanceScheme.farming.startTime / 1000
                balanceScheme.farming.endTime = balanceScheme.farming.endTime / 1000

            return balanceScheme
        except ValidationError as e:
            print(e)
            raise InternalServerException(text.BLUM_ERROR.value)

    async def friendBalance(self) -> FriendBalanceScheme:
        """
        Gets friend balance
        """
        response = await self.webSession.get("https://user-domain.blum.codes/api/v1/friends/balance")
        if response.status_code in range(500, 600):
            raise InvalidRequestException(messageText=text.BLUM_NOT_WORKING.value)

        data = response.json()
        await asyncio.sleep(2)

        return FriendBalanceScheme(**data)

    async def friendClaim(self):
        response = await self.webSession.post("https://user-domain.blum.codes/api/v1/friends/claim")

        if response.status_code in range(500, 600):
            logger.error(f"Friend claim error - {response.text}")
            raise InvalidRequestException(messageText=text.BLUM_NOT_WORKING.value)

        data = response.json()
        amount = data.get("claimBalance")
        return amount

    async def startGame(self):
        """
        Start a new game and return the game ID.
        """
        try:
            response = await self.webSession.post("https://game-domain.blum.codes/api/v2/game/play")
        except httpx.TimeoutException as e:
            logger.error(f"Timout exception - {e.request}")
            return "internal"

        if response.status_code in range(500, 600):
            logger.error(f"Game error - {response.text}")
            return "internal"

        data = response.json()

        if "gameId" in data:
            return data.get("gameId")
        elif "message" in data:
            return data.get("message")

    async def getDataPayload(self):
        url = 'https://raw.githubusercontent.com/zuydd/database/main/blum.json'
        data = requests.get(url=url)
        return data.json()

    async def createPayload(self, gameId, points):
        data = await self.getDataPayload()
        payloadServer = data.get('payloadServer', [])
        filteredData = [item for item in payloadServer if item['status'] == 1]
        randomId = random.choice([item['id'] for item in filteredData])
        resp = await self.webSession.post(f'https://{randomId}.vercel.app/api/blum',
                                          json={'game_id': gameId, 'points': points})

        if resp is not None:
            data = await resp.json()
            if "payload" in data:
                return data["payload"]
            return None

    async def claimGame(self, gameId: str):
        try:
            points = random.randint(190, 230)
            data = await self.createPayload(gameId=gameId, points=points)
            resp = await self.webSession.post(f"https://game-domain.blum.codes/api/v2/game/claim",
                                              json={'payload': data}, ssl=False)
            if resp.status != 200:
                resp = await self.webSession.post(f"https://game-domain.blum.codes/api/v2/game/claim",
                                                  json={'payload': data}, ssl=False)

            txt = await resp.text()

            return True if txt == 'OK' else False, points
        except Exception as e:
            logger.error(e)

    async def getTgWebData(self):
        """
        Get the Telegram web data needed for login.
        """
        await self.client.connect()

        web_view = await self.client.invoke(RequestWebView(
            peer=await self.client.resolve_peer('BlumCryptoBot'),
            bot=await self.client.resolve_peer('BlumCryptoBot'),
            platform='android',
            from_bot_menu=False,
            url='https://telegram.blum.codes/'
        ))

        auth_url = web_view.url
        await self.client.disconnect()
        return unquote(string=unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))
