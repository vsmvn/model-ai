# Hướng dẫn cài đặt — Dựng hệ thống AI từ đầu

Dựng: **VPS GPU (Vast.ai) → ComfyUI → API gateway → tải model → chạy dịch vụ**. Xem [README.md](README.md) để chọn model + VPS.

Repo có sẵn file để copy lên VPS: `api_server.py`, `idle_watchdog.py`, `provision_vps.sh`, `vast_gpu_client.py`, `ai_api.php`, `API_DOCS.md`.

---

## Bước 1 — Thuê VPS Vast.ai
1. Vào **console.vast.ai** → Templates → chọn **ComfyUI** (image `vastai/comfy...`, có sẵn ComfyUI + CUDA + `/venv/main`).
2. Search GPU: chọn theo [bảng VPS trong README](README.md#2-hướng-dẫn-chọn-vps--gpu). **Kéo Disk ≥ 80GB** trước khi RENT.
3. Thêm **SSH key** của bạn vào instance (mục Manage SSH Keys → dán public key → ADD).
4. Đợi "Running" → lấy lệnh SSH (nút 🔑): `ssh -p <port> root@<ip>`.

> Kiểm tra mạng trước khi cài: `ssh ... 'echo ok'`. Nếu **Connection refused** cả direct lẫn proxy → host lỗi, đổi máy.

## Bước 2 — Chuẩn bị môi trường (SSH vào VPS)
```bash
source /venv/main/bin/activate                      # python env có sẵn (torch + ComfyUI)
python -m pip install -q fastapi "uvicorn[standard]" requests python-multipart huggingface_hub
```
ComfyUI có sẵn ở `/workspace/ComfyUI`, chạy qua supervisor (port nội bộ 18188).

## Bước 3 — Tải model
Đặt `M=/workspace/ComfyUI/models` rồi copy các lệnh `hf download` từ [README](README.md) cho model bạn cần.
Ví dụ bộ "ảnh FLUX + video Wan + chat":
```bash
M=/workspace/ComfyUI/models
# FLUX Kontext (ảnh + sửa ảnh)
hf download Comfy-Org/flux1-kontext-dev split_files/diffusion_models/flux1-dev-kontext_fp8_scaled.safetensors --local-dir $M/diffusion_models
mv -f $M/diffusion_models/split_files/diffusion_models/*.safetensors $M/diffusion_models/ ; rm -rf $M/diffusion_models/split_files
hf download comfyanonymous/flux_text_encoders t5xxl_fp8_e4m3fn_scaled.safetensors --local-dir $M/text_encoders
hf download comfyanonymous/flux_text_encoders clip_l.safetensors --local-dir $M/clip
hf download ChuckMcSneed/FLUX.1-dev ae.safetensors --local-dir $M/vae
# SDXL (ảnh nhanh)
hf download stabilityai/stable-diffusion-xl-base-1.0 sd_xl_base_1.0.safetensors --local-dir $M/checkpoints
hf download stabilityai/sdxl-vae sdxl_vae.safetensors --local-dir $M/vae
# Wan 2.2 video (cần custom node ở bước 4)
hf download Kijai/WanVideo_comfy Wan22-Turbo/Wan2_2-TI2V-5B-Turbo_fp16.safetensors --local-dir $M/diffusion_models
mv -f $M/diffusion_models/Wan22-Turbo/*.safetensors $M/diffusion_models/ ; rm -rf $M/diffusion_models/Wan22-Turbo
hf download Kijai/WanVideo_comfy Wan2_2_VAE_bf16.safetensors --local-dir $M/vae
hf download Kijai/WanVideo_comfy umt5-xxl-enc-fp8_e4m3fn.safetensors --local-dir $M/text_encoders
# LTX-Video (video nhanh)
hf download Lightricks/LTX-Video ltxv-2b-0.9.8-distilled.safetensors --local-dir $M/checkpoints
```

## Bước 4 — Custom nodes (chỉ khi dùng Wan)
```bash
cd /workspace/ComfyUI/custom_nodes
git clone --depth 1 https://github.com/kijai/ComfyUI-WanVideoWrapper.git
git clone --depth 1 https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git
python -m pip install -q -r ComfyUI-WanVideoWrapper/requirements.txt
python -m pip install -q -r ComfyUI-VideoHelperSuite/requirements.txt
```
FLUX/SDXL/LTX/HunyuanVideo = **native ComfyUI**, không cần custom node.

## Bước 5 — Cài Chat (Ollama) — tùy chọn
```bash
curl -fsSL https://ollama.com/install.sh | sh
setsid ollama serve >/workspace/logs/ollama.log 2>&1 < /dev/null &
ollama pull qwen2.5:7b
```

## Bước 6 — API gateway
Copy `api_server.py` (trong repo) vào `/workspace/api_server.py`. File này:
- Bọc ComfyUI (localhost:18188) + Ollama (localhost:11434).
- Endpoints: `/chat`, `/generate/image`, `/generate/video`, `/generate/edit`, `/status/{id}`, `/result/{id}`, `/health`.
- **Bảo mật token** (header X-API-Key), **không lưu đĩa** (đọc kết quả vào RAM rồi xóa), **tự dịch prompt VN→EN**.

Chạy bằng supervisor:
```bash
TOKEN=$(python -c "import secrets;print(secrets.token_urlsafe(32))"); echo $TOKEN > /workspace/.api_token
cat > /etc/supervisor/conf.d/genapi.conf <<CONF
[program:genapi]
command=/venv/main/bin/python -m uvicorn api_server:app --host 0.0.0.0 --port 10200
directory=/workspace
autostart=true
autorestart=true
environment=PUBLIC_BASE="http://<IP>:<PORT_NGOAI>",COMFY_URL="http://localhost:18188",OLLAMA_URL="http://localhost:11434",CHAT_MODEL="qwen2.5:7b",API_TOKEN="$TOKEN"
stdout_logfile=/workspace/logs/genapi.log
stderr_logfile=/workspace/logs/genapi.err.log
CONF
supervisorctl reread && supervisorctl update
```
> **Port ngoài**: Vast map nội bộ 10200 → 1 port ngoài. Xem qua `env | grep VAST_TCP_PORT_10200` hoặc `vastai show instance <id> --raw` (field `ports["10200/tcp"]`). API base = `http://<public_ipaddr>:<port_ngoài>`.

## Bước 7 — Tự tắt tiết kiệm (watchdog) — tùy chọn
Copy `idle_watchdog.py` vào `/workspace/`. Thêm supervisor program (INSTANCE_ID, IDLE_SECONDS=600) → tự `vastai stop` khi rảnh 10 phút. Máy gọi tự bật lại qua Vast API (xem `vast_gpu_client.py`).

## Bước 8 — Khởi động & kiểm tra
```bash
supervisorctl restart comfyui genapi
curl -s http://localhost:10200/health           # {"status":"ok","comfyui":"up",...}
TOKEN=$(cat /workspace/.api_token)
curl -s -X POST http://localhost:10200/generate/image -H "X-API-Key: $TOKEN" \
  -H "Content-Type: application/json" -d '{"prompt":"a red apple","model":"flux"}'
```

## Bước 9 — Gọi API / Tích hợp web
- Tài liệu API đầy đủ: [API_DOCS.md](API_DOCS.md).
- Tích hợp PHP (Laragon): `ai_api.php` (proxy giữ token, tránh CORS).
- Client Python tự bật VPS: `vast_gpu_client.py`.

---

## Đổi model sau này (khi đĩa hạn chế)
Đĩa 80GB thường chỉ chứa **1 model video nặng** + ảnh + chat. Muốn đổi:
1. Xóa model cũ: `rm -f $M/diffusion_models/<model_cũ>.safetensors ...`
2. Tải model mới theo lệnh trong [README](README.md).
3. `supervisorctl restart comfyui` (nạp lại), cập nhật workflow trong `api_server.py` nếu cần.
4. Muốn giữ nhiều model video **chọn tức thì** → cần đĩa lớn hơn (đặt ≥120GB lúc thuê), thêm field `model` vào workflow (xem cách `wf_video_wan`/`wf_video_ltx` trong `api_server.py`).

## Sự cố thường gặp
| Triệu chứng | Xử lý |
|---|---|
| Job kẹt "Đang xếp hàng" | Có job nặng đang chạy/dồn hàng: `curl -X POST localhost:18188/queue -d '{"clear":true}'` + `/interrupt` |
| Lỗi validation node | Sai schema: `GET localhost:18188/object_info` xem input đúng; xem template `comfyui_workflow_templates_*` |
| OOM (hết VRAM) | Dùng bản fp8; giảm resolution/frames; bật vae tiling |
| Prompt tiếng Việt ra sai | Model ảnh/video hiểu tiếng Anh — bật tự-dịch (đã có trong api_server) |
| Ảnh ra có "logo/watermark" giả | FLUX bịa — thêm "no watermark, no logo, no text" vào prompt |
| Model gated (401) | Dùng mirror non-gated hoặc đặt HF_TOKEN đã chấp nhận license |
