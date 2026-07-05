# Kỹ thuật — Tự dịch prompt (VN→EN) trước khi tạo ảnh/video

## Vấn đề
Hầu hết model **ảnh/video** (FLUX, SDXL, Wan, HunyuanVideo, LTX...) huấn luyện bằng dữ liệu **tiếng Anh**; text-encoder (CLIP, T5, umt5, llava) hiểu tiếng Anh tốt nhất. → **Prompt tiếng Việt cho kết quả sai/kém.**

**Giải pháp:** chèn 1 bước **tự dịch prompt sang tiếng Anh** (dùng chính LLM chat đã có) **ngay trong API gateway**, trước khi dựng workflow. Người dùng gõ tiếng Việt tự nhiên, chất lượng như gõ tiếng Anh.

> Áp dụng cho: **tạo ảnh, tạo video, sửa ảnh**. KHÔNG áp dụng cho **chat** (LLM hiểu tiếng Việt trực tiếp).

---

## Cách làm (đặt trong api_server.py)

```python
OLLAMA = "http://localhost:11434"
CHAT_MODEL = "qwen2.5:7b"       # LLM dùng để dịch (Qwen dịch VN<->EN tốt)

def maybe_translate(text):
    text = (text or "").strip()
    # 1) Nếu đã là ASCII (tiếng Anh/không dấu) -> bỏ qua, khỏi tốn thời gian
    if not text or text.isascii():
        return text
    # 2) Có ký tự tiếng Việt -> gọi LLM dịch, CHỈ lấy bản dịch
    try:
        r = requests.post(f"{OLLAMA}/api/chat", json={
            "model": CHAT_MODEL,
            "messages": [
                {"role": "system", "content":
                    "You translate Vietnamese image/video generation prompts into concise, "
                    "vivid English. Output ONLY the English prompt — no quotes, no notes, "
                    "no explanation."},
                {"role": "user", "content": text},
            ],
            "stream": False,
            "options": {"temperature": 0.2},   # dịch ổn định, ít bịa
        }, timeout=40)
        out = r.json().get("message", {}).get("content", "").strip().strip('"')
        return out or text
    except Exception:
        return text        # lỗi dịch thì dùng nguyên bản, không chặn việc tạo
```

Áp dụng ở endpoint (dịch prompt trước khi build workflow):
```python
@app.post("/generate/image")
def gen_image(r: ImageReq):
    p = maybe_translate(r.prompt)          # <-- dịch tại đây
    wf = wf_image_sdxl(p, ...) if r.model=="sdxl" else wf_image(p, ...)
    return {"job_id": start_job("image", wf)}

@app.post("/generate/video")
def gen_video(r: VideoReq):
    return {"job_id": start_job("video", wf_video(maybe_translate(r.prompt), r.duration, r.model))}
```
Kết quả test: `"một con mèo cam đang ngủ trên ghế sofa"` → `"a orange cat sleeping on a sofa"` → tạo ảnh đúng.

---

## Điểm kỹ thuật quan trọng

1. **Chỉ dịch khi cần** (`text.isascii()`): prompt tiếng Anh đi thẳng, không tốn 1–2s gọi LLM, không bị LLM "chỉnh sửa" lại.
2. **System prompt chặt**: bắt "Output ONLY the English prompt" → tránh LLM trả lời kiểu hội thoại ("Bản dịch là: ...").
3. **temperature thấp (0.2)**: dịch bám sát, ít bịa thêm.
4. **strip('"')**: LLM hay bọc kết quả trong ngoặc kép → cắt bỏ.
5. **Fail-safe**: lỗi/timeout khi dịch → trả prompt gốc, KHÔNG chặn việc tạo (thà tạo với tiếng Việt còn hơn báo lỗi).
6. **Độ trễ**: thêm ~1–2s/lần (không đáng kể so với tạo ảnh 15s / video 30s).
7. **Prompt sửa ảnh (edit)** cũng dịch tương tự (Kontext hiểu tiếng Anh) — nhưng giữ nguyên các động từ lệnh (change/keep...).

---

## Biến thể & nâng cao

### A. Model dịch chuyên (thay LLM chung)
- Nếu không có LLM chat, dùng model dịch nhẹ: `Helsinki-NLP/opus-mt-vi-en` (~300MB), hoặc `VietAI/envit5-translation`.
```python
# pip install transformers sentencepiece
from transformers import pipeline
_tr = pipeline("translation", model="VietAI/envit5-translation")
def translate(vi): return _tr("vi: "+vi, max_length=256)[0]["translation_text"]
```

### B. Giữ nguyên "tag" tiếng Anh trong prompt hỗn hợp
- Prompt trộn Việt-Anh ("một cô gái, cinematic, 8k") → LLM vẫn dịch phần Việt, giữ tag Anh. System prompt có thể thêm: "keep existing English words/tags".

### C. Thêm tag chất lượng tự động (tùy chọn)
- Sau khi dịch, có thể nối thêm: `", high quality, detailed"` cho ảnh, hoặc negative prompt mạnh — tùy model.

### D. Bật/tắt dịch qua tham số
- Thêm field `translate: true/false` vào request nếu muốn client tự quyết (mặc định bật).

---

## Model có sẵn hỗ trợ tiếng Việt tốt hơn (đỡ cần dịch)
- **Qwen-Image** (20B): text-encoder Qwen hiểu tiếng Việt/Trung khá → prompt tiếng Việt đỡ sai hơn (nhưng vẫn nên dịch để chắc).
- Đa số còn lại (FLUX/SDXL/Wan/Hunyuan/LTX): **bắt buộc tiếng Anh** → dùng auto-translate.

## Tóm tắt
- 1 hàm `maybe_translate()` trong gateway, gọi LLM dịch VN→EN, chỉ khi prompt có dấu tiếng Việt, fail-safe.
- Áp dụng cho ảnh/video/sửa ảnh (không cho chat).
- Người dùng gõ tiếng Việt thoải mái → kết quả đúng như tiếng Anh. Code đầy đủ trong `api_server.py`.
