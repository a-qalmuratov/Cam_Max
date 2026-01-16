"""
Premium UI utility functions for ultra-polished bot experience.
"""

class PremiumUI:
    """Ultra-premium UI components and formatters."""
    
    # Premium Icons
    ICONS = {
        'logo': '🎯',
        'success': '✨',
        'loading': '⚡',
        'camera': '📸',
        'video': '🎬',
        'ai': '🧠',
        'stats': '📊',
        'settings': '⚙️',
        'user': '👤',
        'phone': '📱',
        'shield': '🛡️',
        'crown': '👑',
        'rocket': '🚀',
        'magic': '✨',
        'fire': '🔥',
        'star': '⭐',
        'diamond': '💎',
        'lock': '🔒',
        'unlock': '🔓',
        'check': '✅',
        'cross': '❌',
        'warning': '⚠️',
        'info': 'ℹ️',
        'circle_green': '🟢',
        'circle_red': '🔴',
        'circle_yellow': '🟡',
        'dot': '•',
        'arrow': '→',
        'sparkle': '✨',
    }
    
    # Premium Colors (via emojis)
    GRADIENTS = {
        'top': '▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀',
        'bottom': '▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄',
        'full': '█████████████████████',
        'light': '░░░░░░░░░░░░░░░░░░░░',
        'medium': '▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒',
        'dark': '▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓',
    }
    
    @staticmethod
    def header(title: str, subtitle: str = None) -> str:
        """Create premium header."""
        lines = []
        lines.append("╔═══════════════════╗")
        lines.append(f"║     {title}     ║")
        if subtitle:
            lines.append(f"║  {subtitle}  ║")
        lines.append("╚══════════════════╝")
        return "\n".join(lines)
    
    @staticmethod
    def card(title: str, content: str, footer: str = None) -> str:
        """Create premium card."""
        lines = []
        lines.append("┌──────────────────┐")
        lines.append(f"│ {title}")
        lines.append("├──────────────────┤")
        for line in content.split("\n"):
            lines.append(f"│ {line}")
        if footer:
            lines.append("├──────────────────┤")
            lines.append(f"│ {footer}")
        lines.append("└──────────────────┘")
        return "\n".join(lines)
    
    @staticmethod
    def section_divider(style='light') -> str:
        """Create elegant section divider."""
        styles = {
            'light': '─ ─ ─ ─ ─ ─ ─ ─ ─',
            'medium': '━━━━━━━━━━━━━━━━━',
            'heavy': '═════════════════',
            'dots': '• • • • • • • • • •',
            'fancy': '✦ ─ ─ ─ ─ ─ ─ ─ ─ ✦',
        }
        return styles.get(style, styles['light'])
    
    @staticmethod
    def badge(text: str, style='premium') -> str:
        """Create status badge."""
        styles = {
            'premium': f'✨ {text} ✨',
            'pro': f'👑 {text}',
            'new': f'🆕 {text}',
            'hot': f'🔥 {text}',
            'verified': f'✅ {text}',
        }
        return styles.get(style, text)
    
    @staticmethod
    def stat_card(label: str, value: str, icon: str = '📊') -> str:
        """Create stat display."""
        return f"{icon} {label} \n {value}"
    
    @staticmethod
    def progress_bar(percentage: int, width: int = 8) -> str:
        """Create visual progress bar."""
        filled = int(width * percentage / 100)
        empty = width - filled
        return f"[{'█' * filled}{'░' * empty}] {percentage}%"
    
    @staticmethod
    def list_item(text: str, level: int = 0) -> str:
        """Create nested list item."""
        indent = "   " * level
        return f"{indent}• {text}"

# Export
premium_ui = PremiumUI()
