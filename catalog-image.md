# Catalog — Model ẢNH đầy đủ (kể cả chưa cài)

`M=/workspace/ComfyUI/models`. Model chưa cài vẫn ghi nguồn + cách cài để dùng khi cần.

## 1. Model sinh ảnh (text→image)

| Model | Chất lượng | Tốc độ | VRAM | License TM | Nguồn HF | Ghi chú |
|---|---|---|---|---|---|---|
| SD 1.5 | ⭐⭐ | ⚡⚡⚡ | 4GB | ✅ | `runwayml/stable-diffusion-v1-5` | cổ điển, hệ LoRA/ControlNet khổng lồ |
| SD 2.1 | ⭐⭐ | ⚡⚡ | 6GB | ✅ | `stabilityai/stable-diffusion-2-1` | ít dùng |
| SDXL base | ⭐⭐⭐ | ⚡⚡ | 8GB | ✅ | `stabilityai/stable-diffusion-xl-base-1.0` | chuẩn |
| **Juggernaut XL** | ⭐⭐⭐⭐ | ⚡⚡ | 8GB | ✅ | Civitai / HF | **ảnh thực đẹp** |
| **RealVisXL** | ⭐⭐⭐⭐ | ⚡⚡ | 8GB | ✅ | Civitai / HF | chân thực |
| Playground v2.5 | ⭐⭐⭐⭐ | ⚡⚡ | 8GB | ✅ | `playgroundai/playground-v2.5-1024px-aesthetic` | thẩm mỹ cao |
| PixArt-Sigma | ⭐⭐⭐⭐ | ⚡⚡ | 8GB | ✅ | `PixArt-alpha/PixArt-Sigma-XL-2-1024-MS` | nhẹ, bám prompt |
| Kolors | ⭐⭐⭐⭐ | ⚡⚡ | 10GB | ✅ | `Kwai-Kolors/Kolors` | tốt tiếng Trung/Anh |
| Sana | ⭐⭐⭐⭐ | ⚡⚡⚡ | 8GB | ✅ | `Efficient-Large-Model/Sana_1600M_1024px` | siêu nhanh (NVIDIA) |
| Lumina-Image 2.0 | ⭐⭐⭐⭐ | ⚡⚡ | 10GB | ✅ | `Alpha-VLLM/Lumina-Image-2.0` | mới |
| SD 3.5 Medium | ⭐⭐⭐⭐ | ⚡⚡ | 10GB | ✅ | `stabilityai/stable-diffusion-3.5-medium` | bám prompt |
| SD 3.5 Large | ⭐⭐⭐⭐⭐ | ⚡ | 18GB | ✅ | `stabilityai/stable-diffusion-3.5-large` | 8B, đẹp |
| **FLUX.1 schnell** | ⭐⭐⭐⭐ | ⚡⚡⚡ | 12GB | ✅ Apache | `Comfy-Org/flux1-schnell` | nhanh + **mở TM** |
| **FLUX.1 dev** | ⭐⭐⭐⭐⭐ | ⚡ | 12GB | ⚠️ NC | `Comfy-Org/flux1-dev` | đẹp nhất |
| **FLUX.1 Kontext** | ⭐⭐⭐⭐⭐ | ⚡ | 12GB | ⚠️ NC | `Comfy-Org/flux1-kontext-dev` | tạo + sửa ảnh |
| Chroma | ⭐⭐⭐⭐ | ⚡ | 12GB | ✅ Apache | `lodestones/Chroma` | FLUX-based, mở TM |
| Qwen-Image | ⭐⭐⭐⭐⭐ | ⚡ | 20GB | ✅ | `Qwen/Qwen-Image` | 20B, chữ tiếng Việt/Trung tốt |
| HiDream-I1 | ⭐⭐⭐⭐⭐ | ⚡ | 16–24GB | ✅ | `HiDream-ai/HiDream-I1-Full` | 17B, top chất lượng mở |

