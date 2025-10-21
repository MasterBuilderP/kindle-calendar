import zoneinfo
from datetime import datetime, timedelta, timezone

import gi
from dateutil.rrule import rruleset, rrulestr

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


def format_time(start, end, now):
    if start < now < end:
        return f"> {(end - now).seconds // 60}min"
    return f"{start:%H:%M}"
    # diff = start - now
    # if start.date() == now.date():
    #     return f"{start:%H:%M}"
    # else:
    #     return f"{start:%d.%m %H:%M}"


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


def next_occurrences(
    rrule_text: str,
    dtstart: datetime,
    *,
    exdates: (
        list[str] | None
    ) = None,  # strings like "20251027T120000Z" (can pass [] if none)
    rdates: list[str] | None = None,  # same format
    after: datetime | None = None,  # default: now()
    count: int = 3,
):
    if dtstart.tzinfo is None:
        raise ValueError("dtstart must be timezone-aware")

    rs = rruleset()
    # Parse RRULE; rrulestr understands WKST, BYDAY, UNTIL, COUNT, etc.
    rs.rrule(rrulestr(rrule_text, dtstart=dtstart))

    # TODO: Add explicit inclusions/exclusions if provided
    # for s in (exdates or []):
    #     # Support comma-separated EXDATE property by splitting
    #     for part in s.split(","):
    #         parse_ical_dt(part.strip(), default_tz=dtstart.tzinfo))
    # for s in (rdates or []):
    #     for part in s.split(","):
    #         parse_ical_dt(part.strip(), default_tz=dtstart.tzinfo))

    # Generate next N after a reference time
    ref = after or datetime.now(dtstart.tzinfo)
    out = []
    cur = rs.after(ref, inc=True)
    while cur and len(out) < count:
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

    events = []
    ev = {}
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
            e_start = to_dt(comp.get_dtstart())
            e_end = to_dt(comp.get_dtend())
            if comp.has_recurrences():
                for rule in comp.get_rrules():
                    occ_zip = zip(
                        next_occurrences(rule.to_string(), e_start),
                        next_occurrences(rule.to_string(), e_end),
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
                            }
                        )
                        # print(comp_summary(comp), occ)

            if e_start is None or not (now <= e_end and e_start <= end):
                continue
            upcoming.append(
                {
                    "calendar": src.get_display_name(),
                    "summary": comp_summary(comp),
                    "location": comp_location(comp),
                    "start_dt": e_start,
                    "end_dt": e_end,
                }
            )
    for e in sorted(upcoming, key=lambda x: x["start_dt"]):
        start_local = e["start_dt"]
        end_local = e["end_dt"]
        start_date = start_local.date()
        events.append((format_time(start_local, end_local, now), e["summary"]))
        if start_date not in ev:
            ev[start_date] = []
        ev[start_date].append((format_time(start_local, end_local, now), e["summary"]))
    return ev


if __name__ == "__main__":
    for line in get_events():
        print(line)
