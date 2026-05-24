#!/usr/bin/env python3
"""
📱 Phone Trackpad Server — Windows/Linux/Mac
Kurulum : pip install websockets pyautogui
Çalıştır: python server.py
Telefonda: http://<IP>:8766
"""

import asyncio, json, os, socket, threading, time
from http.server import HTTPServer, SimpleHTTPRequestHandler

try:
    import pyautogui
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0
    HAS_GUI = True
except ImportError:
    HAS_GUI = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:    s.connect(("8.8.8.8", 80)); return s.getsockname()[0]
    except: return "127.0.0.1"
    finally: s.close()

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw): super().__init__(*a, directory=SCRIPT_DIR, **kw)
    def log_message(self, *_): pass

def start_http(port):
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()

# Sub-pixel scroll accumulator (same pattern as fingerfly)
scroll_acc_x = 0.0
scroll_acc_y = 0.0
SCROLL_SPEED = 0.4   # tweak this if scroll is too fast/slow

async def handle(ws):
    global scroll_acc_x, scroll_acc_y
    print(f"📱 Bağlandı: {ws.remote_address[0]}")
    lock_until = 0

    try:
        import websockets
        async for raw in ws:
            if not HAS_GUI: continue
            try:
                msg = json.loads(raw)
                a = msg.get("action") or msg.get("type")

                if a == "move":
                    if time.time() < lock_until: continue
                    x, y = pyautogui.position()
                    pyautogui.moveTo(x + msg.get("dx", 0), y + msg.get("dy", 0))

                elif a == "click":
                    pyautogui.click(button="left")

                elif a == "rightclick":
                    pyautogui.rightClick()
                    lock_until = time.time() + 0.5

                elif a == "doubleclick":
                    pyautogui.doubleClick()

                elif a == "middleclick":
                    pyautogui.click(button="middle")

                elif a == "mousedown":
                    pyautogui.mouseDown()

                elif a == "mouseup":
                    pyautogui.mouseUp()

                elif a == "scroll":
                    # fingerfly sends dx/dy pixel deltas; we accumulate sub-pixel
                    scroll_acc_x += msg.get("dx", 0) * SCROLL_SPEED
                    scroll_acc_y += msg.get("dy", 0) * SCROLL_SPEED

                    sx = int(scroll_acc_x)
                    sy = int(scroll_acc_y)

                    if sx != 0 or sy != 0:
                        # pyautogui.scroll positive = up, negative = down
                        pyautogui.scroll(-sy)   # dy: positive finger down = scroll down
                        scroll_acc_x -= sx
                        scroll_acc_y -= sy

                elif a == "key":
                    key = msg.get("key", "")
                    if key: pyautogui.press(key)

                elif a == "hotkey":
                    keys = msg.get("keys", [])
                    if keys: pyautogui.hotkey(*keys)

                elif a == "type":
                    text = msg.get("text", "")
                    if text: pyautogui.write(text, interval=0.02)

            except Exception as e:
                print(f"⚠ {e}")

    except Exception:
        pass
    print(f"📴 Kesildi: {ws.remote_address[0]}")

async def main():
    import websockets
    ip, ws_port, http_port = get_ip(), 8765, 8766

    threading.Thread(target=start_http, args=(http_port,), daemon=True).start()

    print("=" * 55)
    print("  📱 Phone Trackpad Sunucusu Başlatıldı!")
    print("=" * 55)
    print(f"\n  🌐 Telefonda aç: http://{ip}:{http_port}\n")
    print(f"  WS: ws://{ip}:{ws_port}")
    print(f"\n  Ctrl+C ile durdur")
    print("=" * 55)

    async with websockets.serve(handle, "0.0.0.0", ws_port):
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Kapatıldı.")
