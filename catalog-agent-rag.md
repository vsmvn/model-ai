# Agent / Automation & RAG (chatbot đọc tài liệu)

## Phần A — RAG (chatbot trả lời dựa trên tài liệu của bạn)

**RAG** = LLM + kho tài liệu: nhúng tài liệu thành vector → tìm đoạn liên quan → đưa vào prompt để trả lời chính xác theo dữ liệu riêng (không bịa).

```
Tài liệu → cắt đoạn (chunk) → embedding → lưu Vector DB
Câu hỏi → embedding → tìm top-k đoạn gần → ghép vào prompt → LLM trả lời (kèm nguồn)
```

### Thành phần
| Vai trò | Lựa chọn | Ghi chú |
|---|---|---|
| **Embedding** | `bge-m3` (VN tốt), `nomic-embed-text`, `multilingual-e5` | qua Ollama: `POST /api/embeddings` |
| **Vector DB** | **Qdrant** (khuyên), Chroma, Milvus, pgvector (Postgres) | Qdrant nhẹ, docker 1 lệnh |
| **LLM** | Qwen2.5 7B–32B (tiếng Việt tốt) | qua Ollama/vLLM |
| **Framework** | **LlamaIndex**, LangChain, Haystack | LlamaIndex gọn cho RAG |

### Cài nhanh (tự host)
```bash
# Vector DB
docker run -p 6333:6333 qdrant/qdrant
# Python
pip install llama-index llama-index-vector-stores-qdrant llama-index-embeddings-ollama llama-index-llms-ollama
```
```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
docs = SimpleDirectoryReader("tai_lieu/").load_data()
idx = VectorStoreIndex.from_documents(docs, embed_model=OllamaEmbedding("bge-m3"))
qe = idx.as_query_engine(llm=Ollama(model="qwen2.5:7b"))
print(qe.query("Câu hỏi về tài liệu?"))
```

### RAG "không code" (UI sẵn)
| Công cụ | Ghi chú |
|---|---|
| **AnythingLLM** | upload tài liệu → chat, chạy local, đẹp | 
| **Open WebUI** | giao diện ChatGPT cho Ollama + RAG tích hợp |
| **Dify** | nền tảng LLM app (RAG + workflow) |
| **RAGFlow** | RAG chuyên sâu, OCR tài liệu tốt |

---

## Phần B — Agent / Workflow Automation

Cho AI **tự thực hiện chuỗi việc** (gọi tool, API, nhiều bước) — vd: nhận yêu cầu → tạo ảnh → sửa → đăng bài.

### Nền tảng no-code / low-code
| Công cụ | Việc | Ghi chú |
|---|---|---|
| **n8n** ⭐ | tự động hoá workflow (kéo-thả), gọi API, webhook, lịch | mạnh, self-host free, nối được API AI của bạn |
| **Flowise** | xây AI agent/chatbot bằng kéo-thả (LangChain UI) | RAG + agent |
| **Dify** | LLM app + agent + RAG | |
| **Make / Zapier** | automation đám mây | trả phí |
| **ComfyUI** | "agent" cho ảnh/video (workflow node) | chính là cái đang dùng |

### Framework code (agent LLM)
| Framework | Ghi chú |
|---|---|
| **LangGraph / LangChain** | agent nhiều bước, tool-calling |
| **LlamaIndex Agents** | agent + RAG |
| **CrewAI** | nhiều agent phối hợp (multi-agent) |
| **AutoGen** (Microsoft) | multi-agent hội thoại |
| **Ollama tool-calling** | model gọi function (Qwen2.5, Llama3.1 hỗ trợ) |

### Ví dụ tích hợp với hệ thống của bạn
- **n8n** nhận webhook → gọi `POST /generate/image` (API gateway) → chờ `/status` → tải `/result` → gửi Telegram/đăng web. Tất cả kéo-thả.
- **Agent LLM** (Qwen tool-calling): định nghĩa tool `tao_anh(prompt)`, `tao_video(prompt)` trỏ tới API gateway → LLM tự quyết gọi tool nào theo yêu cầu người dùng.

### Cài n8n (self-host)
```bash
docker run -d --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n n8nio/n8n
# -> http://localhost:5678 , thêm HTTP Request node trỏ tới API gateway của bạn
```

## Gợi ý kiến trúc "trợ lý AI toàn diện"
```
Người dùng ──► n8n / Open WebUI (giao diện)
                  │
                  ├─► API Gateway (ảnh/video/chat) ──► VPS GPU (tự bật/tắt)
                  ├─► RAG (LlamaIndex + Qdrant) ─────► trả lời theo tài liệu
                  └─► Whisper (giọng→text) + TTS (text→giọng)
```
