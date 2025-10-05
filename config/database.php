<?php
// กำหนดค่าการเชื่อมต่อฐานข้อมูล
$host = '127.0.0.1';
$db   = 'smile_panel_php';
$user = 'root';
$pass = ''; // ໃສ່ລະຫັດຜ່ານຂອງທ່ານຖ້າມີ
$charset = 'utf8mb4';

$dsn = "mysql:host=$host;dbname=$db;charset=$charset";
$options = [
    PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    PDO::ATTR_EMULATE_PREPARES   => false,
];

try {
    // สร้าง object PDO สำหรับเชื่อมต่อฐานข้อมูล
    $pdo = new PDO($dsn, $user, $pass, $options);
} catch (\PDOException $e) {
    // หากเชื่อมต่อไม่ได้ ให้โยน error ออกไป
    throw new \PDOException($e->getMessage(), (int)$e->getCode());
}
?>