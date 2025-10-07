<?php
session_start();
header('Content-Type: application/json');
require_once '../../../config/database.php';

if (!isset($_SESSION['admin_id'])) { http_response_code(401); exit(); }
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); exit(); }

$data = json_decode(file_get_contents("php://input"));
if (!isset($data->item_id) || !isset($data->markup_type) || !isset($data->markup_value) || !isset($data->is_active)) {
    http_response_code(400); exit(json_encode(['success' => false, 'message' => 'ข้อมูลไม่ครบถ้วน']));
}

try {
    $stmt = $pdo->prepare("UPDATE product_items SET markup_type = ?, markup_value = ?, is_active = ? WHERE id = ?");
    $stmt->execute([$data->markup_type, $data->markup_value, $data->is_active, $data->item_id]);
    echo json_encode(['success' => true, 'message' => 'อัปเดตข้อมูลสำเร็จ']);
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => $e->getMessage()]);
}
?>