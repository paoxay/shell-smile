<?php
session_start();
header('Content-Type: application/json');
require_once '../../config/database.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); exit(); }
$data = json_decode(file_get_contents("php://input"));
if (!isset($data->username) || !isset($data->password)) { http_response_code(400); exit(); }

try {
    $stmt = $pdo->prepare("SELECT * FROM users WHERE username = ?");
    $stmt->execute([$data->username]);
    $user = $stmt->fetch();
    if ($user && password_verify($data->password, $user['password']) && $user['role'] === 'admin') {
        $_SESSION['admin_id'] = $user['id'];
        $_SESSION['admin_username'] = $user['username'];
        echo json_encode(['success' => true]);
    } else {
        http_response_code(401);
        echo json_encode(['success' => false, 'message' => 'Username ຫຼື Password ບໍ່ຖືກຕ້ອງ']);
    }
} catch (PDOException $e) { http_response_code(500); echo json_encode(['success' => false, 'message' => 'Database error']); }
?>