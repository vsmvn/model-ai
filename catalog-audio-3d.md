# Catalog — ÂM THANH & 3D (kể cả chưa cài)

## 1. TTS — Đọc văn bản thành giọng nói

| Model | Chất lượng | Tiếng Việt | Clone giọng | VRAM | Nguồn / cài |
|---|---|---|---|---|---|
| **Piper** | ⭐⭐⭐ | ✅ | ❌ | ~0 (ONNX) | `pip install piper-tts` + `rhasspy/piper-voices` (vi_VN) — nhẹ, ổn định nhất |
| **viXTTS** | ⭐⭐⭐⭐ | ✅ tự nhiên | ✅ (~6s mẫu) | ~2GB | `pip install coqui-tts` + `capleaf/viXTTS` — ⚠️ kén transformers, dùng venv riêng |
| **F5-TTS** | ⭐⭐⭐⭐ | ✅ (bản VN) | ✅ | ~4GB | `pip install f5-tts` + checkpoint `hynt/F5-TTS-Vietnamese-*` |
| **XTTS-v2** | ⭐⭐⭐⭐ | ❌ | ✅ | ~2GB | `coqui/XTTS-v2` — 17 ngôn ngữ (không VN chính thức) |
| **Kokoro** | ⭐⭐⭐⭐ | ❌ | ❌ | nhẹ | `hexgrad/Kokoro-82M` — nhẹ, tiếng Anh hay |
| **ChatTTS** | ⭐⭐⭐⭐ | một phần | ✅ | ~4GB | `2Noise/ChatTTS` — hội thoại tự nhiên |
| **Fish Speech / OpenAudio** | ⭐⭐⭐⭐⭐ | ✅ | ✅ | ~4GB | `fishaudio/fish-speech-1.5` — đa ngôn ngữ, clone tốt |

## 2. ASR — Giọng nói thành văn bản (speech-to-text)

| Model | Chất lượng | Tiếng Việt | Nguồn / cài |
|---|---|---|---|
| **Whisper large-v3** | ⭐⭐⭐⭐⭐ | ✅ tốt | `openai/whisper-large-v3` (`pip install openai-whisper`) |
| **faster-whisper** | ⭐⭐⭐⭐⭐ | ✅ | `pip install faster-whisper` — nhanh gấp 4 (CTranslate2) |
| WhisperX | ⭐⭐⭐⭐⭐ | ✅ + timestamp/diarization | `pip install whisperx` |
| PhoWhisper | ⭐⭐⭐⭐ | ✅ chuyên VN | `vinai/PhoWhisper-large` |

## 3. Nhạc & Âm thanh (music/sound generation)

| Model | Việc | Nguồn |
|---|---|---|
| **MusicGen** | text→nhạc | `facebook/musicgen-large` (`audiocraft`) |
| **AudioGen** | text→tiếng động | `facebook/audiogen-medium` |
| **Stable Audio Open** | text→nhạc/sfx (mở TM) | `stabilityai/stable-audio-open-1.0` |
| **MMAudio** | video→audio khớp cảnh | `hkchengrex/MMAudio` |
| **ACE-Step** | nhạc có lời (như Suno) | `ACE-Step/ACE-Step-v1-3.5B` |

## 4. Model 3D (text/ảnh → 3D)

| Model | Việc | VRAM | Nguồn |
|---|---|---|---|
| **Hunyuan3D 2.1** | ảnh/text → mesh 3D (đỉnh mở) | 16–24GB | `tencent/Hunyuan3D-2.1` |
| **TRELLIS** | ảnh → 3D chất lượng cao (Microsoft) | 16GB | `microsoft/TRELLIS-image-large` |
| **TripoSR** | ảnh → 3D **siêu nhanh** (~1s) | 6GB | `stabilityai/TripoSR` |
| **InstantMesh** | ảnh → mesh | 12GB | `TencentARC/InstantMesh` |
| **Stable Zero123** | ảnh → nhiều góc nhìn | 8GB | `stabilityai/stable-zero123` |
| **SF3D** | ảnh → 3D có texture | 8GB | `stabilityai/stable-fast-3d` |

> **VPS 3D**: TripoSR/Zero123 chạy 8–12GB; Hunyuan3D/TRELLIS cần 16–24GB. Nhiều model 3D dùng ComfyUI (node `Hunyuan3D`, `TripoSR`) hoặc repo gốc.

## Gợi ý ghép chuỗi (pipeline)
- **Video có tiếng thuyết minh**: tạo video (Wan/LTX) → TTS lời thoại (Piper/viXTTS) → ghép `ffmpeg`.
- **Video có nhạc/tiếng động**: video câm → MMAudio (tiếng động) hoặc MusicGen (nhạc nền) → trộn.
- **Nhân vật 3D từ ảnh**: FLUX tạo ảnh nhân vật → Hunyuan3D → mesh 3D.
