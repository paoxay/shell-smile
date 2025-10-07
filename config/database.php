<?php
// กำหนดค่าการเชื่อมต่อฐานข้อมูล
$host = '127.0.0.1';
$db   = 'smile_panel_php'; // ตรวจสอบชื่อฐานข้อมูลของคุณ
$user = 'root';
$pass = ''; // ใส่รหัสผ่านของคุณถ้ามี
$charset = 'utf8mb4';

$dsn = "mysql:host=$host;dbname=$db;charset=$charset";
$options = [
    PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    PDO::ATTR_EMULATE_PREPARES   => false,
];

try {
    $pdo = new PDO($dsn, $user, $pass, $options);
} catch (\PDOException $e) {
    throw new \PDOException($e->getMessage(), (int)$e->getCode());
}
?>