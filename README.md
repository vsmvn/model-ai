# Tài liệu Model AI — Catalog & Hướng dẫn cài đặt

> Repo tra cứu để **cài đặt model AI theo yêu cầu**. Mỗi model có: nguồn tải, dung lượng, VRAM cần, tốc độ, license, **VPS đề xuất**, và **lệnh cài**. Đọc repo này là cài được ngay.
>
> Nền tảng: **ComfyUI** (ảnh/video) + **Ollama** (chat) + **1 API gateway** (`api_server.py`) chạy trên **VPS GPU thuê ở Vast.ai**. Xem [INSTALL.md](INSTALL.md) để dựng từ đầu.

---

## 📚 Bộ tài liệu (đọc file phù hợp với việc cần làm)
| File | Nội dung |
|---|---|
| **README.md** (đang xem) | Tổng quan + chọn nhanh + chọn VPS + model chính |
| [INSTALL.md](INSTALL.md) | **Hướng dẫn cài đặt** từ đầu (VPS → ComfyUI → API → model) |
| [api-architecture.md](api-architecture.md) | **Kỹ thuật viết API** cho AI + **bật/tắt VPS qua API tiết kiệm** |
| [API_DOCS.md](API_DOCS.md) | Tài liệu API đang chạy (endpoint, ví dụ) |
| [catalog-image.md](catalog-image.md) | **Đầy đủ model ẢNH** + ControlNet/IPAdapter/upscale/tách nền/ghép mặt/inpaint |
| [catalog-video.md](catalog-video.md) | **Đầy đủ model VIDEO** (tự host + API) + audio-cho-video + nối clip |
| [catalog-audio-3d.md](catalog-audio-3d.md) | **TTS (text→giọng) + ASR (giọng→text)** + nhạc + **3D** |
| [catalog-llm.md](catalog-llm.md) | **LLM**: chat + code + vision + embedding |
| [training.md](training.md) | **Train LoRA / fine-tune** model theo dữ liệu riêng |

Code kèm theo (copy lên VPS): `api_server.py`, `idle_watchdog.py`, `provision_vps.sh`, `vast_gpu_client.py`, `ai_api.php`.

---

