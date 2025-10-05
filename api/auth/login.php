<?php
session_start();
header('Content-Type: application/json');

require_once '../../config/database.php';
require_once '../../core/JcApiService.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Method Not Allowed']);
    exit();
}

$data = json_decode(file_get_contents("php://input"));

if (!isset($data->username) || !isset($data->password)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'ຂໍ້ມູນບໍ່ຄົບຖ້ວນ']);
    exit();
}

$jcApiService = new JcApiService();
$loginResult = $jcApiService->attemptLogin($data->username, $data->password);

// --- ຈຸດທີ່ແກ້ໄຂ ---
// ເພີ່ມການກວດສອບວ່າ $loginResult ບໍ່ແມ່ນ null ກ່ອນທີ່ຈະອ່ານຄ່າ
if ($loginResult && $loginResult['success']) {
    
    // ຖ້າລ໋ອກອິນຈາກ API ພາຍນອກສຳເລັດ
    $stmt = $pdo->prepare("SELECT * FROM users WHERE username = ?");
    $stmt->execute([$data->username]);
    $user = $stmt->fetch();

    if (!$user) {
        $hashed_password = password_hash($data->password, PASSWORD_DEFAULT);
        $insert_stmt = $pdo->prepare("INSERT INTO users (username, password) VALUES (?, ?)");
        $insert_stmt->execute([$data->username, $hashed_password]);
        $user_id = $pdo->lastInsertId();
    } else {
        $user_id = $user['id'];
    }

    $_SESSION['user_id'] = $user_id;
    $_SESSION['username'] = $data->username;
    $_SESSION['jc_token'] = $loginResult['token'];

    echo json_encode(['success' => true, 'message' => 'ລ໋ອກອິນສຳເລັດ!']);

} else {
    // ຖ້າລ໋ອກອິນຈາກ API ພາຍນອກລົ້ມເຫຼວ
    http_response_code(401);
    echo json_encode(['success' => false, 'message' => 'ຊື່ຜູ້ໃຊ້ ຫຼື ລະຫັດຜ່ານບໍ່ຖືກຕ້ອງ']);
}
?>