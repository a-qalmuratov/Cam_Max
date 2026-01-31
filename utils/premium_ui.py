"""
Premium UI utility functions for ultra-polished Telegram bot experience.

✅ Features
- Dynamic width boxes (no broken borders)
- Auto wrapping (long lines won't overflow)
- Optional Telegram HTML-safe output
- Optional <pre> monospace mode for perfect alignment

Usage (HTML recommended):
    msg = premium_ui.header("CAM MAX BOT", "Premium Mining Panel", html=True, monospace=True)
    await bot.send_message(chat_id, msg, parse_mode="HTML")
"""

from __future__ import annotations

from dataclasses import dataclass
from html import escape as html_escape
from textwrap import wrap
from typing import Dict, Optional, List


@dataclass(frozen=True)
class PremiumUI:
    """Ultra-premium UI components and formatters."""

    ICONS: Dict[str, str] = None
    GRADIENTS: Dict[str, str] = None

    def __post_init__(self):
        object.__setattr__(self, "ICONS", {
            "logo": "🎯",
            "success": "✨",
            "loading": "⚡",
            "camera": "📸",
            "video": "🎬",
            "ai": "🧠",
            "stats": "📊",
            "settings": "⚙️",
            "user": "👤",
            "phone": "📱",
            "shield": "🛡️",
            "crown": "👑",
            "rocket": "🚀",
            "magic": "✨",
            "fire": "🔥",
            "star": "⭐",
            "diamond": "💎",
            "lock": "🔒",
            "unlock": "🔓",
            "check": "✅",
            "cross": "❌",
            "warning": "⚠️",
            "info": "ℹ️",
            "circle_green": "🟢",
            "circle_red": "🔴",
            "circle_yellow": "🟡",
            "dot": "•",
            "arrow": "→",
            "sparkle": "✨",
        })

        object.__setattr__(self, "GRADIENTS", {
            "top": "▀" * 22,
            "bottom": "▄" * 22,
            "full": "█" * 22,
            "light": "░" * 22,
            "medium": "▒" * 22,
            "dark": "▓" * 22,
        })

    # -------------------------
    # Helpers
    # -------------------------
    @staticmethod
    def _normalize_lines(text: str) -> List[str]:
        return (text or "").replace("\r\n", "\n").replace("\r", "\n").split("\n")

    @staticmethod
    def _fit_width(lines: List[str], min_width: int, max_width: int) -> int:
        longest = max((len(x) for x in lines), default=0)
        return max(min_width, min(longest, max_width))

    @staticmethod
    def _wrap_lines(lines: List[str], width: int) -> List[str]:
        out: List[str] = []
        for ln in lines:
            if ln is None:
                continue
            ln = str(ln)
            if ln == "":
                out.append("")
                continue
            out.extend(
                wrap(
                    ln,
                    width=width,
                    break_long_words=False,
                    break_on_hyphens=False,
                )
            )
        return out

    @staticmethod
    def _box(
        title: Optional[str],
        body_lines: List[str],
        footer: Optional[str] = None,
        *,
        width: int = 34,     # inner text width (without padding/borders)
        padding: int = 1,
        style: str = "rounded",
    ) -> str:
        """
        Create a nice box with dynamic width.
        width is INNER width (text area) before borders.
        """

        styles = {
            "rounded": dict(tl="╭", tr="╮", bl="╰", br="╯", hz="─", vt="│", tee_l="├", tee_r="┤"),
            "double":  dict(tl="╔", tr="╗", bl="╚", br="╝", hz="═", vt="║", tee_l="╠", tee_r="╣"),
            "single":  dict(tl="┌", tr="┐", bl="└", br="┘", hz="─", vt="│", tee_l="├", tee_r="┤"),
        }
        s = styles.get(style, styles["rounded"])

        def line(text: str) -> str:
            inner = (" " * padding) + text.ljust(width) + (" " * padding)
            return f"{s['vt']}{inner}{s['vt']}"

        inner_total = width + padding * 2
        top = f"{s['tl']}{s['hz'] * inner_total}{s['tr']}"
        mid = f"{s['tee_l']}{s['hz'] * inner_total}{s['tee_r']}"
        bottom = f"{s['bl']}{s['hz'] * inner_total}{s['br']}"

        out: List[str] = [top]

        if title:
            out.append(line(title))
            out.append(mid)

        for b in body_lines:
            out.append(line(b))

        if footer:
            out.append(mid)
            out.append(line(footer))

        out.append(bottom)
        return "\n".join(out)

    # -------------------------
    # Public UI
    # -------------------------
    def header(
        self,
        title: str,
        subtitle: Optional[str] = None,
        *,
        icon: Optional[str] = "logo",
        style: str = "double",
        min_width: int = 24,
        max_width: int = 42,
        html: bool = False,
        monospace: bool = False,
    ) -> str:
        """
        Premium header.

        If html=True -> HTML-safe output (use parse_mode="HTML")
        If monospace=True -> wrapped in <pre> for perfect alignment
        """
        t = (title or "").strip()
        if icon:
            ico = self.ICONS.get(icon, icon)
            t = f"{ico} {t}".strip()

        lines = [t]
        if subtitle:
            lines.append((subtitle or "").strip())

        width = self._fit_width(lines, min_width=min_width, max_width=max_width)
        body = self._wrap_lines(lines, width=width)

        box = self._box(None, body, width=width, padding=1, style=style)

        if html:
            safe = html_escape(box)
            return f"<pre>{safe}</pre>" if monospace else safe
        return box

    def card(
        self,
        title: str,
        content: str,
        footer: Optional[str] = None,
        *,
        title_icon: Optional[str] = None,
        style: str = "rounded",
        min_width: int = 28,
        max_width: int = 52,
        wrap_width: Optional[int] = None,
        html: bool = False,
        monospace: bool = False,
    ) -> str:
        """
        Premium content card.
        - wrap_width: if set, wraps content to that width; otherwise uses computed width.
        """
        t = (title or "").strip()
        if title_icon:
            ico = self.ICONS.get(title_icon, title_icon)
            t = f"{ico} {t}".strip()

        content_lines = self._normalize_lines(content)
        candidates = [t, *(content_lines or [""]), *( [footer] if footer else [] )]
        computed = self._fit_width(candidates, min_width=min_width, max_width=max_width)

        w = wrap_width if wrap_width is not None else computed
        wrapped_content = self._wrap_lines(content_lines, width=w)

        body_lines = [t] + wrapped_content
        box = self._box(None, body_lines, footer=footer, width=max(computed, w), padding=1, style=style)

        if html:
            safe = html_escape(box)
            return f"<pre>{safe}</pre>" if monospace else safe
        return box

    @staticmethod
    def section_divider(style: str = "light", width: int = 24) -> str:
        styles = {
            "light": "─",
            "medium": "━",
            "heavy": "═",
            "dots": "•",
            "fancy": "✦",
        }
        ch = styles.get(style, "─")
        if style == "fancy":
            core = "─" * max(0, width - 4)
            return f"✦ {core} ✦"
        if style == "dots":
            return " ".join(["•"] * max(3, width // 2))
        return ch * width

    def badge(self, text: str, style: str = "premium") -> str:
        styles = {
            "premium": f"{self.ICONS['sparkle']} {text} {self.ICONS['sparkle']}",
            "pro": f"{self.ICONS['crown']} {text}",
            "new": f"🆕 {text}",
            "hot": f"{self.ICONS['fire']} {text}",
            "verified": f"{self.ICONS['check']} {text}",
            "warn": f"{self.ICONS['warning']} {text}",
        }
        return styles.get(style, text)

    def stat_line(self, label: str, value: str, icon: str = "stats") -> str:
        ico = self.ICONS.get(icon, icon)
        return f"{ico} {label}: {value}"

    @staticmethod
    def progress_bar(percentage: int, width: int = 10) -> str:
        p = max(0, min(100, int(percentage)))
        filled = int(width * p / 100)
        empty = width - filled
        return f"[{'█' * filled}{'░' * empty}] {p}%"

    @staticmethod
    def list_item(text: str, level: int = 0, bullet: str = "•") -> str:
        indent = "   " * max(0, level)
        return f"{indent}{bullet} {text}"


# Export instance
premium_ui = PremiumUI()
