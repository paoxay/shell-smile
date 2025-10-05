// ແກ້ໄຂໄຟລ໌ create_user.php
$username = 'pao';
$password = 'pao';
$role = 'admin'; // ເພີ່ມບັນທັດນີ້

// ແລ້ວແກ້ໄຂຄຳສັ່ງ INSERT ເປັນ
$insert_stmt = $pdo->prepare("INSERT INTO users (username, password, role) VALUES (?, ?, ?)");
$insert_stmt->execute([$username, $hashed_password, $role]);