# Huấn luyện / Tùy chỉnh model (LoRA & Fine-tune)

Để model "hợp công việc" (nhân vật cố định, phong cách, sản phẩm) → **train LoRA** (adapter nhỏ ~50–300MB) rồi gắn lúc tạo. Rẻ hơn fine-tune toàn phần rất nhiều.

## LoRA cho ẢNH

| Công cụ | Cho model | VRAM train | Nguồn |
|---|---|---|---|
| **ai-toolkit** (ostris) | FLUX, SDXL | ~24GB (FLUX), ~12GB (SDXL) | `github.com/ostris/ai-toolkit` |
| **kohya_ss / sd-scripts** | SDXL, SD1.5, FLUX | 12–24GB | `github.com/kohya-ss/sd-scripts` |
| **SimpleTuner** | FLUX, SD3.5 | 16–24GB | `github.com/bghira/SimpleTuner` |

Quy trình LoRA nhân vật:
1. Chuẩn bị **10–30 ảnh** đối tượng (đa dạng góc/ánh sáng) + caption.
2. Train (~500–2000 step). FLUX LoRA cần ~24GB VRAM → thuê máy 24GB lúc train.
3. Ra file `.safetensors` → đặt `models/loras/` → thêm node `LoraLoader` vào workflow.
4. **Dùng** (inference) chỉ cần 12–16GB → tách máy train và máy chạy để tiết kiệm.

## LoRA cho VIDEO
- **Wan LoRA**: train qua `diffusion-pipe` / musubi-tuner (`github.com/kohya-ss/musubi-tuner`) — nhân vật/động tác nhất quán trong video.
- **HunyuanVideo LoRA**: musubi-tuner hỗ trợ.

## Fine-tune LLM (chat)
- **LoRA/QLoRA** cho LLM: `unsloth` (`github.com/unslothai/unsloth`) — nhanh, ít VRAM; hoặc `axolotl`, `LLaMA-Factory`.
- Xong export GGUF → `ollama create` để chạy bản đã tinh chỉnh.

## TTS clone giọng (không cần train)
- viXTTS / F5-TTS / Fish-Speech: **zero-shot** — chỉ cần 1 mẫu giọng ~6–15s, không phải train.

## VPS đề xuất để TRAIN
| Việc | VRAM | GPU |
|---|---|---|
| LoRA SDXL | 12–16GB | RTX 4060Ti/4090 |
| LoRA FLUX | 24GB | RTX 4090/5090/A6000 |
| LoRA video (Wan/Hunyuan) | 24–48GB | RTX 5090/A6000 |
| Fine-tune LLM 7B (QLoRA) | 16–24GB | RTX 4090 |

> **Mẹo tiết kiệm**: train trên máy VRAM lớn (thuê theo giờ), xong tải LoRA (~vài trăm MB) về máy nhỏ để chạy. Inference với LoRA rất nhẹ.
