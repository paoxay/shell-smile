<?php
session_start();
header('Content-Type: application/json');

require_once '../../config/database.php';

// ກວດສອບວ່າລ໋ອກອິນແລ້ວ ຫຼື ບໍ່
if (!isset($_SESSION['user_id'])) {
    http_response_code(401);
    echo json_encode(['success' => false, 'message' => 'ກະລຸນາລ໋ອກອິນກ່ອນ']);
    exit();
}

// ຮັບຄຳຂໍແບບ GET ເທົ່ານັ້ນ
if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Method Not Allowed']);
    exit();
}

try {
    // ດຶງຂໍ້ມູນຈາກຖານຂໍ້ມູນ
    $stmt = $pdo->prepare(
        "SELECT ref_code, amount, status, created_at 
         FROM transactions 
         WHERE user_id = ? AND type = 'topup' 
         ORDER BY created_at DESC"
    );
    $stmt->execute([$_SESSION['user_id']]);
    $history = $stmt->fetchAll();

    echo json_encode(['success' => true, 'history' => $history]);

} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => 'ເກີດຂໍ້ຜິດພາດໃນການດຶງຂໍ້ມູນ']);
}
?>