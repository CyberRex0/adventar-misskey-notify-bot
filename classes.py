class DummyConfig:
    TOKEN = None
    DOMAIN = None
    CALENDAR_ID = None
    NOTE_VISIBILITY = None
    SHOW_YEAR = None

class ArgT:
    dry_run: bool
    force: bool
    force_day: int
    calendar_id: int