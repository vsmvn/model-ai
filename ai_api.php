<?php
/**
 * Proxy PHP cho AI API — đặt trong Laragon (vd: c:\laragon\www\AI\ai_api.php)
 * Frontend gọi file này thay vì gọi thẳng API GPU (giữ token an toàn + tránh CORS).
 *
 * Cách gọi:
 *   POST ai_api.php?p=/chat                  body JSON {message}
 *   POST ai_api.php?p=/generate/image        body JSON {prompt,width,height,model}
 *   POST ai_api.php?p=/generate/video        body JSON {prompt,duration,model}
 *   POST ai_api.php?p=/generate/edit         multipart form (prompt, image, guidance)
 *   GET  ai_api.php?p=/status/<job_id>
 *   GET  ai_api.php?p=/result/<job_id>       (trả ảnh/video)
 *   GET  ai_api.php?p=/health
 */

$BASE  = "http://14.179.88.48:41497";
$TOKEN = "riiDqlgpAUqH_l3aFDPqADvVS0-lYQLF4Cab4kgMH04";

$p = $_GET['p'] ?? '';
if ($p === '' || $p[0] !== '/') {
    http_response_code(400);
    header('Content-Type: application/json');
    echo json_encode(["error" => "thiếu tham số ?p=/duong-dan"]);
    exit;
}

$url    = $BASE . $p;
$method = $_SERVER['REQUEST_METHOD'];
$ch     = curl_init($url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method);
curl_setopt($ch, CURLOPT_TIMEOUT, 1800);

$headers = ["X-API-Key: $TOKEN"];

if ($method === 'POST') {
    $ctype = $_SERVER['CONTENT_TYPE'] ?? 'application/json';
    if (stripos($ctype, 'multipart/form-data') !== false) {
        // upload ảnh (sửa ảnh): dựng lại multipart từ $_POST + $_FILES
        $fields = $_POST;
        if (!empty($_FILES['image']['tmp_name'])) {
            $fields['image'] = new CURLFile(
                $_FILES['image']['tmp_name'],
                $_FILES['image']['type'] ?: 'application/octet-stream',
                $_FILES['image']['name'] ?: 'upload'
            );
        }
        curl_setopt($ch, CURLOPT_POSTFIELDS, $fields); // cURL tự set Content-Type multipart
    } else {
        // JSON (chat/image/video)
        $body = file_get_contents('php://input');
        curl_setopt($ch, CURLOPT_POSTFIELDS, $body);
        $headers[] = "Content-Type: application/json";
    }
}

curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
$resp = curl_exec($ch);
if ($resp === false) {
    http_response_code(502);
    header('Content-Type: application/json');
    echo json_encode(["error" => "Không kết nối được máy chủ AI (VPS đang tắt?): " . curl_error($ch)]);
    curl_close($ch);
    exit;
}
$code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$rct  = curl_getinfo($ch, CURLINFO_CONTENT_TYPE);
curl_close($ch);

http_response_code($code ?: 200);
if ($rct) header("Content-Type: $rct");
echo $resp;
