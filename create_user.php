<?php
// ໄຟລ໌ນີ້ໃຊ້ສຳລັບສ້າງ User ຊົ່ວຄາວເທົ່ານັ້ນ
// !!! ສຳຄັນ: ຫຼັງຈາກໃຊ້ງານແລ້ວໃຫ້ລຶບໄຟລ໌ນີ້ຖິ້ມທັນທີ !!!

require_once 'config/database.php';

// --- ໃສ່ຂໍ້ມູນ User ທີ່ທ່ານຕ້ອງການສ້າງລົງບ່ອນນີ້ ---
$username = 'aa';
$password = 'aa';
// ------------------------------------------------

echo "<!DOCTYPE html><html><head><title>Create User</title><meta charset='UTF-8'></head><body>";
echo "<h1>ກຳລັງພະຍາຍາມສ້າງຜູ້ໃຊ້...</h1>";

try {
    // 1. ກວດສອບກ່ອນວ່າຊື່ຜູ້ນີ້ມີໃນລະບົບແລ້ວ ຫຼື ບໍ່
    $stmt = $pdo->prepare("SELECT id FROM users WHERE username = ?");
    $stmt->execute([$username]);
    $existing_user = $stmt->fetch();

    if ($existing_user) {
        echo "<p style='color:orange;'>ຜູ້ໃຊ້ຊື່ '<strong>" . htmlspecialchars($username) . "</strong>' ມີຢູ່ໃນຖານຂໍ້ມູນແລ້ວ. ບໍ່ຈຳເປັນຕ້ອງສ້າງໃໝ່.</p>";
    } else {
        // 2. ຖ້າບໍ່ມີ, ໃຫ້ເຂົ້າລະຫັດຜ່ານເພື່ອຄວາມປອດໄພ
        $hashed_password = password_hash($password, PASSWORD_DEFAULT);

        // 3. ບັນທຶກ User ໃໝ່ລົງຖານຂໍ້ມູນ
        $insert_stmt = $pdo->prepare("INSERT INTO users (username, password) VALUES (?, ?)");
        $insert_stmt->execute([$username, $hashed_password]);

        echo "<p style='color:green;'>ສ້າງຜູ້ໃຊ້ຊື່ '<strong>" . htmlspecialchars($username) . "</strong>' ສຳເລັດ!</p>";
    }

} catch (PDOException $e) {
    echo "<p style='color:red;'>ເກີດຂໍ້ຜິດພາດໃນການເຊື່ອມຕໍ່ຖານຂໍ້ມູນ: " . $e->getMessage() . "</p>";
}

echo "<hr>";
echo "<h2 style='color:red;'>ຄຳເຕືອນ: ກະລຸນາລຶບໄຟລ໌นี้ (create_user.php) ຖິ້ມທັນທີຫຼັງຈາກໃຊ້ງານສຳເລັດ!</h2>";
echo "</body></html>";

?>