import os.path
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import frontmatter
import markdown
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
from pathlib import Path
from typing import Iterator

tz = ZoneInfo("Europe/Stockholm")


def plainify(html: str) -> str:
    """Extract plain text from html."""
    return BeautifulSoup(html, "html.parser").get_text("\n", strip=True)


def urlify(s: str) -> str:
    """Turn string into url-compatible string."""

    def transform(c: str) -> str:
        if not c.isascii():
            return ''
        elif c.isalnum():
            return c.lower()
        return '-'

    return ''.join(map(transform, s))


def with_tz(d: datetime) -> datetime:
    return datetime(
        d.year,
        d.month,
        d.day,
        d.hour,
        d.minute,
        tzinfo=tz,
    )


def iterate_events(directory: Path) -> Iterator[Path]:
    for event in directory.iterdir():
        if event.is_file() and event.suffix == '.md':
            yield event


def generate_event(path: Path) -> Event:
    def meta[A](key: str, default=None, transform=None) -> A:
        if key not in metadata and default is None:
            raise RuntimeError(f'Missing required metadata {key}')
        value = metadata.get(key, default)
        if transform is not None:
            value = transform(value)
        return value

    post = frontmatter.load(path)

    metadata = post.metadata

    text_body = post.content

    html_title = markdown.markdown(meta('title'))
    text_title = plainify(html_title)

    html_speaker = markdown.markdown(meta('speaker'))
    text_speaker = plainify(html_speaker)

    event = Event()
    event.uid = f'{urlify(text_title)}@fp.chalmers.se'
    event.summary = f'FP-Talk {text_speaker}'
    event.location = meta('place')

    event.start = with_tz(meta('date')).astimezone(timezone.utc)
    event.end = event.start + timedelta(minutes=meta('duration', default=60))
    event.stamp = datetime.fromtimestamp(os.path.getmtime(path))

    localtime = event.start.astimezone(tz)
    description_timestring = localtime.strftime('%H (%Z) on %B %d')

    event.description = f"""
Time: {description_timestring}
Place: {event.location}
Speaker: {text_speaker}

{text_title}
{text_body}
    """.strip()
    return event


def generate_calendar(events: list[Event]) -> Calendar:
    cal = Calendar()

    cal.version = '2.0'
    cal.prodid = '-//Functional Programming Seminar//EN'
    cal.calscale = 'GREGORIAN'

    for event in sorted(events, key=lambda e: e.start, reverse=True):
        cal.add_component(event)
    return cal


def write_calendar_file(path: Path, events: list[Event]):
    cal = generate_calendar(events)
    path.write_bytes(cal.to_ical())


def convert_all(src: Path, dst: Path):
    all_events = []

    for path in iterate_events(src):
        try:
            event = generate_event(path)
            all_events.append(event)

            write_calendar_file(dst / path.stem.lower() / 'event.ics', [event])
        except Exception as e:
            print(f'{path}: {e}')

    write_calendar_file(dst / 'calendar.ics', all_events)


if __name__ == '__main__':
    convert_all(Path('talks'), Path('public'))
