# -*- coding: utf-8 -*-
"""
Tự động STOP instance Vast khi rảnh quá IDLE_SECONDS (mặc định 600s = 10 phút).
- Coi là "bận" nếu ComfyUI còn job trong hàng đợi -> không stop giữa chừng.
- Mốc hoạt động do api_server.py ghi vào ACTIVITY_FILE mỗi khi có request.
Chạy dưới supervisor (program: idle_watchdog).
"""
import os, time, subprocess, requests

IDLE = int(os.environ.get("IDLE_SECONDS", "600"))
IID = os.environ.get("INSTANCE_ID", "").strip()
ACT = os.environ.get("ACTIVITY_FILE", "/workspace/.last_activity")
COMFY = os.environ.get("COMFY_URL", "http://localhost:18188")
VAST = "/opt/instance-tools/bin/vastai"
CHECK_EVERY = 30

def now():
    return time.time()

def read_activity():
    try:
        return float(open(ACT).read().strip())
    except Exception:
        return None

def touch(ts=None):
    try:
        open(ACT, "w").write(str(ts if ts is not None else now()))
    except OSError:
        pass

def comfy_busy():
    try:
        q = requests.get(f"{COMFY}/queue", timeout=8).json()
        return bool(q.get("queue_running")) or bool(q.get("queue_pending"))
    except Exception:
        return True   # không chắc chắn -> coi như bận cho an toàn

def main():
    if not IID:
        print("[watchdog] thiếu INSTANCE_ID, thoát.", flush=True)
        return
    if read_activity() is None:
        touch()   # grace: coi như vừa hoạt động lúc khởi động
    print(f"[watchdog] theo dõi instance {IID}, idle limit {IDLE}s", flush=True)
    while True:
        time.sleep(CHECK_EVERY)
        if comfy_busy():
            touch()                     # đang render -> reset đồng hồ
            continue
        la = read_activity()
        if la is None:
            touch(); continue
        idle = now() - la
        if idle >= IDLE:
            print(f"[watchdog] rảnh {int(idle)}s >= {IDLE}s -> STOP instance {IID}", flush=True)
            try:
                subprocess.run([VAST, "stop", "instance", str(IID)], timeout=90)
            except Exception as e:
                print(f"[watchdog] lỗi stop: {e}", flush=True)
            time.sleep(120)             # chờ instance tắt

if __name__ == "__main__":
    main()
