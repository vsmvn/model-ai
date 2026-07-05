# Hệ sinh thái đầy đủ theo hãng

Liệt kê **toàn bộ** model theo từng hãng lớn (open-weights tự host + bản API). `M=/workspace/ComfyUI/models`.

**Ảnh:** [A. Black Forest Labs (FLUX)](#a-black-forest-labs--họ-flux) · [B. Stability AI (Stable Diffusion)](#b-stability-ai--họ-stable-diffusion-đa-số-mở-thương-mại)
**Video:** [C. Alibaba (Wan)](#c-alibaba--họ-wan-wanx) · [D. Tencent (Hunyuan)](#d-tencent--họ-hunyuan) · [E. Lightricks (LTX-Video)](#e-lightricks--ltx-video)

---

## A. BLACK FOREST LABS — họ FLUX

### A.1 Open weights (tự host được)
| Model | Việc | License TM | VRAM | Nguồn (mirror non-gated) |
|---|---|---|---|---|
| **FLUX.1 [schnell]** | tạo ảnh nhanh (4 bước) | ✅ **Apache** | 12GB | `Comfy-Org/flux1-schnell` |
| **FLUX.1 [dev]** | tạo ảnh đẹp nhất (20 bước) | ⚠️ Non-commercial | 12GB (fp8) | `Comfy-Org/flux1-dev` |
| **FLUX.1 Kontext [dev]** | **sửa ảnh** giữ nhân vật + tạo ảnh | ⚠️ NC | 12GB | `Comfy-Org/flux1-kontext-dev` |
| **FLUX.1 Fill [dev]** | **inpaint/outpaint** (tô/mở rộng) | ⚠️ NC | 12GB | `Comfy-Org/flux1-fill-dev` |
| **FLUX.1 Canny [dev]** | ControlNet theo đường viền | ⚠️ NC | 12GB | `Comfy-Org` (flux1-canny-dev) |
| **FLUX.1 Depth [dev]** | ControlNet theo chiều sâu | ⚠️ NC | 12GB | `Comfy-Org` (flux1-depth-dev) |
| **FLUX.1 Redux [dev]** | biến thể/chuyển phong cách từ ảnh | ⚠️ NC | 12GB | `Comfy-Org/flux1-redux-dev` |
| **FLUX.1 Canny/Depth LoRA** | ControlNet dạng LoRA (nhẹ) | ⚠️ NC | 12GB | `black-forest-labs/FLUX.1-Canny-dev-lora` |
| **FLUX.2 [dev]** | thế hệ mới (2025), đẹp hơn, bám prompt/chữ tốt | ⚠️ NC | 24GB+ (fp8) | `black-forest-labs/FLUX.2-dev` (gated) / mirror Comfy-Org khi có |
| **FLUX.2 [klein]** | bản distilled nhẹ của FLUX.2 | ✅ (mở hơn) | ~16GB | `black-forest-labs/FLUX.2-klein` |

> **Text encoder chung cho FLUX.1**: `t5xxl_fp8_e4m3fn_scaled` + `clip_l` (`comfyanonymous/flux_text_encoders`). **VAE**: `ae.safetensors` (mirror `ChuckMcSneed/FLUX.1-dev`).
> Bản `black-forest-labs/*` là **gated** (cần token + duyệt license) → dùng mirror `Comfy-Org/*` cho non-gated.

Cài (ví dụ FLUX Fill để inpaint):
```bash
hf download Comfy-Org/flux1-fill-dev flux1-fill-dev-fp8.safetensors --local-dir $M/diffusion_models
# encoders + ae như FLUX.1 (dùng chung)
```

### A.2 Bản API (không tự host — chất lượng cao nhất)
| Model | Ghi chú |
|---|---|
| **FLUX.1 [pro]**, **FLUX 1.1 [pro]** | chất lượng pro, nhanh |
| **FLUX 1.1 [pro] ultra / raw** | 4MP, ảnh thực |
| **FLUX.1 Kontext [pro] / [max]** | sửa ảnh bản pro |
| **FLUX.2 [pro] / [flex]** | thế hệ mới, đỉnh |
| Gọi: `api.bfl.ai` (BFL API) hoặc qua fal.ai/Replicate | ~$0.04–0.06/ảnh |

### A.3 License FLUX (quan trọng)
- **schnell = Apache** (thương mại thoải mái). **dev/Kontext/Fill/Canny/Depth/Redux = Non-commercial** (cần mua license ~$999/tháng để dùng thương mại, hoặc dùng schnell/API).

---

## B. STABILITY AI — họ Stable Diffusion (đa số MỞ thương mại)

### B.1 Ảnh (image)
| Model | Việc | VRAM | Nguồn |
|---|---|---|---|
| **SD 1.5** | cổ điển, hệ LoRA/ControlNet khổng lồ | 4GB | `runwayml/stable-diffusion-v1-5` |
| **SD 2.1** | ít dùng | 6GB | `stabilityai/stable-diffusion-2-1` |
| **SDXL 1.0 base** | chuẩn phổ biến | 8GB | `stabilityai/stable-diffusion-xl-base-1.0` |
| **SDXL Refiner** | tinh chỉnh chi tiết sau base | +4GB | `stabilityai/stable-diffusion-xl-refiner-1.0` |
| **SDXL Turbo** | **1–4 bước, siêu nhanh** | 8GB | `stabilityai/sdxl-turbo` |
| **SDXL Lightning** | 2–8 bước nhanh (ByteDance, nền SDXL) | 8GB | `ByteDance/SDXL-Lightning` |
| **Stable Cascade** | Würstchen, hiệu quả cao | 10GB | `stabilityai/stable-cascade` |
| **SD 3 Medium** | thế hệ 3 | 10GB | `stabilityai/stable-diffusion-3-medium` |
| **SD 3.5 Medium** | 2.5B, bám prompt tốt | 10GB | `stabilityai/stable-diffusion-3.5-medium` |
| **SD 3.5 Large** | 8B, đẹp | 18GB | `stabilityai/stable-diffusion-3.5-large` |
| **SD 3.5 Large Turbo** | 8B, 4 bước nhanh | 18GB | `stabilityai/stable-diffusion-3.5-large-turbo` |
| **SDXL Inpainting** | tô vùng vẽ lại | 8GB | `diffusers/stable-diffusion-xl-1.0-inpainting-0.1` |

### B.2 Video
| Model | Việc | VRAM | Nguồn |
|---|---|---|---|
| **Stable Video Diffusion (SVD)** | **ảnh→video** ~2–4s | 12GB | `stabilityai/stable-video-diffusion-img2vid` |
| **SVD-XT** | ảnh→video 25 frame | 12–16GB | `stabilityai/stable-video-diffusion-img2vid-xt` |

### B.3 3D
| Model | Việc | Nguồn |
|---|---|---|
| **Stable Zero123** | ảnh → nhiều góc nhìn | `stabilityai/stable-zero123` |
| **SV3D** | ảnh → video quay quanh vật thể | `stabilityai/sv3d` |
| **Stable Fast 3D (SF3D)** | ảnh → mesh 3D nhanh | `stabilityai/stable-fast-3d` |
| **SPAR3D** | ảnh → 3D (point-aware) | `stabilityai/stable-point-aware-3d` |

### B.4 Âm thanh
| Model | Việc | Nguồn |
|---|---|---|
| **Stable Audio Open 1.0** | text→nhạc/sfx (**mở TM**) | `stabilityai/stable-audio-open-1.0` |
| Stable Audio 2.0 | nhạc dài (API) | Stability API |

### B.5 License Stability
- SD1.5/2.1/SDXL/Turbo/Cascade/SVD: **CreativeML OpenRAIL / Stability Community License** — **dùng thương mại được** (SD3.5 & mới có Community License: miễn phí nếu doanh thu < $1M/năm, trên đó cần Enterprise).
- **Ưu điểm lớn của Stability vs FLUX dev**: **dùng thương mại thoải mái** hơn.

---

## Chọn giữa FLUX và Stable Diffusion?
| Tiêu chí | FLUX | Stable Diffusion |
|---|---|---|
| Chất lượng/bám prompt/tay/chữ | ⭐⭐⭐⭐⭐ (dev/Kontext) | ⭐⭐⭐⭐ (SD3.5) |
| Tốc độ | dev chậm hơn; schnell nhanh | SDXL Turbo/Lightning **rất nhanh** |
| **License thương mại** | ⚠️ dev NC (schnell Apache) | ✅ **mở** (dễ thương mại) |
| Sửa ảnh giữ nhân vật | ✅ **Kontext** (tốt nhất) | ❌ (dùng inpaint/IPAdapter) |
| Hệ LoRA/ControlNet cộng đồng | đang lớn | **khổng lồ** (SD1.5/SDXL) |
| Ảnh→video | ❌ | ✅ **SVD** |
| 3D | ❌ | ✅ (Zero123/SV3D/SF3D) |

**Tóm lại**: FLUX = chất lượng đỉnh + sửa ảnh (nhưng dev phi thương mại). Stability = mở thương mại + đa dạng (ảnh/video/3D/audio) + hệ sinh thái LoRA/ControlNet lớn nhất + có Turbo siêu nhanh.

---

## C. ALIBABA — họ Wan (Wanx)
Model video mở, mạnh, **có tiếng Việt encoder umt5**. Chạy qua custom node **ComfyUI-WanVideoWrapper** (Kijai) hoặc native ComfyUI. Nguồn chung: `Kijai/WanVideo_comfy` (fp8, tiện ComfyUI) hoặc gốc `Wan-AI/*`.

| Model | Việc | VRAM (fp8) | Đĩa | Ghi chú |
|---|---|---|---|---|
| **Wan 2.1 T2V 1.3B** | text→video nhẹ | 6GB | 3GB | nhanh, nhân vật hay lỗi |
| **Wan 2.1 T2V 14B** | text→video đẹp | 24GB | ~16GB | |
| **Wan 2.1 I2V 14B** (480p/720p) | ảnh→video | 24GB | ~16GB | |
| **Wan 2.1 FLF2V 14B** | video từ khung đầu+cuối | 24GB | ~16GB | nội suy 2 ảnh |
| **Wan 2.1 VACE** | tạo + **sửa/điều khiển** video (all-in-one) | 16–24GB | ~16GB | controlnet cho video |
| **Wan 2.2 TI2V-5B** ⭐ | text+ảnh→video, cân bằng nhất | 12GB | 17GB | nhanh + đẹp |
| **Wan 2.2 T2V A14B** (MoE) | text→video chất lượng cao | 28–48GB | ~30GB | cần GPU lớn |
| **Wan 2.2 I2V A14B** (MoE) | ảnh→video đỉnh | 28–48GB | ~30GB | |
| **Wan 2.2 S2V** | **âm thanh→video** (nói→hình) | 24GB | ~16GB | lip-sync |
| **Wan 2.2 Animate** | animate nhân vật theo pose | 24GB | ~16GB | |

Text encoder: `umt5-xxl-enc-fp8_e4m3fn` · VAE: `Wan2_1_VAE` (2.1) / `Wan2_2_VAE` (2.2).
Cài (Wan 2.2 5B): xem [catalog-video.md](catalog-video.md) hoặc [INSTALL.md](INSTALL.md). License: **Apache 2.0 (mở thương mại)**.

---

## D. TENCENT — họ Hunyuan
Đa dạng: video, ảnh, 3D. Nguồn: `Comfy-Org/HunyuanVideo_repackaged` (native), `Kijai/HunyuanVideo_comfy` (fp8), `tencent/*`.

| Model | Loại | VRAM | Đĩa | Nguồn |
|---|---|---|---|---|
| **HunyuanVideo** (13B) | text→video, đẹp | 18–24GB | 23GB (fp8) | `Comfy-Org/HunyuanVideo_repackaged` |
| **HunyuanVideo I2V** | ảnh→video | 18–24GB | +13GB | `Kijai/HunyuanVideo_comfy` |
| **HunyuanVideo 1.5** | bản mới, **nhẹ hơn** | 12–16GB | ~13GB | `tencent/HunyuanVideo-1.5` |
| **HunyuanVideo-Foley** | tạo **âm thanh** cho video | 12GB | ~8GB | `tencent/HunyuanVideo-Foley` |
| **HunyuanVideo-Avatar** | nhân vật nói (avatar) | 24GB | ~16GB | `tencent/HunyuanVideo-Avatar` |
| **HunyuanImage 2.1** | tạo **ẢNH** chất lượng cao | 16–24GB | ~20GB | `tencent/HunyuanImage-2.1` |
| **HunyuanDiT** | tạo ảnh (bản cũ, tiếng Trung tốt) | 12GB | ~8GB | `Tencent-Hunyuan/HunyuanDiT` |
| **Hunyuan3D 2.0 / 2.1** | ảnh/text → **mesh 3D** (đỉnh mở) | 16–24GB | ~15GB | `tencent/Hunyuan3D-2.1` |

Text encoder video: `llava_llama3_fp8` + `clip_l`. License: **Tencent Hunyuan Community** (mở, hạn chế vùng EU/UK và >100tr user).

---

## E. LIGHTRICKS — LTX-Video
Video **nhanh nhất** (gần real-time), native ComfyUI. Nguồn: `Lightricks/LTX-Video`. Text encoder: `t5xxl` (dùng chung FLUX), type `ltxv`.

| Model | Việc | VRAM | Đĩa | Ghi chú |
|---|---|---|---|---|
| **LTXV 2B 0.9.6/0.9.8 distilled** ⭐ | text/ảnh→video **siêu nhanh** | 8GB | 6GB | ~10–15s/clip |
| **LTXV 2B 0.9.x dev** | bản đầy đủ 2B | 10GB | 6GB | |
| **LTXV 13B 0.9.8 dev/distilled** | bản lớn, đẹp hơn | 16–24GB | 15–28GB | fp8 ~15GB |
| **LTXV spatial/temporal upscaler** | nâng cấp video LTX | +2GB | 0.5GB | nét + mượt hơn |
| **LTX-2** (mới) | thế hệ 2, **có audio**, 4K | 24GB+ | lớn | text/ảnh→video kèm tiếng |
| **LTXV IC-LoRA** (pose/depth/canny) | điều khiển video | +nhẹ | nhỏ | controlnet cho LTX |

Cài (LTXV 2B nhanh): xem [catalog-video.md](catalog-video.md). License: **mở** (LTXV có bản dùng thương mại — kiểm tra từng bản).

---

## Tổng kết video theo hãng
| Hãng | Điểm mạnh | Bản nên dùng (GPU 24–32GB) |
|---|---|---|
| **Alibaba (Wan)** | cân bằng, đa dạng (T2V/I2V/S2V/VACE), **mở TM** | Wan 2.2 TI2V-5B |
| **Tencent (Hunyuan)** | chất lượng cao, có ảnh+3D+audio | HunyuanVideo (đẹp) / 1.5 (nhẹ) |
| **Lightricks (LTX)** | **nhanh nhất**, real-time, có upscaler | LTXV 2B distilled |
