from __future__ import annotations

from typing import Optional
from datetime import datetime,timezone
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.uow  import UnitOfWork
from app.core.auth.password import hash_password, verify_password
from app.core.auth.jwt import create_access_token
from app.infra.repo.user_repository import UserRepository
from app.infra.repo.refresh_token_repository import RefreshTokenRepository
from app.core.exceptions.auth.invalid_token import InvalidTokenException
from app.core.exceptions.auth.invalid_credentials import InvalidCredentialsException
from app.core.exceptions.common.bad_request import BadRequestException  # assume exists


import os

DOMAIN = os.getenv("DOMAIN", 'local')

class AuthService:
    """Registration, login, refresh token logic."""

    def __init__(self, db=None):
        # 如果直接提供了db则使用它，否则在每个方法中使用传入的db
        self._db = db
        # 我们将在使用的时候初始化repositories
        self._user_repo = None
        self._rt_repo = None

    def _init_repos(self, db):
        # 延迟初始化repositories
        if self._user_repo is None:
            self._user_repo = UserRepository(db=db)
        if self._rt_repo is None:
            self._rt_repo = RefreshTokenRepository(db=db)

    async def register(self, db: AsyncSession, *, name: str, email: str, password: str):
        self._init_repos(db)
        if await self._user_repo.exists_by_email(email):  # 移除db参数
            raise BadRequestException(message="Email already registered")
        user = await self._user_repo.create(
            {
                "name": name,
                "email": email,
                "password": hash_password(password),
            },
        )
        return user
    
    async def guest(self, db: AsyncSession):
        self._init_repos(db)
        new_uuid = str(uuid.uuid4()).lower()
        user = await self._user_repo.create(
            {
                "name": f"Guest {new_uuid}",
                "email": f"guest.{new_uuid}@{DOMAIN}.com",
                "password": hash_password(new_uuid),
            },
        )
        assess_token = create_access_token(user.id)
        rt_data = self._rt_repo.model.create_token(user.id)
        # rt_data已经是一个字典，不需要再调用__dict__
        await self._rt_repo.create(rt_data)
        return assess_token, rt_data["token"]

    async def login(self, db: AsyncSession, email: str, password: str):
        self._init_repos(db)
        user = await self._user_repo.get_by_email(email)  # 移除db参数
        if user is None or not verify_password(password, user.password):
            raise InvalidCredentialsException()

        access_token = create_access_token(user.id)
        rt_data = self._rt_repo.model.create_token(user.id)
        # rt_data已经是一个字典，不需要再调用__dict__
        await self._rt_repo.create(rt_data)
        return access_token, rt_data["token"]

    async def refresh(self, db: AsyncSession, *, refresh_token: str):
        self._init_repos(db)
        rt = await self._rt_repo.get_by_token(refresh_token)  # 移除db参数
        if rt is None or rt.revoked:
            raise InvalidTokenException()

        # 使用不带时区的datetime进行比较
        if rt.expires_at < datetime.now():
            raise InvalidTokenException()

        access_token = create_access_token(rt.user_id)
        return access_token 