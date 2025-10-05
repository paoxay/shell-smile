<?php
session_start();
header('Content-Type: application/json');

require_once '../../core/JcApiService.php';

if (!isset($_SESSION['user_id'])) { /* ... */ exit(); }

try {
    $jcApiService = new JcApiService();
    // ເອີ້ນໃຊ້ຟັງຊັນໂດຍບໍ່ຕ້ອງສົ່ງ token
    $products = $jcApiService->getStoreProducts();
    
    if ($products !== null) {
        echo json_encode(['success' => true, 'products' => $products]);
    } else {
        throw new Exception('ບໍ່ສາມາດດຶງຂໍ້ມູນສິນຄ້າໄດ້');
    }
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => $e->getMessage()]);
}
?>