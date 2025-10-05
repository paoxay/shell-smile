<?php
session_start();
header('Content-Type: application/json');

// ທີ່ຢູ່ນີ້ສຳຄັນ ເພາະເຮົາຢູ່ໃນໂຟເດີ admin/api/
require_once '../../../config/database.php'; 

if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); exit(); }

$data = json_decode(file_get_contents("php://input"));

if (!isset($data->username) || !isset($data->password)) { /* ... */ exit(); }

try {
    $stmt = $pdo->prepare("SELECT * FROM users WHERE username = ?");
    $stmt->execute([$data->username]);
    $user = $stmt->fetch();

    // ກວດສອບລະຫັດຜ່ານ ແລະ ກວດສອບວ່າເປັນ admin ຫຼືບໍ່
    if ($user && password_verify($data->password, $user['password']) && $user['role'] === 'admin') {
        
        // ສ້າງ Session ສະເພາະຂອງ Admin
        $_SESSION['admin_id'] = $user['id'];
        $_SESSION['admin_username'] = $user['username'];

        echo json_encode(['success' => true, 'message' => 'ລ໋ອກອິນສຳເລັດ!']);
    } else {
        http_response_code(401);
        echo json_encode(['success' => false, 'message' => 'Username, Password ບໍ່ຖືກຕ້ອງ ຫຼື ທ່ານບໍ່ແມ່ນ Admin']);
    }
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => 'Database connection error']);
}
?>