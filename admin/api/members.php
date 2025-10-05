<?php
session_start();
header('Content-Type: application/json');

require_once '../../../config/database.php';

// ກວດສອບວ່າເປັນ Admin ທີ່ລ໋ອກອິນຢູ່ ຫຼື ບໍ່
if (!isset($_SESSION['admin_id'])) {
    http_response_code(401);
    echo json_encode(['success' => false, 'message' => 'Unauthorized']);
    exit();
}

try {
    // ດຶງສະເພາະ user ທີ່ມີ role ເປັນ 'member'
    $stmt = $pdo->prepare("SELECT id, username, balance, created_at FROM users WHERE role = 'member' ORDER BY id DESC");
    $stmt->execute();
    $members = $stmt->fetchAll();
    echo json_encode(['success' => true, 'members' => $members]);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => 'Database error']);
}
?>