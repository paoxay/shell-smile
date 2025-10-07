-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 07, 2025 at 04:21 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `smile_panel_php`
--

-- --------------------------------------------------------

--
-- Table structure for table `products`
--

CREATE TABLE `products` (
  `id` int(11) NOT NULL,
  `external_id` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `image_url` varchar(255) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `products`
--

INSERT INTO `products` (`id`, `external_id`, `name`, `image_url`, `is_active`, `created_at`, `updated_at`) VALUES
(1, '6767dbb63e6a5f8141a52a37', 'Smile One Code (Brazil)', 'https://jcplaycoin.com/assets/images/product/1758270174680-smilecoinbr.jpeg', 1, '2025-10-07 03:07:10', '2025-10-07 03:07:10'),
(2, '67fce47bcaaefc9a28e04ab4', 'Smile One Code (Philippines)', 'https://jcplaycoin.com/assets/images/product/1751389047927-Smile-PH.jpg', 0, '2025-10-07 03:07:11', '2025-10-07 03:07:50'),
(3, '6805bd461462ffe389d6a19a', 'Smilecoin TopUp (Philippines)', 'https://jcplaycoin.com/assets/images/product/1757518183417-smilephilipe.jpeg', 0, '2025-10-07 03:07:12', '2025-10-07 03:07:54'),
(4, '6805bd461462ffe389d6a198', 'Smilecoin TopUp (Brazil)', 'https://jcplaycoin.com/assets/images/product/1751389039518-Smile-Top-Up-BR.jpg', 0, '2025-10-07 03:07:12', '2025-10-07 07:07:15'),
(5, '6870cc63d4da09ab95b101b8', 'PUBG Mobile Code', 'https://jcplaycoin.com/assets/images/product/1752223356686-PUBG-SMILE.jpg', 1, '2025-10-07 03:07:13', '2025-10-07 08:52:04'),
(6, '687199a7a9fb92a8a9f69f94', 'Honor of Kings Code', 'https://jcplaycoin.com/assets/images/product/1758270558518-hok.jpeg', 0, '2025-10-07 03:07:13', '2025-10-07 03:07:41');

-- --------------------------------------------------------

--
-- Table structure for table `product_items`
--

CREATE TABLE `product_items` (
  `id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `external_item_id` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `base_price` decimal(15,4) NOT NULL,
  `markup_type` enum('percentage','fixed') NOT NULL DEFAULT 'percentage',
  `markup_value` decimal(15,4) NOT NULL DEFAULT 0.0000,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `product_items`
--

INSERT INTO `product_items` (`id`, `product_id`, `external_item_id`, `name`, `base_price`, `markup_type`, `markup_value`, `is_active`, `created_at`, `updated_at`) VALUES
(1, 1, '6767dbd03e6a5f8141a52a44', 'R$ 30', 5.5080, 'percentage', 0.5500, 1, '2025-10-07 03:07:11', '2025-10-07 05:42:55'),
(2, 1, '6767dbd03e6a5f8141a52a47', 'R$ 100', 18.3610, 'percentage', 0.5500, 1, '2025-10-07 03:07:11', '2025-10-07 05:42:55'),
(3, 1, '6767dbd03e6a5f8141a52a4a', 'R$ 500', 91.8020, 'percentage', 0.5500, 1, '2025-10-07 03:07:11', '2025-10-07 05:42:55'),
(4, 1, '6767dbd03e6a5f8141a52a4d', 'R$ 1000', 183.6030, 'percentage', 0.5500, 1, '2025-10-07 03:07:11', '2025-10-07 05:42:55'),
(5, 1, '6767dbd03e6a5f8141a52a50', 'R$ 5000', 918.0130, 'percentage', 0.5500, 1, '2025-10-07 03:07:11', '2025-10-07 05:42:55'),
(6, 2, '67fce48ecaaefc9a28e04abf', 'PHP 1120', 19.1440, 'percentage', 0.0000, 0, '2025-10-07 03:07:12', '2025-10-07 05:42:56'),
(7, 2, '67fce48ecaaefc9a28e04ac2', 'PHP 5600', 95.7210, 'percentage', 0.0000, 0, '2025-10-07 03:07:12', '2025-10-07 05:42:56'),
(8, 2, '67fce48ecaaefc9a28e04ac5', 'PHP 11200', 191.4420, 'percentage', 0.0000, 0, '2025-10-07 03:07:12', '2025-10-07 05:42:56'),
(9, 2, '67fce48ecaaefc9a28e04ac8', 'PHP 56000', 957.2080, 'percentage', 0.0000, 0, '2025-10-07 03:07:12', '2025-10-07 05:42:56'),
(10, 3, '6828088a6d070d02d9d66164', 'PHP 280', 4.7860, 'percentage', 0.0000, 0, '2025-10-07 03:07:12', '2025-10-07 05:42:56'),
(11, 3, '6828088a6d070d02d9d66167', 'PHP 560', 9.5720, 'percentage', 0.0000, 0, '2025-10-07 03:07:12', '2025-10-07 05:42:56'),
(12, 3, '6828088a6d070d02d9d6616a', 'PHP 1120', 19.1440, 'percentage', 0.0000, 0, '2025-10-07 03:07:12', '2025-10-07 05:42:56'),
(13, 3, '6828088a6d070d02d9d6616d', 'PHP 2240', 38.2880, 'percentage', 0.0000, 0, '2025-10-07 03:07:12', '2025-10-07 05:42:56'),
(14, 3, '6828088a6d070d02d9d66170', 'PHP 5600', 95.7210, 'percentage', 0.0000, 0, '2025-10-07 03:07:12', '2025-10-07 05:42:56'),
(15, 3, '6828088a6d070d02d9d66173', 'PHP 11200', 191.4420, 'percentage', 0.0000, 0, '2025-10-07 03:07:12', '2025-10-07 05:42:56'),
(16, 3, '6828088a6d070d02d9d66176', 'PHP 28000', 478.6040, 'percentage', 0.0000, 0, '2025-10-07 03:07:12', '2025-10-07 05:42:56'),
(17, 3, '6828088a6d070d02d9d66179', 'PHP 56000', 957.2080, 'percentage', 0.0000, 0, '2025-10-07 03:07:12', '2025-10-07 05:42:56'),
(18, 4, '6828d32758198474faf67e2f', 'R$ 30', 5.5080, 'percentage', 0.5500, 0, '2025-10-07 03:07:13', '2025-10-07 07:07:15'),
(19, 4, '6828d32758198474faf67e32', 'R$ 100', 18.3610, 'percentage', 0.5500, 0, '2025-10-07 03:07:13', '2025-10-07 07:07:15'),
(20, 4, '6828d32758198474faf67e35', 'R$ 500', 91.8020, 'percentage', 0.5500, 0, '2025-10-07 03:07:13', '2025-10-07 07:07:15'),
(21, 4, '6828d32758198474faf67e38', 'R$ 1000', 183.6030, 'percentage', 0.5500, 0, '2025-10-07 03:07:13', '2025-10-07 07:07:15'),
(22, 4, '6828d32758198474faf67e3b', 'R$ 5000', 918.0130, 'percentage', 0.5500, 0, '2025-10-07 03:07:13', '2025-10-07 07:07:15'),
(23, 5, '6870ccedd4da09ab95b10466', 'PUBG Mobile code  - 60 UC', 0.8680, 'percentage', 0.5500, 1, '2025-10-07 03:07:13', '2025-10-07 08:52:30'),
(24, 5, '6870ccedd4da09ab95b10469', 'PUBG Mobile code  - 300 & 25 UC', 4.3790, 'percentage', 0.5500, 1, '2025-10-07 03:07:13', '2025-10-07 08:52:30'),
(25, 5, '6870ccedd4da09ab95b1046c', 'PUBG Mobile code  - 600 & 60 UC', 8.7680, 'percentage', 0.5500, 1, '2025-10-07 03:07:13', '2025-10-07 08:52:29'),
(26, 5, '6870ccedd4da09ab95b1046f', 'PUBG Mobile code  - 1500 & 300 UC', 21.9360, 'percentage', 0.5500, 1, '2025-10-07 03:07:13', '2025-10-07 08:52:29'),
(27, 5, '6870ccedd4da09ab95b10472', 'PUBG Mobile code  - 3000 & 850 UC', 43.8810, 'percentage', 0.5500, 1, '2025-10-07 03:07:13', '2025-10-07 08:52:28'),
(28, 5, '6870ccedd4da09ab95b10475', 'PUBG Mobile code  - 6000& 2100 UC', 87.7730, 'percentage', 0.5500, 1, '2025-10-07 03:07:13', '2025-10-07 08:52:28'),
(29, 6, '68719a06a9fb92a8a9f69fa1', '16 TOKENS', 0.1700, 'percentage', 0.0000, 0, '2025-10-07 03:07:13', '2025-10-07 03:07:41'),
(30, 6, '68719a06a9fb92a8a9f69fa4', '80 TOKENS', 0.8390, 'percentage', 0.0000, 0, '2025-10-07 03:07:13', '2025-10-07 03:07:41'),
(31, 6, '68719a06a9fb92a8a9f69fa7', '240 TOKENS', 2.5350, 'percentage', 0.0000, 0, '2025-10-07 03:07:13', '2025-10-07 03:07:41'),
(32, 6, '68719a06a9fb92a8a9f69faa', '400 TOKENS', 4.2300, 'percentage', 0.0000, 0, '2025-10-07 03:07:13', '2025-10-07 03:07:41'),
(33, 6, '68719a06a9fb92a8a9f69fad', '800 +30 TOKENS', 8.4680, 'percentage', 0.0000, 0, '2025-10-07 03:07:13', '2025-10-07 03:07:41'),
(34, 6, '68719a06a9fb92a8a9f69fb0', '1200 +45 TOKENS', 12.7050, 'percentage', 0.0000, 0, '2025-10-07 03:07:13', '2025-10-07 03:07:41'),
(35, 6, '68719a06a9fb92a8a9f69fb3', '2400 +108 TOKENS', 25.4190, 'percentage', 0.0000, 0, '2025-10-07 03:07:13', '2025-10-07 03:07:41'),
(36, 6, '68719a06a9fb92a8a9f69fb6', '4000 +180 TOKENS', 42.3700, 'percentage', 0.0000, 0, '2025-10-07 03:07:13', '2025-10-07 03:07:41'),
(37, 6, '68719a06a9fb92a8a9f69fb9', '8000 + 360 TOKENS', 84.7480, 'percentage', 0.0000, 0, '2025-10-07 03:07:13', '2025-10-07 03:07:41');

-- --------------------------------------------------------

--
-- Table structure for table `transactions`
--

CREATE TABLE `transactions` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `ref_code` varchar(255) DEFAULT NULL,
  `type` enum('topup','purchase','adjustment') NOT NULL,
  `amount` decimal(15,4) NOT NULL,
  `balance_before` decimal(15,4) DEFAULT NULL,
  `balance_after` decimal(15,4) DEFAULT NULL,
  `status` enum('pending','success','failed') NOT NULL,
  `details` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`details`)),
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `transactions`
--

INSERT INTO `transactions` (`id`, `user_id`, `ref_code`, `type`, `amount`, `balance_before`, `balance_after`, `status`, `details`, `created_at`) VALUES
(6, 4, 'TRX-2865371210282025958', 'topup', 1.8800, 0.0000, 1.0000, 'success', '{\"statusCode\": 200, \"success\": true, \"message\": \"Topup request confirmed successfully\", \"data\": {\"_id\": \"68e4a515b85c80a2e5bffae1\", \"userId\": \"6849377ec9443da301c80abf\", \"ref\": \"TRX-2865371210282025958\", \"amount\": 1.88, \"type\": \"topup-cn\", \"status\": \"success\", \"items\": [], \"createdAt\": \"2025-10-07T05:28:53.290Z\", \"updatedAt\": \"2025-10-07T05:30:33.739Z\", \"callbackDetail\": {\"txId\": \"0xc645d396214cbc834a5b38475194080f5a03f70f00da020029716bdf9c271d3a\", \"amount\": \"1.88\", \"currency\": \"USDT\", \"confirmedAt\": \"2025-10-07T05:30:33.738Z\"}}}', '2025-10-07 05:28:54'),
(7, 4, 'TRX-5281071210352025000', 'topup', 1.9440, NULL, NULL, 'pending', '{\"ref\": \"TRX-5281071210352025000\", \"amount\": \"1.944\", \"wallet_address\": \"0x43f66a55b2161a3e10b9f5d945288471296ab7c7\", \"network\": \"BEP20\", \"currency\": \"USDT\"}', '2025-10-07 05:35:11'),
(8, 4, 'ADJ-1759819031-4', 'adjustment', 10.0000, 1.0000, 11.0000, 'success', '{\"remark\":\"\",\"admin_id\":5}', '2025-10-07 06:37:11'),
(9, 4, 'TRX-995671310372025461', 'purchase', -5.5383, 11.0000, 5.4617, 'success', '{\"userId\": \"6849377ec9443da301c80abf\", \"ref\": \"TRX-995671310372025461\", \"amount\": 5.509, \"type\": \"purchase\", \"status\": \"success\", \"items\": [{\"productId\": \"6767dbb63e6a5f8141a52a37\", \"itemsId\": \"6767dbd03e6a5f8141a52a44\", \"itemsPid\": \"1\", \"quantity\": 1, \"_id\": \"68e4b545b85c80a2e5c00dfd\"}], \"callbackDetail\": {\"orderId\": \"SC251007033756910K\"}, \"_id\": \"68e4b545b85c80a2e5c00dfc\", \"createdAt\": \"2025-10-07T06:37:57.847Z\", \"updatedAt\": \"2025-10-07T06:37:57.847Z\"}', '2025-10-07 06:37:58'),
(10, 4, 'ADJ-1759824118-4', 'adjustment', 5.0000, 5.4617, 10.4617, 'success', '{\"remark\":\"\",\"admin_id\":5}', '2025-10-07 08:01:58'),
(11, 4, 'TRX-546167151022025614', 'purchase', -5.5323, 10.4617, 4.9294, 'success', '{\"userId\": \"6849377ec9443da301c80abf\", \"ref\": \"TRX-546167151022025614\", \"amount\": 5.503, \"type\": \"purchase\", \"status\": \"success\", \"items\": [{\"productId\": \"6767dbb63e6a5f8141a52a37\", \"itemsId\": \"6767dbd03e6a5f8141a52a44\", \"itemsPid\": \"1\", \"quantity\": 1, \"_id\": \"68e4c90ab85c80a2e5c02871\"}], \"callbackDetail\": {\"orderId\": \"SC251007050217318Q\"}, \"_id\": \"68e4c90ab85c80a2e5c02870\", \"createdAt\": \"2025-10-07T08:02:18.494Z\", \"updatedAt\": \"2025-10-07T08:02:18.494Z\"}', '2025-10-07 08:02:19'),
(12, 4, 'ADJ-1759824427-4', 'adjustment', 1000.0000, 4.9294, 1004.9294, 'success', '{\"remark\":\"\",\"admin_id\":5}', '2025-10-07 08:07:07'),
(13, 4, 'TRX-875271510432025760', 'purchase', -5.5323, 1004.9294, 999.3971, 'success', '{\"userId\": \"6849377ec9443da301c80abf\", \"ref\": \"TRX-875271510432025760\", \"amount\": 5.503, \"type\": \"purchase\", \"status\": \"success\", \"items\": [{\"productId\": \"6767dbb63e6a5f8141a52a37\", \"itemsId\": \"6767dbd03e6a5f8141a52a44\", \"itemsPid\": \"1\", \"quantity\": 1, \"_id\": \"68e4d29db85c80a2e5c031e7\"}], \"callbackDetail\": {\"orderId\": \"SC251007054308636N\"}, \"_id\": \"68e4d29db85c80a2e5c031e6\", \"createdAt\": \"2025-10-07T08:43:09.787Z\", \"updatedAt\": \"2025-10-07T08:43:09.787Z\"}', '2025-10-07 08:43:13'),
(14, 4, 'TRX-5123671510482025118', 'topup', 1.4240, NULL, NULL, 'pending', '{\"ref\": \"TRX-5123671510482025118\", \"amount\": \"1.424\", \"wallet_address\": \"0x43f66a55b2161a3e10b9f5d945288471296ab7c7\", \"network\": \"BEP20\", \"currency\": \"USDT\"}', '2025-10-07 08:48:37'),
(15, 4, 'TRX-8681771510502025436', 'topup', 200.5170, NULL, NULL, 'pending', '{\"ref\": \"TRX-8681771510502025436\", \"amount\": \"200.517\", \"wallet_address\": \"0x43f66a55b2161a3e10b9f5d945288471296ab7c7\", \"network\": \"BEP20\", \"currency\": \"USDT\"}', '2025-10-07 08:50:19'),
(16, 4, 'TRX-4334871510502025774', 'purchase', -5.5313, 999.3971, 993.8658, 'success', '{\"userId\": \"6849377ec9443da301c80abf\", \"ref\": \"TRX-4334871510502025774\", \"amount\": 5.502, \"type\": \"purchase\", \"status\": \"success\", \"items\": [{\"productId\": \"6767dbb63e6a5f8141a52a37\", \"itemsId\": \"6767dbd03e6a5f8141a52a44\", \"itemsPid\": \"1\", \"quantity\": 1, \"_id\": \"68e4d46cb85c80a2e5c03468\"}], \"callbackDetail\": {\"orderId\": \"SC251007055051831P\"}, \"_id\": \"68e4d46cb85c80a2e5c03467\", \"createdAt\": \"2025-10-07T08:50:52.406Z\", \"updatedAt\": \"2025-10-07T08:50:52.406Z\"}', '2025-10-07 08:50:55');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `telegram_id` bigint(20) DEFAULT NULL,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `balance` decimal(15,4) NOT NULL DEFAULT 0.0000,
  `role` varchar(50) NOT NULL DEFAULT 'member',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `telegram_id`, `username`, `password`, `balance`, `role`, `created_at`) VALUES
(4, 2043446589, 'Paoxayyasan', 'telegram_user', 993.8658, 'member', '2025-10-07 05:25:39'),
(5, NULL, 'pao', '$2y$10$Uxab3c.glKAIEqbWJoqoUepgrc5NKnJ0JFokgV0e38CDcU.8Yujoe', 0.0000, 'admin', '2025-10-07 06:33:12');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `external_id` (`external_id`);

--
-- Indexes for table `product_items`
--
ALTER TABLE `product_items`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `external_item_id` (`external_item_id`),
  ADD KEY `product_id` (`product_id`);

--
-- Indexes for table `transactions`
--
ALTER TABLE `transactions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `telegram_id` (`telegram_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `products`
--
ALTER TABLE `products`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `product_items`
--
ALTER TABLE `product_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=75;

--
-- AUTO_INCREMENT for table `transactions`
--
ALTER TABLE `transactions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `product_items`
--
ALTER TABLE `product_items`
  ADD CONSTRAINT `product_items_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `transactions`
--
ALTER TABLE `transactions`
  ADD CONSTRAINT `transactions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