## 0. Mục lục
- [1. Chọn nhanh theo nhu cầu](#1-chọn-nhanh-theo-nhu-cầu)
- [2. Hướng dẫn chọn VPS / GPU](#2-hướng-dẫn-chọn-vps--gpu)
- [3. Model TẠO ẢNH](#3-model-tạo-ảnh-image) (nhanh → chất lượng cao)
- [4. Model SỬA ẢNH](#4-model-sửa-ảnh-editing)
- [5. Model TẠO VIDEO](#5-model-tạo-video-nhanh--chất-lượng-cao)
- [6. Model CHAT / LLM](#6-model-chat--llm-ollama)
- [7. Model VISION (đọc ảnh)](#7-model-vision-đọc-hiểu-ảnh)
- [8. Model TTS (đọc văn bản)](#8-model-tts-text-to-speech)
- [9. Cài đặt & workflow](INSTALL.md)

---

## 1. Chọn nhanh theo nhu cầu

| Tôi cần… | Model | VPS tối thiểu |
|---|---|---|
| Tạo ảnh nhanh, rẻ | SDXL / SDXL finetune | 12–16GB VRAM |
| Tạo ảnh đẹp nhất, bám prompt | **FLUX.1 dev** | 16–24GB |
| Sửa ảnh giữ nhân vật | **FLUX.1 Kontext** | 16–24GB |
| Video nhanh nhất | **LTX-Video 2B** | 12–16GB |
| Video đẹp + nhanh (cân bằng) | **Wan 2.2 TI2V-5B** | 16–24GB |
| Video chất lượng cao nhất | **Wan 2.2 14B / HunyuanVideo 13B** | 24–48GB |
| Chat tiếng Việt | Qwen2.5 7B–14B | 8–16GB (kèm ảnh cần 24GB+) |
| Đọc/hiểu ảnh (vision) | Qwen2.5-VL 7B | 8–16GB |
| Đọc văn bản (TTS) tiếng Việt | Piper / viXTTS | 2–6GB |

> **Quy tắc VRAM:** dùng bản **fp8** để tiết kiệm ~½ VRAM. GPU 32GB chạy được hầu hết bản fp8, chỉ 14B video/48GB-class mới cần GPU lớn.

---

## 2. Hướng dẫn chọn VPS / GPU

### Bảng cấu hình đề xuất (thuê ở Vast.ai)

| Mức | GPU | VRAM | Đĩa | Chạy được | Giá tham khảo/hr |
|---|---|---|---|---|---|
| Nhẹ | RTX 4060Ti/5060Ti/3060 | 12–16GB | 40–60GB | SDXL, LTX, Wan 5B (fp8), chat 7B | $0.1–0.2 |
| **Cân bằng** ⭐ | **RTX 4090 / 5090** | **24–32GB** | **80–120GB** | FLUX dev/Kontext + Wan 2.2 5B + LTX + chat, **chạy đồng thời** | $0.35–0.6 |
| Cao | RTX A6000 / L40S / 6000 Ada | 48GB | 150GB | + **Wan 2.2 14B**, HunyuanVideo 13B, nhiều model song song | $0.6–0.9 |
| Rất cao | A100 / H100 | 80GB | 200GB+ | Mọi thứ, batch lớn, nhiều luồng | $1.5–3 |

### Mẹo chọn máy trên Vast (rút kinh nghiệm thực tế)
- **Ưu tiên nhiều VRAM + đĩa lớn** hơn là GPU đời mới nhất. RTX 5090 32GB thường **rẻ hơn** 4090 24GB mà mạnh hơn.
- **Kiểm tra mạng (ports)**: chọn máy nhiều ports + IP gần bạn (tải model từ HuggingFace nhanh, ổn định). Tránh máy China (GFW chặn HF).
- **Test kết nối trước khi cài**: SSH báo `Permission denied (publickey)` = mạng OK chỉ thiếu key; báo `Connection refused` (cả direct lẫn proxy) = **host lỗi mạng → đổi máy khác**.
- **Max Duration cao** (263 tháng…) = host giữ máy lâu, ít bị thu hồi.
- **Đĩa**: kéo thanh "Disk Space to Allocate" lúc thuê (mặc định thấp). Sau khi thuê **khó tăng đĩa** (Vast không hỗ trợ resize dễ dàng) → đặt đủ ngay từ đầu.
- **Chi phí khi Stop**: vẫn tính phí đĩa (~$0.5/ngày cho 80GB). **Hết credit → Vast XÓA instance** (mất data). Nạp tiền hoặc Destroy khi nghỉ dài.

### Ước lượng đĩa cho từng bộ
| Bộ model | Đĩa |
|---|---|
| FLUX Kontext (ảnh+sửa) | ~18GB |
| FLUX dev (all-in-one fp8) | ~17GB |
| SDXL | ~7GB |
| Wan 2.2 5B | ~17GB |
| LTX-Video 2B | ~6GB |
| HunyuanVideo 13B | ~23GB (fp8) / ~35GB (bf16) |
| Chat Qwen 7B | ~5GB |

---

## 3. Model TẠO ẢNH (image) — nhanh → chất lượng cao

| Model | Chất lượng | Tốc độ | VRAM | Đĩa | License TM | Đọc thêm |
|---|---|---|---|---|---|---|
| **SD 1.5** | ⭐⭐ | ⚡⚡⚡ | ~4GB | ~2–4GB | ✅ mở | cổ điển, nhẹ nhất |
| **SDXL base 1.0** | ⭐⭐⭐ | ⚡⚡ | ~8GB | ~6.5GB | ✅ mở | chuẩn phổ biến |
| **SDXL finetune** (Juggernaut XL, RealVisXL) | ⭐⭐⭐⭐ | ⚡⚡ | ~8GB | ~6.5GB | ✅ mở | **ảnh thực đẹp**, thay SDXL base |
| **SD 3.5 Medium** | ⭐⭐⭐⭐ | ⚡⚡ | ~10GB | ~5GB | ✅ mở | bám prompt tốt |
| **FLUX.1 schnell** | ⭐⭐⭐⭐ | ⚡⚡⚡ (4 bước) | ~12GB | ~17GB | ✅ **Apache** | nhanh + mở TM |
| **FLUX.1 dev** ⭐ | ⭐⭐⭐⭐⭐ | ⚡ (20 bước) | ~12GB (fp8) | ~17GB | ⚠️ Non-commercial | **đẹp nhất**, tay/chữ/prompt |
| **FLUX.1 Kontext dev** | ⭐⭐⭐⭐⭐ | ⚡ | ~12GB | ~18GB | ⚠️ Non-commercial | tạo ảnh + **sửa ảnh** |

### Lệnh cài (dùng `hf download`; `M=/workspace/ComfyUI/models`)

**SDXL base:**
```bash
hf download stabilityai/stable-diffusion-xl-base-1.0 sd_xl_base_1.0.safetensors --local-dir $M/checkpoints
hf download stabilityai/sdxl-vae sdxl_vae.safetensors --local-dir $M/vae
```
Workflow: `CheckpointLoaderSimple(sd_xl_base_1.0)` → `CLIPTextEncode` (pos/neg) → `EmptyLatentImage` → `KSampler`(cfg 7, 30 bước, dpmpp_2m, karras) → `VAEDecode` → `SaveImage`.

**SDXL finetune**: thay file checkpoint bằng Juggernaut-XL / RealVisXL (tải từ HuggingFace/Civitai) vào `$M/checkpoints`, cùng workflow SDXL.

**FLUX.1 dev (all-in-one fp8, non-gated):**
```bash
hf download Comfy-Org/flux1-dev flux1-dev-fp8.safetensors --local-dir $M/checkpoints
```
Workflow: `CheckpointLoaderSimple(flux1-dev-fp8)` → `CLIPTextEncode` → `FluxGuidance(3.5)` → `EmptySD3LatentImage` → `KSampler`(cfg 1, 20 bước, euler, simple) → `VAEDecode` → `SaveImage`.

**FLUX.1 Kontext dev (split, non-gated):**
```bash
hf download Comfy-Org/flux1-kontext-dev split_files/diffusion_models/flux1-dev-kontext_fp8_scaled.safetensors --local-dir $M/diffusion_models   # rồi mv về flat
hf download comfyanonymous/flux_text_encoders t5xxl_fp8_e4m3fn_scaled.safetensors --local-dir $M/text_encoders
hf download comfyanonymous/flux_text_encoders clip_l.safetensors --local-dir $M/clip
hf download ChuckMcSneed/FLUX.1-dev ae.safetensors --local-dir $M/vae     # BFL & schnell gated -> dùng mirror này
```
Workflow text→ảnh: `UNETLoader(weight_dtype=fp8_e4m3fn)` + `DualCLIPLoader(clip_l,t5xxl,flux)` + `VAELoader(ae)` → `CLIPTextEncode` → `FluxGuidance(3.5)` → `EmptySD3LatentImage` → `KSampler`(cfg1,20,euler,simple) → `VAEDecode`.

> ⚠️ **Model gated** (`black-forest-labs/FLUX.1-dev`, `FLUX.1-schnell`): cần HF token + chấp nhận license. Dùng mirror non-gated: `Comfy-Org/*`, `ChuckMcSneed/*`.

---

## 4. Model SỬA ẢNH (editing)

| Model | Việc | VRAM | Đĩa | Ghi chú |
|---|---|---|---|---|
| **FLUX.1 Kontext dev** ⭐ | Upload ảnh + câu lệnh → sửa, **GIỮ nhân vật** | ~12GB | ~18GB | tốt nhất hiện nay |
| SDXL inpaint | Tô vùng cần sửa | ~8GB | ~6.5GB | sửa cục bộ |

**Kontext — workflow sửa ảnh** (từ template `flux_kontext_dev_basic`):
`LoadImage` → `FluxKontextImageScale` → `VAEEncode(ae)` → latent;
`CLIPTextEncode(instruction)` → `ReferenceLatent(latent)` → `FluxGuidance(2.5–4.5)` → positive;
`ConditioningZeroOut` → negative;
`KSampler`(cfg1, 20 bước, euler, simple, denoise1, latent_image = VAEEncode) → `VAEDecode`.
- **Mẹo prompt giữ nhân vật**: dùng động từ *change/add/remove/replace*; nêu rõ *"keep the person's face and pose unchanged"*; guidance cao (3.5–4.5) khi ảnh không chịu đổi.

---

## 5. Model TẠO VIDEO — nhanh → chất lượng cao

| Model | Chất lượng | Tốc độ (clip 3s) | VRAM | Đĩa | Ảnh→video | Ghi chú |
|---|---|---|---|---|---|---|
| **LTX-Video 2B distilled** | ⭐⭐⭐ | **~10–15s** ⚡⚡⚡ | ~8GB | ~6GB | ✅ | **nhanh nhất** |
| **Wan 2.1 T2V 1.3B** | ⭐⭐ | ~30s ⚡⚡ | ~6GB | ~3GB | ✅ | nhẹ, nhân vật hay lỗi |
| **Wan 2.2 TI2V-5B** ⭐ | ⭐⭐⭐⭐ | ~30–40s ⚡ | ~12GB | ~17GB | ✅ | **đẹp + nhanh, cân bằng nhất** |
| **CogVideoX-5B** | ⭐⭐⭐ | ~1–2 phút | ~12GB | ~11GB | ✅ | trung bình |
| **Mochi 1** (10B) | ⭐⭐⭐⭐ | vài phút 🐢 | ~24GB | ~20GB | ❌ | nặng |
| **HunyuanVideo** (13B) | ⭐⭐⭐⭐⭐ | ~2 phút 🐢 | ~18–24GB | ~23GB (fp8) | ✅ (model I2V riêng) | đẹp, chậm |
| **Wan 2.2 I2V A14B** | ⭐⭐⭐⭐⭐ | vài phút | ~28–48GB | ~30GB | ✅ | đẹp nhất, **cần GPU 48GB** |
| **LTX-2 / LTXV 13B** | ⭐⭐⭐⭐ | ~30–60s | ~16–24GB | ~15–28GB | ✅ | bản mới, đẹp + khá nhanh |
| **AnimateDiff** | ⭐⭐ | ~20s ⚡ | ~6GB | ~5GB | ❌ | hoạt hình/stylized, nền SD |

### Lệnh cài

**LTX-Video 2B (nhanh nhất, native ComfyUI):**
```bash
hf download Lightricks/LTX-Video ltxv-2b-0.9.8-distilled.safetensors --local-dir $M/checkpoints
# t5xxl_fp8 (dùng chung FLUX). Nếu chưa có: hf download comfyanonymous/flux_text_encoders t5xxl_fp8_e4m3fn_scaled.safetensors --local-dir $M/text_encoders
```
Workflow: `CheckpointLoaderSimple(ltxv)` + `CLIPLoader(t5xxl, type=ltxv)` → `CLIPTextEncode`(pos/neg) → `LTXVConditioning(frame_rate=25)` → `EmptyLTXVLatentVideo(768x512, length=8n+1)` → `LTXVScheduler(12 bước)` → `KSamplerSelect(euler)` → `SamplerCustom(cfg1)` → `VAEDecode` → `VHS_VideoCombine(25fps)`.

**Wan 2.2 TI2V-5B (cân bằng nhất — cần custom node WanVideoWrapper):**
```bash
# custom node: git clone https://github.com/kijai/ComfyUI-WanVideoWrapper.git ; và Kosinkadink/ComfyUI-VideoHelperSuite
hf download Kijai/WanVideo_comfy Wan22-Turbo/Wan2_2-TI2V-5B-Turbo_fp16.safetensors --local-dir $M/diffusion_models   # rồi mv về flat
hf download Kijai/WanVideo_comfy Wan2_2_VAE_bf16.safetensors --local-dir $M/vae
hf download Kijai/WanVideo_comfy umt5-xxl-enc-fp8_e4m3fn.safetensors --local-dir $M/text_encoders
```
Workflow T2V: `WanVideoModelLoader(quantization=fp8_e4m3fn)` + `WanVideoVAELoader(Wan2_2_VAE)` + `LoadWanVideoT5TextEncoder(umt5)` + `WanVideoTextEncode` → `WanVideoEmptyEmbeds(704x480,num_frames=4n+1)` → `WanVideoSampler`(8 bước, cfg1, shift5, unipc) → `WanVideoDecode` → `VHS_VideoCombine(24fps)`.
Ảnh→video: thêm `LoadImage→ImageScale→WanVideoEncode` → đưa latent vào `WanVideoEmptyEmbeds.extra_latents`.

**HunyuanVideo 13B (đẹp, chậm — native ComfyUI):**
```bash
hf download Comfy-Org/HunyuanVideo_repackaged split_files/diffusion_models/hunyuan_video_t2v_720p_bf16.safetensors --local-dir $M/diffusion_models   # 24GB bf16, nạp fp8. (fp8 13GB: Kijai/HunyuanVideo_comfy)
hf download Comfy-Org/HunyuanVideo_repackaged split_files/text_encoders/llava_llama3_fp8_scaled.safetensors --local-dir $M/text_encoders
hf download Comfy-Org/HunyuanVideo_repackaged split_files/vae/hunyuan_video_vae_bf16.safetensors --local-dir $M/vae
```
Workflow: `UNETLoader(weight_dtype=fp8_e4m3fn)` + `DualCLIPLoader(clip_l,llava_llama3,hunyuan_video)` + `VAELoader` → `ModelSamplingSD3(shift7)`+`BasicGuider`; `CLIPTextEncode`→`FluxGuidance(6)`; `KSamplerSelect(euler)`+`BasicScheduler(simple,20)`+`RandomNoise`+`EmptyHunyuanLatentVideo(848x480,length=4n+1)` → `SamplerCustomAdvanced` → `VAEDecodeTiled` → `VHS_VideoCombine(24fps)`.

---

## 6. Model CHAT / LLM (Ollama)

Cài Ollama: `curl -fsSL https://ollama.com/install.sh | sh` ; chạy `ollama serve` ; kéo model `ollama pull <model>`.

| Model | Chất lượng | VRAM (4-bit) | Tiếng Việt | Lệnh |
|---|---|---|---|---|
| **Qwen2.5 7B** ⭐ | ⭐⭐⭐⭐ | ~5GB | tốt | `ollama pull qwen2.5:7b` |
| Qwen2.5 14B | ⭐⭐⭐⭐ | ~9GB | rất tốt | `ollama pull qwen2.5:14b` |
| Qwen2.5 32B | ⭐⭐⭐⭐⭐ | ~20GB | xuất sắc | `ollama pull qwen2.5:32b` |
| Llama 3.1 8B | ⭐⭐⭐⭐ | ~5GB | khá | `ollama pull llama3.1:8b` |
| Gemma 2 9B | ⭐⭐⭐⭐ | ~6GB | khá | `ollama pull gemma2:9b` |
| DeepSeek-R1 (reasoning) | ⭐⭐⭐⭐⭐ | 7B~5GB | tốt | `ollama pull deepseek-r1:7b` |

Gọi API: `POST http://localhost:11434/api/chat` body `{"model":"qwen2.5:7b","messages":[...],"stream":false}`.
> **Dịch prompt VN→EN cho ảnh/video**: dùng chính LLM này (model ảnh/video hiểu tiếng Anh tốt nhất).

---

## 7. Model VISION (đọc/hiểu ảnh)

| Model | Việc | VRAM | Lệnh |
|---|---|---|---|
| **Qwen2.5-VL 7B** ⭐ | mô tả ảnh, OCR (cả tiếng Việt), phân tích | ~6GB | `ollama pull qwen2.5vl:7b` |
| LLaVA 1.6 | mô tả ảnh | ~6GB | `ollama pull llava:7b` |
| Llama 3.2 Vision 11B | đọc ảnh | ~8GB | `ollama pull llama3.2-vision:11b` |

Gọi (Ollama): `POST /api/chat` với `messages:[{role:user, content:"...", images:["<base64>"]}]`.

---

## 8. Model TTS (Text-to-Speech)

| Model | Chất lượng | Tiếng Việt | Clone giọng | Cài |
|---|---|---|---|---|
| **Piper** ⭐ | ⭐⭐⭐ | ✅ (vais1000) | ❌ | `pip install piper-tts` + tải giọng `rhasspy/piper-voices vi/vi_VN/vais1000/medium/*` |
| **viXTTS** | ⭐⭐⭐⭐ | ✅ tự nhiên | ✅ (mẫu ~6s) | `pip install coqui-tts` + model `capleaf/viXTTS`. ⚠️ hay xung đột `transformers` với ComfyUI → cài **venv riêng** hoặc container riêng |
| **F5-TTS** | ⭐⭐⭐⭐ | ✅ (bản VN) | ✅ | `pip install f5-tts` + checkpoint VN |
| **XTTS-v2** | ⭐⭐⭐⭐ | ❌ (không có VN chính thức) | ✅ | đa ngôn ngữ, VN dùng viXTTS |

> **Lưu ý**: coqui-tts/XTTS thường kén phiên bản `transformers` → tách môi trường riêng khỏi ComfyUI. Piper nhẹ (ONNX, không cần torch) → ổn định nhất.

---

## Ghi chú chung
- **Bản fp8** tiết kiệm ~½ VRAM, chất lượng gần bằng bf16 → ưu tiên cho GPU ≤32GB.
- **Model gated** (BFL FLUX…) → dùng mirror non-gated (Comfy-Org, Kijai, ChuckMcSneed).
- **1 GPU chạy tuần tự** (nhiều request tự xếp hàng). Song song thật cần nhiều GPU.
- **ComfyUI** hỗ trợ native: FLUX, SDXL, LTX-Video, HunyuanVideo, SD3.5, Mochi… Riêng **Wan** cần custom node `ComfyUI-WanVideoWrapper` + `ComfyUI-VideoHelperSuite`.
- Lấy đúng workflow/tham số: `GET http://localhost:18188/object_info` (schema node) + xem template trong `comfyui_workflow_templates_*`.

👉 Xem **[INSTALL.md](INSTALL.md)** để dựng nguyên hệ thống (VPS → ComfyUI → API → model) từ đầu.
