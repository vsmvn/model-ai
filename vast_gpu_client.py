# -*- coding: utf-8 -*-
"""
Client dùng TRÊN MÁY CHỦ GỌI (luôn online) để:
  1) Tự BẬT instance Vast nếu đang stopped (qua Vast REST API)
  2) Tự dò lại địa chỉ API (port map có thể đổi sau mỗi lần start)
  3) Chờ ComfyUI sẵn sàng, gửi job, poll kết quả, TẢI VỀ và LƯU tại máy gọi

Cài đặt: pip install requests
Biến môi trường cần đặt:
  VAST_API_KEY      = API key tài khoản Vast (Console -> Account -> API Key)
  VAST_INSTANCE_ID  = 43798651
  GPU_API_TOKEN     = token của API server (X-API-Key)
"""
import os, time, requests

VAST_KEY   = os.environ["VAST_API_KEY"]
INSTANCE   = os.environ.get("VAST_INSTANCE_ID", "43798651")
API_TOKEN  = os.environ["GPU_API_TOKEN"]
PORT_KEY   = "10200/tcp"                      # port nội bộ của API gateway
VAST_API   = "https://console.vast.ai/api/v0"
VHDR       = {"Authorization": f"Bearer {VAST_KEY}"}
AHDR       = {"X-API-Key": API_TOKEN}


# ----------------------------- Vast control ----------------------------------
def _instance():
    r = requests.get(f"{VAST_API}/instances/{INSTANCE}/", headers=VHDR, timeout=30)
    r.raise_for_status()
    return r.json()["instances"]

def _set_state(state):   # state = "running" | "stopped"
    r = requests.put(f"{VAST_API}/instances/{INSTANCE}/", headers=VHDR,
                     json={"state": state}, timeout=30)
    r.raise_for_status()

def base_url():
    inst = _instance()
    ip = (inst.get("public_ipaddr") or "").strip()
    hp = inst["ports"][PORT_KEY][0]["HostPort"]
    return f"http://{ip}:{hp}"

def ensure_ready(timeout=900):
    """Bật instance nếu cần, chờ tới khi /health báo comfyui=up. Trả base_url."""
    inst = _instance()
    if inst.get("actual_status") != "running":
        print("[client] instance đang stop -> gửi lệnh start...")
        _set_state("running")
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            if _instance().get("actual_status") == "running":
                b = base_url()
                h = requests.get(f"{b}/health", timeout=8).json()
                if h.get("comfyui") == "up":
                    print(f"[client] sẵn sàng: {b}")
                    return b
        except Exception:
            pass
        time.sleep(5)
    raise TimeoutError("Instance/ComfyUI không sẵn sàng kịp thời")

def stop_now():
    """(Tùy chọn) chủ động stop ngay để tiết kiệm, thay vì đợi watchdog."""
    _set_state("stopped")


# ----------------------------- Job helpers -----------------------------------
def _wait(b, job_id, timeout=1800):
    t0 = time.time()
    while time.time() - t0 < timeout:
        s = requests.get(f"{b}/status/{job_id}", headers=AHDR, timeout=15).json()
        if s["status"] == "completed":
            return s["result_url"]
        if s["status"] in ("failed", "expired"):
            raise RuntimeError(f"job lỗi: {s}")
        time.sleep(3)
    raise TimeoutError("job quá thời gian")

def _download(url, save_to):
    data = requests.get(url, headers=AHDR, timeout=180).content
    if save_to:
        with open(save_to, "wb") as f:
            f.write(data)
    return data

def generate_image(prompt, width=1024, height=1024, save_to=None):
    b = ensure_ready()
    jid = requests.post(f"{b}/generate/image", headers=AHDR,
                        json={"prompt": prompt, "width": width, "height": height},
                        timeout=30).json()["job_id"]
    print(f"[client] image job {jid} ...")
    return _download(_wait(b, jid), save_to)

def generate_video(prompt, duration=3, save_to=None):
    b = ensure_ready()
    jid = requests.post(f"{b}/generate/video", headers=AHDR,
                        json={"prompt": prompt, "duration": duration},
                        timeout=30).json()["job_id"]
    print(f"[client] video job {jid} ...")
    return _download(_wait(b, jid, timeout=3600), save_to)


if __name__ == "__main__":
    # Demo: tạo 1 ảnh và 1 video, lưu tại máy gọi
    generate_image("a red sports car on a mountain road, cinematic", save_to="out.png")
    print("Đã lưu out.png")
    generate_video("a red fox running through snow, cinematic", duration=3, save_to="out.mp4")
    print("Đã lưu out.mp4")
