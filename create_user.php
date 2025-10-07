<?php
// ໄຟລ໌ນີ້ໃຊ້ສຳລັບສ້າງ User ຊົ່ວຄາວເທົ່ານັ້ນ
// !!! ສຳຄັນ: ຫຼັງຈາກໃຊ້ງານແລ້ວໃຫ້ລຶບໄຟລ໌ນີ້ຖິ້ມທັນທີ !!!

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

// --- ຈຸດທີ່ແກ້ໄຂ ---
require_once 'config/database.php';

// --- ຕັ້ງຄ່າຜູ້ໃຊ້ທີ່ຕ້ອງການສ້າງຢູ່ບ່ອນນີ້ ---
$username = 'pao';
$password = 'pao';
$role     = 'admin';
// ------------------------------------------------

echo "<!DOCTYPE html><html><head><title>Create User</title><meta charset='UTF-8'></head><body>";
echo "<h1>ກຳລັງດຳເນີນການສ້າງຜູ້ໃຊ້...</h1>";

try {
    $stmt = $pdo->prepare("SELECT id FROM users WHERE username = ?");
    $stmt->execute([$username]);
    $existing_user = $stmt->fetch();

    if ($existing_user) {
        echo "<p style='color:orange;'>ຜູ້ໃຊ້ຊື່ '<strong>" . htmlspecialchars($username) . "</strong>' ມີຢູ່ໃນຖານຂໍ້ມູນແລ້ວ.</p>";
    } else {
        $hashed_password = password_hash($password, PASSWORD_DEFAULT);
        $insert_stmt = $pdo->prepare("INSERT INTO users (username, password, role) VALUES (?, ?, ?)");
        $insert_stmt->execute([$username, $hashed_password, $role]);
        echo "<p style='color:green;'>ສ້າງຜູ້ໃຊ້ '<strong>" . htmlspecialchars($username) . "</strong>' ພ້ອມກັບສິດ '<strong>" . htmlspecialchars($role) . "</strong>' ສຳເລັດ!</p>";
    }
} catch (PDOException $e) {
    echo "<p style='color:red;'>ເກີດຂໍ້ຜິດພາດ: " . $e->getMessage() . "</p>";
}

echo "<hr>";
echo "<h2 style='color:red;'>ຄຳເຕືອນ: ກະລຸນາລຶບໄຟລ໌นี้ (create_user.php) ຖິ້ມທັນທີຫຼັງຈາກໃຊ້ງານສຳເລັດ!</h2>";
echo "</body></html>";
?>