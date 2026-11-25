"""Local stand-in for the Pi2Clock G1 phone API, for page development and screenshots.

Usage: python tools/phone_web_mock.py firmware/pico2w_c/services/phone_web/index.html [port]
Then open http://127.0.0.1:8765/ in a browser. GET /mock/<ring|timer|music|direct|offline|untrusted|quiet>
switches demo states. The responses follow the JSON field names of phone_web.c, but the command
handling is a simplified model: it is not evidence of firmware behavior."""
import json, sys, time, threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

PAGE = sys.argv[1]
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8765
lock = threading.Lock()
EPOCH = 123

def berlin():
    t = time.gmtime(time.time() + 3600)
    return t

S = {
    "firmware": {"name": "Pi2Clock G1", "generation": "G1", "version": "1.0.0+82.gabc1234", "build": "g1-abc1234def56-bt-mp3-wifi-phone-ota17-trial",
                 "board": "pico2_w", "author": "FlintUA", "ota_sequence": 17},
    "ota_control": True, "clock_control": True, "bt_control": True, "network_control": True, "browser_control": True, "wifi_control": True,
    "timer_running": False, "timer_seconds": 300, "player": "Closed", "track": 12, "output": "BT",
    "epoch": EPOCH, "home_trusted": True, "track_count": 45, "player_mode": "SHUF", "player_test": False,
    "player_interrupted": False, "player_sleep_preset": 0, "player_sleep_seconds": 0,
    "command_id": 0, "command_nonce": 0, "command_result": "none",
    "settings": {"snapshot_id": 0, "volume_local": 8, "volume_bt": 8, "language": 0, "audio_manual": 1, "audio_hourly": 0, "audio_timer": 1, "audio_alarm": 0,
                 "light_mode": 2, "light_day": 80, "light_night": 15, "timer_sound": 0, "timer_track": 7, "timer_voice": 1, "timer_random": 0, "timer_warning": 0,
                 "auto_enabled": 1, "clock_mode": 0, "half_hour": 1, "exact_hour": 1, "quiet_enabled": 1, "quiet_start": 22, "quiet_end": 7,
                 "editing": False, "idle": True, "bt_supported": True, "saving": "saved"},
    "alarms": [
        {"enabled": True, "hour": 6, "minute": 45, "days": 31, "sound": 0, "track": 1, "revision": 1},
        {"enabled": True, "hour": 8, "minute": 30, "days": 96, "sound": 1, "track": 12, "revision": 1},
        {"enabled": False, "hour": 7, "minute": 15, "days": 127, "sound": 2, "track": 3, "revision": 1},
        {"enabled": False, "hour": 12, "minute": 0, "days": 21, "sound": 0, "track": 1, "revision": 1},
        {"enabled": False, "hour": 0, "minute": 0, "days": 127, "sound": 0, "track": 1, "revision": 1}],
    "birthdays": [{"enabled": False, "month": 1, "day": 1, "hour": 9, "minute": 0, "birth_year": 0, "revision": 1} for _ in range(15)],
    "overview": {"rtc_valid": True, "sound_on": True, "quiet_now": False, "timer_sound_id": 0,
                 "alarm": {"active": 0, "active_id": 0, "snooze_revision": 1, "deferred": 0, "next_slot": 1, "next_at": "", "next_snoozed": False,
                           "snoozes": 0, "snooze_slot": 0, "snooze_seconds": 0, "snooze_waiting": False},
                 "bluetooth": {"state": "connected", "name": "PRO X 2"},
                 "network": {"mode": "home", "state": "ready", "seconds": 0},
                 "ntp": {"available": True, "configured": True, "sampled": True, "synced": True, "pending": False, "requesting": False, "retry": False,
                         "failed": False, "sample_age": 240, "sync_age": 240, "offset": 0}},
}
S["birthdays"][0].update(enabled=True, day=14, month=3, birth_year=1987)
S["birthdays"][1].update(enabled=True, day=2, month=7, hour=8, minute=30)
BT = {"epoch": EPOCH, "snapshot_id": 0, "supported": True, "available": True, "scanning": False, "connected": True, "target": "042144FAA90E", "known_count": 3,
      "devices": [{"id": "042144FAA90E", "name": "PRO X 2", "saved": True}, {"id": "123456789ABC", "name": "Portable", "saved": True},
                  {"id": "A1B2C3D4E5F6", "name": "Nest", "saved": True}]}
