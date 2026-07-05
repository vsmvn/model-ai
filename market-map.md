# Bản đồ MÃ NGUỒN MỞ đầy đủ (tự host được)

Chỉ liệt kê model **open-weights — tải về tự chạy**. Đánh dấu license thương mại: ✅ mở TM · ⚠️ hạn chế (phi thương mại/community).
> Chi tiết theo hãng: [ecosystems.md](ecosystems.md). Theo danh mục: [catalog-image](catalog-image.md), [catalog-video](catalog-video.md), [catalog-audio-3d](catalog-audio-3d.md), [catalog-llm](catalog-llm.md).

---

## 1. Ảnh (open-weights)
| Model | Hãng | TM | VRAM | Nguồn HF |
|---|---|---|---|---|
| SD 1.5 / SDXL / SD3.5 / Turbo / Cascade | Stability | ✅ | 4–18GB | ecosystems.md (B) |
| FLUX schnell | BFL | ✅ Apache | 12GB | `Comfy-Org/flux1-schnell` |
| FLUX dev / Kontext / Fill / Canny / Depth / Redux / FLUX.2 | BFL | ⚠️ NC | 12–24GB | ecosystems.md (A) |
| Qwen-Image (20B) | Alibaba | ✅ | 20GB | `Qwen/Qwen-Image` |
| HunyuanImage 2.1, HunyuanDiT | Tencent | ✅* | 12–24GB | `tencent/HunyuanImage-2.1` |
| Kolors | Kwai | ✅ | 10GB | `Kwai-Kolors/Kolors` |
| Sana 0.6B/1.6B (siêu nhanh) | NVIDIA | ✅ | 8GB | `Efficient-Large-Model/Sana_*` |
| PixArt-Sigma | PixArt | ✅ | 8GB | `PixArt-alpha/PixArt-Sigma-*` |
| Playground v2.5 | Playground | ✅ | 8GB | `playgroundai/playground-v2.5-*` |
| Lumina-Image 2.0 | Alpha-VLLM | ✅ | 10GB | `Alpha-VLLM/Lumina-Image-2.0` |
| HiDream-I1 (17B) | HiDream | ✅ | 16–24GB | `HiDream-ai/HiDream-I1-Full` |
| Chroma (FLUX-based) | lodestones | ✅ Apache | 12GB | `lodestones/Chroma` |
| **OmniGen / OmniGen2** (tạo+sửa hợp nhất) | VectorSpaceLab | ✅ | 12–16GB | `Shitao/OmniGen-v1`, `OmniGen2/OmniGen2` |

## 2. Video (open-weights)
| Model | Hãng | TM | VRAM | Nguồn |
|---|---|---|---|---|
| LTX-Video 2B/13B, LTX-2 | Lightricks | ✅ | 8–24GB | `Lightricks/LTX-Video` |
| Wan 2.1/2.2 (1.3B–14B, I2V/S2V/VACE/Animate) | Alibaba | ✅ Apache | 6–48GB | `Kijai/WanVideo_comfy` |
| HunyuanVideo 13B/1.5/I2V/Foley/Avatar | Tencent | ✅* | 12–24GB | `Comfy-Org/HunyuanVideo_repackaged` |
| Mochi 1 (10B) | Genmo | ✅ Apache | 24GB | `genmo/mochi-1-preview` |
| CogVideoX 2B/5B | THUDM | ✅ | 8–12GB | `THUDM/CogVideoX-5b` |
| Allegro | Rhymes AI | ✅ Apache | 12GB | `rhymes-ai/Allegro` |
| Open-Sora 2.0 | HPC-AI | ✅ | 24GB+ | `hpcai-tech/Open-Sora-v2` |
| SkyReels V2 | Skywork | ✅ | 16–24GB | `Skywork/SkyReels-V2-*` |
| Pyramid Flow | rain1011 | ✅ | 12GB | `rain1011/pyramid-flow-sd3` |
| Step-Video T2V (30B) | StepFun | ✅ | 40GB+ | `stepfun-ai/stepvideo-t2v` |
| Stable Video Diffusion (ảnh→video) | Stability | ✅ | 12GB | `stabilityai/stable-video-diffusion-*` |
| AnimateDiff | — | ✅ | 6GB | `guoyww/animatediff` |
| Cosmos (world model) | NVIDIA | ✅ | 24GB+ | `nvidia/Cosmos-*` |

