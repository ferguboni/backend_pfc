#Pydantic vai validar dados de entrada/saída nas rotas

# Auth
from typing import Optional, Any
from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator,Field
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class UserOut(BaseModel):
    id: str
    email: EmailStr
    name: Optional[str] = None

    # Permite preencher a partir de objetos ORM
    model_config = ConfigDict(from_attributes=True)

    # Converte UUID (ou qualquer coisa) para string ANTES de validar
    @field_validator("id", mode="before")
    @classmethod
    def _id_to_str(cls, v: Any) -> str:
        return str(v)

class TokenOut(BaseModel):
    access_token: str

# Favorites
class FavoriteIn(BaseModel):
    coin_id: str

class FavoriteOut(BaseModel):
    id: UUID
    coin_id: str
    user_id: UUID
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

# Newsletter
class NewsletterSubscribeIn(BaseModel):
    email: EmailStr

class NewsletterSubscribeOut(BaseModel):
    id: str
    email: EmailStr

    class Config:
        from_attributes = True

# Prices / News
class PriceQuery(BaseModel):
    vs_currency: str = "usd"
    per_page: int = 10

class NewsItem(BaseModel):
    title: str
    link: str
    source: str
    image: str | None = None
    published_at: Optional[str] = None

class UserListItem(BaseModel):
    name: str | None
    email: EmailStr

class ForgotPasswordIn(BaseModel):
    email: EmailStr

class ResetPasswordIn(BaseModel):
    token: str = Field(min_length=10)
    new_password: str = Field(min_length=8, max_length=128)


