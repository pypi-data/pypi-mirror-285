import abc
import typing

import pylogram.errors
import telethon.errors

from ks_session_manager.errors import ConverterSessionUnauthorizedYetError
from ks_session_manager.types import SessionUserInfo
from .pylogram import PylogramClient
from .telethon import TelethonClient
from ..errors import ConverterSessionUnauthorized


class BaseTelegramAdapter(abc.ABC):
    @property
    @abc.abstractmethod
    def is_connected(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_user_info(self) -> SessionUserInfo:
        raise NotImplementedError

    @abc.abstractmethod
    async def start(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def stop(self):
        raise NotImplementedError

    async def __aenter__(self) -> typing.Self:
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self.stop()
        except Exception:
            pass

        if exc_val:
            raise exc_val


class TelethonTelegramAdapter(BaseTelegramAdapter):
    def __init__(self, client: TelethonClient):
        self.client = client

    @property
    def is_connected(self) -> bool:
        return self.client.is_connected()

    async def get_user_info(self) -> SessionUserInfo:
        if not self.is_connected:
            raise RuntimeError('Client is not connected')

        me = await self.client.get_me()

        if me is None:
            raise ConverterSessionUnauthorizedYetError

        return SessionUserInfo(
            id=self.client.me.id,
            first_name=self.client.me.first_name,
            last_name=self.client.me.last_name,
            username=self.client.me.username,
            phone_number=self.client.me.phone,
            is_premium=self.client.me.premium,
        )

    async def start(self):
        # noinspection PyUnresolvedReferences
        await self.client.connect()

    async def stop(self):
        await self.client.disconnect()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self.stop()
        except Exception:
            pass

        if isinstance(exc_val, (telethon.errors.UnauthorizedError, telethon.errors.AuthKeyError)):
            raise ConverterSessionUnauthorized(str(exc_val), original_exception=exc_val) from exc_val


class PylogramTelegramAdapter(BaseTelegramAdapter):
    def __init__(self, client: PylogramClient):
        self.client = client

    @property
    def is_connected(self) -> bool:
        return self.client.is_connected

    async def get_user_info(self) -> SessionUserInfo:
        if not self.is_connected:
            raise RuntimeError('Client is not connected')

        return SessionUserInfo(
            id=self.client.me.id,
            first_name=self.client.me.first_name,
            last_name=self.client.me.last_name,
            username=self.client.me.username,
            phone_number=self.client.me.phone_number,
            is_premium=self.client.me.is_premium,
        )

    async def start(self):
        try:
            await self.client.start(authorize=False)
        except RuntimeError as e:
            raise ConverterSessionUnauthorizedYetError from e

    async def stop(self):
        await self.client.stop()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self.stop()
        except Exception:
            pass

        if isinstance(exc_val, (pylogram.errors.Unauthorized, pylogram.errors.AuthKeyDuplicated)):
            raise ConverterSessionUnauthorized(str(exc_val), original_exception=exc_val) from exc_val
