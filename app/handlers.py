import csv
import io
from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from sqlalchemy import select

from app.analytics import summarize_rounds
from app.config import get_settings
from app.db import SessionFactory
from app.keyboards import main_menu
from app.models import GameRound

router = Router(name="private-owner")
settings = get_settings()


def is_owner(user_id: int | None, chat_type: str | None) -> bool:
    return user_id == settings.owner_id and chat_type == "private"


async def deny(message: Message) -> None:
    if message.chat.type == "private":
        await message.answer("⛔ هذا البوت خاص وغير متاح لهذا الحساب.")


async def fetch_rounds(game: str | None = None) -> list[GameRound]:
    async with SessionFactory() as session:
        statement = select(GameRound).order_by(GameRound.recorded_at.desc())
        if game:
            statement = statement.where(GameRound.game == game)
        result = await session.execute(statement.limit(5000))
        return list(result.scalars().all())


async def add_record(message: Message, game: str, outcome: str, multiplier: float | None, notes: str | None) -> None:
    async with SessionFactory() as session:
        session.add(GameRound(game=game, outcome=outcome, multiplier=multiplier,
                              notes=notes[:500] if notes else None, source="manual", details={}))
        await session.commit()
    await message.answer(f"✅ تم حفظ نتيجة {game} بنجاح.")


@router.message(CommandStart())
async def start(message: Message) -> None:
    if not is_owner(message.from_user.id if message.from_user else None, message.chat.type):
        return await deny(message)
    await message.answer("مرحباً بك في Mini-Nations.\nلوحة خاصة لتسجيل وتحليل بيانات ألعاب Linebet.\n\nاختر لعبة أو افتح لوحة الإحصائيات.", reply_markup=main_menu())


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    if not is_owner(message.from_user.id if message.from_user else None, message.chat.type):
        return await deny(message)
    await message.answer(
        "الأوامر المتاحة:\n/dashboard — ملخص الإحصائيات\n"
        "/record_aviator &lt;multiplier&gt; &lt;win|loss&gt; [notes]\n"
        "/record_apple &lt;win|loss&gt; [notes]\n"
        "/stats_aviator — إحصائيات الطائرة\n/stats_apple — إحصائيات التفاحة\n"
        "/export — تصدير السجل CSV\n\n"
        "الإحصائيات تصف السجل السابق ولا تتنبأ بنتائج عشوائية."
    )


@router.message(Command("record_aviator"))
async def record_aviator(message: Message) -> None:
    if not is_owner(message.from_user.id if message.from_user else None, message.chat.type):
        return await deny(message)
    parts = (message.text or "").split(maxsplit=3)
    if len(parts) < 3:
        return await message.answer("الصيغة: /record_aviator 2.35 win ملاحظة اختيارية")
    try:
        multiplier = float(parts[1])
    except ValueError:
        return await message.answer("المضاعف يجب أن يكون رقماً مثل 2.35.")
    if not 0 < multiplier <= 1_000_000:
        return await message.answer("أدخل مضاعفاً أكبر من صفر وبحد أقصى 1,000,000.")
    outcome = parts[2].lower()
    if outcome not in {"win", "loss"}:
        return await message.answer("النتيجة يجب أن تكون win أو loss.")
    await add_record(message, "aviator", outcome, multiplier, parts[3] if len(parts) > 3 else None)


@router.message(Command("record_apple"))
async def record_apple(message: Message) -> None:
    if not is_owner(message.from_user.id if message.from_user else None, message.chat.type):
        return await deny(message)
    parts = (message.text or "").split(maxsplit=2)
    if len(parts) < 2 or parts[1].lower() not in {"win", "loss"}:
        return await message.answer("الصيغة: /record_apple win ملاحظة اختيارية")
    await add_record(message, "apple", parts[1].lower(), None, parts[2] if len(parts) > 2 else None)


async def stats_text(game: str | None = None) -> str:
    rows = await fetch_rounds(game)
    if not rows:
        return "لا توجد نتائج مسجلة بعد."
    summary = summarize_rounds(rows)
    title = game or "جميع الألعاب"
    fmt = lambda value: f"{value:.2f}x" if value is not None else "غير متاح"
    return (
        f"📊 إحصائيات {title}\n\nالجولات المسجلة: {summary.total}\n"
        f"الفوز: {summary.wins}\nالخسارة: {summary.losses}\n"
        f"نسبة الفوز المسجلة: {summary.win_rate:.1f}%\n"
        f"متوسط المضاعف: {fmt(summary.average_multiplier)}\n"
        f"الوسيط: {fmt(summary.median_multiplier)}\n"
        f"أعلى مضاعف مسجل: {fmt(summary.highest_multiplier)}\n\n"
        "هذه مؤشرات تاريخية وليست توقعاً للجولة التالية."
    )


@router.message(Command("dashboard"))
async def dashboard(message: Message) -> None:
    if not is_owner(message.from_user.id if message.from_user else None, message.chat.type):
        return await deny(message)
    await message.answer(await stats_text(), reply_markup=main_menu())


@router.message(Command("stats_aviator"))
async def aviator_stats(message: Message) -> None:
    if not is_owner(message.from_user.id if message.from_user else None, message.chat.type):
        return await deny(message)
    await message.answer(await stats_text("aviator"))


@router.message(Command("stats_apple"))
async def apple_stats(message: Message) -> None:
    if not is_owner(message.from_user.id if message.from_user else None, message.chat.type):
        return await deny(message)
    await message.answer(await stats_text("apple"))


@router.callback_query(F.data.startswith("game:"))
async def game_info(callback: CallbackQuery) -> None:
    if not is_owner(callback.from_user.id, callback.message.chat.type if callback.message else None):
        return await callback.answer("غير مصرح.", show_alert=True)
    game = callback.data.split(":", 1)[1]
    if game not in {"aviator", "apple"}:
        return await callback.answer("لعبة غير معروفة.", show_alert=True)
    if callback.message:
        await callback.message.answer(await stats_text(game))
    await callback.answer()


@router.callback_query(F.data == "dashboard")
async def dashboard_callback(callback: CallbackQuery) -> None:
    if not is_owner(callback.from_user.id, callback.message.chat.type if callback.message else None):
        return await callback.answer("غير مصرح.", show_alert=True)
    if callback.message:
        await callback.message.answer(await stats_text(), reply_markup=main_menu())
    await callback.answer()


async def build_export_file() -> BufferedInputFile:
    rows = await fetch_rounds()
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "game", "outcome", "multiplier", "notes", "source", "recorded_at"])
    for row in reversed(rows):
        writer.writerow([row.id, row.game, row.outcome, row.multiplier, row.notes, row.source, row.recorded_at.isoformat()])
    return BufferedInputFile(buffer.getvalue().encode("utf-8-sig"),
                             filename=f"mini-nations-rounds-{datetime.now(timezone.utc):%Y%m%d}.csv")


@router.message(Command("export"))
async def export_command(message: Message) -> None:
    if not is_owner(message.from_user.id if message.from_user else None, message.chat.type):
        return await deny(message)
    await message.answer_document(await build_export_file(), caption="سجل النتائج")


@router.callback_query(F.data == "export")
async def export_callback(callback: CallbackQuery) -> None:
    if not is_owner(callback.from_user.id, callback.message.chat.type if callback.message else None):
        return await callback.answer("غير مصرح.", show_alert=True)
    if callback.message:
        await callback.message.answer_document(await build_export_file(), caption="سجل النتائج")
    await callback.answer("تم تجهيز الملف.")