> Cài: gần hết là native ComfyUI. FLUX/SD3.5/SDXL dùng `CheckpointLoaderSimple` (all-in-one) hoặc `UNETLoader`+`DualCLIPLoader`+`VAELoader` (split). Xem workflow chuẩn ở template `comfyui_workflow_templates_media_image`.

## 2. Điều khiển tạo ảnh (conditioning)

| Công cụ | Việc | Nguồn | Ghi chú |
|---|---|---|---|
| **ControlNet** | Ép theo pose/depth/canny/lineart/scribble | `lllyasviel/ControlNet-v1-1` (SD1.5), `xinsir/controlnet-*` (SDXL), `Shakker-Labs/FLUX.1-dev-ControlNet-Union` (FLUX) | node `ControlNetLoader`+`ControlNetApply` |
| **IPAdapter** | Chuyển phong cách/khuôn mặt từ ảnh tham chiếu | `h94/IP-Adapter`, custom node `ComfyUI_IPAdapter_plus` | style/face transfer |
| **InstantID** | Giữ **khuôn mặt** người từ 1 ảnh (SDXL) | `InstantX/InstantID` | ID nhất quán |
| **PuLID / PuLID-FLUX** | Giữ mặt (chất lượng cao, FLUX) | `guozinan/PuLID` | tốt hơn InstantID |
| **T2I-Adapter** | nhẹ hơn ControlNet | `TencentARC/T2I-Adapter` | |
| **Redux (FLUX)** | biến thể ảnh theo tham chiếu | `Comfy-Org/flux1-redux-dev` | |

## 3. Nâng cấp / Phục hồi ảnh (upscale/restore)

| Model | Việc | Nguồn | Ghi chú |
|---|---|---|---|
| **Real-ESRGAN 4x** | phóng to 4x | `ai-forever/Real-ESRGAN` / `4x-UltraSharp` | node `UpscaleModelLoader` |
| **SUPIR** | phục hồi + upscale (đỉnh) | `Kijai/SUPIR_pruned` | nặng, đẹp nhất |
| **GFPGAN** | phục hồi **khuôn mặt** | `TencentARC/GFPGAN` | face restore |
| **CodeFormer** | phục hồi mặt (điều chỉnh độ) | `sczhou/CodeFormer` | |
| 4x-UltraSharp / 4x-AnimeSharp | ESRGAN model file | OpenModelDB | tải file `.pth` |

## 4. Tách nền / Phân vùng (segmentation)

| Model | Việc | Nguồn |
|---|---|---|
| **RMBG 2.0 / BiRefNet** | xóa nền chính xác | `briaai/RMBG-2.0`, `ZhengPeng7/BiRefNet` |
| **SAM 2** (Segment Anything) | chọn/tách đối tượng bất kỳ | `facebook/sam2-hiera-large` |
| rembg | xóa nền nhanh (lib) | `pip install rembg` |

## 5. Ghép mặt / Chỉnh sửa nâng cao

| Công cụ | Việc | Nguồn / node |
|---|---|---|
| **ReActor** | face swap (ghép mặt) | custom node `ComfyUI-ReActor` + inswapper |
| **IC-Light** | đổi ánh sáng (relighting) | `lllyasviel/IC-Light` |
| **IDM-VTON / CatVTON** | thử đồ ảo (virtual try-on) | `yisol/IDM-VTON`, `zhengchong/CatVTON` |
| **Inpaint (FLUX Fill / SDXL inpaint)** | tô vùng cần vẽ lại | `Comfy-Org/flux1-fill-dev`, `diffusers/stable-diffusion-xl-1.0-inpainting-0.1` |
| **Outpaint** | mở rộng khung ảnh | dùng inpaint + pad |

> **Ghi chú license**: FLUX dev/Kontext/Fill = phi thương mại. SDXL/SD3.5/Chroma/Qwen-Image/Sana/PixArt/Playground = mở, dùng thương mại được.
