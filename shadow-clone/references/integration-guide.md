# Integration Guide

## Discord Webhook Setup

### Option A: Channel Webhook (Simplest)

1. Open Discord channel settings (gear icon)
2. Go to Integrations, then Webhooks
3. Click "New Webhook"
4. Set the webhook URL to: `http://YOUR_SERVER:8000/webhook/discord`
5. Note: Channel webhooks forward all messages to the URL

### Option B: Discord Bot (More Control)

1. Create a bot at https://discord.com/developers/applications
2. Enable "Message Content Intent" in bot settings
3. Add bot to your server with Read Messages permission
4. Use a listener script that forwards messages to the Shadow Clone server:

```python
import discord
import httpx

client = discord.Client(intents=discord.Intents.default() | discord.Intents(message_content=True))
SIGNAL_CHANNEL_ID = 123456789  # Your signal channel
SHADOW_CLONE_URL = "http://localhost:8000/process"

@client.event
async def on_message(message):
    if message.channel.id == SIGNAL_CHANNEL_ID and not message.author.bot:
        async with httpx.AsyncClient() as http:
            await http.post(SHADOW_CLONE_URL, json={
                "source": "discord",
                "message": message.content,
                "username": str(message.author),
            })

client.run("YOUR_BOT_TOKEN")
```

## Telegram Bot Setup

1. Create a bot via @BotFather on Telegram
2. Get the bot token
3. Set the webhook URL:

```bash
curl -X POST "https://api.telegram.org/botYOUR_TOKEN/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://YOUR_PUBLIC_URL/webhook/telegram", "secret_token": "YOUR_WEBHOOK_SECRET"}'
```

4. Add the bot to the signal group (it needs to read messages)
5. For channels: add bot as admin with "Post Messages" permission

## Exposing the Server Publicly

The server runs locally. To receive webhooks from Discord/Telegram, expose it:

### localtunnel (Free, Quick)

```bash
npx localtunnel --port 8000
# Output: your url is: https://random-name.loca.lt
```

### ngrok (Free Tier Available)

```bash
ngrok http 8000
# Output: Forwarding https://abc123.ngrok.io -> http://localhost:8000
```

### Cloudflare Tunnel (Production)

```bash
cloudflared tunnel --url http://localhost:8000
```

Use the generated public URL as your webhook endpoint.

## Alpaca Paper Trading Setup

1. Sign up at https://alpaca.markets (free paper trading account)
2. Generate API keys from the dashboard
3. Add to `.env`:

```
EXECUTION_MODE=alpaca
ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_secret_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

4. Restart the server. Orders will route to Alpaca paper trading.

## Testing the Full Pipeline

### 1. Start the server

```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Send test signals

```bash
# Standard format
curl -X POST http://localhost:8000/test \
  -H "Content-Type: application/json" \
  -d '{"message": "BUY NVDA 170.00 SL 168.00 TP 175.00"}'

# Emoji format
curl -X POST http://localhost:8000/test \
  -H "Content-Type: application/json" \
  -d '{"message": "TSLA 🟢 Buy @ 245.50 | SL: 243.00 | TP: 250.00"}'

# Options shorthand
curl -X POST http://localhost:8000/test \
  -H "Content-Type: application/json" \
  -d '{"message": "$SPY calls 520"}'
```

### 3. Check results

```bash
# List recent signals
curl http://localhost:8000/signals

# Check positions
curl http://localhost:8000/positions

# Health check
curl http://localhost:8000/health
```
