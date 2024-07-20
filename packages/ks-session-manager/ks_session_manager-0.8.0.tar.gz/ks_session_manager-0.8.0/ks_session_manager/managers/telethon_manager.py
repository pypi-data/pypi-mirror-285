from __future__ import annotations

from typing import Any

import telethon.sessions
import telethon.types
from telethon import crypto as telethon_crypto

from ks_session_manager.managers.base_manager import BaseSessionFileManager
from ks_session_manager.types import SessionData
from ks_session_manager.utils.parsers import parse_none_if_null_str


class TelethonSessionFileManager(BaseSessionFileManager):
    @property
    def session_file_extension(self) -> str:
        return telethon.sessions.sqlite.EXTENSION

    def _get_file_storage(self, *, exists: bool = False) -> telethon.sessions.SQLiteSession:
        if not exists and self.session_path.exists():
            raise FileExistsError(f"Session storage is already exists in {self.session_path}")

        if exists and not self.session_path.exists():
            raise FileNotFoundError(f"Session storage not found in {self.session_path}")

        if self.session_path.is_dir():
            raise IsADirectoryError(f"Session file path {self.session_path} points to a directory")

        return telethon.sessions.SQLiteSession(str(self.session_path))

    async def read_session_storage(self) -> SessionData:
        session = self._get_file_storage(exists=True)
        # Telethon feature to save current user id in entities
        self_entity = session.get_entity_rows_by_id(0)

        return SessionData(
            dc_id=session.dc_id,
            user_id=self_entity[1] if bool(self_entity) else None,
            auth_key=session.auth_key.key,
            server_address=parse_none_if_null_str(session.server_address),
            server_port=session.port,
            takeout_id=parse_none_if_null_str(session.takeout_id),
        )

    async def write_session_storage(
            self,
            data: SessionData,
            *,
            in_memory: bool = False,
            exist_ok: bool = False
    ) -> Any:
        if not bool(data.user_id):
            raise ValueError("user_id must be set in session data")

        if in_memory:
            storage = telethon.sessions.MemorySession()
        else:
            try:
                storage = self._get_file_storage(exists=False)
            except FileExistsError:
                if exist_ok:
                    return self._get_file_storage(exists=True)

                raise

        storage.set_dc(data.dc_id, data.server_address, data.server_port)
        storage.auth_key = telethon_crypto.AuthKey(data.auth_key)
        storage.takeout_id = data.takeout_id
        # noinspection PyTypeChecker
        current_user_entity = telethon.types.contacts.ResolvedPeer(
            None,
            [telethon.types.InputPeerUser(0, data.user_id)],
            []
        )
        storage.process_entities(current_user_entity)
        storage.save()
        storage.close()
        return storage
