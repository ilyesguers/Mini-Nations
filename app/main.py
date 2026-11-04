import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from sqlalchemy import text

from app.config import get_settings
from app.db import SessionFactory, close_database
from app.handlers import router

settings = get_settings()
logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    bot = Bot(
        token=settings.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    try:
        async with SessionFactory() as session:
            await session.execute(text("SELECT 1"))

        await bot.set_my_commands([
            BotCommand(command="start", description="فتح القائمة الرئيسية"),
            BotCommand(command="help", description="عرض المساعدة والأوامر"),
            BotCommand(command="dashboard", description="ملخص الإحصائيات"),
            BotCommand(command="stats_aviator", description="إحصائيات Aviator"),
            BotCommand(command="stats_apple", description="إحصائيات Apple"),
            BotCommand(command="export", description="تصدير سجل النتائج"),
        ])
        logger.info("Database connection verified. Starting private bot polling.")
        await dispatcher.start_polling(
            bot,
            allowed_updates=dispatcher.resolve_used_update_types(),
            close_bot_session=False,
        )
    finally:
        await bot.session.close()
        await close_database()
