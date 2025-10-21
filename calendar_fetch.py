import zoneinfo
from datetime import datetime, timedelta, timezone

import gi
from dateutil.rrule import rruleset, rrulestr

gi.require_version("EDataServer", "1.2")
gi.require_version("ECal", "2.0")

from gi.repository import ECal, EDataServer, Gio  # noqa: E402

LOOKAHEAD_DAYS = 5


def to_dt(ecal_comp_dt):
    if not ecal_comp_dt:
        return None
    v = ecal_comp_dt.get_value()
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


def next_occurrences(rrule_text, dtstart, after, before):
    if dtstart.tzinfo is None:
        raise ValueError("dtstart must be timezone-aware")

    rs = rruleset()
    # Parse RRULE; rrulestr understands WKST, BYDAY, UNTIL, COUNT, etc.
    rs.rrule(rrulestr(rrule_text, dtstart=dtstart))

    out = []
    cur = rs.after(after, inc=True)
    while cur and cur < before:
        out.append(cur)
        cur = rs.after(cur)
    return out


def get_events():
    cancellable = Gio.Cancellable()
    registry = EDataServer.SourceRegistry.new_sync(cancellable)

    # Only calendar sources
    sources = EDataServer.SourceRegistry.list_sources(
        registry, EDataServer.SOURCE_EXTENSION_CALENDAR
    )

    now = datetime.now().astimezone()
    end = now + timedelta(days=LOOKAHEAD_DAYS)

    events = {}
    upcoming = []

    for src in sources:
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
            e_start = to_dt(comp.get_dtstart())
            e_end = to_dt(comp.get_dtend())
            if comp.has_recurrences():
                for rule in comp.get_rrules():
                    occ_zip = zip(
                        next_occurrences(rule.to_string(), e_start, now, end),
                        next_occurrences(rule.to_string(), e_end, now, end),
                    )
                    for occ_start, occ_end in occ_zip:
                        if occ_start is None or not (
                            now <= occ_end and occ_start <= end
                        ):
                            continue
                        upcoming.append(
                            {
                                "calendar": src.get_display_name(),
                                "summary": comp_summary(comp),
                                "location": comp_location(comp),
                                "start_dt": occ_start,
                                "end_dt": occ_end,
                                "in_progress": occ_start < now < occ_end,
                            }
                        )

            if e_start is None or not (now <= e_end and e_start <= end):
                continue
            upcoming.append(
                {
                    "calendar": src.get_display_name(),
                    "summary": comp_summary(comp),
                    "location": comp_location(comp),
                    "start_dt": e_start,
                    "end_dt": e_end,
                    "in_progress": e_start < now < e_end,
                }
            )
    for e in sorted(upcoming, key=lambda x: x["start_dt"]):
        start_date = e["start_dt"].date()
        if start_date not in events:
            events[start_date] = []
        events[start_date].append(e)
    return events


if __name__ == "__main__":
    for date, line in get_events().items():
        print(date, line)
