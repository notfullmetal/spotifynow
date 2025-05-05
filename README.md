# Spotipie

A Telegram bot for sharing your currently playing Spotify song with friends.

## Features

- Share your currently playing Spotify song with friends
- Customize your display name and background style
- LastFM integration for sharing LastFM songs
- Inline query support for easy sharing

## Setup

### Prerequisites

- Python 3.7+
- PostgreSQL database
- Telegram Bot API key
- Spotify Developer credentials

### Environment Variables

Create a `.env` file with the following variables:

```
API_KEY=your_telegram_bot_token
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
TEMP_CHANNEL=your_temp_channel_id
REDIRECT_URI=your_cloudflare_worker_url
JSON_BLOB_ID=your_json_blob_id

# PostgreSQL Configuration
POSTGRES_USER=postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=spotipie
```

### Installation

#### Option 1: Local Installation

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your PostgreSQL database
4. Run the bot: `python -m sp_bot`

#### Option 2: Docker Compose (Recommended)

1. Clone this repository
2. Create a `.env` file with the required variables
3. Run with Docker Compose:

```bash
docker-compose up -d
```

This will start both the PostgreSQL database and the Spotipie bot in containers. The database data will be persisted in a named volume.

To check the logs:

```bash
docker-compose logs -f
```

To stop the services:

```bash
docker-compose down
```

## Authentication Flow

This bot uses a Cloudflare Worker for authentication. The flow works as follows:

1. User triggers `/register` in the bot
2. Bot provides a link to Spotify authorization
3. User authenticates with Spotify
4. Spotify redirects to the Cloudflare Worker with an auth code
5. The Worker stores the code in a JSON blob and redirects to Telegram with a key
6. The bot fetches the full auth code from the JSON blob using the key
7. The bot exchanges the auth code for a refresh token with Spotify
8. The bot stores the refresh token for future API calls

## Cloudflare Worker Setup

To set up the Cloudflare Worker:

1. Create a new Worker on Cloudflare
2. Create a JSON Blob at https://jsonblob.com/ and note the ID in the URL
3. Use the provided code (replace YOUR_JSON_BLOB_ID with your actual ID):

```javascript
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)
  const code = url.searchParams.get('code')
  const jsonBlobId = 'YOUR_JSON_BLOB_ID'  // Replace with your JSON Blob ID

  if (!code) {
    return new Response('Hey! This is SpotifyNow\'s authentication server.', { status: 400 })
  }

  const key = code.slice(-4)
  const redirectURL = `http://t.me/fullmetaltestbot/?start=${key}`

  await fetch(`https://jsonblob.com/api/${jsonBlobId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ [key]: code }),
  })

  return Response.redirect(redirectURL, 302)
}
```

4. Set the Worker URL as your `REDIRECT_URI` in the .env file
5. Set the JSON Blob ID as your `JSON_BLOB_ID` in the .env file

## Database Configuration

This bot uses PostgreSQL as the database. The tables are created automatically when the bot starts.

When using Docker Compose, the PostgreSQL database is automatically set up and configured.

## Commands

- `/now` - Share currently playing song
- `/name` - Change your display name
- `/register` - Connect your Spotify account
- `/unregister` - Disconnect your Spotify account
- `/style` - Change background style
- `/last` - Share LastFM song
- `/linkfm` - Connect LastFM account
- `/namefm` - Set LastFM display name
- `/unlinkfm` - Disconnect LastFM account
- `/status` - Show recently played song via LastFM