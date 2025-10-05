<?php
session_start();
header('Content-Type: application/json');

require_once '../../core/JcApiService.php';

if (!isset($_SESSION['user_id'])) { /* ... */ exit(); }
if (!isset($_GET['id'])) { /* ... */ exit(); }

$productId = $_GET['id'];

try {
    $jcApiService = new JcApiService();
    // ເອີ້ນໃຊ້ຟັງຊັນໂດຍບໍ່ຕ້ອງສົ່ງ token
    $items = $jcApiService->getProductDetails($productId);
    
    if ($items !== null) {
        echo json_encode(['success' => true, 'items' => $items]);
    } else {
        throw new Exception('ບໍ່ສາມາດດຶງຂໍ້ມູນລາຍລະອຽດສິນຄ້າໄດ້');
    }
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => $e->getMessage()]);
}
?>