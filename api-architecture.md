# Kỹ thuật — Viết API cho AI & Bật/Tắt VPS tiết kiệm

Tài liệu thiết kế: cách xây **1 API gateway** thống nhất cho AI (chat/ảnh/video/...) và cách **tự động bật/tắt VPS GPU qua Vast API** để chỉ trả tiền khi dùng.

---

## Phần A — Kiến trúc API gateway

```
[Máy gọi / Web / App]
        │  HTTP + token
        ▼
[API Gateway  api_server.py :10200]  ──►  ComfyUI :18188  (ảnh/video)
   • token, dịch VN→EN, no-persist     └►  Ollama  :11434  (chat/vision)
        │                              └►  TTS/khác
        ▼  (Vast map 10200 -> port ngoài)
   http://<ip>:<port_ngoài>
```

### Vì sao cần gateway (đừng gọi thẳng ComfyUI/Ollama)
1. **Bảo mật**: giữ token 1 chỗ; ComfyUI/Ollama không có auth, không nên phơi ra internet.
2. **Đơn giản hoá**: che workflow phức tạp của ComfyUI sau endpoint gọn (`/generate/image {prompt}`).
3. **Chuẩn hoá**: cùng 1 kiểu request/response cho mọi model; đổi model backend không đổi API.
4. **Tính năng chung**: dịch prompt, không lưu đĩa, hàng đợi, quản lý job.

### Các mẫu thiết kế (design patterns)

**1. Job bất đồng bộ (ảnh/video — mất giây→phút):**
```
POST /generate/xxx  -> {job_id}          (nhận việc, chạy nền)
GET  /status/{id}   -> {status,progress} (poll tới completed)
GET  /result/{id}   -> bytes             (tải kết quả)
```
Lý do: request tạo ảnh/video lâu → không giữ HTTP mở; client poll.

**2. Đồng bộ (chat/TTS — nhanh):** gọi 1 lần trả kết quả ngay (`POST /chat -> {reply}`).

**3. Bảo mật token:** middleware kiểm header `X-API-Key`/`Bearer`; chừa `/health` mở.
```python
@app.middleware("http")
async def gate(request, call_next):
    if API_TOKEN and request.url.path not in OPEN_PATHS:
        tok = request.headers.get("x-api-key") or request.headers.get("authorization","")[7:]
        if tok != API_TOKEN:
            return JSONResponse({"detail":"unauthorized"}, 401)
    return await call_next(request)
```