NET = {"epoch": EPOCH, "snapshot_id": 0, "supported": True, "available": True, "mode": "home", "configured": True, "direct_key_ready": True,
       "home_ssid": "FRITZ!Box 7590 KQ", "home_address": "192.168.2.116", "address": "192.168.2.116", "home_state": "ready", "home_seconds": 0,
       "transition": "idle", "target": "direct", "seconds": 0}
WIFI = {"epoch": EPOCH, "state": "idle", "reason": "none", "request_id": 0, "seconds": 0, "direct": False, "available": True, "saved_ssid": "FRITZ!Box 7590 KQ",
        "test_ssid": "", "address": "192.168.2.116", "profiles_revision": 1, "scan_supported": True, "scan_available": True, "connected_profile": 1,
        "connect_available": True, "profiles": [{"slot": 1, "ssid": "FRITZ!Box 7590 KQ", "open": False}, {"slot": 2, "ssid": "Garten-Repeater", "open": False}]}
BROWSERS = {"epoch": EPOCH, "revision": 3, "capacity": 4, "home_trusted": True, "entries": [{"slot": 1, "scope": "home"}, {"slot": 2, "scope": "direct"}]}
OTA = {"supported": True, "available": True, "state": "idle", "error": "none", "current_sequence": 17, "active": "B", "received": 0, "size": 0, "session": 0,
       "mode_restore": True, "restart_mode": "home"}
timer_end = [0.0]
sleep_end = [0.0]
snooze_end = [0.0]
OFFLINE = [0.0]

def refresh():
    t = berlin()
    S["time"] = "%02d:%02d:%02d" % (t.tm_hour, t.tm_min, t.tm_sec)
    o = S["overview"]
    o["date"] = "%04d-%02d-%02d" % (t.tm_year, t.tm_mon, t.tm_mday)
    o["weekday"] = t.tm_wday + 1
    tomorrow = time.gmtime(time.time() + 3600 + 86400)
    o["alarm"]["next_at"] = "%04d-%02d-%02dT08:30:00" % (tomorrow.tm_year, tomorrow.tm_mon, tomorrow.tm_mday)
    o["alarm"]["next_slot"] = 2 if any(a["enabled"] for a in S["alarms"]) else 0
    if S["timer_running"]:
        left = int(round(timer_end[0] - time.time()))
        if left <= 0:
            S["timer_running"] = False; S["timer_seconds"] = S.get("timer_set", 300); o["timer_sound_id"] = 77
        else:
            S["timer_seconds"] = left
    if S["player_sleep_preset"] and S["player"] != "Closed":
        S["player_sleep_seconds"] = max(0, int(sleep_end[0] - time.time()))
    if o["alarm"]["snoozes"]:
        o["alarm"]["snooze_seconds"] = max(0, int(snooze_end[0] - time.time()))
    S["settings"]["idle"] = S["player"] == "Closed" and not S["timer_running"] and not o["alarm"]["active"]

