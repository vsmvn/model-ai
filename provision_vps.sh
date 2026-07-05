#!/usr/bin/env bash
# Provision SDXL + Wan2.1 + Gateway API trên Vast.ai instance (đã tùy biến đúng máy)
set -Eeuo pipefail

COMFY="/workspace/ComfyUI"
PUBLIC_IP="116.127.115.27"
API_INT_PORT="10200"          # nội bộ
API_EXT_PORT="40791"          # map ra ngoài (VAST_TCP_PORT_10200)
PUBLIC_BASE="http://${PUBLIC_IP}:${API_EXT_PORT}"
COMFY_URL="http://localhost:18188"
PY="/venv/main/bin/python"
HF="/venv/main/bin/hf"
LOG_DIR="/workspace/logs"
mkdir -p "$LOG_DIR"

step(){ echo -e "\n==> $*"; }
ok(){ echo "    [OK] $*"; }
die(){ echo -e "\n[LỖI] $*" >&2; exit 1; }
trap 'die "dừng ở dòng $LINENO"' ERR

dl(){ # repo file destdir
  local repo="$1" file="$2" dir="$3"
  mkdir -p "$dir"
  if [ -s "$dir/$(basename "$file")" ]; then ok "đã có $(basename "$file")"; return 0; fi
  step "tải $file"
  "$HF" download "$repo" "$file" --local-dir "$dir" >/dev/null || die "tải thất bại: $repo/$file"
  ok "xong $(basename "$file") ($(du -h "$dir/$(basename "$file")" 2>/dev/null | cut -f1))"
}

step "0. Kiểm tra disk"
df -h /workspace | tail -1

step "1. Model tạo ảnh (SDXL base + VAE)"
dl "stabilityai/stable-diffusion-xl-base-1.0" "sd_xl_base_1.0.safetensors" "$COMFY/models/checkpoints"
dl "stabilityai/sdxl-vae" "sdxl_vae.safetensors" "$COMFY/models/vae"

step "2. Model tạo video (Wan 2.1 T2V 1.3B)"
dl "Kijai/WanVideo_comfy" "Wan2_1-T2V-1_3B_fp16.safetensors" "$COMFY/models/wan"
dl "Kijai/WanVideo_comfy" "umt5-xxl-enc-fp8_e4m3fn.safetensors" "$COMFY/models/text_encoders"
dl "Kijai/WanVideo_comfy" "Wan2_1_VAE_bf16.safetensors" "$COMFY/models/vae"
mkdir -p "$COMFY/models/diffusion_models"
ln -sf "$COMFY/models/wan/Wan2_1-T2V-1_3B_fp16.safetensors" \
       "$COMFY/models/diffusion_models/Wan2_1-T2V-1_3B_fp16.safetensors"
ok "đã liên kết Wan vào diffusion_models"

step "2b. Plugin WanVideoWrapper + VideoHelperSuite"
CN="$COMFY/custom_nodes"
clone(){ local repo="$1" d="$CN/$2";
  if [ -d "$d/.git" ]; then git -C "$d" pull --ff-only -q || true;
  else git clone -q --depth 1 "$repo" "$d" || die "clone $2"; fi
  [ -f "$d/requirements.txt" ] && "$PY" -m pip install -q -r "$d/requirements.txt" || true
  ok "plugin $2"; }
clone "https://github.com/kijai/ComfyUI-WanVideoWrapper.git" "ComfyUI-WanVideoWrapper"
clone "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git" "ComfyUI-VideoHelperSuite"

step "3. Cài FastAPI + uvicorn"
"$PY" -m pip install -q --upgrade fastapi "uvicorn[standard]" requests pydantic || die "pip fastapi"
ok "fastapi/uvicorn ok"

step "3b. Ghi /workspace/api_server.py"
cat > /workspace/api_server.py <<'PYEOF'
# -*- coding: utf-8 -*-
import os, time, uuid, threading, random, requests
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

COMFY = os.environ.get("COMFY_URL", "http://localhost:18188")
COMFY_OUT = "/workspace/ComfyUI/output"
PUBLIC_BASE = os.environ.get("PUBLIC_BASE", "http://116.127.115.27:40791")

app = FastAPI(title="ComfyUI Gateway")
os.makedirs(COMFY_OUT, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=COMFY_OUT), name="outputs")

JOBS = {}
LOCK = threading.Lock()
NEG = "text, watermark, low quality, blurry, deformed"

