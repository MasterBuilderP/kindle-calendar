import argparse
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

from calendar_fetch import get_events

WIDTH, HEIGHT = 1448, 1072
BG_COLOR = 255
PANEL_COLOR = 240
PANEL_WIDTH = 10
PANEL_OUTLINE_COLOR = 0
TEXT_COLOR = 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="path to the output file")
    args = parser.parse_args()

    img = Image.new("L", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 60)
    text_font = ImageFont.truetype("DejaVuSans.ttf", 48)
    time_font = ImageFont.truetype("DejaVuSans.ttf", 100)

    # === DATE PANEL ===
    today = datetime.now()
    date_text = today.strftime("%A, %B %d, %Y")
    time_text = today.strftime("%H:%M")

    date_panel = (50, 50, WIDTH - 50, 250)
    draw.rounded_rectangle(
        date_panel,
        radius=30,
        fill=PANEL_COLOR,
        outline=PANEL_OUTLINE_COLOR,
        width=PANEL_WIDTH,
    )
    draw.text((100, 90), date_text, fill=TEXT_COLOR, font=title_font)
    draw.text((1050, 100), time_text, fill=TEXT_COLOR, font=time_font)

    # === CALENDAR PANEL ===
    cal_panel = (50, 300, WIDTH - 50, HEIGHT - 50)
    draw.rounded_rectangle(
        cal_panel,
        radius=30,
        fill=PANEL_COLOR,
        outline=PANEL_OUTLINE_COLOR,
        width=PANEL_WIDTH,
    )

    # 13 lines fit
    cal_events = get_events()[:13]
    cal = "\n".join([f"{diff:10} | {text}" for diff, text in cal_events])
    cal_diffs = "\n".join([f"{diff:10}" for diff, text in cal_events])
    cal_texts = "\n".join([f"| {text}" for diff, text in cal_events])
    draw.text((100, 330), cal_diffs, fill=TEXT_COLOR, font=text_font)
    draw.text((350, 330), cal_texts, fill=TEXT_COLOR, font=text_font)

    rotated = img.rotate(90, expand=True)
    rotated.save(args.filename, bits=8)
