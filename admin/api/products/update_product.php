<?php
session_start();
header('Content-Type: application/json');

// ຮັບປະກັນວ່າເສັ້ນທາງຖືກຕ້ອງ
require_once '../../../config/database.php';

// 1. ກວດສອບສິດ ແລະ Method
if (!isset($_SESSION['admin_id'])) { 
    http_response_code(401); 
    echo json_encode(['success' => false, 'message' => 'Unauthorized']);
    exit(); 
}
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { 
    http_response_code(405); 
    exit(); 
}

// 2. ຮັບຂໍ້ມູນທີ່ສົ່ງມາຈາກ JavaScript
$data = json_decode(file_get_contents("php://input"));

// 3. ກວດສອບຄວາມຄົບຖ້ວນຂອງຂໍ້ມູນ
if (!isset($data->product_id) || !isset($data->is_active)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'ຂໍ້ມູນບໍ່ຄົບຖ້ວນ']);
    exit();
}

try {
    // ເລີ່ມ Transaction ເພື່ອຮັບປະກັນວ່າທຸກຄຳສັ່ງຈະສຳເລັດ ຫຼື ລົ້ມເຫຼວໄປພ້ອມກັນ
    $pdo->beginTransaction();
    
    // 4. ແປງຄ່າ boolean (true/false) ຈາກ JavaScript ໃຫ້ເປັນ integer (1/0) ສຳລັບຖານຂໍ້ມູນ
    $is_active_int = $data->is_active ? 1 : 0;

    // 5. ອັບເດດສະຖານະຂອງໝວດສິນຄ້າຫຼັກ (ຕາຕະລາງ products)
    $stmt1 = $pdo->prepare("UPDATE products SET is_active = ? WHERE id = ?");
    $stmt1->execute([$is_active_int, $data->product_id]);

    // 6. ອັບເດດສະຖານະຂອງແພັກເກັດຍ່ອຍທັງໝົດທີ່ຢູ່ພາຍໃຕ້ໝວດນັ້ນ (ຕາຕະລາງ product_items)
    $stmt2 = $pdo->prepare("UPDATE product_items SET is_active = ? WHERE product_id = ?");
    $stmt2->execute([$is_active_int, $data->product_id]);

    // 7. ຢືນຢັນການບັນທຶກຂໍ້ມູນລົງຖານຂໍ້ມູນ
    $pdo->commit();
    
    echo json_encode(['success' => true, 'message' => 'ອັບເດດສະຖານະໝວດສິນຄ້າສຳເລັດ']);

} catch (Exception $e) {
    // ຖ້າເກີດຂໍ້ຜິດພາດ, ໃຫ້ຍົກເລີກການບັນທຶກທັງໝົດ
    if ($pdo->inTransaction()) {
        $pdo->rollBack();
    }
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => $e->getMessage()]);
}
?>
