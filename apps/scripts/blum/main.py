import asyncio
import datetime
import random
from asyncio import sleep
from datetime import timedelta
from random import uniform

import httpx
import pyrogram.errors.exceptions.unauthorized_401

from apps.accounts.models import Account, BlumAccount, Proxy
from apps.accounts.scheme import Status, ProxyDetailScheme
from apps.common.exceptions import AiogramException, InvalidRequestException
from apps.common.settings import settings
from apps.core.keyboards import startMenuMarkup
from apps.core.models import User
from apps.core.scheme import FriendBalanceScheme
from apps.payment.models import AccountSubscription
from apps.scripts.blum.blum_bot import BlumBot
from bot import bot, logger
from utils import text


class BlumManager:
    def __init__(self, account: Account, user: User):
        self.subscription = None
        self.account = account
        self.user = user
        self.sessionName = account.sessionName
        self.mainText = text.STARTED_FARMING.format(sessionName=self.sessionName)

    def formatDuration(self, seconds):
        duration_td = timedelta(seconds=seconds)
        hours, remainder = divmod(duration_td.total_seconds(), 3600)
        return round(hours, 1)

    async def playGame(self, playPasses: int, blum: BlumBot, editMessageId: int, blumAccount: BlumAccount,
                       subscription: AccountSubscription):
        tempPlayedGames = 1

        while playPasses:
            isAllowedPlay = (not subscription.isFreeTrial or
                             (subscription.isFreeTrial and blumAccount.playedGames < settings.ALLOWED_FREE_GAMES))

            if not isAllowedPlay:
                break

            if tempPlayedGames % 10 == 0:
                self.mainText += text.LONG_INTERVAL_GAME.value
                await bot.edit_message_text(chat_id=self.user.telegramId, text=self.mainText, message_id=editMessageId)
                await sleep(uniform(10, 15))
            gameId = await blum.startGame()

            if gameId == "internal":
                self.mainText += text.NOT_AVAILABLE_GAME_INTERNAL.value
                await bot.edit_message_text(chat_id=self.user.telegramId, text=self.mainText, message_id=editMessageId)
                playPasses -= 1
                continue
            elif not gameId or gameId == "cannot start game":
                self.mainText += text.COULD_NOT_PLAY_GAMES.value
                await bot.edit_message_text(chat_id=self.user.telegramId, text=self.mainText, message_id=editMessageId)
                await asyncio.sleep(3)
                playPasses -= 1
                continue

            self.mainText += text.PLAYING_GAME.value
            await bot.edit_message_text(chat_id=self.user.telegramId, text=self.mainText, message_id=editMessageId)

            await asyncio.sleep(random.uniform(30, 35))

            isClaimed, points = await blum.claimGame(gameId)

            if isClaimed == "internal":
                self.mainText += text.NOT_AVAILABLE_GAME_INTERNAL.value
                await bot.edit_message_text(chat_id=self.user.telegramId, text=self.mainText, message_id=editMessageId)
                playPasses -= 1
                continue
            elif not isClaimed:
                self.mainText += text.COULD_NOT_PLAY_GAMES.value
                await bot.edit_message_text(chat_id=self.user.telegramId, text=self.mainText, message_id=editMessageId)
                playPasses -= 1
                continue
            else:
                self.mainText += text.SUCCESSFULLY_PLAYED_GAMES.format(points=points)
                await bot.edit_message_text(chat_id=self.user.telegramId, text=self.mainText, message_id=editMessageId)

            tempPlayedGames += 1
            playPasses -= 1
            blumAccount.availablePlayPasses -= 1
            blumAccount.playedGames += 1
            if points is not None:
                blumAccount.earnedBlumCoins += points
            else:
                blumAccount.earnedBlumCoins += 245
            await self.account.save()
            await blumAccount.save()

    async def starter(self):
        retries = 0
        maxRetries = 2
        earnedBlumCoins = 0

        while retries < maxRetries:
            try:
                editMessage = await bot.send_message(self.user.telegramId, text.STARTED_FARMING.format(
                    sessionName=self.sessionName))
                editMessageId = editMessage.message_id
                proxy = None

                if self.account.proxyId is not None:
                    proxy = await Proxy.get(self.account.proxyId)
                    proxy = ProxyDetailScheme(**proxy.to_dict())

                blum = BlumBot(sessionName=self.sessionName, proxy=proxy)
                await blum.initWebSession()
                await blum.login()

                blumAccount = await BlumAccount.createOrGetByAccountId(self.account.id)
                subscription = await AccountSubscription.getByAccountId(accountId=self.account.id)
                balanceScheme = await blum.balance()

                if await blum.claimDailyReward():
                    earnedBlumCoins += random.randint(10, 100)
                    self.mainText += text.DAILY_REWARD_CLAIM.value
                else:
                    self.mainText += text.NO_DAILY_REWARD.value

                await bot.edit_message_text(chat_id=self.user.telegramId, text=self.mainText,
                                            message_id=editMessageId)

                friendBalance = await blum.friendBalance()
                if friendBalance.amountForClaim != 0 and friendBalance.canClaim:
                    earnedBlumCoins += 30
                    amount = await blum.friendClaim()
                    self.mainText += text.CLAIMED_FRIENDS_REWARD.format(amount=amount)

                else:
                    self.mainText += text.NO_REWARD_FRIENDS.value

                await bot.edit_message_text(text=self.mainText, chat_id=self.user.telegramId,
                                            message_id=editMessageId)

                if balanceScheme.farming is None:
                    self.mainText += text.FARMING_STARTED.value
                    await blum.start()
                elif balanceScheme.timestamp >= balanceScheme.farming.endTime:
                    await blum.claim()
                    self.mainText += text.TIMER_FARMING_CLAIMED.value
                    blumAccount.farmingFreezeHours = 8
                    earnedBlumCoins += 80
                elif balanceScheme.farming.endTime is not None and balanceScheme.timestamp is not None:
                    sleep_duration = balanceScheme.farming.endTime - balanceScheme.timestamp
                    blumAccount.farmingFreezeHours = self.formatDuration(sleep_duration)
                    self.mainText += text.IN_PROGRESS_FARMING.format(sleepDuration=self.formatDuration(sleep_duration))
                    await blum.refresh()

                self.account.lastUpdated = datetime.datetime.now()
                blumAccount.needRemind = True
                blumAccount.earnedBlumCoins += earnedBlumCoins
                await blumAccount.save()
                await self.account.save()
                await bot.edit_message_text(text=self.mainText, chat_id=self.user.telegramId,
                                            message_id=editMessageId)

                if blumAccount.availablePlayPasses > 0 and balanceScheme.allPlayPasses > 0:
                    await self.playGame(blumAccount.availablePlayPasses, blum=blum, editMessageId=editMessageId,
                                        blumAccount=blumAccount, subscription=subscription)
                else:
                    self.mainText += text.PLAYING_NOT_AVAILABLE.value
                    await bot.edit_message_text(text=self.mainText, chat_id=self.user.telegramId,
                                                message_id=editMessageId)

                balanceScheme = await blum.balance()
                blumAccount.availableBalance = float(balanceScheme.availableBalance)
                blumAccount.allPlayPasses = balanceScheme.allPlayPasses
                blumAccount.status = Status.ACTIVE
                blumAccount.earnedBlumCoins += earnedBlumCoins
                self.account.lastUpdated = datetime.datetime.now()
                await self.account.save()
                await blumAccount.save()

                self.mainText += text.FINISHED_FARM.format(availableBalance=balanceScheme.availableBalance,
                                                           playPasses=balanceScheme.allPlayPasses,
                                                           availablePlayPasses=blumAccount.availablePlayPasses)

                await bot.edit_message_text(text=self.mainText, chat_id=self.user.telegramId,
                                            message_id=editMessageId)

                if not ((subscription.isFreeTrial and blumAccount.playedGames < settings.ALLOWED_FREE_GAMES) or
                                 not subscription.isFreeTrial):
                    await bot.send_message(chat_id=self.user.telegramId, text=text.FORBIDDEN_TO_PLAY_GAMES.value)
                break

            except InvalidRequestException as e:
                logger.error(e.messageText)
                return await bot.send_message(self.user.telegramId, e.messageText)

            except httpx.TimeoutException as e:
                logger.error(f"Timeout error - {e._request}")
                logger.error(f"Attempt {retries + 1}/{maxRetries} failed: {e}")
                retries += 1

                await bot.send_message(self.user.telegramId, text.CONNECTION_TIMEOUT.format(retries=retries))

                if retries >= 2:
                    return await bot.send_message(self.user.telegramId, text.BLUM_NOT_WORKING.value)

                await asyncio.sleep(5)
            except pyrogram.errors.exceptions.unauthorized_401.SessionRevoked as e:
                logger.error(e)
                print(e)
                return await bot.send_message(self.user.telegramId,
                                              text.SOMETHING_WRONG_ON_BLUM.format(sessionName=self.sessionName))

            except Exception as e:
                logger.error(e)
                print(e)
                return await bot.send_message(self.user.telegramId,
                                       text.SOMETHING_WRONG_ON_BLUM.format(sessionName=self.sessionName))
