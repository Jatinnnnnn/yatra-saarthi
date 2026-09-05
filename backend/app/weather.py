"""Simulated weather - demo ke liye. Phase 5.
   (Asli open-meteo API M2 Week 3 me jodega; sim mode judge demo ke liye zaroori hai.)"""
_STATE = {"condition": "CLEAR", "rain_mm": 0.0, "district": "Dehradun"}


def get_weather():
    return dict(_STATE)


def set_storm(district="Dehradun", rain_mm=45.0):
    _STATE.update(condition="STORM", rain_mm=rain_mm, district=district)
    return get_weather()


def clear():
    _STATE.update(condition="CLEAR", rain_mm=0.0)
    return get_weather()