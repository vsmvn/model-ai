# Tài liệu API — AI Generation (Chat / Ảnh / Video / Sửa ảnh)

Cập nhật: 2026-07-05 · Máy chủ GPU RTX 5090 trên Vast.ai.

---

## 1. Kết nối & Xác thực

| Mục | Giá trị |
|---|---|
| **Base URL** | `http://14.179.88.48:41497` |
| **Token** | `riiDqlgpAUqH_l3aFDPqADvVS0-lYQLF4Cab4kgMH04` |
| **Cách gửi token** | Header `X-API-Key: <token>` **hoặc** `Authorization: Bearer <token>` |

- Mọi endpoint cần token, **trừ** `GET /health`.
- Thiếu/sai token → `401`.
- ⚠️ **Base URL có thể đổi port** sau khi VPS stop/start (Vast map lại). Nếu tích hợp lâu dài, nên giữ VPS chạy hoặc dò port động qua Vast API (xem §7). Token thì **không đổi**.
- ⚠️ **VPS tự tắt sau 10 phút không có request** (tiết kiệm chi phí). Khi tắt, API không phản hồi → cần bật lại (dashboard hoặc Vast API). Muốn luôn sẵn sàng thì tắt watchdog.

---

## 2. Mô hình có sẵn

| Loại | Model | Tham số chọn |
|---|---|---|
| 💬 Chat | Qwen 2.5 7B (hiểu tiếng Việt) | — |
| 🖼️ Tạo ảnh | FLUX Kontext / SDXL | `model: "flux"` (mặc định) \| `"sdxl"` |
| ✏️ Sửa ảnh (giữ nhân vật) | FLUX Kontext | — |
| 🎬 Video | Wan 2.2 (đẹp) / LTX-Video (nhanh) | `model: "wan"` (mặc định) \| `"ltx"` |

> **Tự động dịch:** prompt tiếng Việt cho **ảnh / video / sửa ảnh** được tự dịch sang tiếng Anh trước khi tạo (để model hiểu đúng). Chat thì hiểu tiếng Việt trực tiếp.

---

## 3. Luồng hoạt động

- **Chat & TTS**: đồng bộ — gọi 1 lần, nhận kết quả ngay.
- **Ảnh / Video / Sửa ảnh**: bất đồng bộ:
  1. `POST /generate/...` → nhận `{job_id}`
  2. `GET /status/{job_id}` lặp lại tới khi `status = "completed"`
  3. `GET /result/{job_id}` → tải bytes ảnh/video về

Kết quả giữ trong RAM **60 phút** rồi tự xóa (server không lưu đĩa).

---

## 4. Endpoints

### `GET /health`  (không cần token)
```json
{ "status": "ok", "comfyui": "up", "chat": "up", "results_in_ram": 0 }
```

### `POST /chat`  — trò chuyện (đồng bộ)
Body: `{ "message": "Xin chào" }`
Trả về: `{ "reply": "Xin chào! Tôi có thể giúp gì?" }`

### `POST /generate/image`  — tạo ảnh
Body:
```json
{ "prompt": "một con mèo cam trên ghế sofa", "width": 1024, "height": 1024, "model": "flux" }
```
- `model`: `"flux"` (đẹp, mặc định) hoặc `"sdxl"` (nhanh). `width`/`height` bội số 8.
Trả về: `{ "job_id": "abc123..." }`

### `POST /generate/video`  — tạo video (text→video)
Body:
```json
{ "prompt": "cáo chạy trong tuyết", "duration": 3, "model": "wan" }
```
- `model`: `"wan"` (Wan 2.2, đẹp ~30s) hoặc `"ltx"` (LTX, nhanh ~10-15s). `duration`: 2–10 giây.
Trả về: `{ "job_id": "..." }`

### `POST /generate/edit`  — sửa ảnh giữ nhân vật (multipart/form-data)
Fields:
- `prompt` (text): câu lệnh sửa, vd "change background to a beach, keep the person unchanged"
- `image` (file): ảnh cần sửa
- `guidance` (số, tùy chọn): mức sửa — `2.5` nhẹ / `3.5` vừa (mặc định) / `4.5` mạnh
Trả về: `{ "job_id": "..." }`

### `GET /status/{job_id}`
```json
{ "status": "running", "progress": 42, "result_url": null, "error": null }
```
`status`: `queued` → `running` → `completed` | `failed` | `expired`.
Khi `completed`: `result_url` có giá trị (dùng `/result/{job_id}` để tải).

### `GET /result/{job_id}`  — tải kết quả (cần token)
Trả về **bytes** ảnh (`image/png`) hoặc video (`video/mp4`). `410` nếu hết hạn/đã xóa.

### `DELETE /result/{job_id}`  — xóa kết quả khỏi RAM ngay (tùy chọn)
`{ "deleted": true }`

---

## 5. Ví dụ curl

