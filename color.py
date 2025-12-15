"""Color and text formatting for terminal output."""

class Colors:
    """ANSI color codes for terminal output."""
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    
    # Reset
    RESET = '\033[0m'


def color_text(text, color):
    """Apply color to text and reset after."""
    return f"{color}{text}{Colors.RESET}"


def bold(text):
    """Make text bold."""
    return f"{Colors.BOLD}{text}{Colors.RESET}"


def dim(text):
    """Dim text."""
    return f"{Colors.DIM}{text}{Colors.RESET}"


def title(text):
    """Format as title (bold cyan)."""
    return color_text(bold(text), Colors.CYAN)


def success(text):
    """Format as success (bright green)."""
    return color_text(text, Colors.BRIGHT_GREEN)


def error(text):
    """Format as error (bright red)."""
    return color_text(text, Colors.BRIGHT_RED)


def warning(text):
    """Format as warning (bright yellow)."""
    return color_text(text, Colors.BRIGHT_YELLOW)


def info(text):
    """Format as info (bright blue)."""
    return color_text(text, Colors.BRIGHT_BLUE)


def highlight(text):
    """Highlight text (bold yellow)."""
    return color_text(bold(text), Colors.YELLOW)


def dim_text(text):
    """Dim gray text."""
    return color_text(text, Colors.BRIGHT_BLACK)
