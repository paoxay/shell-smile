<?php
session_start();
header('Content-Type: application/json');

require_once '../../config/database.php';
require_once '../../core/JcApiService.php';

if (!isset($_SESSION['user_id'])) { /* ... */ exit(); }
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { /* ... */ exit(); }

$data = json_decode(file_get_contents("php://input"), true);
if (!isset($data['items']) || empty($data['items']) || !isset($data['productId'])) { /* ... */ exit(); }

$jcApiService = new JcApiService();
$userId = $_SESSION['user_id'];
$itemsFromClient = $data['items'];
$productId = $data['productId'];

try {
    // ຄຳນວນລາຄາໃໝ່ທີ່ Server
    $total_price = 0;
    $items_for_external_api = [];
    $productItemsFromApi = $jcApiService->getProductDetails($productId); // ບໍ່ຕ້ອງສົ່ງ token
    
    foreach ($itemsFromClient as $clientItem) {
        $found = false;
        foreach ($productItemsFromApi as $apiItem) {
            if ($apiItem['item_id'] === $clientItem['itemId']) {
                $total_price += $apiItem['base_price'] * $clientItem['quantity'];
                $items_for_external_api[] = [
                    'productId' => $productId,
                    'itemsId'   => $apiItem['item_id'],
                    'itemsPid'  => $apiItem['item_pid'],
                    'quantity'  => $clientItem['quantity']
                ];
                $found = true;
                break;
            }
        }
        if (!$found) throw new Exception("พบรายการสินค้าที่ไม่ถูกต้อง");
    }
    
    // ກວດສອບຍອດເງິນ
    $stmt = $pdo->prepare("SELECT balance FROM users WHERE id = ?");
    $stmt->execute([$userId]);
    $user = $stmt->fetch();
    if ($user['balance'] < $total_price) {
        http_response_code(402);
        echo json_encode(['success' => false, 'message' => 'ຍອດເງິນຂອງທ່ານບໍ່ພຽງພໍ']);
        exit();
    }
    
    // ສົ່ງຄຳສັ່ງຊື້
    $orderResult = $jcApiService->createOrder($items_for_external_api, $total_price); // ບໍ່ຕ້ອງສົ່ງ token
    if (!$orderResult || !isset($orderResult['success']) || !$orderResult['success']) {
        throw new Exception($orderResult['message'] ?? 'ການສັ່ງຊື້ທີ່ API ປາຍທາງລົ້ມເຫຼວ');
    }

    // ບັນທຶກ ແລະ ຫັກເງິນ
    $pdo->beginTransaction();
    // ... (database transaction logic remains the same) ...
    $updateBalance = $pdo->prepare("UPDATE users SET balance = balance - ? WHERE id = ?");
    $updateBalance->execute([$total_price, $userId]);
    $insertTrans = $pdo->prepare(
        "INSERT INTO transactions (user_id, ref_code, type, amount, status, details) VALUES (?, ?, 'purchase', ?, 'success', ?)"
    );
    $insertTrans->execute([$userId, $orderResult['data']['ref'], $total_price, json_encode($orderResult['data'])]);
    $pdo->commit();
    
    echo json_encode(['success' => true, 'message' => 'ການສັ່ງຊື້ສຳເລັດ!', 'data' => $orderResult['data']]);

} catch (Exception $e) {
    if ($pdo->inTransaction()) $pdo->rollBack();
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => $e->getMessage()]);
}
?>