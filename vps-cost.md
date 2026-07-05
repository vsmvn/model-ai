# VPS & Chi phí — Cài toàn bộ model?

## Cài TẤT CẢ model thì cần gì?

### Đĩa (ước lượng nếu tải hết catalog)
| Nhóm | Dung lượng |
|---|---|
| Ảnh (SDXL, FLUX ×3, SD3.5, Qwen-Image, HiDream, Sana, Kolors, Chroma...) | ~200GB |
| Video (LTX ×2, Wan ×4, Hunyuan, Mochi, CogVideoX, Open-Sora, SkyReels, Step-Video) | ~275GB |
| LLM (Qwen 7/14/32/72B, Llama 70B, coder, vision, embedding) | ~200GB |
| Tools (ControlNet, IPAdapter, upscaler, restore, faceswap...) | ~50GB |
| Audio/TTS/ASR/3D | ~50GB |
| Text encoders chung, buffer | ~50GB |
| **TỔNG** | **~800GB – 1TB** (nên để **1.5–2TB** cho thoải mái) |

### VRAM (để chạy được cả model nặng nhất)
> Không chạy tất cả cùng lúc — ComfyUI/Ollama nạp **từng model một**. Nhưng phải đủ VRAM cho con **NẶNG NHẤT**:
- Step-Video 30B, LLM 72B (4-bit ~45GB), Wan 2.2 14B (~28–48GB) → **cần 48GB tối thiểu, 80GB thoải mái**.
- Nếu bỏ mấy con siêu nặng (Step-Video, 72B) → **32GB (RTX 5090)** chạy được ~95% catalog.

### Cấu hình đề xuất để "có tất cả"
| Mức | GPU | VRAM | Đĩa | RAM | Chạy được |
|---|---|---|---|---|---|
| Đủ dùng | RTX 5090 | 32GB | 1TB | 64GB | ~95% (trừ 14B video, 72B LLM, Step-Video) |
| **Đầy đủ** ⭐ | RTX A6000 / L40S | 48GB | 1.5TB | 128GB | gần hết, kể cả Wan 14B |
| Tất cả | A100 / H100 | 80GB | 2TB | 128GB+ | mọi thứ, batch lớn |

---

## Chi phí (Vast.ai, tham khảo 2026)

### Chạy 24/7 (liên tục cả tháng)
| GPU | VRAM | Giá compute/hr | Compute/tháng | + Đĩa 1–2TB | **Tổng/tháng 24/7** |
|---|---|---|---|---|---|
| RTX 5090 | 32GB | ~$0.4 | ~$290 | ~$15–30 | **~$300–320** |
| RTX A6000/L40S | 48GB | ~$0.7 | ~$500 | ~$20–40 | **~$520–540** |
| A100 | 80GB | ~$1.2 | ~$860 | ~$30–50 | **~$900–910** |
| H100 | 80GB | ~$2.5 | ~$1.800 | ~$40 | **~$1.850** |

### 💡 Chạy 24/7 là LÃNG PHÍ — dùng auto-stop rẻ hơn nhiều
GPU chỉ tính tiền khi **Running**. Với watchdog tự-tắt (xem [api-architecture.md](api-architecture.md)), bạn chỉ trả cho **giờ thật sự dùng** + phí đĩa.

**Ví dụ dùng ~4 giờ/ngày** (A6000 48GB, $0.7/hr):
```
Compute: 4h × 30 ngày × $0.7 = ~$84/tháng
Đĩa 1.5TB (luôn tính, kể cả stop): ~$30/tháng
-------------------------------------------------
TỔNG ≈ ~$114/tháng   (so với $520 nếu 24/7 → rẻ hơn ~4.5 lần)
```

| Cách dùng | A6000 48GB | RTX 5090 32GB |
|---|---|---|
| 24/7 | ~$520/mo | ~$300/mo |
| ~4h/ngày (auto-stop) | ~$114/mo | ~$75/mo |
| ~1h/ngày | ~$50/mo | ~$40/mo |
| Chỉ stop (không chạy) | ~$30/mo (chỉ đĩa) | ~$25/mo (chỉ đĩa) |

---

## ⚠️ Lời khuyên thực tế
1. **ĐỪNG cài tất cả** — phần lớn model trùng chức năng/thử nghiệm. Cài **theo nhu cầu** (đó là lý do có catalog): 1–2 model ảnh + 1–2 video + 1 chat + TTS là đủ cho 99% việc, chỉ ~60–80GB đĩa, GPU 24–32GB.
2. **ĐỪNG chạy 24/7** — dùng auto-stop, tiết kiệm 4–5 lần.
3. **Nhớ giữ credit** — Stop vẫn trừ phí đĩa; hết tiền Vast **XÓA instance** (mất hết). Đĩa 1–2TB thì phí đĩa đáng kể (~$30/mo) → cạn credit nhanh nếu để lâu.
4. **Muốn "kho model khổng lồ" mà rẻ**: thuê máy đĩa lớn nhưng **stop khi không dùng** → chỉ trả phí đĩa + giờ chạy thực. Hoặc lưu model ở **network volume** của Vast (giữ data mà không cần instance chạy).
5. **Model API thương mại** (Veo/Sora/GPT/Claude...): không cần VPS, trả theo lượt — hợp khi dùng ít/không muốn quản hạ tầng (xem [api-providers.md](api-providers.md)).

## Tóm tắt
- **Cài tất cả**: ~1–2TB đĩa + GPU **48GB (A6000)** ≈ **$520/tháng nếu 24/7**, nhưng chỉ **~$110/tháng nếu auto-stop dùng 4h/ngày**.
- **Thực tế nên**: cài theo nhu cầu (GPU 24–32GB, đĩa 80–120GB) + auto-stop → **~$40–115/tháng**.
