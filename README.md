# Telegram Bot Search Safe

A secure Telegram bot built with python-telegram-bot that exposes only a safe, allowlisted public search flow. It reads the bot token and admin IDs from environment variables, stores search history in SQLite using parameterized queries, and blocks unauthorized personal-data searches.

## Features

- /start and /help commands
- Inline keyboard with Search, Archive, and Help buttons
- Search for public or explicitly authorized sources only
- SQLite-backed search history for each user
- Admin-only /admin command with basic usage statistics
- Sensitive-data protections for passwords, private phone records, private messages, and other restricted content
- Replit-friendly configuration and startup

## Requirements

- Python 3.11+
- Telegram bot token
- Admin Telegram user IDs in ADMIN_IDS

## Environment variables

Set these in your shell, Replit Secrets, or your hosting environment:

- BOT_TOKEN=your_bot_token_here
- ADMIN_IDS=123456789,987654321

Optional:

- BOT_DB_PATH=data/search_history.db

## Local development

1. Clone the repository.
2. Create a virtual environment:
   python -m venv .venv
   source .venv/bin/activate
3. Install dependencies:
   pip install -r requirements.txt
4. Export the environment variables:
   export BOT_TOKEN="your_token"
   export ADMIN_IDS="123456789,987654321"
5. Start the bot:
   python main.py

## Replit setup

1. Open your Replit project.
2. In the Secrets panel, add:
   - BOT_TOKEN
   - ADMIN_IDS
3. Keep the Python version at 3.11+.
4. Create a `main.py` entrypoint or use the provided one.
5. Run the project with the console command:
   python main.py
6. Use the Replit "Always On" or a proper process manager if needed for continuous uptime.

## Security notes

- Only the bot token is read from the environment variable.
- The bot does not accept arbitrary private-source searches.
- The bot blocks searches involving leaked passwords, phone records, private message content, or other sensitive personal data unless an explicit authorization model is added and enforced separately.
- Use a dedicated bot account and restrict admin access to trusted IDs only.

## Project structure

- app/config.py - environment configuration and validation
- app/database.py - SQLite schema and parameterized queries
- app/search_service.py - search validation and public-source lookups
- app/handlers.py - Telegram command handlers and UI
- app/bot.py - application builder and startup
- main.py - entry point

## License

This project is provided as a starter example and may be used as a base for internal or authorized chatbot deployments.
