from datetime import datetime, time, timedelta

from PIL import Image, ImageDraw, ImageFont

from .cache import cache

WIDTH, HEIGHT = 1448, 1072
BG_COLOR = 255
PANEL_COLOR = 240
PANEL_WIDTH = 10
PANEL_MARGIN = 50
PANEL_OUTLINE_COLOR = 0
TEXT_COLOR = 0
TEXT_SIZE = 60
TITLE_SIZE = 120
TIME_SIZE = 100


def draw_date_panel(draw, title_font, time_font):
    today = datetime.now()
    date_text = today.strftime("%a, %b %d")
    time_text = today.strftime("%H:%M")

    date_panel = (PANEL_MARGIN, PANEL_MARGIN, WIDTH - PANEL_MARGIN, 250)
    draw.rounded_rectangle(
        date_panel,
        radius=30,
        fill=PANEL_COLOR,
        outline=PANEL_OUTLINE_COLOR,
        width=PANEL_WIDTH,
    )
    draw.text((100, 90), date_text, fill=TEXT_COLOR, font=title_font)
    draw.text((1050, 100), time_text, fill=TEXT_COLOR, font=time_font)


def get_battery_percent():
    try:
        with open("/sys/class/power_supply/max77696-battery/capacity") as f:
            return int(f.read().strip())
    except Exception as e:
        print("Error reading battery level:", e)
        return None


def load_data():
    cal_events = {}
    for _, e in sorted(cache().items(), key=lambda x: x[1]["start_dt"]):
        start_date = e["start_dt"].date()
        if start_date not in cal_events:
            cal_events[start_date] = []
        cal_events[start_date].append(e)
    return cal_events


def main(args):
    img = Image.new("L", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    if args.kindle:
        title_font = ImageFont.truetype(
            "/usr/java/lib/fonts/AmazonEmberBold-Bold.ttf", TITLE_SIZE
        )
        time_font = ImageFont.truetype(
            "/usr/java/lib/fonts/AmazonEmberBold-Regular.ttf", TIME_SIZE
        )
        text_font = ImageFont.truetype(
            "/usr/java/lib/fonts/Amazon-Ember-Regular.ttf", TEXT_SIZE
        )
        text_font_bold = ImageFont.truetype(
            "/usr/java/lib/fonts/AmazonEmberBold-Bold.ttf", TEXT_SIZE
        )

        battery_font = ImageFont.truetype(
            "/usr/java/lib/fonts/Amazon-Ember-Regular.ttf", 30
        )
    else:
        title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", TITLE_SIZE)
        text_font = ImageFont.truetype("DejaVuSans.ttf", TEXT_SIZE)
        text_font_bold = ImageFont.truetype("DejaVuSans-Bold.ttf", TEXT_SIZE)
        time_font = ImageFont.truetype("DejaVuSans.ttf", TIME_SIZE)

    draw_date_panel(draw, title_font, time_font)
    if args.kindle:
        battery = get_battery_percent()
        draw.text((1375, 5), f"{battery}%", fill=TEXT_COLOR, font=battery_font)

    # === CALENDAR PANEL ===
    cal_panel = (PANEL_MARGIN, 260, WIDTH - PANEL_MARGIN, HEIGHT - PANEL_MARGIN)
    draw.rounded_rectangle(
        cal_panel,
        radius=30,
        fill=PANEL_COLOR,
        outline=PANEL_OUTLINE_COLOR,
        width=PANEL_WIDTH,
    )

    text_end = HEIGHT - (2 * PANEL_MARGIN + PANEL_WIDTH)
    max_width = WIDTH - 200
    current_height = 300

    all_lines = 0
    cal_events = load_data()
    for date in cal_events:
        if current_height + TEXT_SIZE * 2 > text_end:
            break
        if date == datetime.today().date():
            cal_date_text = "Today"
        elif date == datetime.today().date() + timedelta(days=1):
            cal_date_text = "Tomorrow"
        else:
            cal_date_text = f"{date:%d.%m}"
        draw.text(
            (100, current_height),
            cal_date_text,
            fill=TEXT_COLOR,
            font=text_font_bold,
        )
        n_lines = 1
        for event in cal_events[date]:
            if current_height + TEXT_SIZE + n_lines * TEXT_SIZE > text_end:
                break
            sep = (
                ">"
                if event["start_dt"] < datetime.now().astimezone() < event["end_dt"]
                else "|"
            )
            time_text = (
                ""
                if event["start_dt"].time() == time(0, 0)
                else f"{event['start_dt']:%H:%M}"
            )
            event_text = (
                f"{time_text}{' ' if time_text else ''}{sep} {event['summary']}"
            )
            while (
                event_text and draw.textlength(event_text, font=text_font) > max_width
            ):
                event_text = event_text[:-1]
            draw.text(
                (145, current_height + n_lines * TEXT_SIZE),
                event_text,
                fill=TEXT_COLOR,
                font=text_font,
            )
            n_lines += 1
        current_height = current_height + n_lines * TEXT_SIZE
        all_lines += n_lines

    rotated = img.rotate(90, expand=True)
    rotated.save(args.filename, bits=8)
