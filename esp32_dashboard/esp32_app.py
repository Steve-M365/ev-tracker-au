# ESP32 MicroPython dashboard (lvgl) — Waveshare C6 LCD
# USB serial + WiFi TCP JSON metrics
# Draws CPU/mem/network bars; touches ack Hermes/opencode alerts

# Boot / main.py — place on ESP32 root filesystem
# Requires lvgl + st7789/freertos MicroPython firmware from espressif or Waveshare build

CONFIG = {
    "wifi_ssid": "YOUR_WIFI",
    "wifi_pass": "YOUR_PASS",
    "host_tcp_port": 9000,
    "serial_baud": 115200,
    "chart_seconds": 60,
}

import json
import network
import time
import socket
from machine import UART, Pin, TouchPad, Timer

try:
    import lvgl as lv
    from lvgl import driver  # depends on build
except Exception as e:
    print("lvgl import failed:", e)
    lv = None

# Dummy display init if lv not available
_DISP = None
_CHART = None
_LABEL_ALERT = None


def wifi_connect(ssid, password):
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    if not sta.isconnected():
        sta.connect(ssid, password)
        for _ in range(20):
            if sta.isconnected():
                return sta
            time.sleep(0.5)
    return sta


def build_ui():
    global _DISP, _CHART, _LABEL_ALERT
    if lv is None:
        return
    lv.init()
    # Replace with actual display driver init for your hardware.
    # For Waveshare ESP32-C6-Touch-LCD-1.83, use provided ili/st7789 SPI driver.
    _DISP = lv.disp_create(320, 240)  # placeholder; use real driver
    scr = lv.scr_act()

    _LABEL_ALERT = lv.label(scr)
    _LABEL_ALERT.set_text("No alerts")
    _LABEL_ALERT.align(lv.ALIGN.TOP_MID, 0, 10)

    _CHART = lv.chart(scr)
    _CHART.set_size(300, 140)
    _CHART.align(lv.ALIGN.CENTER, 0, 40)
    _CHART.set_type(lv.chart.TYPE.LINE)
    _CHART.set_div_line_count(4, 4)
    ser1 = _CHART.add_series(lv.color_hex(0x0000FF))
    ser2 = _CHART.add_series(lv.color_hex(0xFF0000))
    _CHART.set_range(lv.CHART.AXIS.PRIMARY_Y, 0, 100)
    _CHART.set_range(lv.CHART.AXIS.PRIMARY_X, 0, 12)


def update_chart(cpu, mem):
    if _CHART is None:
        return
    # Roll history by adding points and shifting old
    _CHART.set_next_value(_CHART, cpu)  # series pointer implicit in some builds
    # If build requires explicit series pointer, replace with `chart.set_next_value(series, val)`


def touch_ack(pin):
    global _LABEL_ALERT
    if _LABEL_ALERT:
        _LABEL_ALERT.set_text("Alert ack'd")
        time.sleep(1)
        _LABEL_ALERT.set_text("No alerts")


def read_serial():
    # Try to read one JSON line from USB serial if wired
    uart = UART(1, baudrate=CONFIG["serial_baud"], rx=17, tx=18)
    line = uart.readline()
    if not line:
        return None
    try:
        return json.loads(line)
    except Exception:
        return None


def read_tcp():
    # Read one line from WiFi TCP host if connected
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        s.connect(("192.168.1.100", CONFIG["host_tcp_port"]))
        f = s.makefile("rwb")
        line = f.readline()
        s.close()
        if line:
            return json.loads(line)
    except Exception:
        return None


def loop():
    build_ui()
    wifi = wifi_connect(CONFIG["wifi_ssid"], CONFIG["wifi_pass"])
    tp = TouchPad(Pin(14))
    tp.irq(trigger=TouchPad.TOUCH_DOWN, handler=touch_ack)

    while True:
        data = read_serial() or read_tcp()
        if data:
            cpu = data.get("cpu", 0)
            mem = data.get("mem", 0)
            alert = data.get("alert", {})
            update_chart(cpu, mem)
            if alert and isinstance(alert, dict) and alert.get("alert"):
                _LABEL_ALERT.set_text("Hermes/Opencode needs input")
            else:
                _LABEL_ALERT.set_text("No alerts")
        time.sleep(5)


if __name__ == "__main__":
    loop()
