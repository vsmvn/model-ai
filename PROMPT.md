# PROMPT triển khai 1-lần (copy gửi cho AI)

Sao chép **nguyên khối** dưới đây gửi cho một AI agent có quyền chạy lệnh/SSH (Claude Code, Cursor, v.v.). Điền phần `<...>` rồi gửi 1 lần — AI sẽ tự dựng toàn bộ hệ thống.

---

````
Bạn là kỹ sư triển khai. Hãy dựng cho tôi một hệ thống AI tự host (chat + tạo ảnh + sửa ảnh + tạo video) với 1 API gateway, trên VPS GPU Vast.ai. Đọc repo https://github.com/vsmvn/model-ai (README.md, INSTALL.md, api-architecture.md) và dùng các file code có sẵn trong repo (api_server.py, idle_watchdog.py, vast_gpu_client.py, ai_api.php).

THÔNG TIN VPS CỦA TÔI:
- Lệnh SSH: <ssh -p PORT root@IP>   (đã thêm SSH key, VPS đang Running, template ComfyUI, /venv/main có sẵn torch)
- Đĩa đã cấp: <80> GB

MODEL CẦN CÀI (bộ mặc định, hợp GPU 24-32GB):
- Ảnh + sửa ảnh: FLUX.1 Kontext dev (fp8)  [+ SDXL base cho ảnh nhanh]
- Video: Wan 2.2 TI2V-5B (đẹp) VÀ LTX-Video 2B distilled (nhanh) — chọn model qua field "model"
- Chat: Ollama + qwen2.5:7b
(Nếu tôi ghi model khác ở đây thì ưu tiên: <để trống nếu dùng mặc định>)

YÊU CẦU BẮT BUỘC:
1. Tải model bằng `hf download` (dùng mirror non-gated: Comfy-Org, Kijai, ChuckMcSneed — KHÔNG dùng repo gated của black-forest-labs/stability). Lệnh chính xác lấy từ INSTALL.md + catalog trong repo.
2. Cài custom node ComfyUI-WanVideoWrapper + ComfyUI-VideoHelperSuite (cho Wan). FLUX/LTX/SDXL = native.
3. Cài Ollama + pull qwen2.5:7b (chạy qua supervisor).
4. Copy api_server.py (trong repo) vào /workspace/, chạy bằng supervisor port 10200. Tính năng phải có: token (X-API-Key), KHÔNG lưu đĩa (kết quả vào RAM), TỰ DỊCH prompt tiếng Việt -> tiếng Anh trước khi tạo (dùng Qwen), chọn model video qua field "model" (wan|ltx), chọn model ảnh qua "model" (flux|sdxl).
5. Sinh token ngẫu nhiên, lưu /workspace/.api_token. Đặt PUBLIC_BASE = http://IP:PORT_NGOAI (dò port ngoài của 10200 qua `env | grep VAST_TCP_PORT_10200` hoặc vastai show instance).
6. Cài idle_watchdog (tự stop VPS khi rảnh 10 phút) nhưng để autostart=false (tôi tự bật khi cần).
7. Lấy workflow/tham số node ĐÚNG bằng `GET localhost:18188/object_info` + template trong comfyui_workflow_templates_* nếu cần (đừng đoán).

SAU KHI CÀI XONG, TEST và BÁO CÁO:
- Test thật: 1 chat, 1 ảnh (FLUX), 1 video (LTX), xác nhận completed.
- In ra: API base URL (http://IP:PORT), token, và danh sách endpoint:
  POST /chat {message} · POST /generate/image {prompt,width,height,model} · POST /generate/video {prompt,duration,model} · POST /generate/edit (multipart) · GET /status/{id} · GET /result/{id} · GET /health
- Cảnh báo: Stop vẫn tốn phí đĩa; hết credit Vast sẽ xóa instance.

LƯU Ý KỸ THUẬT (từ repo, tránh lỗi đã biết):
- Wan cần model Wan2_2-TI2V-5B-Turbo_fp16 + Wan2_2_VAE_bf16 + umt5-xxl-enc-fp8; nạp quantization=fp8_e4m3fn.
- FLUX Kontext: UNETLoader(default) + DualCLIPLoader(clip_l,t5xxl_fp8,flux) + VAELoader(ae.safetensors). ae lấy từ ChuckMcSneed/FLUX.1-dev (BFL gated).
- LTX: CheckpointLoaderSimple(ltxv-2b-0.9.8-distilled) + CLIPLoader(t5xxl_fp8,type=ltxv) + LTXVConditioning + EmptyLTXVLatentVideo(768x512,length=8n+1) + LTXVScheduler(12) + SamplerCustom(cfg1) + VAEDecode + VHS_VideoCombine(25fps).
- Nếu SSH báo "Connection refused" cả direct lẫn proxy => host lỗi mạng, báo tôi đổi máy.

Hãy làm tuần tự, tải model chạy nền, và báo tôi khi xong kèm API để tôi tích hợp.
````

---

## Prompt ngắn (khi model đã cài sẵn, chỉ cần đổi/thêm 1 model)
````
Đọc repo github.com/vsmvn/model-ai. SSH vào VPS <ssh -p PORT root@IP>. Cài thêm model <TÊN MODEL> theo lệnh trong catalog tương ứng (dùng mirror non-gated), thêm workflow vào /workspace/api_server.py (lấy schema node từ localhost:18188/object_info), restart genapi, test 1 lần và báo kết quả. Đĩa còn <X>GB — nếu không đủ thì đề xuất xóa model nào.
````

## Prompt tính chi phí / tư vấn (không triển khai)
````
Đọc github.com/vsmvn/model-ai (market-map.md, vps-cost.md, api-providers.md). Tôi cần <mô tả nhu cầu: loại nội dung, số lượng/tháng, số luồng đồng thời, thương mại hay không>. Hãy đề xuất: model nào (mã nguồn mở), VPS/GPU nào, chi phí ước tính/tháng, và nên tự host hay dùng API.
````
