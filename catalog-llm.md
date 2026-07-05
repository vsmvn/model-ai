# Catalog — LLM (Chat / Code / Vision / Embedding)

Chạy qua **Ollama** (`ollama pull <model>`, API `localhost:11434`) hoặc **vLLM** (nhanh hơn, OpenAI-compatible).

## 1. Chat / Đa năng

| Model | Chất lượng | VRAM (4-bit) | Tiếng Việt | Lệnh |
|---|---|---|---|---|
| **Qwen2.5 7B** ⭐ | ⭐⭐⭐⭐ | ~5GB | tốt | `ollama pull qwen2.5:7b` |
| Qwen2.5 14B/32B/72B | ⭐⭐⭐⭐⭐ | 9/20/45GB | rất tốt | `ollama pull qwen2.5:32b` |
| Qwen3 (mới) | ⭐⭐⭐⭐⭐ | tùy | tốt | `ollama pull qwen3:8b` |
| Llama 3.1/3.3 8B–70B | ⭐⭐⭐⭐ | 5–45GB | khá | `ollama pull llama3.1:8b` |
| Gemma 2/3 9B–27B | ⭐⭐⭐⭐ | 6–18GB | khá | `ollama pull gemma2:9b` |
| Mistral / Mixtral | ⭐⭐⭐⭐ | 5–28GB | khá | `ollama pull mistral` |
| **DeepSeek-R1** (reasoning) | ⭐⭐⭐⭐⭐ | 7B~5GB | tốt | `ollama pull deepseek-r1:7b` |
| Phi-4 (nhỏ mà mạnh) | ⭐⭐⭐⭐ | ~9GB | khá | `ollama pull phi4` |

## 2. Code (lập trình)

| Model | Nguồn / lệnh | Ghi chú |
|---|---|---|
| **Qwen2.5-Coder 7B/32B** | `ollama pull qwen2.5-coder:7b` | code tốt nhất mở |
| DeepSeek-Coder V2 | `ollama pull deepseek-coder-v2` | |
| CodeLlama | `ollama pull codellama` | cổ điển |
| Codestral | `ollama pull codestral` | Mistral, 22B |

## 3. Vision (đọc/hiểu ảnh — multimodal)

| Model | Việc | VRAM | Lệnh |
|---|---|---|---|
| **Qwen2.5-VL 7B** ⭐ | mô tả ảnh, OCR (VN), phân tích | ~6GB | `ollama pull qwen2.5vl:7b` |
| LLaVA 1.6 | mô tả ảnh | ~6GB | `ollama pull llava` |
| Llama 3.2 Vision 11B/90B | đọc ảnh | 8/55GB | `ollama pull llama3.2-vision` |
| MiniCPM-V 2.6 | nhẹ, mạnh | ~6GB | `ollama pull minicpm-v` |
| InternVL / Molmo | phân tích sâu | tùy | HF repo |

Gọi vision (Ollama): `POST /api/chat` với `messages:[{role:"user",content:"mô tả ảnh",images:["<base64>"]}]`.

## 4. Embedding (RAG / tìm kiếm ngữ nghĩa)

| Model | Việc | Lệnh |
|---|---|---|
| **bge-m3** | embedding đa ngôn ngữ (VN tốt) | `ollama pull bge-m3` |
| nomic-embed-text | nhẹ, tốt | `ollama pull nomic-embed-text` |
| multilingual-e5-large | đa ngôn ngữ | `intfloat/multilingual-e5-large` |

Gọi: `POST http://localhost:11434/api/embeddings` `{"model":"bge-m3","prompt":"..."}`.

## Chọn theo VRAM
- **8–16GB**: 7B–9B (chat/code/vision) chạy tốt.
- **24GB**: 14B thoải mái, 32B (4-bit) được.
- **48GB+**: 70B (4-bit).
- Chạy **cùng ảnh/video**: LLM 7B (~5GB) + model diffusion (ComfyUI tự tráo) → 24GB đủ.

## vLLM (khi cần nhanh + nhiều luồng)
```bash
pip install vllm
python -m vllm.entrypoints.openai.api_server --model Qwen/Qwen2.5-7B-Instruct --port 8000
# -> API OpenAI-compatible: POST /v1/chat/completions
```
