<?php
session_start();
header('Content-Type: application/json');
require_once '../../config/database.php';

if (!isset($_SESSION['admin_id'])) {
    http_response_code(401);
    exit();
}

try {
    // 1. นับจำนวนสมาชิก
    $stmt1 = $pdo->query("SELECT COUNT(id) FROM users WHERE role = 'member'");
    $total_members = $stmt1->fetchColumn();

    // 2. รวมยอดเงินทั้งหมดของสมาชิก
    $stmt2 = $pdo->query("SELECT SUM(balance) FROM users WHERE role = 'member'");
    $total_balance = $stmt2->fetchColumn();

    // 3. รวมยอดเติมเงินที่สำเร็จ
    $stmt3 = $pdo->query("SELECT SUM(amount) FROM transactions WHERE type = 'topup' AND status = 'success'");
    $total_topup = $stmt3->fetchColumn();

    // 4. รวมยอดสั่งซื้อที่สำเร็จ (ยอดติดลบ)
    $stmt4 = $pdo->query("SELECT SUM(amount) FROM transactions WHERE type = 'purchase' AND status = 'success'");
    $total_purchase = $stmt4->fetchColumn();

    $stats = [
        'total_members' => (int)$total_members,
        'total_balance' => (float)($total_balance ?? 0),
        'total_topup' => (float)($total_topup ?? 0),
        'total_purchase' => abs((float)($total_purchase ?? 0)), // ใช้ค่า tuyệt đối
    ];

    echo json_encode(['success' => true, 'stats' => $stats]);

} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => $e->getMessage()]);
}
?>