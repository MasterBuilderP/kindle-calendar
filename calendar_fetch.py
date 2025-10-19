import zoneinfo
from datetime import datetime, timedelta, timezone

import gi

gi.require_version("EDataServer", "1.2")
gi.require_version("ECal", "2.0")

from gi.repository import ECal, EDataServer, Gio  # noqa: E402

LOOKAHEAD_DAYS = 30


def format_timedelta(delta: timedelta) -> str:
    days = delta.days
    weeks = days // 7
    hours = delta.seconds // 3600
    mins = delta.seconds // 60

    if weeks > 0:
        return f"{weeks} week{'s' if weeks != 1 else ''}"
    elif days > 0:
        return f"{days} day{'s' if days != 1 else ''}"
    elif hours > 0:
        return f"{hours} hour{'s' if hours != 1 else ''}"
    else:
        return f"{mins} min{'s' if mins != 1 else ''}"


def to_dt(ecal_comp):
    dt = ecal_comp.get_dtstart()
    if not dt:
        return None
    v = dt.get_value()
    vtz = v.get_timezone()
    # If no TZ info is present, assume its local timezone
    if vtz is None:
        utc_dt = datetime.fromtimestamp(v.as_timet(), timezone.utc)
        tz_dt = utc_dt.replace(tzinfo=datetime.now().astimezone().tzinfo).astimezone()
    else:
        tz_dt = datetime.fromtimestamp(
            v.as_timet_with_zone(), zoneinfo.ZoneInfo(vtz.get_tzid())
        )
    return tz_dt


def comp_summary(ecal_comp):
    txt = ecal_comp.get_summary()
    return txt.get_value() if txt else "(no title)"


def comp_location(ecal_comp):
    loc = ecal_comp.get_location()
    # Some versions return a plain str, others a ComponentText; handle both.
    return loc.get_value() if hasattr(loc, "get_value") else (loc or "")


def get_events():
    cancellable = Gio.Cancellable()
    registry = EDataServer.SourceRegistry.new_sync(cancellable)

    # Only calendar sources
    sources = EDataServer.SourceRegistry.list_sources(
        registry, EDataServer.SOURCE_EXTENSION_CALENDAR
    )

    now = datetime.now().astimezone()
    end = now + timedelta(days=LOOKAHEAD_DAYS)

    events = []
    upcoming = []

    for src in sources:
        # (Optionally) skip disabled sources if your bindings expose it
        if hasattr(src, "get_enabled") and not src.get_enabled():
            continue

        client = ECal.Client.connect_sync(
            source=src,
            source_type=ECal.ClientSourceType.EVENTS,
            wait_for_connected_seconds=2,
            cancellable=cancellable,
        )

        if not client:
            continue

        # Grab all objects; filter in Python (simplest path)
        comps = client.get_object_list_as_comps_sync(sexp="#t", cancellable=cancellable)
        # Some GI versions return (ok, comps); normalize
        if isinstance(comps, tuple) and len(comps) == 2:
            _, comps = comps

        for comp in comps or []:
            dt = to_dt(comp)
            if dt is None or not (now <= dt <= end):
                continue
            upcoming.append(
                {
                    "calendar": src.get_display_name(),
                    "summary": comp_summary(comp),
                    "location": comp_location(comp),
                    "start_dt": dt,
                }
            )

    for e in sorted(upcoming, key=lambda x: x["start_dt"]):
        start_local = e["start_dt"].astimezone()
        diff = start_local - now
        events.append((format_timedelta(diff), e["summary"]))
    return events


if __name__ == "__main__":
    for line in get_events():
        print(line)
