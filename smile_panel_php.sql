-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 05, 2025 at 02:44 PM
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
-- Table structure for table `transactions`
--

CREATE TABLE `transactions` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `ref_code` varchar(255) DEFAULT NULL,
  `type` enum('topup','purchase') NOT NULL,
  `amount` decimal(15,4) NOT NULL,
  `status` enum('pending','success','failed') NOT NULL,
  `details` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`details`)),
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `transactions`
--

INSERT INTO `transactions` (`id`, `user_id`, `ref_code`, `type`, `amount`, `status`, `details`, `created_at`) VALUES
(1, 1, 'TRX-6435942110392025584', 'topup', 100.0700, 'pending', '{\"userId\":\"6849377ec9443da301c80abf\",\"ref\":\"TRX-6435942110392025584\",\"amount\":100.07,\"type\":\"topup-cn\",\"status\":\"pending\",\"_id\":\"68e131bfb85c80a2e5be17e5\",\"items\":[],\"createdAt\":\"2025-10-04T14:39:59.647Z\",\"updatedAt\":\"2025-10-04T14:39:59.647Z\"}', '2025-10-04 14:40:00'),
(2, 1, 'TRX-8502942110452025713', 'topup', 100.4550, 'pending', '{\"userId\":\"6849377ec9443da301c80abf\",\"ref\":\"TRX-8502942110452025713\",\"amount\":100.455,\"type\":\"topup-cn\",\"status\":\"pending\",\"_id\":\"68e13309b85c80a2e5be186d\",\"items\":[],\"createdAt\":\"2025-10-04T14:45:29.853Z\",\"updatedAt\":\"2025-10-04T14:45:29.853Z\",\"payment_details\":{\"wallet_address\":\"0x43f66a55b2161a3e10b9f5d945288471296ab7c7\",\"network\":\"BEP20\",\"currency\":\"USDT\"}}', '2025-10-04 14:45:30');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `balance` decimal(15,4) DEFAULT 0.0000,
  `role` varchar(50) DEFAULT 'member',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password`, `balance`, `role`, `created_at`) VALUES
(1, 'paoxai5555', '$2y$10$aYZsD5i2wV0gqGAJ/6LRqemLrjePpLyF/jSmk9/CzwGsIso46cZru', 0.0000, 'member', '2025-10-04 14:33:27'),
(2, 'aa', '$2y$10$/UicevcEsXGNQSsKIQP6SOmVe/c8ac5tE9mD7/09DHdnMFaj0XlRO', 0.0000, 'member', '2025-10-04 15:11:16');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `transactions`
--
ALTER TABLE `transactions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ref_code` (`ref_code`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `transactions`
--
ALTER TABLE `transactions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `transactions`
--
ALTER TABLE `transactions`
  ADD CONSTRAINT `transactions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
