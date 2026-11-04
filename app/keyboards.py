from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✈️ Aviator", callback_data="game:aviator"), InlineKeyboardButton(text="🍎 Apple", callback_data="game:apple")],
        [InlineKeyboardButton(text="📊 Dashboard", callback_data="dashboard"), InlineKeyboardButton(text="📁 Export CSV", callback_data="export")],
    ])