class ImageReq(BaseModel):
    prompt: str
    width: int = 1024
    height: int = 1024

class VideoReq(BaseModel):
    prompt: str
    duration: int = 3

def wf_image(prompt, w, h):
    seed = random.randint(1, 2**31)
    return {
        "4":  {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}},
        "10": {"class_type": "VAELoader", "inputs": {"vae_name": "sdxl_vae.safetensors"}},
        "5":  {"class_type": "EmptyLatentImage", "inputs": {"width": w, "height": h, "batch_size": 1}},
        "6":  {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["4", 1]}},
        "7":  {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["4", 1]}},
        "3":  {"class_type": "KSampler", "inputs": {
                    "seed": seed, "steps": 30, "cfg": 7.0,
                    "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0,
                    "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0]}},
        "8":  {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["10", 0]}},
        "9":  {"class_type": "SaveImage", "inputs": {"filename_prefix": "api_img", "images": ["8", 0]}},
    }

def wf_video(prompt, duration):
    seed = random.randint(1, 2**31)
    frames = max(1, int(duration) * 16)
    frames = ((frames - 1) // 4) * 4 + 1
    return {
        "1": {"class_type": "WanVideoVAELoader", "inputs": {
                "model_name": "Wan2_1_VAE_bf16.safetensors", "precision": "bf16"}},
        "2": {"class_type": "LoadWanVideoT5TextEncoder", "inputs": {
                "model_name": "umt5-xxl-enc-fp8_e4m3fn.safetensors", "precision": "fp8_e4m3fn",
                "load_device": "offload_device", "quantization": "disabled"}},
        "3": {"class_type": "WanVideoModelLoader", "inputs": {
                "model": "Wan2_1-T2V-1_3B_fp16.safetensors", "base_precision": "bf16",
                "quantization": "disabled", "load_device": "main_device", "attention_mode": "sdpa"}},
        "4": {"class_type": "WanVideoTextEncode", "inputs": {
                "positive_prompt": prompt, "negative_prompt": NEG,
                "t5": ["2", 0], "force_offload": True}},
        "5": {"class_type": "WanVideoEmptyEmbeds", "inputs": {
                "width": 480, "height": 480, "num_frames": frames}},
        "6": {"class_type": "WanVideoSampler", "inputs": {
                "model": ["3", 0], "text_embeds": ["4", 0], "image_embeds": ["5", 0],
                "steps": 25, "cfg": 6.0, "shift": 8.0, "seed": seed,
                "scheduler": "unipc", "force_offload": True}},
        "7": {"class_type": "WanVideoDecode", "inputs": {
                "vae": ["1", 0], "samples": ["6", 0], "enable_vae_tiling": True}},
        "8": {"class_type": "VHS_VideoCombine", "inputs": {
                "images": ["7", 0], "frame_rate": 16, "loop_count": 0,
                "filename_prefix": "api_vid", "format": "video/h264-mp4",
                "pingpong": False, "save_output": True}},
    }

def submit(workflow):
    r = requests.post(f"{COMFY}/prompt", json={"prompt": workflow}, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"ComfyUI reject: {r.status_code} {r.text[:400]}")
    return r.json()["prompt_id"]

def find_result_url(entry):
    for node in entry.get("outputs", {}).values():
        for key in ("images", "gifs", "videos"):
            for item in node.get(key, []):
                fn = item.get("filename")
                if not fn: continue
                sub = item.get("subfolder", "")
                rel = f"{sub}/{fn}" if sub else fn
                return f"{PUBLIC_BASE}/outputs/{rel}"
    return None

def poll_job(job_id):
    jd = JOBS[job_id]; pid = jd["prompt_id"]
    for _ in range(1800):
        try:
            h = requests.get(f"{COMFY}/history/{pid}", timeout=15).json()
        except Exception:
            time.sleep(2); continue
        if pid in h:
            entry = h[pid]
            st = entry.get("status", {})
            url = find_result_url(entry)
            if url:
                with LOCK: jd.update(status="completed", progress=100, result_url=url); return
            if st.get("status_str") == "error":
                with LOCK: jd.update(status="failed", progress=100, error=str(st.get("messages"))); return
        try:
            q = requests.get(f"{COMFY}/queue", timeout=10).json()
            running = any(str(pid) == str(x[1]) for x in q.get("queue_running", []))
            with LOCK:
                if running and jd["progress"] < 90:
                    jd.update(status="running", progress=jd["progress"] + 3)
        except Exception:
            pass
        time.sleep(2)
    with LOCK: jd.update(status="failed", error="timeout", progress=100)

def start_job(t, wf):
    jid = uuid.uuid4().hex[:12]
    try: pid = submit(wf)
    except Exception as e: raise HTTPException(502, str(e))
    with LOCK:
        JOBS[jid] = {"prompt_id": pid, "type": t, "status": "queued",
                     "progress": 0, "result_url": None, "error": None}
    threading.Thread(target=poll_job, args=(jid,), daemon=True).start()
    return jid

@app.get("/health")
def health():
    try: up = requests.get(f"{COMFY}/system_stats", timeout=5).status_code == 200
    except Exception: up = False
    return {"status": "ok", "comfyui": "up" if up else "down"}

@app.post("/generate/image")
def gen_image(r: ImageReq): return {"job_id": start_job("image", wf_image(r.prompt, r.width, r.height))}

@app.post("/generate/video")
def gen_video(r: VideoReq): return {"job_id": start_job("video", wf_video(r.prompt, r.duration))}

@app.get("/status/{job_id}")
def status(job_id: str):
    with LOCK:
        jd = JOBS.get(job_id)
        if not jd: raise HTTPException(404, "job_id không tồn tại")
        return {"status": jd["status"], "progress": jd["progress"],
                "result_url": jd["result_url"], "error": jd["error"]}
PYEOF
ok "api_server.py đã ghi"

step "4. Đăng ký API vào supervisor (auto-restart)"
cat > /etc/supervisor/conf.d/genapi.conf <<CONF
[program:genapi]
command=/venv/main/bin/python -m uvicorn api_server:app --host 0.0.0.0 --port ${API_INT_PORT}
directory=/workspace
autostart=true
autorestart=true
startretries=999
environment=PUBLIC_BASE="${PUBLIC_BASE}",COMFY_URL="${COMFY_URL}"
stdout_logfile=${LOG_DIR}/genapi.log
stderr_logfile=${LOG_DIR}/genapi.err.log
CONF
supervisorctl reread >/dev/null && supervisorctl update >/dev/null
ok "supervisor: genapi đã thêm"

step "4b. Restart ComfyUI để nạp plugin Wan"
supervisorctl restart comfyui >/dev/null || die "restart comfyui"
ok "comfyui restarting"

step "5. Chờ ComfyUI online (nạp lại có thể mất 1-2 phút)"
for i in $(seq 1 90); do
  curl -sf "$COMFY_URL/system_stats" >/dev/null 2>&1 && { ok "ComfyUI online"; break; }
  sleep 2
done
step "5b. Chờ API online"
for i in $(seq 1 30); do
  curl -sf "http://localhost:${API_INT_PORT}/health" >/dev/null 2>&1 && { ok "API online"; break; }
  sleep 2
done

step "6. Test tạo 1 ảnh"
resp="$(curl -s -X POST "http://localhost:${API_INT_PORT}/generate/image" -H 'Content-Type: application/json' \
  -d '{"prompt":"a cute cat astronaut, highly detailed","width":1024,"height":1024}')"