```bash
BASE=http://14.179.88.48:41497
TOKEN=riiDqlgpAUqH_l3aFDPqADvVS0-lYQLF4Cab4kgMH04

# Chat
curl -s -X POST $BASE/chat -H "X-API-Key: $TOKEN" -H "Content-Type: application/json" \
  -d '{"message":"Thủ đô Việt Nam là gì?"}'

# Tạo ảnh -> lấy job_id -> chờ -> tải
JID=$(curl -s -X POST $BASE/generate/image -H "X-API-Key: $TOKEN" -H "Content-Type: application/json" \
  -d '{"prompt":"một ly cà phê trên bàn gỗ","width":1024,"height":1024,"model":"flux"}' \
  | python -c "import sys,json;print(json.load(sys.stdin)['job_id'])")
until curl -s $BASE/status/$JID -H "X-API-Key: $TOKEN" | grep -q completed; do sleep 3; done
curl -s $BASE/result/$JID -H "X-API-Key: $TOKEN" -o out.png

# Video nhanh (LTX)
curl -s -X POST $BASE/generate/video -H "X-API-Key: $TOKEN" -H "Content-Type: application/json" \
  -d '{"prompt":"sóng biển hoàng hôn","duration":3,"model":"ltx"}'

# Sửa ảnh
curl -s -X POST $BASE/generate/edit -H "X-API-Key: $TOKEN" \
  -F "prompt=đổi nền thành bãi biển, giữ nguyên người" -F "guidance=3.5" -F "image=@photo.jpg"
```

---

## 6. Client Python (copy dùng ngay)

```python
import requests, time

BASE  = "http://14.179.88.48:41497"
TOKEN = "riiDqlgpAUqH_l3aFDPqADvVS0-lYQLF4Cab4kgMH04"
H = {"X-API-Key": TOKEN}

def chat(message):
    return requests.post(f"{BASE}/chat", headers=H, json={"message": message}, timeout=180).json()["reply"]

def _wait(job_id, timeout=1800):
    t0 = time.time()
    while time.time() - t0 < timeout:
        s = requests.get(f"{BASE}/status/{job_id}", headers=H, timeout=15).json()
        if s["status"] == "completed":
            return requests.get(f"{BASE}/result/{job_id}", headers=H, timeout=180).content
        if s["status"] in ("failed", "expired"):
            raise RuntimeError(s)
        time.sleep(3)
    raise TimeoutError()

def gen_image(prompt, width=1024, height=1024, model="flux", save_to=None):
    jid = requests.post(f"{BASE}/generate/image", headers=H,
        json={"prompt": prompt, "width": width, "height": height, "model": model}, timeout=30).json()["job_id"]
    data = _wait(jid)
    if save_to: open(save_to, "wb").write(data)
    return data

def gen_video(prompt, duration=3, model="wan", save_to=None):
    jid = requests.post(f"{BASE}/generate/video", headers=H,
        json={"prompt": prompt, "duration": duration, "model": model}, timeout=30).json()["job_id"]
    data = _wait(jid)
    if save_to: open(save_to, "wb").write(data)
    return data

def edit_image(image_path, instruction, guidance=3.5, save_to=None):
    with open(image_path, "rb") as f:
        jid = requests.post(f"{BASE}/generate/edit", headers=H,
            files={"image": f}, data={"prompt": instruction, "guidance": guidance}, timeout=60).json()["job_id"]
    data = _wait(jid)
    if save_to: open(save_to, "wb").write(data)
    return data

# Dùng:
print(chat("Xin chào"))
gen_image("một con mèo cam dễ thương", save_to="cat.png")
gen_video("cáo chạy trong tuyết", model="ltx", save_to="fox.mp4")
edit_image("cat.png", "đổi nền thành bãi biển, giữ nguyên con mèo", save_to="cat_beach.png")
```

---

## 7. (Nâng cao) Dò port động + tự bật VPS

Nếu VPS hay stop/start, port ngoài có thể đổi. Dùng Vast API để lấy port hiện tại + bật VPS:
```
GET  https://console.vast.ai/api/v0/instances/43823400/    (header Authorization: Bearer <VAST_ACCOUNT_KEY>)
     -> instances.public_ipaddr + instances.ports["10200/tcp"][0].HostPort  = base URL hiện tại
     -> instances.actual_status  ("running"/"exited")
PUT  https://console.vast.ai/api/v0/instances/43823400/   body {"state":"running"}   (bật VPS)
```
(File `vast_gpu_client.py` kèm theo đã hiện thực sẵn phần này.)

---

## 8. Tóm tắt nhanh
```
Base : http://14.179.88.48:41497   ·   Header: X-API-Key: <token>
POST /chat                    {message}                              -> {reply}
POST /generate/image          {prompt,width,height,model:flux|sdxl}  -> {job_id}
POST /generate/video          {prompt,duration,model:wan|ltx}        -> {job_id}
POST /generate/edit           multipart: prompt,image,guidance       -> {job_id}
GET  /status/{job_id}                                                -> {status,progress,result_url}
GET  /result/{job_id}         (bytes ảnh/video, cần token)
GET  /health                  (không cần token)
```
Prompt tiếng Việt OK (tự dịch cho ảnh/video/sửa ảnh). Kết quả không lưu server, giữ RAM 60 phút.