**4. Không lưu đĩa (no-persist):** đọc file kết quả vào RAM → **xóa file** → phục vụ qua `/result` (TTL 60'). Tránh đầy đĩa + riêng tư.

**5. Tự dịch prompt VN→EN:** model ảnh/video hiểu tiếng Anh tốt nhất → dịch qua LLM trước khi tạo:
```python
def maybe_translate(text):
    if text.isascii(): return text        # đã là tiếng Anh
    r = requests.post(f"{OLLAMA}/api/chat", json={"model":CHAT_MODEL,"messages":[
        {"role":"system","content":"Translate to concise English. Output only the translation."},
        {"role":"user","content":text}],"stream":False})
    return r.json()["message"]["content"].strip() or text
```

**6. Chọn model động:** field `model` trong request → dispatch workflow:
```python
def wf_video(prompt, duration, model="wan"):
    return wf_video_ltx(...) if model=="ltx" else wf_video_wan(...)
```

### Gọi ComfyUI từ gateway
```python
# gửi workflow (API format) -> nhận prompt_id
pid = requests.post(f"{COMFY}/prompt", json={"prompt": workflow}).json()["prompt_id"]
# poll /history/{pid} tới khi có outputs -> đọc file trong ComfyUI/output
h = requests.get(f"{COMFY}/history/{pid}").json()
```
Lấy đúng **workflow API-format**: dựng trong ComfyUI UI → Save (API Format), hoặc suy từ template + `GET /object_info` (schema node).

### Thêm 1 model/endpoint mới (checklist)
1. Tải model → `models/...` (xem catalog).
2. Viết hàm `wf_xxx(prompt,...)` trả JSON workflow (tham số đúng theo `/object_info`).
3. Thêm endpoint `@app.post("/generate/xxx")` → `start_job(...)`.
4. (Nếu cần chọn) thêm field `model` + dispatch.
5. Restart genapi. Test bằng curl.

### Endpoint chuẩn của gateway (tham khảo api_server.py)
`/health` · `/chat` · `/generate/image` · `/generate/video` · `/generate/edit` · `/status/{id}` · `/result/{id}` · `/tts` (nếu có).

---

## Phần B — Bật/Tắt VPS qua API để TIẾT KIỆM

**Nguyên tắc:** GPU chỉ tính tiền khi **Running**. Khi rảnh → **Stop** (ngưng phí GPU, chỉ còn phí đĩa nhỏ). Khi có việc → **Start** lại. Vì lúc Stop thì API tắt theo, việc "đánh thức" phải do **máy gọi** (luôn online) làm qua **Vast API**.

### Vast REST API (điều khiển instance)
Header: `Authorization: Bearer <VAST_ACCOUNT_KEY>` (lấy ở console.vast.ai → **Keys**; **key tài khoản**, KHÁC key instance `/root/.vast_api_key` bị giới hạn quyền).

```
GET  https://console.vast.ai/api/v0/instances/<ID>/
     -> instances.actual_status  ("running" | "exited")
     -> instances.public_ipaddr
     -> instances.ports["10200/tcp"][0].HostPort   (port ngoài hiện tại)
PUT  https://console.vast.ai/api/v0/instances/<ID>/   body {"state":"running"}   (bật)
PUT  https://console.vast.ai/api/v0/instances/<ID>/   body {"state":"stopped"}   (tắt)
```
> ⚠️ **Port ngoài có thể đổi sau mỗi Start** → luôn dò lại từ `ports`, đừng hard-code.

### 1. Tự-STOP khi rảnh (chạy TRÊN VPS) — `idle_watchdog.py`
Theo dõi mốc hoạt động; rảnh > N phút + ComfyUI không có job → tự stop:
```python
IDLE=600; IID="<instance_id>"; ACT="/workspace/.last_activity"
while True:
    time.sleep(30)
    q = requests.get("http://localhost:18188/queue").json()
    if q["queue_running"] or q["queue_pending"]:
        open(ACT,"w").write(str(time.time())); continue      # đang render -> reset
    if time.time() - float(open(ACT).read()) >= IDLE:
        subprocess.run(["/opt/instance-tools/bin/vastai","stop","instance",IID])
```
Gateway ghi mốc mỗi request: `open("/workspace/.last_activity","w").write(str(time.time()))` trong middleware.

### 2. Tự-START khi cần (chạy Ở MÁY GỌI) — `vast_gpu_client.py`
Trước mỗi request: kiểm tra → nếu stopped thì bật → chờ /health → dò port → gọi:
```python
VAST="https://console.vast.ai/api/v0"; VH={"Authorization":f"Bearer {VAST_KEY}"}
def instance(): return requests.get(f"{VAST}/instances/{IID}/",headers=VH).json()["instances"]
def base_url():
    inst=instance(); ip=inst["public_ipaddr"].strip()
    return f"http://{ip}:{inst['ports']['10200/tcp'][0]['HostPort']}"
def ensure_ready(timeout=900):
    if instance()["actual_status"]!="running":
        requests.put(f"{VAST}/instances/{IID}/",headers=VH,json={"state":"running"})   # bật
    t0=time.time()
    while time.time()-t0<timeout:                        # chờ boot + /health up
        try:
            if instance()["actual_status"]=="running":
                b=base_url()
                if requests.get(f"{b}/health",timeout=8).json().get("comfyui")=="up": return b
        except: pass
        time.sleep(5)
    raise TimeoutError("VPS chưa sẵn sàng")
```

### 3. Luồng hoàn chỉnh (server-to-server)
```
Máy gọi cần tạo ảnh
  1. ensure_ready()      -> nếu VPS tắt: PUT state=running, chờ ~1–2 phút, dò port
  2. POST base/generate/image -> {job_id}
  3. poll base/status/{id} -> completed
  4. GET base/result/{id} -> lưu ảnh
  ... 10 phút không request -> watchdog trên VPS tự stop
```

### Chi phí & rủi ro (BẮT BUỘC biết)
- **Stop KHÔNG miễn phí**: vẫn tính **phí đĩa** (~$0.01–0.02/hr cho 80GB ≈ vài đô/tháng).
- 🚨 **Hết credit → Vast XÓA instance** (mất model + cài đặt). Giữ credit hoặc Destroy khi nghỉ dài.
- **Cold start**: sau Start mất ~30–120s boot + nạp model vào VRAM (request đầu chậm). `ensure_ready` đã chờ sẵn.
- **Start không đảm bảo tức thì**: nếu host hết GPU trống, instance stopped có thể chưa start được ngay (giới hạn marketplace).
- **Key**: dùng **account key** cho start/stop (key instance trên máy bị giới hạn, chỉ đủ vài thao tác).

### Bật/tắt watchdog thủ công
```bash
supervisorctl start idle_watchdog     # bật tự-stop
supervisorctl stop  idle_watchdog     # tắt (giữ VPS luôn chạy, vd khi phục vụ nhiều người)
```

---

## Tóm tắt
- **Gateway** = 1 lớp API gọn + an toàn che ComfyUI/Ollama; dùng job bất đồng bộ cho ảnh/video, đồng bộ cho chat.
- **Tiết kiệm** = watchdog tự-stop trên VPS + máy gọi tự-start qua Vast API + dò port động; chỉ trả tiền GPU khi dùng, nhưng nhớ giữ credit kẻo bị xóa.
- Code mẫu: `api_server.py`, `idle_watchdog.py`, `vast_gpu_client.py` (trong repo).
