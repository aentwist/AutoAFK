from typing import TypedDict


class AppSettings(TypedDict):
    emulator_path: str
    port: int
    debug_mode: bool

    start_delay_min: int
    wait_multiplier: int
    victory_check_freq_min: int
    surpress_victory_check_spam: bool
    ignore_formations: bool
    use_popular_formations: bool
    copy_artifacts: bool
    hibernate_when_finished: bool

    enable_telegram: bool
    token: str
    chat_id: int


app_settings: AppSettings = None
