import re
from datetime import datetime, timedelta, timezone

from telegram import Update
from telegram.ext import ContextTypes, Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from app.config import ADMIN_IDS, BOT_TOKEN
from app.database import get_recent_searches, get_usage_stats, init_db, log_search
from app.search_service import search_public_sources, validate_search_query
from app.handlers import help_command, main_menu, start, handle_button


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["searching"] = True
    await update.effective_message.reply_text("Send a search query. Public or explicitly authorized sources only.")


async def archive_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    rows = get_recent_searches(update.effective_user.id, limit=10)
    if not rows:
        await update.effective_message.reply_text("Your archive is empty.")
        return

    lines = ["Your recent searches:"]
    for index, (search_text, source, created_at) in enumerate(rows, 1):
        lines.append(f"{index}. {search_text} [{source}]")
    await update.effective_message.reply_text("\n".join(lines)[:4000])


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        await update.effective_message.reply_text("Access denied: admin privileges required.")
        return

    stats = get_usage_stats()
    message = (
        "Admin usage statistics:\n"
        f"Total searches: {stats['total_searches']}\n"
        f"Unique users: {stats['unique_users']}\n"
        f"Searches in last 24h: {stats['recent_24h']}"
    )
    await update.effective_message.reply_text(message)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.user_data.get("searching"):
        await update.effective_message.reply_text("Use /search or the Search button to begin a safe public search.")
        return

    raw_query = update.effective_message.text
    try:
        query = validate_search_query(raw_query)
    except ValueError as exc:
        await update.effective_message.reply_text(f"Search rejected: {exc}")
        context.user_data["searching"] = False
        return

    context.user_data["searching"] = False
    status_message = await update.effective_message.reply_text("Searching approved public sources...")

    try:
        result = search_public_sources(query)
    except requests.RequestException:
        await status_message.edit_text("The search provider is temporarily unavailable. Please try again later.")
        return
    except ValueError as exc:
        await status_message.edit_text(f"Search rejected: {exc}")
        return
    except Exception:
        await status_message.edit_text("An unexpected error occurred while searching. Please try again.")
        return

    if not result or not result.get("items"):
        await status_message.edit_text("No public results were found for that safe search request.")
        return

    source_name = result["source"]
    log_search(update.effective_user.id, query, source_name)

    for item in result["items"]:
        title = item["title"]
        url = item["url"]
        snippet = item["snippet"]
        text = f"{title}\n\n{snippet}\n\n{url}"
        await update.effective_message.reply_text(text[:4000], disable_web_page_preview=True)

    await status_message.delete()


def setup_handlers(application: Application) -> None:
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("archive", archive_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CallbackQueryHandler(handle_button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
