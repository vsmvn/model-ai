# -*- coding: utf-8 -*-
import os, io, time, uuid, threading, random, requests
from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel

COMFY = os.environ.get("COMFY_URL", "http://localhost:18188")
COMFY_OUT = "/workspace/ComfyUI/output"
COMFY_IN = "/workspace/ComfyUI/input"
PUBLIC_BASE = os.environ.get("PUBLIC_BASE", "http://116.127.115.27:40791")
OLLAMA = os.environ.get("OLLAMA_URL", "http://localhost:11434")
CHAT_MODEL = os.environ.get("CHAT_MODEL", "qwen2.5:7b")
TTS_URL = os.environ.get("TTS_URL", "http://localhost:10300")
RESULT_TTL = int(os.environ.get("RESULT_TTL", "3600"))   # giây giữ trong RAM
MAX_RESULTS = 50                                          # số kết quả tối đa giữ trong RAM
API_TOKEN = os.environ.get("API_TOKEN", "").strip()      # rỗng = tắt bảo mật
ACTIVITY_FILE = os.environ.get("ACTIVITY_FILE", "/workspace/.last_activity")
OPEN_PATHS = ("/health", "/docs", "/openapi.json", "/redoc")

app = FastAPI(title="ComfyUI Gateway")


@app.middleware("http")
async def gate(request: Request, call_next):
    path = request.url.path
    # ghi mốc thời gian hoạt động (cho watchdog tự-stop) — trừ /health
    if path != "/health":
        try:
            with open(ACTIVITY_FILE, "w") as fh:
                fh.write(str(time.time()))
        except OSError:
            pass
    # kiểm tra token (bỏ qua các path công khai)
    if API_TOKEN and path not in OPEN_PATHS:
        tok = request.headers.get("x-api-key", "")
        auth = request.headers.get("authorization", "")
        if auth[:7].lower() == "bearer ":
            tok = auth[7:].strip()
        if tok != API_TOKEN:
            return JSONResponse({"detail": "unauthorized: thiếu hoặc sai API token"}, status_code=401)
    return await call_next(request)

JOBS = {}          # job_id -> {status, progress, result_url, error, prompt_id, type}
RESULTS = {}       # job_id -> {bytes, media_type, filename, ts}
LOCK = threading.Lock()
NEG = "text, watermark, low quality, blurry, deformed"
NEG_VID = "bright colors, overexposed, static, blurred details, subtitles, worst quality, low quality"

MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".webp": "image/webp", ".gif": "image/gif",
        ".mp4": "video/mp4", ".webm": "video/webm", ".mkv": "video/x-matroska"}

class ImageReq(BaseModel):
    prompt: str
    width: int = 1024
    height: int = 1024
    model: str = "flux"          # "flux" (Kontext) | "sdxl" (Stable Diffusion XL)

class VideoReq(BaseModel):
    prompt: str
    duration: int = 3
    model: str = "wan"           # "wan" (Wan 2.2, đẹp) | "ltx" (LTX-Video, nhanh nhất)

class ChatReq(BaseModel):
    message: str
    system: str = "Bạn là trợ lý AI hữu ích, trả lời ngắn gọn bằng tiếng Việt."

class TTSReq(BaseModel):
    text: str
    voice: str = "nu-nhe-nhang"

# ----------------------------- Workflows -------------------------------------
def _flux_loaders():
    # FLUX.1 Kontext dev (split): UNET + DualCLIP + VAE
    return {
        "37": {"class_type": "UNETLoader", "inputs": {
                "unet_name": "flux1-dev-kontext_fp8_scaled.safetensors", "weight_dtype": "default"}},
        "38": {"class_type": "DualCLIPLoader", "inputs": {
                "clip_name1": "clip_l.safetensors", "clip_name2": "t5xxl_fp8_e4m3fn_scaled.safetensors",
                "type": "flux"}},
        "39": {"class_type": "VAELoader", "inputs": {"vae_name": "ae.safetensors"}},
    }

