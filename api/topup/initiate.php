<?php
session_start();
header('Content-Type: application/json');

require_once '../../config/database.php';
require_once '../../core/JcApiService.php';

// ກວດສອບວ່າລ໋ອກອິນ (ໃນລະບົບເຮົາ) ແລ້ວ ຫຼື ບໍ່
if (!isset($_SESSION['user_id'])) {
    http_response_code(401);
    echo json_encode(['success' => false, 'message' => 'ກະລຸນາລ໋ອກອິນກ່ອນ']);
    exit();
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') { /* ... */ exit(); }

$data = json_decode(file_get_contents("php://input"));

if (!isset($data->amount) || !is_numeric($data->amount) || $data->amount <= 0) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'ຈຳນວນເງິນບໍ່ຖືກຕ້ອງ']);
    exit();
}

try {
    $jcApiService = new JcApiService();
    // ເອີ້ນໃຊ້ຟັງຊັນໂດຍບໍ່ຕ້ອງສົ່ງ token
    $topupResult = $jcApiService->initiateTopup($data->amount);

    if ($topupResult && $topupResult['success']) {
        $stmt = $pdo->prepare(
            "INSERT INTO transactions (user_id, ref_code, type, amount, status, details) VALUES (?, ?, 'topup', ?, 'pending', ?)"
        );
        $stmt->execute([
            $_SESSION['user_id'],
            $topupResult['data']['ref'],
            $topupResult['data']['amount'],
            json_encode($topupResult['data'])
        ]);
        
        echo json_encode(['success' => true, 'data' => $topupResult['data']]);
    } else {
        throw new Exception('ບໍ່ສາມາດສ້າງລາຍການເຕີມເງິນໄດ້');
    }

} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => $e->getMessage()]);
}
?>