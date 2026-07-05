# 🤖 model-ai — Tài liệu & triển khai AI mã nguồn mở

Bộ tài liệu + code để **tự dựng hệ thống AI** (chat · tạo ảnh · sửa ảnh · tạo video) trên VPS GPU, và **tra cứu mọi model mã nguồn mở** trên thị trường. Thiết kế để *AI đọc repo là cài được ngay*.

> Nền tảng: **ComfyUI** (ảnh/video) + **Ollama** (chat) + **1 API gateway** (`api_server.py`) trên **VPS GPU (Vast.ai)** — tự bật/tắt để tiết kiệm, tự dịch prompt Việt→Anh, không lưu đĩa.

---

## 🚀 Bắt đầu nhanh

| Việc | Làm gì |
|---|---|
| **Triển khai cả hệ thống** | Copy prompt trong **[PROMPT.md](PROMPT.md)**, điền SSH → gửi 1 lần cho AI (Claude Code…) là xong |
| **Tính chi phí (build vs API)** | Mở **[index.html](index.html)** — chọn model + số lượng → so sánh & gợi ý |
| **Cài tay từng bước** | Theo **[INSTALL.md](INSTALL.md)** |
| **Tra model để cài** | **[market-map.md](market-map.md)** (tất cả model mở) hoặc catalog theo loại |

---

## 📚 Tài liệu

**Triển khai & kỹ thuật**
- [PROMPT.md](PROMPT.md) — prompt triển khai 1-lần cho AI
- [INSTALL.md](INSTALL.md) — cài từ đầu (VPS → ComfyUI → API → model)
- [api-architecture.md](api-architecture.md) — viết API cho AI + **bật/tắt VPS tiết kiệm**
- [auto-translate.md](auto-translate.md) — tự dịch prompt Việt→Anh trước khi tạo
- [API_DOCS.md](API_DOCS.md) — tài liệu API (endpoint + ví dụ)
- [vps-cost.md](vps-cost.md) — cấu hình VPS & chi phí (24/7 vs auto-stop)

**Catalog model (mã nguồn mở)**
- [market-map.md](market-map.md) — **bản đồ tổng** mọi model mở (ảnh/video/LLM/audio/3D/vision)
- [ecosystems.md](ecosystems.md) — trọn hệ sinh thái theo hãng (FLUX, SD, Wan, Hunyuan, LTX)
- [catalog-image.md](catalog-image.md) — ảnh + ControlNet/upscale/tách nền/ghép mặt/inpaint
- [catalog-video.md](catalog-video.md) — video (tự host)
- [catalog-audio-3d.md](catalog-audio-3d.md) — TTS + ASR + nhạc + 3D
- [catalog-llm.md](catalog-llm.md) — chat + code + vision + embedding
- [catalog-agent-rag.md](catalog-agent-rag.md) — RAG (chatbot đọc tài liệu) + Agent/Automation
- [training.md](training.md) — train LoRA / fine-tune
- [api-providers.md](api-providers.md) — so sánh giá API thương mại (cho quyết định build-vs-buy)

**Code** (copy lên VPS): `api_server.py` · `idle_watchdog.py` · `vast_gpu_client.py` · `provision_vps.sh` · `ai_api.php`

---

## 🎯 Chọn nhanh theo nhu cầu

| Cần… | Model | VPS tối thiểu |
|---|---|---|
| Ảnh nhanh, rẻ | SDXL / finetune | 12–16GB |
| Ảnh đẹp nhất | **FLUX.1 dev** | 16–24GB |
| Sửa ảnh giữ nhân vật | **FLUX.1 Kontext** | 16–24GB |
| Video nhanh nhất | **LTX-Video 2B** | 12–16GB |
| Video đẹp + nhanh | **Wan 2.2 TI2V-5B** | 16–24GB |
| Video chất lượng cao | Wan 2.2 14B / HunyuanVideo | 24–48GB |
| Chat tiếng Việt | Qwen2.5 7B–14B | 8–16GB |
| Đọc/hiểu ảnh | Qwen2.5-VL | 8–16GB |
| Đọc văn bản (TTS) | Piper / viXTTS | 2–6GB |

---

## 🖥️ Chọn VPS / GPU

| Mức | GPU | VRAM | Đĩa | Chạy được | ~$/giờ |
|---|---|---|---|---|---|
| Nhẹ | RTX 4060Ti/5060Ti | 12–16GB | 40–60GB | SDXL, LTX, Wan 5B, chat 7B | $0.1–0.2 |
| **Cân bằng** ⭐ | RTX 4090/5090 | 24–32GB | 80–120GB | FLUX + Wan 5B + LTX + chat (đồng thời) | $0.35–0.6 |
| Cao | A6000/L40S | 48GB | 150GB | + Wan 14B, HunyuanVideo | $0.6–0.9 |
| Rất cao | A100/H100 | 80GB | 200GB+ | mọi thứ, nhiều luồng | $1.5–3 |

**Mẹo:** ưu tiên nhiều VRAM + đĩa lớn hơn GPU đời mới. RTX 5090 32GB thường rẻ hơn 4090 mà mạnh hơn. Chọn máy nhiều ports + IP gần VN (tải HuggingFace nhanh). Chi tiết + chi phí: [vps-cost.md](vps-cost.md).

---

## ⚡ Nguyên tắc tiết kiệm
- **1 GPU chạy tuần tự** — nhiều luồng đồng thời cần nhiều GPU.
- **Auto-stop** khi rảnh → chỉ trả tiền GPU khi dùng (xem [api-architecture.md](api-architecture.md)).
- ⚠️ **Stop vẫn tốn phí đĩa** (~$0.5/ngày cho 80GB) — **hết credit Vast sẽ XÓA instance**. Giữ credit hoặc Destroy khi nghỉ dài.

---
*Tài liệu tổng hợp bởi AI. Model & giá thay đổi thường xuyên — kiểm tra nguồn chính thức trước khi dùng thương mại.*