def wf_image(prompt, w, h):
    # FLUX Kontext — text -> image
    seed = random.randint(1, 2**31)
    g = _flux_loaders()
    g["6"]  = {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["38", 0]}}
    g["35"] = {"class_type": "FluxGuidance", "inputs": {"conditioning": ["6", 0], "guidance": 3.5}}
    g["45"] = {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["6", 0]}}
    g["5"]  = {"class_type": "EmptySD3LatentImage", "inputs": {"width": w, "height": h, "batch_size": 1}}
    g["31"] = {"class_type": "KSampler", "inputs": {
                "seed": seed, "steps": 20, "cfg": 1.0, "sampler_name": "euler",
                "scheduler": "simple", "denoise": 1.0,
                "model": ["37", 0], "positive": ["35", 0], "negative": ["45", 0], "latent_image": ["5", 0]}}
    g["8"]  = {"class_type": "VAEDecode", "inputs": {"samples": ["31", 0], "vae": ["39", 0]}}
    g["9"]  = {"class_type": "SaveImage", "inputs": {"filename_prefix": "api_img", "images": ["8", 0]}}
    return g

def wf_image_sdxl(prompt, w, h):
    # Stable Diffusion XL base 1.0
    seed = random.randint(1, 2**31)
    return {
        "4":  {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}},
        "10": {"class_type": "VAELoader", "inputs": {"vae_name": "sdxl_vae.safetensors"}},
        "5":  {"class_type": "EmptyLatentImage", "inputs": {"width": w, "height": h, "batch_size": 1}},
        "6":  {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["4", 1]}},
        "7":  {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["4", 1]}},
        "3":  {"class_type": "KSampler", "inputs": {
                    "seed": seed, "steps": 30, "cfg": 7.0, "sampler_name": "dpmpp_2m",
                    "scheduler": "karras", "denoise": 1.0,
                    "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0]}},
        "8":  {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["10", 0]}},
        "9":  {"class_type": "SaveImage", "inputs": {"filename_prefix": "api_img", "images": ["8", 0]}},
    }

def wf_edit(instruction, image_name, guidance=3.0):
    # FLUX Kontext — ảnh + câu lệnh -> sửa ảnh, GIỮ nhân vật.
    # guidance cao = bám câu lệnh mạnh hơn (đỡ bị "trả lại ảnh gốc").
    seed = random.randint(1, 2**31)
    g = _flux_loaders()
    g["41"] = {"class_type": "LoadImage", "inputs": {"image": image_name}}
    g["42"] = {"class_type": "FluxKontextImageScale", "inputs": {"image": ["41", 0]}}
    g["43"] = {"class_type": "VAEEncode", "inputs": {"pixels": ["42", 0], "vae": ["39", 0]}}
    g["6"]  = {"class_type": "CLIPTextEncode", "inputs": {"text": instruction, "clip": ["38", 0]}}
    g["44"] = {"class_type": "ReferenceLatent", "inputs": {"conditioning": ["6", 0], "latent": ["43", 0]}}
    g["35"] = {"class_type": "FluxGuidance", "inputs": {"conditioning": ["44", 0], "guidance": float(guidance)}}
    g["45"] = {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["6", 0]}}
    g["31"] = {"class_type": "KSampler", "inputs": {
                "seed": seed, "steps": 20, "cfg": 1.0, "sampler_name": "euler",
                "scheduler": "simple", "denoise": 1.0,
                "model": ["37", 0], "positive": ["35", 0], "negative": ["45", 0], "latent_image": ["43", 0]}}
    g["8"]  = {"class_type": "VAEDecode", "inputs": {"samples": ["31", 0], "vae": ["39", 0]}}
    g["9"]  = {"class_type": "SaveImage", "inputs": {"filename_prefix": "api_edit", "images": ["8", 0]}}
    return g

def _combine(img_node, fps):
    return {"class_type": "VHS_VideoCombine", "inputs": {
            "images": [img_node, 0], "frame_rate": float(fps), "loop_count": 0,
            "filename_prefix": "api_vid", "format": "video/h264-mp4",
            "pingpong": False, "save_output": True}}