def command(target, action, value):
    s, o = S["settings"], S["overview"]
    if target == "timer":
        if action == "set": S["timer_seconds"] = S["timer_set"] = int(value)
        elif action == "start":
            S["timer_set"] = int(value); S["timer_running"] = True; timer_end[0] = time.time() + int(value); S["timer_seconds"] = int(value)
        elif action == "cancel": S["timer_running"] = False; S["timer_seconds"] = S.get("timer_set", 300)
        elif action == "stop_sound": o["timer_sound_id"] = 0
    elif target == "player":
        if action in ("play", "resume"): S["player"] = "Playing"
        elif action == "pause": S["player"] = "Paused"
        elif action == "next": S["track"] = S["track"] % 45 + 1; S["player"] = "Playing"
        elif action == "previous": S["track"] = (S["track"] - 2) % 45 + 1; S["player"] = "Playing"
        elif action == "stop": S["player"] = "Closed"; S["player_sleep_preset"] = 0; S["player_sleep_seconds"] = 0; S["player_test"] = False
        elif action == "mode": S["player_mode"] = ["NORM", "SHUF", "REP1"][int(value)]
        elif action == "sleep": S["player_sleep_preset"] = int(value); sleep_end[0] = time.time() + 60 * int(value)
        elif action == "test_track": S["player_test"] = True; S["player"] = "Playing"; S["track"] = int(value)
        elif action == "test_stop": S["player_test"] = False; S["player"] = "Closed"
    elif target == "control":
        if action == "sound": o["sound_on"] = bool(int(value))
        elif action == "alarm_stop": o["alarm"]["active"] = 0
        elif action == "alarm_snooze":
            o["alarm"].update(snoozes=1, snooze_slot=o["alarm"]["active"], active=0); snooze_end[0] = time.time() + 180
        elif action == "snooze_cancel": o["alarm"].update(snoozes=0, snooze_slot=0); o["alarm"]["snooze_revision"] += 1
    elif target == "settings":
        s[action] = int(value); s["saving"] = "pending"
    elif target in ("alarm", "birthday"):
        v = [int(x) for x in str(value).split()]
        rec = S[target + "s"][v[0] - 1]
        if v[1] != rec["revision"]: return "conflict"
        if target == "alarm": rec.update(enabled=bool(v[2]), hour=v[3], minute=v[4], days=v[5], sound=v[6], track=v[7])
        else: rec.update(enabled=bool(v[2]), month=v[3], day=v[4], hour=v[5], minute=v[6], birth_year=v[7])
        rec["revision"] += 1
    elif target == "bluetooth":
        if action == "disconnect": BT.update(target="", connected=False); o["bluetooth"] = {"state": "off", "name": ""}
        elif action == "connect":
            dev = "%012X" % int(value); BT.update(target=dev, connected=True)
            o["bluetooth"] = {"state": "connected", "name": next(d["name"] for d in BT["devices"] if d["id"] == dev)}
        elif action == "scan": BT.update(scanning=True, target="", connected=False); o["bluetooth"] = {"state": "scanning", "name": ""}
        elif action == "cancel": BT.update(scanning=False); o["bluetooth"] = {"state": "off", "name": ""}
        BT["snapshot_id"] = S["command_id"]
    elif target == "network":
        NET["snapshot_id"] = S["command_id"]
    return "applied"

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else body.encode()
        self.send_response(code); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)
    def do_GET(self):
        path = self.path.split("?")[0]
        if path.startswith("/mock/"):
            scenario = path[6:]
            with lock:
                o = S["overview"]
                if scenario == "ring": o["alarm"].update(active=1, active_id=55)
                if scenario == "timer": S["timer_running"] = True; S["timer_set"] = 300; timer_end[0] = time.time() + 8
                if scenario == "music": S["player"] = "Playing"; S["player_sleep_preset"] = 30; sleep_end[0] = time.time() + 1750
                if scenario == "direct": o["network"]["mode"] = "direct"; NET.update(mode="direct", address="192.168.4.1"); WIFI.update(direct=True)
                if scenario == "offline": OFFLINE[0] = time.time() + 30
                if scenario == "untrusted": S["home_trusted"] = False
                if scenario == "quiet": o["quiet_now"] = True
            return self.send(200, "ok", "text/plain")
        if time.time() < OFFLINE[0] and path.endswith(".json"):
            return self.send(503, "{}")
        if path in ("/", "/index.html"):
            return self.send(200, open(PAGE, "rb").read(), "text/html; charset=utf-8")
        with lock:
            refresh()
            body = {"/status.json": S, "/bluetooth.json": BT, "/network.json": NET, "/wifi.json": WIFI, "/browsers.json": BROWSERS,
                    "/ota.json": OTA, "/wifi-scan.json": {"epoch": EPOCH, "revision": 1, "state": "idle", "entries": []}}.get(path)
        if body is None: return self.send(404, "{}")
        self.send(200, json.dumps(body))
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0)); body = self.rfile.read(length).decode()
        target = self.path.strip("/")
        if target == "access": return self.send(200, json.dumps({"slot": 1, "epoch": EPOCH, "revision": 3}))
        parts = body.split(" ", 5)
        with lock:
            if int(parts[2]) != S["command_id"] + 1: return self.send(409, "{}")
            S["command_id"] = int(parts[2]); S["command_nonce"] = int(parts[3])
            result = command(target, parts[4], parts[5] if len(parts) > 5 else "0")
            S["command_result"] = result; S["settings"]["snapshot_id"] = S["command_id"]
            if S["settings"]["saving"] == "pending":
                threading.Timer(5, lambda: S["settings"].__setitem__("saving", "saved")).start()
        self.send(200, "{}")

ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
