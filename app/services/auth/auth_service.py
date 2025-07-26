from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.uow  import UnitOfWork
from app.core.auth.password import hash_password, verify_password
from app.core.auth.jwt import create_access_token
from app.infra.repo.user_repository import UserRepository
from app.infra.repo.refresh_token_repository import RefreshTokenRepository
from app.core.exceptions.auth.invalid_token import InvalidTokenException
from app.core.exceptions.auth.invalid_credentials import InvalidCredentialsException
from app.core.exceptions.common.bad_request import BadRequestException  # assume exists


class AuthService:
    """Registration, login, refresh token logic."""

    def __init__(self):
        self._user_repo = UserRepository()
        self._rt_repo = RefreshTokenRepository()

    async def register(self, db: AsyncSession, *, name: str, email: str, password: str):
        if await self._user_repo.exists_by_email(db, email):  # assume helper exists
            raise BadRequestException(message="Email already registered")
        user = await self._user_repo.create(
            db,
            {
                "name": name,
                "email": email,
                "password": hash_password(password),
            },
        )
        return user

    async def login(self, db: AsyncSession, email: str, password: str):
        user = await self._user_repo.get_by_email(db, email)  # assume helper exists
        if user is None or not verify_password(password, user.password):
            raise InvalidCredentialsException()

        access_token = create_access_token(user.id)
        rt = self._rt_repo.model.create_token(user.id)
        await self._rt_repo.create(db, rt.__dict__)
        return access_token, rt.token

    async def refresh(self, db: AsyncSession, *, refresh_token: str):
        rt = await self._rt_repo.get_by_token(db, refresh_token)  # assume helper
        if rt is None or rt.revoked:
            raise InvalidTokenException()
        from datetime import datetime, timezone

        if rt.expires_at < datetime.now(timezone.utc):
            raise InvalidTokenException()

        access_token = create_access_token(rt.user_id)
        return access_token 