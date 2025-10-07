<?php
session_start();
header('Content-Type: application/json');
require_once '../../../config/database.php';
require_once '../../../core/JcApiService.php';

if (!isset($_SESSION['admin_id'])) { http_response_code(401); exit(); }

try {
    $jcApiService = new JcApiService();
    $productsFromApi = $jcApiService->getStoreProducts();
    
    $product_count = 0;
    $item_count = 0;

    $pdo->beginTransaction();
    foreach($productsFromApi as $productData) {
        $stmt = $pdo->prepare("SELECT id FROM products WHERE external_id = ?");
        $stmt->execute([$productData['id']]);
        $existing_product = $stmt->fetch();

        if ($existing_product) {
            $product_id = $existing_product['id'];
            $stmt = $pdo->prepare("UPDATE products SET name = ?, image_url = ? WHERE id = ?");
            $stmt->execute([$productData['name'], $productData['image_url'], $product_id]);
        } else {
            $stmt = $pdo->prepare("INSERT INTO products (external_id, name, image_url) VALUES (?, ?, ?)");
            $stmt->execute([$productData['id'], $productData['name'], $productData['image_url']]);
            $product_id = $pdo->lastInsertId();
        }
        $product_count++;

        $itemsFromApi = $jcApiService->getProductDetails($productData['id']);
        foreach($itemsFromApi as $itemData) {
            $stmt = $pdo->prepare("INSERT INTO product_items (product_id, external_item_id, name, base_price) VALUES (?, ?, ?, ?) ON DUPLICATE KEY UPDATE name = VALUES(name), base_price = VALUES(base_price)");
            $stmt->execute([$product_id, $itemData['item_id'], $itemData['name'], $itemData['base_price']]);
            $item_count++;
        }
    }
    $pdo->commit();
    echo json_encode(['success' => true, 'message' => "Sync ສຳເລັດ! ພົບ {$product_count} ໝວດສິນຄ້າ ແລະ {$item_count} ລາຍການ."]);
} catch (Exception $e) {
    if ($pdo->inTransaction()) $pdo->rollBack();
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => $e->getMessage()]);
}
?>