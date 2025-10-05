<?php
session_start();
header('Content-Type: application/json');

require_once '../../config/database.php';
require_once '../../core/JcApiService.php';

if (!isset($_SESSION['user_id'])) { /* ... */ exit(); }
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { /* ... */ exit(); }

$data = json_decode(file_get_contents("php://input"));

if (!isset($data->ref) || !isset($data->txId)) { /* ... */ exit(); }

try {
    $jcApiService = new JcApiService();
    // ເອີ້ນໃຊ້ຟັງຊັນໂດຍບໍ່ຕ້ອງສົ່ງ token
    $confirmResult = $jcApiService->confirmTopup($data->ref, $data->txId);

    if ($confirmResult && $confirmResult['success']) {
        $pdo->beginTransaction();
        try {
            $updateTrans = $pdo->prepare("UPDATE transactions SET status = 'success' WHERE ref_code = ? AND user_id = ?");
            $updateTrans->execute([$data->ref, $_SESSION['user_id']]);

            $amountToAdd = $confirmResult['data']['amount'];
            $updateUser = $pdo->prepare("UPDATE users SET balance = balance + ? WHERE id = ?");
            $updateUser->execute([$amountToAdd, $_SESSION['user_id']]);
            
            $pdo->commit();
            echo json_encode(['success' => true, 'message' => 'ຢືນຢັນການເຕີມເງິນສຳເລັດ!']);
        } catch (Exception $e) {
            $pdo->rollBack();
            throw $e;
        }
    } else {
        throw new Exception('ການຢືນຢັນບໍ່ສຳເລັດ, TxID ອາດຈະບໍ່ຖືກຕ້ອງ');
    }

} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => $e->getMessage()]);
}
?>