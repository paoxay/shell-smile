<?php
session_start();
header('Content-Type: application/json');
require_once '../../../config/database.php';
require_once '../../../core/JcApiService.php';

if (!isset($_SESSION['admin_id'])) { http_response_code(401); exit(); }

try {
    // 1. ดึงข้อมูลสินค้าและการตั้งค่า Markup จาก DB ของเรา
    $stmt = $pdo->query(
        "SELECT p.id as product_id, p.name as product_name, p.external_id as product_external_id, p.is_active as product_is_active,
                pi.id as item_id, pi.external_item_id, pi.name as item_name, pi.markup_type, pi.markup_value, pi.is_active as item_is_active
         FROM products p
         LEFT JOIN product_items pi ON p.id = pi.product_id
         ORDER BY p.name, pi.id"
    );
    $db_results = $stmt->fetchAll();

    // 2. จัดกลุ่มข้อมูล
    $products_from_db = [];
    foreach($db_results as $row) {
        if(!isset($products_from_db[$row['product_id']])) {
            $products_from_db[$row['product_id']] = [
                'product_id' => $row['product_id'],
                'product_name' => $row['product_name'],
                'product_external_id' => $row['product_external_id'],
                'product_is_active' => $row['product_is_active'],
                'items' => []
            ];
        }
        if($row['item_id']) {
             $products_from_db[$row['product_id']]['items'][] = $row;
        }
    }
    
    $jcApiService = new JcApiService();
    $final_products = [];

    // 3. สำหรับสินค้าแต่ละหมวด, ไปดึงราคา Real-time แล้วนำมาอัปเดต
    foreach ($products_from_db as $product_id => $product_data) {
        $real_time_items = $jcApiService->getProductDetails($product_data['product_external_id']);
        
        $updated_items = [];
        if ($real_time_items) {
            $real_time_prices = [];
            foreach ($real_time_items as $rt_item) {
                // เก็บทั้งราคาต้นทุน (base_price) และ Original Price
                $real_time_prices[$rt_item['item_id']] = [
                    'base_price' => $rt_item['base_price'],
                    'original_price' => $rt_item['original_price']
                ];
            }

            // อัปเดตราคาในข้อมูลจาก DB ของเรา
            foreach ($product_data['items'] as $db_item) {
                if (isset($real_time_prices[$db_item['external_item_id']])) {
                    $db_item['base_price'] = $real_time_prices[$db_item['external_item_id']]['base_price'];
                    $db_item['original_price'] = $real_time_prices[$db_item['external_item_id']]['original_price'];
                    $updated_items[] = $db_item;
                }
            }
        }
        $product_data['items'] = $updated_items;
        $final_products[] = $product_data;
    }
    
    echo json_encode(['success' => true, 'products' => $final_products]);

} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => $e->getMessage(), 'trace' => $e->getTraceAsString()]);
}
?>
