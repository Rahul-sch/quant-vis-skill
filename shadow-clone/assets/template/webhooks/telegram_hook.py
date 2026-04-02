"""Telegram webhook receiver endpoint.

Receives Telegram Bot API webhook updates and extracts message text.
"""

from __future__ import annotations

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional

from config import config

router = APIRouter(prefix="/webhook/telegram", tags=["telegram"])


class TelegramUser(BaseModel):
    id: int
    first_name: Optional[str] = None
    username: Optional[str] = None


class TelegramChat(BaseModel):
    id: int
    type: str
    title: Optional[str] = None


class TelegramMessage(BaseModel):
    message_id: int
    text: Optional[str] = None
    caption: Optional[str] = None
    chat: Optional[TelegramChat] = None
    from_user: Optional[TelegramUser] = None

    model_config = {"populate_by_name": True}  # Pydantic v2


class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[TelegramMessage] = None
    channel_post: Optional[TelegramMessage] = None


@router.post("")
async def receive_telegram_webhook(update: TelegramUpdate, request: Request):
    """Receive a Telegram Bot API webhook update.

    Handles both private messages and channel posts.
    """
    # Verify secret token if configured
    if config.WEBHOOK_SECRET:
        token = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if token != config.WEBHOOK_SECRET:
            raise HTTPException(status_code=401, detail="Invalid secret token")

    # Extract message from either direct message or channel post
    msg = update.message or update.channel_post
    if not msg:
        return {"status": "skipped", "reason": "no message in update"}

    text = msg.text or msg.caption or ""
    if not text:
        return {"status": "skipped", "reason": "no text content"}

    username = None
    if msg.from_user:
        username = msg.from_user.username or msg.from_user.first_name

    return {
        "status": "received",
        "source": "telegram",
        "username": username,
        "chat_id": msg.chat.id if msg.chat else None,
        "message": text,
    }
