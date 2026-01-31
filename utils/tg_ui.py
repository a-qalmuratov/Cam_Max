"""
Telegram UI helpers for consistent premium-looking messages.

✅ What this gives you
- One function to SEND or EDIT a message
- Supports Telegram HTML parse_mode
- Safe escaping handled by premium_ui (if you use html=True)
- Optional: auto-disable web page preview

⚠️ Adapted for python-telegram-bot library
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Any

from telegram import Update, Message
from telegram.constants import ParseMode

# Import premium_ui from utils directory
from utils.premium_ui import premium_ui


@dataclass
class TgUI:
    """
    Minimal helper layer so every handler stays clean:
        await ui.send_or_edit(message, text, reply_markup=kb)
    """

    parse_mode: str = ParseMode.HTML
    disable_preview: bool = True

    async def send_or_edit(
        self,
        message: Message,
        text: str,
        *,
        reply_markup=None,
        edit: bool = True,
        disable_web_page_preview: Optional[bool] = None,
        **kwargs: Any,
    ) -> Message:
        """
        If edit=True -> tries to edit current message, if fails -> sends new message.
        """
        if disable_web_page_preview is None:
            disable_web_page_preview = self.disable_preview

        # Try edit first
        if edit:
            try:
                return await message.edit_text(
                    text,
                    parse_mode=self.parse_mode,
                    reply_markup=reply_markup,
                    disable_web_page_preview=disable_web_page_preview,
                    **kwargs,
                )
            except Exception:
                # Most common reasons:
                # - message is not editable (too old)
                # - content not modified
                # - message is not from bot
                pass

        # Send new
        return await message.reply_text(
            text,
            parse_mode=self.parse_mode,
            reply_markup=reply_markup,
            disable_web_page_preview=disable_web_page_preview,
            **kwargs,
        )

    # -----------------------
    # Convenience wrappers
    # -----------------------
    async def show_header(
        self,
        message: Message,
        title: str,
        subtitle: Optional[str] = None,
        *,
        icon: str = "logo",
        edit: bool = True,
        reply_markup=None,
    ) -> Message:
        text = premium_ui.header(
            title,
            subtitle,
            icon=icon,
            html=True,
            monospace=True,
        )
        return await self.send_or_edit(message, text, edit=edit, reply_markup=reply_markup)

    async def show_card(
        self,
        message: Message,
        title: str,
        content: str,
        footer: Optional[str] = None,
        *,
        title_icon: Optional[str] = None,
        edit: bool = True,
        reply_markup=None,
    ) -> Message:
        text = premium_ui.card(
            title=title,
            content=content,
            footer=footer,
            title_icon=title_icon,
            html=True,
            monospace=True,
        )
        return await self.send_or_edit(message, text, edit=edit, reply_markup=reply_markup)

    async def show_error(
        self,
        message: Message,
        title: str,
        details: str,
        *,
        edit: bool = True,
        reply_markup=None,
    ) -> Message:
        content = "\n".join([
            premium_ui.badge("ERROR", "warn"),
            details,
        ])
        text = premium_ui.card(
            title=title,
            content=content,
            footer="Try again or contact support",
            title_icon="warning",
            html=True,
            monospace=True,
        )
        return await self.send_or_edit(message, text, edit=edit, reply_markup=reply_markup)

    async def show_success(
        self,
        message: Message,
        title: str,
        details: str,
        *,
        edit: bool = True,
        reply_markup=None,
    ) -> Message:
        content = "\n".join([
            premium_ui.badge("SUCCESS", "verified"),
            details,
        ])
        text = premium_ui.card(
            title=title,
            content=content,
            footer="✅ Completed",
            title_icon="success",
            html=True,
            monospace=True,
        )
        return await self.send_or_edit(message, text, edit=edit, reply_markup=reply_markup)


# Export instance
ui = TgUI()