echo "    resp: $resp"
jid="$(echo "$resp" | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4 || true)"
if [ -n "${jid:-}" ]; then
  for i in $(seq 1 80); do
    s="$(curl -s "http://localhost:${API_INT_PORT}/status/$jid")"
    echo "    [$i] $s"
    echo "$s" | grep -q '"status":"completed"' && { ok "TẠO ẢNH THÀNH CÔNG"; break; }
    echo "$s" | grep -q '"status":"failed"'    && { echo "    [!] ảnh fail"; break; }
    sleep 3
  done
fi

echo -e "\n================= HOÀN TẤT ================="
echo "  API base (dùng cái này):  ${PUBLIC_BASE}"
echo "  ComfyUI UI:               http://${PUBLIC_IP}:40794"
echo "  Endpoints:"
echo "    GET  ${PUBLIC_BASE}/health"
echo "    POST ${PUBLIC_BASE}/generate/image   {prompt,width,height}"
echo "    POST ${PUBLIC_BASE}/generate/video   {prompt,duration}"
echo "    GET  ${PUBLIC_BASE}/status/<job_id>"
echo "    file ảnh/video: ${PUBLIC_BASE}/outputs/<filename>"
echo "  Logs: ${LOG_DIR}/genapi.log  |  supervisorctl status"
echo "============================================"
