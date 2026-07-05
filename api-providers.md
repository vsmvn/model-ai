# Model qua API thương mại — so sánh & giá tham khảo

Khi **không muốn tự host** (dùng ít, cần chất lượng đỉnh, không quản hạ tầng) → gọi API trả phí. Giá 2026, **tham khảo** (kiểm tra lại trên trang chính thức trước khi dùng).

## 1. LLM / Chat (giá theo triệu token)
| Nhà | Model | ~Giá input/output (1M token) | Ghi chú |
|---|---|---|---|
| **OpenAI** | GPT-5 / GPT-4.1 / mini | $$$ / $ | mạnh, phổ biến |
| **Anthropic** | Claude Opus / Sonnet / Haiku | $$$ / $$ / $ | viết + code tốt |
| **Google** | Gemini 2.5 Pro / Flash | $$ / $ | rẻ, context dài |
| **DeepSeek** | V3 / R1 | rất rẻ | reasoning tốt, giá thấp |
| **xAI** | Grok | $$ | |
| **Together / Fireworks / Groq** | host model mở (Llama, Qwen...) | rẻ, nhanh | Groq siêu nhanh |

> Rẻ nhất: DeepSeek, Gemini Flash, model mở qua Together/Groq. Chất lượng đỉnh: GPT-5, Claude Opus, Gemini Pro.

## 2. Tạo ảnh (API)
| Nhà | Model | ~Giá/ảnh | Ghi chú |
|---|---|---|---|
| **Black Forest Labs** | FLUX Pro / 1.1 / Kontext | ~$0.04–0.05 | đẹp, có editing |
| **OpenAI** | GPT-Image / DALL·E 3 | ~$0.04–0.08 | |
| **Google** | Imagen 4 | ~$0.04 | |
| **Ideogram** | v2/v3 | ~$0.08 | chữ trong ảnh tốt |
| **Recraft** | v3 | ~$0.04 | thiết kế/vector |
| **Stability** | SD3.5 / Core | ~$0.03–0.06 | |
| **fal.ai / Replicate** | host nhiều model mở | theo giây GPU | tiện thử nhiều model |

## 3. Tạo video (API — chất lượng đỉnh)
| Nhà | Model | ~Giá | Ghi chú |
|---|---|---|---|
| **Google** | Veo 3 | ~$0.30–0.75/giây | đẹp nhất + có audio |
| **OpenAI** | Sora | theo gói | video dài, nhất quán |
| **Kling** | 1.6/2.0 | ~$0.03–0.10/giây | phổ biến, mượt |
| **Runway** | Gen-3/4 | ~$0.05/giây | điện ảnh |
| **Luma** | Dream Machine | ~$0.02–0.05/giây | nhanh |
| **MiniMax/Hailuo** | | rẻ | tốt/giá |
| **Pika** | | | hiệu ứng |

> Video API **đắt** (vài chục cent/giây) → tự host (Wan/LTX/Hunyuan) rẻ hơn nhiều nếu làm số lượng lớn.

## 4. Giọng nói (TTS/ASR API)
| Nhà | Việc | ~Giá | Ghi chú |
|---|---|---|---|
| **ElevenLabs** | TTS đỉnh + clone giọng | ~$0.10–0.30/1K ký tự | tự nhiên nhất, có tiếng Việt |
| **OpenAI** | TTS + Whisper (ASR) | TTS ~$15/1M ký tự; ASR ~$0.006/phút | |
| **Google** | TTS/STT | theo ký tự/phút | nhiều giọng VN |
| **PlayHT / Cartesia** | TTS realtime | | nhanh |
| **Deepgram / AssemblyAI** | ASR (giọng→text) | ~$0.004–0.01/phút | nhanh, chính xác |

## 5. 3D (API)
| Nhà | Ghi chú |
|---|---|
| **Meshy / Tripo / Rodin** | ảnh/text → 3D, trả theo lượt |

---

## Tự host vs API — chọn cái nào?
| Tiêu chí | Tự host (VPS GPU) | API thương mại |
|---|---|---|
| Chi phí ít việc | cao (phí VPS) | **rẻ** (trả theo lượt) |
| Chi phí nhiều việc/số lượng lớn | **rẻ hơn nhiều** | đắt dần |
| Chất lượng đỉnh (Veo/Sora/GPT-5) | không có | **có** |
| Riêng tư/dữ liệu | **kiểm soát hoàn toàn** | gửi lên nhà cung cấp |
| License thương mại | tùy model (chọn model mở) | có sẵn |
| Quản lý | phải tự quản | không cần |

**Chiến lược hỗn hợp (khuyên):** tự host model mở cho việc thường xuyên/số lượng lớn (rẻ) + gọi API thương mại khi cần chất lượng đỉnh hoặc dùng ít.

> Giá $ chỉ mang tính tương đối ($=rẻ, $$=vừa, $$$=đắt). **Luôn xem trang giá chính thức** vì thay đổi thường xuyên.
