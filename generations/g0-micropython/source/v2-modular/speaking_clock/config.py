"""
Configuration constants for Speaking Timer Clock v2.0
All hardware pins, default settings, and system constants.
"""

# ============================================================
# HARDWARE PINS (Raspberry Pi Pico / RP2040)
# ============================================================

# I2C0 - LCD 1602 (PCF8574)
I2C_SDA_PIN = 0
I2C_SCL_PIN = 1
I2C_FREQ = 400_000
LCD_I2C_ADDR = 0x3F
LCD_ROWS = 2
LCD_COLS = 16

# UART0 - DFPlayer Mini
UART_ID = 0
UART_TX_PIN = 16
UART_RX_PIN = 17
UART_BAUDRATE = 9600
DFPLAYER_BUSY_PIN = 18

# DS1302 RTC
RTC_CLK_PIN = 2
RTC_DAT_PIN = 5
RTC_RST_PIN = 4

# Rotary Encoder 1 (Left) - Volume / Navigation
ENC1_DT_PIN = 14   # DATA
ENC1_CLK_PIN = 15  # CLK
ENC1_SW_PIN = 20   # Switch (button)

# Rotary Encoder 2 (Right) - Timer values / Selection
ENC2_DT_PIN = 11   # DATA
ENC2_CLK_PIN = 10  # CLK
ENC2_SW_PIN = 19   # Switch (button)

# Buttons (5x momentary, pull-up)
BTN1_PIN = 28   # Music play/pause / shuffle
BTN2_PIN = 21   # Speak time / Cycle language
BTN3_PIN = 22   # Menu enter / Chime demo
BTN4_PIN = 26   # Timer preset 1 (5/10/15 min)
BTN5_PIN = 27   # Timer preset 2 (30/45/60 min)

# Built-in LED (for status/heartbeat)
LED_PIN = "LED"  # Pico onboard LED

# ============================================================
# DISPLAY SETTINGS
# ============================================================
DISPLAY_BRIGHTNESS_DEFAULT = 80        # 0-100%
DISPLAY_TIMEOUT_DEFAULT = 30           # seconds, 0 = never off
DISPLAY_SHOW_SECONDS_DEFAULT = True
DISPLAY_24H_FORMAT = True

# ============================================================
# AUDIO SETTINGS
# ============================================================
VOLUME_DEFAULT = 15              # 0-30 (DFPlayer range)
VOLUME_MIN = 0
VOLUME_MAX = 30
VOLUME_STEP = 1

# Quiet mode (night mode)
QUIET_MODE_ENABLED_DEFAULT = True
QUIET_START_DEFAULT = 22         # hour (22:00)
QUIET_END_DEFAULT = 7            # hour (07:00)
QUIET_MODE_PRESETS = {
    "early": (21, 6),
    "standard": (22, 7),
    "owl": (23, 8),
    "custom": None,
}

# Chime settings
CHIME_HOURLY_ENABLED_DEFAULT = True
CHIME_HALF_HOUR_ENABLED_DEFAULT = True
CHIME_STYLE_DEFAULT = "grandfather"  # "grandfather", "westminster", "simple"

# Speech queue limits
SPEECH_QUEUE_MAX_CRITICAL = 1
SPEECH_QUEUE_MAX_HIGH = 3
SPEECH_QUEUE_MAX_NORMAL = 5
SPEECH_QUEUE_MAX_LOW = 10

# ============================================================
# TIMER SETTINGS
# ============================================================
TIMER_MAX_SECONDS = 24 * 3600      # 24 hours max
TIMER_DEFAULT_SECONDS = 300        # 5 minutes
TIMER_PRESETS_1 = [300, 600, 900]      # 5, 10, 15 min (Btn4)
TIMER_PRESETS_2 = [1800, 2700, 3600]   # 30, 45, 60 min (Btn5)

# Pomodoro defaults (hidden in Advanced menu)
POMODORO_WORK_DEFAULT = 1500       # 25 min
POMODORO_SHORT_BREAK_DEFAULT = 300  # 5 min
POMODORO_LONG_BREAK_DEFAULT = 900   # 15 min
POMODORO_CYCLES_DEFAULT = 4

# ============================================================
# ALARM SETTINGS
# ============================================================
MAX_ALARMS = 10
ALARM_DEFAULT_SOUND = "alarm_1"
ALARM_SNOOZE_MINUTES = 5
ALARM_AUTO_DISMISS_SECONDS = 180   # 3 minutes

# Default alarms (migrated from v1)
DEFAULT_ALARMS = [
    {"id": 1, "enabled": True, "time": "11:49", "days": 0x7F, "sound": "alarm_1", "label": "Alarm 1"},
    {"id": 2, "enabled": True, "time": "12:35", "days": 0x7F, "sound": "alarm_1", "label": "Alarm 2"},
    {"id": 3, "enabled": True, "time": "14:00", "days": 0x7F, "sound": "alarm_1", "label": "Alarm 3"},
    {"id": 4, "enabled": True, "time": "16:00", "days": 0x7F, "sound": "alarm_1", "label": "Alarm 4"},
    {"id": 5, "enabled": True, "time": "17:00", "days": 0x7F, "sound": "alarm_1", "label": "Alarm 5"},
]

# Days bitmask: bit 0=Mon ... bit 6=Sun
DAYS_ALL = 0x7F
DAYS_WEEKDAYS = 0x3F  # Mon-Fri
DAYS_WEEKEND = 0xC0   # Sat-Sun

# ============================================================
# RTC CALIBRATION
# ============================================================
RTC_CORRECTION_PPM_DEFAULT = 0.0     # parts per million, +/-20 typical
RTC_CORRECTION_MIN = -50.0
RTC_CORRECTION_MAX = 50.0

# ============================================================
# LOCALE / LANGUAGE
# ============================================================
SUPPORTED_LOCALES = ["ru", "de", "ua"]
DEFAULT_LOCALE = "ru"
LOCALE_CYCLE_ORDER = ["ru", "de", "ua"]  # Btn2 long press cycles through these

# ============================================================
# FILE SYSTEM / STORAGE
# ============================================================
CONFIG_FILE = "config.json"
CONFIG_VERSION = 2

# SD Card paths (new structure)
SD_ROOT = "/sd"
TTS_ROOT = f"{SD_ROOT}/tts"
MUSIC_ROOT = f"{SD_ROOT}/music"
CHIMES_ROOT = f"{SD_ROOT}/chimes"
SYSTEM_ROOT = f"{SD_ROOT}/system"

# Legacy paths (for migration)
LEGACY_SOUND_ROOT = "/sd/sound/_sdcard"

# ============================================================
# TIMING CONSTANTS
# ============================================================
MAIN_LOOP_INTERVAL_MS = 50         # 20 Hz main loop
DISPLAY_REFRESH_MS = 500           # 2 Hz display update (when not dirty)
RTC_SYNC_INTERVAL_MS = 1000        # 1 Hz time update
BUTTON_DEBOUNCE_MS = 50
BUTTON_LONG_PRESS_MS = 1000
ENCODER_ACCEL_THRESHOLD = 4        # steps before acceleration kicks in
ENCODER_ACCEL_MULTIPLIER = 3

# Speech timing
SPEECH_INTER_PHRASE_MS = 100       # gap between TTS segments
SPEECH_MAX_PHRASE_MS = 10000       # max single phrase duration

# ============================================================
# SYSTEM
# ============================================================
WATCHDOG_TIMEOUT_MS = 8000
BOOT_DELAY_MS = 1000               # wait for hardware to settle
FIRST_BOOT_FLAG_FILE = ".first_boot_done"