def wf_video_wan(prompt, duration):
    # Wan 2.2 TI2V-5B (WanVideoWrapper) — nhanh ~40s, đẹp
    seed = random.randint(1, 2**31)
    W, H, FPS = 704, 480, 24
    frames = ((max(1, int(duration) * FPS) - 1) // 4) * 4 + 1
    return {
        "1": {"class_type": "WanVideoVAELoader", "inputs": {"model_name": "Wan2_2_VAE_bf16.safetensors", "precision": "bf16"}},
        "2": {"class_type": "LoadWanVideoT5TextEncoder", "inputs": {
                "model_name": "umt5-xxl-enc-fp8_e4m3fn.safetensors", "precision": "bf16",
                "load_device": "offload_device", "quantization": "fp8_e4m3fn"}},
        "3": {"class_type": "WanVideoModelLoader", "inputs": {
                "model": "Wan2_2-TI2V-5B-Turbo_fp16.safetensors", "base_precision": "bf16",
                "quantization": "fp8_e4m3fn", "load_device": "main_device"}},
        "4": {"class_type": "WanVideoTextEncode", "inputs": {
                "positive_prompt": prompt, "negative_prompt": NEG_VID, "t5": ["2", 0], "force_offload": True}},
        "5": {"class_type": "WanVideoEmptyEmbeds", "inputs": {"width": W, "height": H, "num_frames": frames}},
        "6": {"class_type": "WanVideoSampler", "inputs": {
                "model": ["3", 0], "image_embeds": ["5", 0], "text_embeds": ["4", 0],
                "steps": 8, "cfg": 1.0, "shift": 5.0, "seed": seed, "force_offload": True,
                "scheduler": "unipc", "riflex_freq_index": 0}},
        "7": {"class_type": "WanVideoDecode", "inputs": {
                "vae": ["1", 0], "samples": ["6", 0], "enable_vae_tiling": True,
                "tile_x": 272, "tile_y": 272, "tile_stride_x": 144, "tile_stride_y": 128}},
        "8": _combine("7", FPS),
    }

def wf_video_ltx(prompt, duration):
    # LTX-Video 2B distilled — rất nhanh ~15s
    seed = random.randint(1, 2**31)
    W, H, FPS = 768, 512, 25
    length = ((max(1, int(duration) * FPS) - 1) // 8) * 8 + 1
    return {
        "1":  {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "ltxv-2b-0.9.8-distilled.safetensors"}},
        "2":  {"class_type": "CLIPLoader", "inputs": {"clip_name": "t5xxl_fp8_e4m3fn_scaled.safetensors", "type": "ltxv"}},
        "3":  {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": prompt}},
        "4":  {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": NEG_VID}},
        "5":  {"class_type": "LTXVConditioning", "inputs": {
                "positive": ["3", 0], "negative": ["4", 0], "frame_rate": float(FPS)}},
        "6":  {"class_type": "EmptyLTXVLatentVideo", "inputs": {
                "width": W, "height": H, "length": length, "batch_size": 1}},
        "7":  {"class_type": "LTXVScheduler", "inputs": {
                "steps": 12, "max_shift": 2.05, "base_shift": 0.95, "stretch": True, "terminal": 0.1}},
        "8":  {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
        "9":  {"class_type": "SamplerCustom", "inputs": {
                "model": ["1", 0], "add_noise": True, "noise_seed": seed, "cfg": 1.0,
                "positive": ["5", 0], "negative": ["5", 1], "sampler": ["8", 0],
                "sigmas": ["7", 0], "latent_image": ["6", 0]}},
        "10": {"class_type": "VAEDecode", "inputs": {"samples": ["9", 0], "vae": ["1", 2]}},
        "11": _combine("10", FPS),
    }

def wf_video(prompt, duration, model="wan"):
    return wf_video_ltx(prompt, duration) if model == "ltx" else wf_video_wan(prompt, duration)

def wf_i2v(prompt, duration, image_name):
    raise HTTPException(503, "Ảnh→video hiện chưa bật với bộ model này.")

def upload_image_to_comfy(raw, filename):
    """Đẩy ảnh vào ComfyUI/input, trả tên file để LoadImage dùng."""
    boundary = "----apiboundary" + uuid.uuid4().hex
    ct = "image/png" if filename.lower().endswith(".png") else "image/jpeg"
    body = (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{filename}\"\r\n"
        f"Content-Type: {ct}\r\n\r\n").encode() + raw + \
        f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{boundary}--\r\n".encode()
    r = requests.post(f"{COMFY}/upload/image", data=body,
                      headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"upload ảnh vào ComfyUI lỗi: {r.status_code} {r.text[:200]}")
    j = r.json()
    return (j.get("subfolder") + "/" + j["name"]) if j.get("subfolder") else j["name"]

# ----------------------------- ComfyUI helpers -------------------------------
def submit(workflow):
    r = requests.post(f"{COMFY}/prompt", json={"prompt": workflow}, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"ComfyUI reject: {r.status_code} {r.text[:500]}")
    return r.json()["prompt_id"]

def list_output_files(entry):
    """Trả về [(subfolder, filename)] các file kết quả (bỏ preview 'temp')."""
    files = []
    for node in entry.get("outputs", {}).values():
        for key in ("images", "gifs", "videos"):
            for item in node.get(key, []):
                fn = item.get("filename")
                if not fn or item.get("type") == "temp":
                    continue
                files.append((item.get("subfolder", ""), fn))
    return files

def purge_expired():
    now = time.time()
    with LOCK:
        for jid in [j for j, v in RESULTS.items() if now - v["ts"] > RESULT_TTL]:
            RESULTS.pop(jid, None)
            if jid in JOBS:
                JOBS[jid]["status"] = "expired"
                JOBS[jid]["result_url"] = None
        # giới hạn số lượng: bỏ cái cũ nhất
        while len(RESULTS) > MAX_RESULTS:
            oldest = min(RESULTS, key=lambda k: RESULTS[k]["ts"])
            RESULTS.pop(oldest, None)

def capture_and_wipe(job_id, entry):
    """Đọc file kết quả vào RAM rồi XÓA khỏi đĩa. True nếu có kết quả."""
    outs = list_output_files(entry)
    if not outs:
        return False
    # ưu tiên file video nếu có, ngược lại lấy file đầu
    def is_video(fn): return os.path.splitext(fn)[1].lower() in (".mp4", ".webm", ".mkv", ".gif")
    primary = next(((s, f) for s, f in outs if is_video(f)), outs[0])
    sub, fn = primary
    path = os.path.join(COMFY_OUT, sub, fn)
    data = None
    for _ in range(10):                       # chờ file ghi xong
        try:
            with open(path, "rb") as fh:
                data = fh.read()
            if data:
                break
        except FileNotFoundError:
            pass
        time.sleep(0.5)
    if not data:
        return False
    media_type = MIME.get(os.path.splitext(fn)[1].lower(), "application/octet-stream")
    with LOCK:
        RESULTS[job_id] = {"bytes": data, "media_type": media_type, "filename": fn, "ts": time.time()}
    # XÓA mọi file kết quả của job này khỏi đĩa
    for s, f in outs:
        try:
            os.remove(os.path.join(COMFY_OUT, s, f))
        except OSError:
            pass
    return True

def _del_input(name):
    if not name:
        return
    try:
        os.remove(os.path.join(COMFY_IN, os.path.basename(name)))
    except OSError:
        pass

def poll_job(job_id):
    jd = JOBS[job_id]; pid = jd["prompt_id"]; inp = jd.get("input_image")
    for _ in range(2400):
        try:
            h = requests.get(f"{COMFY}/history/{pid}", timeout=15).json()
        except Exception:
            time.sleep(2); continue
        if pid in h:
            entry = h[pid]
            st = entry.get("status", {})
            if capture_and_wipe(job_id, entry):
                purge_expired(); _del_input(inp)
                with LOCK:
                    jd.update(status="completed", progress=100,
                              result_url=f"{PUBLIC_BASE}/result/{job_id}")
                return
            if st.get("status_str") == "error":
                _del_input(inp)
                with LOCK: jd.update(status="failed", progress=100, error=str(st.get("messages"))); return
        try:
            q = requests.get(f"{COMFY}/queue", timeout=10).json()
            running = any(str(pid) == str(x[1]) for x in q.get("queue_running", []))
            with LOCK:
                if running and jd["progress"] < 90:
                    jd.update(status="running", progress=jd["progress"] + 2)
        except Exception:
            pass
        time.sleep(2)
    _del_input(inp)
    with LOCK: jd.update(status="failed", error="timeout", progress=100)

def start_job(t, wf, input_image=None):
    jid = uuid.uuid4().hex[:12]
    try: pid = submit(wf)
    except Exception as e: raise HTTPException(502, str(e))
    with LOCK:
        JOBS[jid] = {"prompt_id": pid, "type": t, "status": "queued",
                     "progress": 0, "result_url": None, "error": None, "input_image": input_image}
    threading.Thread(target=poll_job, args=(jid,), daemon=True).start()
    return jid

def maybe_translate(text):
    """Nếu prompt có tiếng Việt (non-ASCII) -> dịch sang tiếng Anh qua Qwen để model ảnh/video hiểu đúng."""
    text = (text or "").strip()
    if not text or text.isascii():
        return text
    try:
        r = requests.post(f"{OLLAMA}/api/chat", json={"model": CHAT_MODEL, "messages": [
            {"role": "system", "content": "You translate Vietnamese image/video generation prompts into concise, vivid English. Output ONLY the English prompt — no quotes, no notes, no explanation."},
            {"role": "user", "content": text}], "stream": False, "options": {"temperature": 0.2}}, timeout=40)
        out = r.json().get("message", {}).get("content", "").strip().strip('"')
        return out or text
    except Exception:
        return text

# ----------------------------- Endpoints -------------------------------------
@app.get("/health")
def health():
    try: up = requests.get(f"{COMFY}/system_stats", timeout=5).status_code == 200
    except Exception: up = False
    try: chat_up = requests.get(f"{OLLAMA}/api/tags", timeout=3).status_code == 200
    except Exception: chat_up = False
    return {"status": "ok", "comfyui": "up" if up else "down",
            "chat": "up" if chat_up else "down", "results_in_ram": len(RESULTS)}

@app.post("/chat")
def chat(r: ChatReq):
    msgs = []
    if r.system: msgs.append({"role": "system", "content": r.system})
    msgs.append({"role": "user", "content": r.message})
    try:
        resp = requests.post(f"{OLLAMA}/api/chat",
                             json={"model": CHAT_MODEL, "messages": msgs, "stream": False}, timeout=180)
        if resp.status_code != 200:
            raise HTTPException(502, f"chat lỗi: {resp.status_code} {resp.text[:200]}")
        return {"reply": resp.json().get("message", {}).get("content", "")}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(502, f"chat lỗi: {e}")

@app.post("/generate/image")
def gen_image(r: ImageReq):
    p = maybe_translate(r.prompt)
    wf = wf_image_sdxl(p, r.width, r.height) if r.model == "sdxl" else wf_image(p, r.width, r.height)
    return {"job_id": start_job("image", wf)}

@app.post("/generate/edit")
async def gen_edit(prompt: str = Form(...), image: UploadFile = File(...), guidance: float = Form(3.0)):
    raw = await image.read()
    if not raw:
        raise HTTPException(400, "ảnh trống")
    ext = ".png" if (image.filename or "").lower().endswith(".png") else ".jpg"
    name = f"api_edit_in_{uuid.uuid4().hex[:10]}{ext}"
    try:
        comfy_name = upload_image_to_comfy(raw, name)
    except Exception as e:
        raise HTTPException(502, str(e))
    return {"job_id": start_job("edit", wf_edit(maybe_translate(prompt), comfy_name, guidance), input_image=comfy_name)}

VIDEO_ENABLED = True   # Wan 2.2 5B đã cài
VIDEO_MSG = "Tạo video tạm ngưng: đã gỡ Wan để cài FLUX (ảnh). Cần VPS lớn hơn để chạy cả hai."

@app.post("/generate/video")
def gen_video(r: VideoReq):
    return {"job_id": start_job("video", wf_video(maybe_translate(r.prompt), r.duration, r.model))}

@app.post("/generate/image-to-video")
async def gen_i2v(prompt: str = Form(""), duration: int = Form(3), image: UploadFile = File(...)):
    raise HTTPException(503, "Ảnh→video chưa có: HunyuanVideo hiện chỉ cài bản text→video.")
    raw = await image.read()
    if not raw:
        raise HTTPException(400, "ảnh trống")
    ext = ".png" if (image.filename or "").lower().endswith(".png") else ".jpg"
    name = f"api_in_{uuid.uuid4().hex[:10]}{ext}"
    try:
        comfy_name = upload_image_to_comfy(raw, name)
    except Exception as e:
        raise HTTPException(502, str(e))
    jid = start_job("i2v", wf_i2v(prompt, duration, comfy_name), input_image=comfy_name)
    return {"job_id": jid}

@app.get("/status/{job_id}")
def status(job_id: str):
    purge_expired()
    with LOCK:
        jd = JOBS.get(job_id)
        if not jd: raise HTTPException(404, "job_id không tồn tại")
        return {"status": jd["status"], "progress": jd["progress"],
                "result_url": jd["result_url"], "error": jd["error"]}

@app.get("/result/{job_id}")
def result(job_id: str):
    purge_expired()
    with LOCK:
        res = RESULTS.get(job_id)
    if not res:
        raise HTTPException(410, "kết quả không còn (đã hết hạn hoặc đã xóa)")
    headers = {"Content-Disposition": f'inline; filename="{res["filename"]}"'}
    return Response(content=res["bytes"], media_type=res["media_type"], headers=headers)

@app.delete("/result/{job_id}")
def delete_result(job_id: str):
    with LOCK:
        existed = RESULTS.pop(job_id, None) is not None
        if job_id in JOBS:
            JOBS[job_id]["result_url"] = None
    return {"deleted": existed}
