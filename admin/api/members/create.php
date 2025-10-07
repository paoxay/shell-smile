<?php
session_start();
header('Content-Type: application/json');
require_once '../../../config/database.php';

// ກວດສອບວ່າເປັນ Admin ຫຼືບໍ່
if (!isset($_SESSION['admin_id'])) {
    http_response_code(401);
    echo json_encode(['success' => false, 'message' => 'Unauthorized']);
    exit();
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    exit();
}

$data = json_decode(file_get_contents("php://input"));

// ກວດສອບຂໍ້ມູນທີ່ສົ່ງມາ
if (!isset($data->username) || !isset($data->password) || empty($data->username) || empty($data->password)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'ກະລຸນາປ້ອນ Username ແລະ Password']);
    exit();
}

try {
    // ກວດສອບວ່າ username ຊ້ຳບໍ່
    $stmt = $pdo->prepare("SELECT id FROM users WHERE username = ?");
    $stmt->execute([$data->username]);
    if ($stmt->fetch()) {
        http_response_code(409); // Conflict
        echo json_encode(['success' => false, 'message' => 'Username ນີ້ມີຜູ້ໃຊ້ງານແລ້ວ']);
        exit();
    }

    // ເຂົ້າລະຫັດຜ່ານເພື່ອຄວາມປອດໄພ
    $hashed_password = password_hash($data->password, PASSWORD_DEFAULT);

    // ເພີ່ມຜູ້ໃຊ້ໃໝ່ (role ເປັນ 'member' ໂດຍອັດຕະໂນມັດ)
    $insert_stmt = $pdo->prepare("INSERT INTO users (username, password, role) VALUES (?, ?, 'member')");
    $insert_stmt->execute([$data->username, $hashed_password]);

    echo json_encode(['success' => true, 'message' => 'ສ້າງຜູ້ໃຊ້ໃໝ່ສຳເລັດ!']);

} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => $e->getMessage()]);
}
?>