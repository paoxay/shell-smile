<?php
session_start();
header('Content-Type: application/json');
require_once '../../config/database.php';

if (!isset($_SESSION['admin_id'])) {
    http_response_code(401);
    exit();
}

try {
    $stmt = $pdo->prepare(
        "SELECT t.id, t.type, t.amount, t.status, t.created_at, u.username, t.balance_before, t.balance_after 
         FROM transactions t
         JOIN users u ON t.user_id = u.id
         ORDER BY t.created_at DESC
         LIMIT 20"
    );
    $stmt->execute();
    $transactions = $stmt->fetchAll();
    
    echo json_encode(['success' => true, 'transactions' => $transactions]);

} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => $e->getMessage()]);
}
?>