"""Discord webhook receiver endpoint.

Discord sends webhook payloads when messages are posted in a channel.
This module validates and extracts the message content.
"""

from __future__ import annotations

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional

from config import config

router = APIRouter(prefix="/webhook/discord", tags=["discord"])


class DiscordEmbed(BaseModel):
    description: Optional[str] = None
    title: Optional[str] = None


class DiscordPayload(BaseModel):
    content: Optional[str] = None
    username: Optional[str] = None
    embeds: Optional[list[DiscordEmbed]] = None


@router.post("")
async def receive_discord_webhook(payload: DiscordPayload, request: Request):
    """Receive a Discord webhook payload and extract the message text.

    Returns the extracted message for processing by the signal pipeline.
    Discord channel webhooks send the message content directly.
    For Discord bot integrations, the payload may include embeds.
    """
    # Verify webhook secret if configured
    if config.WEBHOOK_SECRET:
        auth = request.headers.get("Authorization", "")
        if auth != f"Bearer {config.WEBHOOK_SECRET}":
            raise HTTPException(status_code=401, detail="Invalid webhook secret")

    # Extract message from content or embeds
    message = payload.content or ""

    if not message and payload.embeds:
        # Some bots put signals in embed descriptions
        for embed in payload.embeds:
            if embed.description:
                message = embed.description
                break
            if embed.title:
                message = embed.title
                break

    if not message:
        return {"status": "skipped", "reason": "no message content"}

    return {
        "status": "received",
        "source": "discord",
        "username": payload.username,
        "message": message,
    }
