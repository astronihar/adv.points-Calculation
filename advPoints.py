from typing import Tuple
import math
from datetime import datetime, timedelta
import swisseph as swe

# Constants
ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula",
    "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# Utilities
def normalize_deg(deg: float) -> float:
    return deg % 360

def deg_to_zodiac(degree: float) -> Tuple[str, str, int, float]:
    degree = normalize_deg(degree)
    zodiac_index = int(degree // 30)
    zodiac = ZODIAC_SIGNS[zodiac_index]

    sign_degree = degree % 30  # Degree within the sign

    nak_index = int((degree % 360) / (360 / 27))
    nakshatra = NAKSHATRAS[nak_index]
    pada = int(((degree % (360 / 27)) % (360 / 27)) / (360 / 108)) + 1

    return zodiac, nakshatra, pada, sign_degree

def format_result(deg: float) -> Tuple[str, str, str, int]:
    deg = normalize_deg(deg)
    zodiac, nakshatra, pada, sign_degree = deg_to_zodiac(deg)
    d = int(sign_degree)
    m = int((sign_degree - d) * 60)
    s = int((((sign_degree - d) * 60) - m) * 60)
    dms_str = f"{d}°{m}′{s}″"
    return dms_str, zodiac, nakshatra, pada

# Core Point Calculations
def calc_bhrigu_bindu(moon_deg, rahu_deg):
    return format_result((moon_deg + rahu_deg) / 2)

def calc_prana_sphuta(lagna_deg, sun_deg, moon_deg):
    return format_result(lagna_deg + sun_deg + moon_deg)

def calc_deha_sphuta(lagna_deg, sun_deg, moon_deg):
    return format_result(lagna_deg + moon_deg - sun_deg)

def calc_mrityu_sphuta(lagna_deg, sun_deg, moon_deg):
    return format_result(lagna_deg + sun_deg - moon_deg)

def calc_tithi_sphuta(sun_deg, moon_deg):
    return format_result(sun_deg + moon_deg)

def calc_chatusphuta(lagna, sun, moon, gulika):
    return format_result(lagna + sun + moon + gulika)

def calc_panchasphuta(lagna, sun, moon, gulika, mandi):
    return format_result(lagna + sun + moon + gulika + mandi)

def calc_yoga_sphuta(sun, moon):
    return format_result(sun + moon)

def calc_avayoga_sphuta(sun, moon):
    return format_result(360 - ((sun + moon) % 360))

def calc_gulika(weekday: int, sunrise_deg: float) -> float:
    gulika_portions = {0: 7, 1: 6, 2: 5, 3: 4, 4: 3, 5: 2, 6: 1}
    offset_min = gulika_portions[weekday] * (720 / 8)
    return normalize_deg(sunrise_deg + (offset_min / 4))

def calc_mandi(weekday: int, sunrise_deg: float) -> float:
    mandi_portions = {0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1, 6: 0}
    offset_min = mandi_portions[weekday] * (720 / 8)
    return normalize_deg(sunrise_deg + (offset_min / 4))

# Swiss Ephemeris Setup
def compute_special_points():
    latitude = 28.6139   # Delhi
    longitude = 77.2090

    now_ist = datetime.now()
    now_utc = now_ist - timedelta(hours=5, minutes=30)

    swe.set_sid_mode(swe.SIDM_LAHIRI)

    jd = swe.julday(now_utc.year, now_utc.month, now_utc.day,
                    now_utc.hour + now_utc.minute / 60 + now_utc.second / 3600)

    cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b'A', swe.FLG_SIDEREAL)
    lagna = ascmc[swe.ASC]

    planets = {
        'Sun': swe.SUN,
        'Moon': swe.MOON,
        'Rahu': swe.MEAN_NODE
    }

    degs = {}
    for name, code in planets.items():
        pos, _ = swe.calc(jd, code, swe.FLG_SIDEREAL)
        degs[name] = pos[0]

    weekday = now_ist.weekday()
    sunrise_deg = 90.0  # Assume 6AM = 90° on ecliptic

    gulika_deg = calc_gulika(weekday, sunrise_deg)
    mandi_deg = calc_mandi(weekday, sunrise_deg)

    return {
        "Gulika": format_result(gulika_deg),
        "Mandi": format_result(mandi_deg),
        "Bhrigu Bindu": calc_bhrigu_bindu(degs['Moon'], degs['Rahu']),
        "Prana Sphuta": calc_prana_sphuta(lagna, degs['Sun'], degs['Moon']),
        "Deha Sphuta": calc_deha_sphuta(lagna, degs['Sun'], degs['Moon']),
        "Mrityu Sphuta": calc_mrityu_sphuta(lagna, degs['Sun'], degs['Moon']),
        "Tithi Sphuta": calc_tithi_sphuta(degs['Sun'], degs['Moon']),
        "Chatusphuta": calc_chatusphuta(lagna, degs['Sun'], degs['Moon'], gulika_deg),
        "PanchaSphuta": calc_panchasphuta(lagna, degs['Sun'], degs['Moon'], gulika_deg, mandi_deg),
        "Yoga Sphuta": calc_yoga_sphuta(degs['Sun'], degs['Moon']),
        "Avayoga Sphuta": calc_avayoga_sphuta(degs['Sun'], degs['Moon'])
    }

# Optional test
if __name__ == '__main__':
    from pprint import pprint
    pprint(compute_special_points())
