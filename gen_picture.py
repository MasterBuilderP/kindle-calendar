import argparse
from datetime import datetime, timedelta

from PIL import Image, ImageDraw, ImageFont

from calendar_fetch import get_events

WIDTH, HEIGHT = 1448, 1072
BG_COLOR = 255
PANEL_COLOR = 240
PANEL_WIDTH = 10
PANEL_OUTLINE_COLOR = 0
TEXT_COLOR = 0


def draw_date_panel(draw):
    today = datetime.now()
    date_text = today.strftime("%a, %b %d")
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


def draw_partial_image():
    img = Image.new("L", (WIDTH, 255), BG_COLOR)
    draw = ImageDraw.Draw(img)

    draw_date_panel(draw)

    rotated = img.rotate(90, expand=True)
    rotated.save(args.filename, bits=8)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="path to the output file")
    parser.add_argument(
        "--partial", action="store_true", help="Only generate date Panel"
    )
    args = parser.parse_args()

    text_size = 60
    title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 120)
    text_font = ImageFont.truetype("DejaVuSans.ttf", text_size)
    text_font_bold = ImageFont.truetype("DejaVuSans-Bold.ttf", text_size)
    time_font = ImageFont.truetype("DejaVuSans.ttf", 100)

    if args.partial:
        draw_partial_image()
        exit()

    img = Image.new("L", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    draw_date_panel(draw)

    # === CALENDAR PANEL ===
    cal_panel = (50, 260, WIDTH - 50, HEIGHT - 50)
    draw.rounded_rectangle(
        cal_panel,
        radius=30,
        fill=PANEL_COLOR,
        outline=PANEL_OUTLINE_COLOR,
        width=PANEL_WIDTH,
    )

    max_width = WIDTH - 200
    current_height = 300
    cal_events = get_events()
    all_lines = 0
    for date in cal_events:
        if current_height + text_size * 3 > HEIGHT:
            break
        if date == datetime.today().date():
            cal_date_text = "Today"
        elif date == datetime.today().date() + timedelta(days=1):
            cal_date_text = "Tomorrow"
        else:
            cal_date_text = f"{date:%d.%m}"
        draw.text(
            (100, current_height), cal_date_text, fill=TEXT_COLOR, font=text_font_bold
        )
        n_lines = 1
        for event in cal_events[date]:
            if current_height + text_size + n_lines * text_size * 2 > HEIGHT:
                break
            event_text = f"{event[0]} | {event[1]}"
            while (
                event_text and draw.textlength(event_text, font=text_font) > max_width
            ):
                event_text = event_text[:-1]
            draw.text(
                (145, current_height + n_lines * text_size),
                event_text,
                fill=TEXT_COLOR,
                font=text_font,
            )
            n_lines += 1
        current_height = current_height + n_lines * text_size
        all_lines += n_lines

    # 13 lines fit
    # cal_events = get_events()[:13]
    # cal_diffs = "\n".join([f"{diff:10}" for diff, text in cal_events])
    # cal_texts = "\n".join([f"| {text[:35]}" for diff, text in cal_events])
    # draw.text((100, 330), cal_diffs, fill=TEXT_COLOR, font=text_font)
    # draw.text((400, 330), cal_texts, fill=TEXT_COLOR, font=text_font)

    rotated = img.rotate(90, expand=True)
    rotated.save(args.filename, bits=8)
