# Catalog — Model VIDEO đầy đủ (kể cả chưa cài)

## 1. Model tạo video (tự host, mã nguồn mở)

| Model | Chất lượng | Tốc độ (3s) | VRAM (fp8) | Đĩa | T2V | I2V | Nguồn HF | Ghi chú |
|---|---|---|---|---|---|---|---|---|
| **LTX-Video 2B** | ⭐⭐⭐ | ~10–15s ⚡⚡⚡ | 8GB | 6GB | ✅ | ✅ | `Lightricks/LTX-Video` | nhanh nhất, native |
| **LTX-Video 13B** | ⭐⭐⭐⭐ | ~30–60s | 16–24GB | 15–28GB | ✅ | ✅ | `Lightricks/LTX-Video` | bản lớn, đẹp hơn |
| Wan 2.1 T2V 1.3B | ⭐⭐ | ~30s | 6GB | 3GB | ✅ | ✅ | `Kijai/WanVideo_comfy` | nhẹ nhất |
| Wan 2.1 T2V/I2V 14B | ⭐⭐⭐⭐ | vài phút | 24GB | ~16GB | ✅ | ✅ | `Kijai/WanVideo_comfy` | |
| **Wan 2.2 TI2V-5B** | ⭐⭐⭐⭐ | ~30–40s ⚡ | 12GB | 17GB | ✅ | ✅ | `Kijai/WanVideo_comfy` | **cân bằng nhất** |
| **Wan 2.2 I2V A14B** | ⭐⭐⭐⭐⭐ | vài phút 🐢 | 28–48GB | ~30GB | ✅ | ✅ | `Kijai/WanVideo_comfy` | đẹp nhất, cần 48GB |
| **HunyuanVideo 13B** | ⭐⭐⭐⭐⭐ | ~2 phút 🐢 | 18–24GB | 23GB | ✅ | ✅* | `Comfy-Org/HunyuanVideo_repackaged`, `Kijai/HunyuanVideo_comfy` | *I2V model riêng |
| **CogVideoX-5B** | ⭐⭐⭐ | ~1–2 phút | 12GB | 11GB | ✅ | ✅ | `THUDM/CogVideoX-5b` | |
| **Mochi 1** (10B) | ⭐⭐⭐⭐ | vài phút | 24GB | 20GB | ✅ | ❌ | `genmo/mochi-1-preview` | |
| **Pyramid Flow** | ⭐⭐⭐ | ~1 phút | 12GB | ~8GB | ✅ | ✅ | `rain1011/pyramid-flow-sd3` | |
| **Open-Sora 2.0** | ⭐⭐⭐⭐ | vài phút | 24GB+ | ~30GB | ✅ | ✅ | `hpcai-tech/Open-Sora-v2` | mở hoàn toàn |
| **SkyReels V2** | ⭐⭐⭐⭐ | vài phút | 16–24GB | ~16GB | ✅ | ✅ | `Skywork/SkyReels-V2-*` | phim dài, Wan-based |
| **Step-Video T2V** | ⭐⭐⭐⭐ | rất chậm | 40GB+ | ~60GB | ✅ | ❌ | `stepfun-ai/stepvideo-t2v` | 30B, cần GPU khủng |
| **AnimateDiff** | ⭐⭐ | ~20s ⚡ | 6GB | 5GB | ✅ | ❌ | `guoyww/animatediff` | nền SD1.5/SDXL, stylized |

## 2. Video có ÂM THANH

| Model | Việc | Nguồn | Ghi chú |
|---|---|---|---|
| **HunyuanVideo-Foley / MMAudio** | tạo tiếng động khớp video câm | `hkchengrex/MMAudio` | video→audio |
| **Ovi (Wan-based)** | tạo thẳng video + audio | node `ComfyUI-WanVideoWrapper` (Ovi) | |

## 3. Nâng cấp / mượt video

| Công cụ | Việc | Nguồn |
|---|---|---|
| **RIFE / FILM** | nội suy khung (mượt, slow-mo) | node `ComfyUI-Frame-Interpolation` |
| **LTXV upscaler** | upscale video LTX | `Lightricks/LTX-Video` (spatial/temporal upscaler) |
| Real-ESRGAN (per-frame) | upscale từng frame | như phần ảnh |

## 4. Model video qua API (không tự host — chất lượng cao nhất thị trường)

> Các model này **không tải về máy được**, chỉ gọi API trả phí. Chất lượng đỉnh, dùng khi cần thương mại/chất lượng cao.

| Dịch vụ | Điểm mạnh | Cách dùng |
|---|---|---|
| **Google Veo 3** | đẹp nhất + có audio | Google Gemini API / Vertex |
| **OpenAI Sora** | video dài, nhất quán | OpenAI API |
| **Kling AI** | chuyển động mượt, phổ biến | Kling API |
| **Runway Gen-3/4** | điện ảnh | Runway API |
| **Luma Dream Machine** | nhanh, đẹp | Luma API |
| **Pika** | hiệu ứng | Pika API |
| **MiniMax / Hailuo** | rẻ, tốt | MiniMax API |

## Cách "nối clip thành video dài"
Model open chỉ tạo ~5–10s/clip. Muốn dài: **nối clip** (lấy khung cuối clip trước làm ảnh đầu clip sau qua I2V) + ghép bằng `ffmpeg`. Chất lượng trôi dần sau ~1–2 phút → phim dài cần dựng nhiều CẢNH có cắt (như làm phim thật), không nối liền tù tì.

> **Tự host trên GPU 24–32GB**: LTX (nhanh), Wan 2.2 5B (cân bằng), HunyuanVideo (đẹp). **Cần 48GB+**: Wan 2.2 14B, Step-Video, Open-Sora 2.
