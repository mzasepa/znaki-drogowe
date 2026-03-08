"""UI theme - child-friendly colors and styles."""

# Color palette
PRIMARY = "#4A90D9"      # friendly blue
SECONDARY = "#7BC67E"    # soft green
ACCENT = "#F5A623"       # warm orange
DANGER = "#E74C3C"       # red for wrong answers
SUCCESS = "#27AE60"      # green for correct answers
BG_COLOR = "#F0F4F8"     # light background
CARD_BG = "#FFFFFF"      # white cards

BUTTON_STYLE_GREEN = (
    "background-color: #27AE60; color: white; font-size: 1.1rem; "
    "padding: 12px 24px; border-radius: 12px;"
)
BUTTON_STYLE_RED = (
    "background-color: #E74C3C; color: white; font-size: 1.1rem; "
    "padding: 12px 24px; border-radius: 12px;"
)
BUTTON_STYLE_BLUE = (
    "background-color: #4A90D9; color: white; font-size: 1.1rem; "
    "padding: 12px 24px; border-radius: 12px;"
)
BUTTON_STYLE_ORANGE = (
    "background-color: #F5A623; color: white; font-size: 1.1rem; "
    "padding: 12px 24px; border-radius: 12px;"
)
BUTTON_STYLE_GRAY = (
    "background-color: #BDC3C7; color: white; font-size: 1.1rem; "
    "padding: 12px 24px; border-radius: 12px;"
)

PAGE_STYLE = f"background-color: {BG_COLOR}; min-height: 100vh;"

CARD_STYLE = (
    "padding: 24px; border-radius: 16px; "
    "box-shadow: 0 2px 8px rgba(0,0,0,0.1);"
)

TITLE_STYLE = f"color: {PRIMARY}; font-size: 2rem; font-weight: bold;"
