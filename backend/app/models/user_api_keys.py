"""
User API Keys Model

Stores encrypted API credentials for external exchanges (KIS, Upbit, etc.)
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, UniqueConstraint
from sqlmodel import Field, SQLModel


class UserApiKeyBase(SQLModel):
    # 거래소 유형 ('KIS', 'UPBIT' 등)
    exchange_type: str = Field(max_length=20, nullable=False)

    # 암호화된 API 키 (평문 저장 금지)
    # 주의: 실제 저장 시 암호화 필수!
    encrypted_api_key: str = Field(max_length=1000, nullable=False)

    # 암호화된 API 시크릿 (평문 저장 금지)
    # 주의: 실제 저장 시 암호화 필수!
    encrypted_api_secret: str = Field(max_length=1000, nullable=False)

    # 계좌번호 (한국투자증권 등에서 필요)
    # 선택 사항이며, 필요한 경우 암호화 권장
    account_number: str | None = Field(default=None, max_length=100)

    # 모의투자 여부 (실전/모의 구분)
    is_demo: bool = Field(default=False)

    # 활성화 여부 (비활성화 시 해당 키 사용 불가)
    is_active: bool = Field(default=True)

    # 키 설명 또는 별칭 (사용자가 여러 키를 구분하기 위함)
    nickname: str | None = Field(default=None, max_length=100)


class UserApiKeyCreate(UserApiKeyBase):
    # API 생성 시 평문 키를 받지만, 저장 전 암호화 필요
    pass


class UserApiKeyUpdate(SQLModel):
    exchange_type: str | None = Field(default=None, max_length=20)
    encrypted_api_key: str | None = Field(default=None, max_length=1000)
    encrypted_api_secret: str | None = Field(default=None, max_length=1000)
    account_number: str | None = Field(default=None, max_length=100)
    is_demo: bool | None = None
    is_active: bool | None = None
    nickname: str | None = Field(default=None, max_length=100)


class UserApiKey(UserApiKeyBase, table=True):
    # 복합 유니크 제약: 동일 유저는 거래소당 하나의 실전/모의 키만 가능
    # (단, is_active=false인 키는 여러 개 가능)
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "exchange_type",
            "is_demo",
            "is_active",
            name="uq_user_exchange_demo_active",
        ),
    )

    # 프라이머리 키
    id: int | None = Field(default=None, primary_key=True)

    # 외래 키: users 테이블 참조 (CASCADE 삭제)
    # 사용자 삭제 시 해당 사용자의 모든 API 키도 삭제됨
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )

    # 생성 일시
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )

    # 수정 일시
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )


class UserApiKeyPublic(SQLModel):
    """
    API 응답용 모델 (민감한 정보 제외)

    주의: 암호화된 키/시크릿은 절대 클라이언트에 노출하지 않음
    """

    id: int
    user_id: uuid.UUID
    exchange_type: str
    account_number: str | None
    is_demo: bool
    is_active: bool
    nickname: str | None
    created_at: datetime
    updated_at: datetime
    # encrypted_api_key와 encrypted_api_secret은 의도적으로 제외


class UserApiKeysPublic(SQLModel):
    data: list[UserApiKeyPublic]
    count: int