## 3. LLM (open-weights)
| Model | Hãng | TM | Lệnh Ollama |
|---|---|---|---|
| Qwen2.5 / Qwen3 (0.5B–72B) | Alibaba | ✅ Apache | `ollama pull qwen2.5:7b` |
| Llama 3.1/3.3/4 | Meta | ✅* | `ollama pull llama3.1:8b` |
| Gemma 2/3 | Google | ✅ | `ollama pull gemma2:9b` |
| DeepSeek V3 / R1 | DeepSeek | ✅ | `ollama pull deepseek-r1:7b` |
| Mistral / Mixtral / Codestral | Mistral | ✅ Apache* | `ollama pull mistral` |
| Phi-4 | Microsoft | ✅ MIT | `ollama pull phi4` |
| Yi 1.5 | 01.AI | ✅ | `ollama pull yi` |
| Nemotron | NVIDIA | ✅ | `ollama pull nemotron` |
| Granite 3 | IBM | ✅ Apache | `ollama pull granite3-dense` |
| DBRX | Databricks | ✅ | HF |
| Falcon 3 | TII | ✅ | `ollama pull falcon3` |
| **Code**: Qwen2.5-Coder, DeepSeek-Coder, CodeLlama, Codestral | — | ✅ | `ollama pull qwen2.5-coder:7b` |
| **Vision**: Qwen2.5-VL, LLaVA, Llama3.2-Vision, MiniCPM-V, InternVL, Molmo | — | ✅ | `ollama pull qwen2.5vl:7b` |
| **Embedding**: bge-m3, nomic-embed, e5 | — | ✅ | `ollama pull bge-m3` |

## 4. Giọng nói & Nhạc (open-weights)
| Loại | Model | Nguồn |
|---|---|---|
| TTS | Piper, viXTTS, F5-TTS, Fish-Speech, Kokoro, ChatTTS, XTTS-v2 | catalog-audio-3d.md |
| TTS realtime/hội thoại | Kyutai **Moshi**, Nari **Dia**, Sesame **CSM** | `kyutai/moshi`, `nari-labs/Dia-1.6B` |
| Dịch giọng | Meta **Seamless** | `facebook/seamless-m4t-v2-large` |
| ASR (giọng→text) | Whisper large-v3, faster-whisper, WhisperX, **PhoWhisper** (VN), NVIDIA Parakeet/Canary | catalog-audio-3d.md |
| Nhạc | Meta **MusicGen/AudioCraft**, **Stable Audio Open**, **ACE-Step** | catalog-audio-3d.md |
| Audio cho video | **MMAudio**, HunyuanVideo-Foley | `hkchengrex/MMAudio` |

## 5. 3D (open-weights)
| Model | Hãng | Nguồn |
|---|---|---|
| Hunyuan3D 2.0/2.1 | Tencent | `tencent/Hunyuan3D-2.1` |
| TRELLIS | Microsoft | `microsoft/TRELLIS-image-large` |
| TripoSR (siêu nhanh) | Stability | `stabilityai/TripoSR` |
| InstantMesh | TencentARC | `TencentARC/InstantMesh` |
| SV3D / SF3D / SPAR3D / Zero123 | Stability | ecosystems.md (B.3) |

## 6. Thị giác / Công cụ (open-weights, dùng trong pipeline)
| Việc | Model | Nguồn |
|---|---|---|
| Phân vùng đối tượng | **SAM 2** | `facebook/sam2` |
| Chiều sâu | **Depth Anything V2** | `depth-anything/Depth-Anything-V2-Large` |
| Nhận diện | YOLO v11, Grounding DINO | `ultralytics`, `IDEA-Research/grounding-dino` |
| Pose người | DWPose, OpenPose | ControlNet-aux |
| Xóa nền | RMBG-2.0, BiRefNet | catalog-image.md |
| OCR (đọc chữ ảnh) | **GOT-OCR2**, PaddleOCR, docTR | `stepfun-ai/GOT-OCR2_0` |
| Face restore / Upscale | GFPGAN, CodeFormer, Real-ESRGAN, SUPIR | catalog-image.md |
| ControlNet / IPAdapter / InstantID / PuLID | — | catalog-image.md |
| Robotics (VLA) | OpenVLA, Pi0 | `openvla/openvla-7b` |

---

## Ghi chú
- **✅*** = license community/hạn chế nhẹ (Llama: giới hạn >700tr user; Hunyuan: hạn chế EU/UK; Mistral một số bản Research). Đa số vẫn **dùng thương mại được** ở quy mô thường.
- **⚠️ NC** (FLUX dev/Kontext...) = phi thương mại (cần license để bán). Bản mở TM thay thế: **FLUX schnell (Apache)** hoặc **SD/SDXL, Qwen-Image, Chroma**.
- Cài bất kỳ model nào → xem [INSTALL.md](INSTALL.md) + lệnh `hf download` trong catalog tương ứng.
