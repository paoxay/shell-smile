<?php
session_start();
header('Content-Type: application/json');
require_once '../../../config/database.php';

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

if (!isset($data->user_id) || !isset($data->amount) || !is_numeric($data->amount)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'ข้อมูลไม่ครบถ้วน']);
    exit();
}

try {
    $pdo->beginTransaction();

    // 1. ดึงยอดเงินเก่ามาก่อน
    $stmt_get = $pdo->prepare("SELECT balance FROM users WHERE id = ?");
    $stmt_get->execute([$data->user_id]);
    $balance_before = $stmt_get->fetchColumn();
    if ($balance_before === false) {
        throw new Exception("ไม่พบผู้ใช้งาน ID: " . $data->user_id);
    }

    // 2. คำนวณยอดเงินใหม่
    $balance_after = (float)$balance_before + (float)$data->amount;

    // 3. ปรับปรุงยอดเงินของ user
    $stmt_update = $pdo->prepare("UPDATE users SET balance = ? WHERE id = ?");
    $stmt_update->execute([$balance_after, $data->user_id]);

    // 4. บันทึกรายการลง transactions พร้อมยอดก่อน-หลัง
    $details = json_encode(['remark' => $data->remark ?? 'Admin adjustment', 'admin_id' => $_SESSION['admin_id']]);
    $ref_code = 'ADJ-' . time() . '-' . $data->user_id;
    $stmt_insert = $pdo->prepare(
        "INSERT INTO transactions (user_id, ref_code, type, amount, status, details, balance_before, balance_after) VALUES (?, ?, 'adjustment', ?, 'success', ?, ?, ?)"
    );
    $stmt_insert->execute([$data->user_id, $ref_code, $data->amount, $details, $balance_before, $balance_after]);

    $pdo->commit();
    echo json_encode(['success' => true, 'message' => 'ปรับปรุงยอดเงินสำเร็จ']);

} catch (PDOException $e) {
    if ($pdo->inTransaction()) {
        $pdo->rollBack();
    }
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => $e->getMessage()]);
}
?>