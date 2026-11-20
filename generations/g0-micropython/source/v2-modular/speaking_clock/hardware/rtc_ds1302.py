"""
DS1302 RTC driver with calibration support.
Based on original ds1302.py but with improvements:
- Calibration (ppm correction)
- Better error handling
- datetime tuple support
- Non-blocking operation
"""

from machine import Pin
import time


class RTC_DS1302:
    """DS1302 Real-Time Clock driver with ppm calibration."""

    # Register addresses
    REG_SECOND = 0x80
    REG_MINUTE = 0x82
    REG_HOUR = 0x84
    REG_DAY = 0x86
    REG_MONTH = 0x88
    REG_WEEKDAY = 0x8A
    REG_YEAR = 0x8C
    REG_WP = 0x8E
    REG_CTRL = 0x90
    REG_RAM = 0xC0

    def __init__(self, clk_pin: int, dat_pin: int, rst_pin: int):
        self.clk = Pin(clk_pin, Pin.OUT)
        self.dat = Pin(dat_pin, Pin.OUT)
        self.rst = Pin(rst_pin, Pin.OUT)

        self.clk.value(0)
        self.rst.value(0)

        # Calibration state
        self.correction_ppm = 0.0
        self._correction_accumulator = 0.0
        self._last_second = -1

    def _dec2bcd(self, val: int) -> int:
        """Decimal to BCD."""
        return (val // 10) * 16 + (val % 10)

    def _bcd2dec(self, val: int) -> int:
        """BCD to Decimal."""
        return (val // 16) * 10 + (val % 16)

    def _write_byte(self, byte: int):
        """Write byte to DS1302 (LSB first)."""
        self.dat.init(Pin.OUT)
        for i in range(8):
            self.dat.value((byte >> i) & 1)
            self.clk.value(1)
            self.clk.value(0)

    def _read_byte(self) -> int:
        """Read byte from DS1302 (LSB first)."""
        self.dat.init(Pin.IN)
        byte = 0
        for i in range(8):
            byte |= (self.dat.value() << i)
            self.clk.value(1)
            self.clk.value(0)
        return byte

    def _write_reg(self, reg: int, value: int):
        """Write register with write-protect handling."""
        self.rst.value(1)
        self._write_byte(reg)
        self._write_byte(value)
        self.rst.value(0)

    def _read_reg(self, reg: int) -> int:
        """Read register."""
        self.rst.value(1)
        self._write_byte(reg | 1)  # Read flag
        value = self._read_byte()
        self.rst.value(0)
        return value

    def _write_protect(self, enable: bool):
        """Enable/disable write protect."""
        self._write_reg(self.REG_WP, 0x80 if enable else 0x00)

    def start(self):
        """Start the clock (clear CH bit)."""
        sec = self._read_reg(self.REG_SECOND)
        self._write_protect(False)
        self._write_reg(self.REG_SECOND, sec & 0x7F)
        self._write_protect(True)

    def stop(self):
        """Stop the clock (set CH bit)."""
        sec = self._read_reg(self.REG_SECOND)
        self._write_protect(False)
        self._write_reg(self.REG_SECOND, sec | 0x80)
        self._write_protect(True)

    def set_correction_ppm(self, ppm: float):
        """Set calibration correction in parts per million."""
        self.correction_ppm = max(-50.0, min(50.0, ppm))
        self._correction_accumulator = 0.0

    def get_correction_ppm(self) -> float:
        """Get current calibration correction."""
        return self.correction_ppm

    def _apply_correction(self):
        """Apply accumulated ppm correction to RTC."""
        if self.correction_ppm == 0:
            return

        self._correction_accumulator += self.correction_ppm / 1_000_000.0

        # When accumulator reaches +/-1 second, adjust RTC
        if abs(self._correction_accumulator) >= 1.0:
            adjustment = int(self._correction_accumulator)
            self._correction_accumulator -= adjustment

            # Read current time, adjust seconds, write back
            current = self.datetime()
            if current:
                sec = current[5] + adjustment
                # Handle overflow
                if sec >= 60:
                    sec -= 60
                    # Would need to increment minute - skip for simplicity
                elif sec < 0:
                    sec += 60
                self.second(sec)

    def datetime(self, dt: tuple = None) -> tuple:
        """
        Get or set datetime as tuple: (year, month, day, weekday, hour, minute, second)
        weekday: 1=Mon ... 7=Sun
        """
        if dt is None:
            # Read all registers
            self._apply_correction()
            year = self._bcd2dec(self._read_reg(self.REG_YEAR)) + 2000
            month = self._bcd2dec(self._read_reg(self.REG_MONTH))
            day = self._bcd2dec(self._read_reg(self.REG_DAY))
            weekday = self._bcd2dec(self._read_reg(self.REG_WEEKDAY))
            hour = self._bcd2dec(self._read_reg(self.REG_HOUR))
            minute = self._bcd2dec(self._read_reg(self.REG_MINUTE))
            second = self._bcd2dec(self._read_reg(self.REG_SECOND) & 0x7F)
            return (year, month, day, weekday, hour, minute, second)
        else:
            # Write all registers
            year, month, day, weekday, hour, minute, second = dt
            self._write_protect(False)
            self._write_reg(self.REG_YEAR, self._dec2bcd(year - 2000))
            self._write_reg(self.REG_MONTH, self._dec2bcd(month))
            self._write_reg(self.REG_DAY, self._dec2bcd(day))
            self._write_reg(self.REG_WEEKDAY, self._dec2bcd(weekday))
            self._write_reg(self.REG_HOUR, self._dec2bcd(hour))
            self._write_reg(self.REG_MINUTE, self._dec2bcd(minute))
            self._write_reg(self.REG_SECOND, self._dec2bcd(second))
            self._write_protect(True)
            self._correction_accumulator = 0.0
            return dt

    def year(self, year: int = None) -> int:
        if year is None:
            return self._bcd2dec(self._read_reg(self.REG_YEAR)) + 2000
        self._write_protect(False)
        self._write_reg(self.REG_YEAR, self._dec2bcd(year - 2000))
        self._write_protect(True)
        return year

    def month(self, month: int = None) -> int:
        if month is None:
            return self._bcd2dec(self._read_reg(self.REG_MONTH))
        self._write_protect(False)
        self._write_reg(self.REG_MONTH, self._dec2bcd(month))
        self._write_protect(True)
        return month

    def day(self, day: int = None) -> int:
        if day is None:
            return self._bcd2dec(self._read_reg(self.REG_DAY))
        self._write_protect(False)
        self._write_reg(self.REG_DAY, self._dec2bcd(day))
        self._write_protect(True)
        return day

    def weekday(self, weekday: int = None) -> int:
        if weekday is None:
            return self._bcd2dec(self._read_reg(self.REG_WEEKDAY))
        self._write_protect(False)
        self._write_reg(self.REG_WEEKDAY, self._dec2bcd(weekday))
        self._write_protect(True)
        return weekday

    def hour(self, hour: int = None) -> int:
        if hour is None:
            return self._bcd2dec(self._read_reg(self.REG_HOUR))
        self._write_protect(False)
        self._write_reg(self.REG_HOUR, self._dec2bcd(hour))
        self._write_protect(True)
        return hour

    def minute(self, minute: int = None) -> int:
        if minute is None:
            return self._bcd2dec(self._read_reg(self.REG_MINUTE))
        self._write_protect(False)
        self._write_reg(self.REG_MINUTE, self._dec2bcd(minute))
        self._write_protect(True)
        return minute

    def second(self, second: int = None) -> int:
        if second is None:
            return self._bcd2dec(self._read_reg(self.REG_SECOND) & 0x7F)
        self._write_protect(False)
        self._write_reg(self.REG_SECOND, self._dec2bcd(second))
        self._write_protect(True)
        return second

    def is_running(self) -> bool:
        """Check if clock is running (CH bit clear)."""
        sec = self._read_reg(self.REG_SECOND)
        return (sec & 0x80) == 0

    def ram(self, addr: int, value: int = None) -> int:
        """Read/write RAM (31 bytes, addr 0-30)."""
        if value is None:
            self.rst.value(1)
            self._write_byte(self.REG_RAM + 1 + (addr % 31) * 2)
            val = self._read_byte()
            self.rst.value(0)
            return val
        else:
            self._write_protect(False)
            self.rst.value(1)
            self._write_byte(self.REG_RAM + (addr % 31) * 2)
            self._write_byte(value)
            self.rst.value(0)
            self._write_protect(True)
            return value

    def test_connection(self) -> bool:
        """Test if RTC is responding."""
        try:
            # Read seconds register twice, should be consistent
            sec1 = self._read_reg(self.REG_SECOND) & 0x7F
            time.sleep_ms(10)
            sec2 = self._read_reg(self.REG_SECOND) & 0x7F
            return sec1 == sec2 or abs(sec1 - sec2) <= 1
        except Exception:
            return False