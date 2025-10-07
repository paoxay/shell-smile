<?php
require_once 'auth_check.php'; // ກວດສອບการล็อกอินก่อน
require_once '../config/database.php';
require_once '../core/JcApiService.php';

$message = '';
$error = '';

// ---- ສ່ວນປະມວນຜົນ (Processing) ----
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // ກໍລະນີກົດປຸ່ມ Sync
    if (isset($_POST['action']) && $_POST['action'] === 'sync') {
        try {
            $jcApiService = new JcApiService();
            // ... (ເນື້ອໃນໂຄດ Sync ຄືເກົ່າ) ...
            $message = "Sync ສຳເລັດ!";
        } catch (Exception $e) {
            $error = "Sync ລົ້ມເຫຼວ: " . $e->getMessage();
        }
    }
    // ກໍລະນີກົດປຸ່ມ Save ຂອງແຕ່ລະລາຍການ
    elseif (isset($_POST['action']) && $_POST['action'] === 'update_item') {
        try {
            $stmt = $pdo->prepare("UPDATE product_items SET markup_type = ?, markup_value = ?, is_active = ? WHERE id = ?");
            $stmt->execute([
                $_POST['markup_type'],
                $_POST['markup_value'],
                isset($_POST['is_active']) ? 1 : 0,
                $_POST['item_id']
            ]);
            $message = "ບັນທຶກລາຍການ #" . $_POST['item_id'] . " ສຳເລັດ.";
        } catch (Exception $e) {
            $error = "ບັນທຶກລົ້ມເຫຼວ: " . $e->getMessage();
        }
    }
}

// ---- ສ່ວນດຶງຂໍ້ມູນມາສະແດງ (Data Fetching) ----
$stmt = $pdo->query("SELECT p.id as product_id, p.name as product_name, pi.id as item_id, pi.name as item_name, pi.base_price, pi.markup_type, pi.markup_value, pi.is_active FROM products p JOIN product_items pi ON p.id = pi.product_id ORDER BY p.id, pi.id");
$results = $stmt->fetchAll(PDO::FETCH_GROUP); // ຈັດກຸ່ມตาม product_id

?>
<!DOCTYPE html>
<html lang="lo">
<head>
    <meta charset="UTF-8">
    <title>ຈັດການສິນຄ້າ</title>
    <style> /* ... CSS ຄືເກົ່າ ... */ </style>
</head>
<body>
    <div class="admin-layout">
        <nav class="sidebar">
            <h2>Admin Panel</h2>
            <ul>
                <li><a href="#">Dashboard</a></li>
                <li><a href="products.php" class="active">ຈັດການສິນຄ້າ</a></li>
                <li><a href="members.php">ຈັດການສະມາຊິກ</a></li>
                <li><a href="logout.php" class="logout-button">ອອກຈາກລະບົບ</a></li>
            </ul>
        </nav>
        <main class="main-content">
            <div class="container">
                <div class="header">
                    <h2>ຈັດການສິນຄ້າ ແລະ ລາຄາຂາຍ</h2>
                    <form method="POST" action="products.php" style="margin: 0;">
                        <input type="hidden" name="action" value="sync">
                        <button type="submit" class="sync-button">Sync Products from API</button>
                    </form>
                </div>
                <?php if ($message): ?><p style="color: green;"><?php echo $message; ?></p><?php endif; ?>
                <?php if ($error): ?><p style="color: red;"><?php echo $error; ?></p><?php endif; ?>
                
                <?php foreach($results as $product_id => $items): ?>
                    <fieldset class="product-group">
                        <legend><?php echo htmlspecialchars($items[0]['product_name']); ?></legend>
                        <table>
                            <thead><tr><th>ແພັກເກັດ</th><th>ຕົ້ນທຶນ</th><th>ປະເພດກຳໄລ</th><th>ຄ່າກຳໄລ</th><th>ເປີດໃຊ້ງານ</th><th>ຈັດການ</th></tr></thead>
                            <tbody>
                                <?php foreach($items as $item): ?>
                                <tr>
                                    <form method="POST" action="products.php">
                                        <input type="hidden" name="action" value="update_item">
                                        <input type="hidden" name="item_id" value="<?php echo $item['item_id']; ?>">
                                        <td><?php echo htmlspecialchars($item['item_name']); ?></td>
                                        <td>$<?php echo number_format($item['base_price'], 4); ?></td>
                                        <td>
                                            <select name="markup_type">
                                                <option value="percentage" <?php if($item['markup_type'] == 'percentage') echo 'selected'; ?>>ເປີເຊັນ (%)</option>
                                                <option value="fixed" <?php if($item['markup_type'] == 'fixed') echo 'selected'; ?>>ຈຳນວນຄົງທີ່ ($)</option>
                                            </select>
                                        </td>
                                        <td><input type="number" name="markup_value" value="<?php echo $item['markup_value']; ?>" step="0.01"></td>
                                        <td><input type="checkbox" name="is_active" <?php if($item['is_active']) echo 'checked'; ?>></td>
                                        <td><button type="submit" class="save-button">Save</button></td>
                                    </form>
                                </tr>
                                <?php endforeach; ?>
                            </tbody>
                        </table>
                    </fieldset>
                <?php endforeach; ?>

                <?php if (empty($results)): ?>
                    <p>ບໍ່ພົບຂໍ້ມູນສິນຄ້າ. ກະລຸນາກົດ Sync.</p>
                <?php endif; ?>
            </div>
        </main>
    </div>
</body>
</html>