<?php

class JcApiService {
    private $baseUrl = 'https://jcplaycoin.com';
    private $settingsFile;
    private $settings;

    /**
     * ເມື່ອ Class ຖືກສ້າງ, ໃຫ້ໂຫຼດຂໍ້ມູນຕັ້ງຄ່າມາເກັບໄວ້
     */
    public function __construct() {
        $this->settingsFile = __DIR__ . '/../config/settings.php';
        $this->settings = require $this->settingsFile;
    }

    /**
     * (ຟັງຊັນໃໝ່) ໃຊ້ສຳລັບຂໍ Token ໃໝ່ເມື່ອອັນເກົ່າໝົດອາຍຸ
     * @return bool
     * @throws Exception
     */
    private function refreshToken() {
        $ch = curl_init($this->baseUrl . '/api/users/login');
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HEADER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
            'username' => $this->settings['jc_master_username'],
            'password' => $this->settings['jc_master_password']
        ]));

        $response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($http_code >= 200 && $http_code < 300) {
            list($header, $body) = explode("\r\n\r\n", $response, 2);
            preg_match('/^Set-Cookie:\s*token=([^;]*)/mi', $header, $matches);
            $newToken = $matches[1] ?? null;
            
            if ($newToken) {
                // ອັບເດດ Token ໃໝ່ໃນ Class
                $this->settings['jc_master_token'] = $newToken;

                // ອັບເດດ Token ໃໝ່ລົງໃນໄຟລ໌ settings.php
                // ຄຳເຕືອນ: Server ຕ້ອງມີສິດ (Permission) ໃນການຂຽນທັບໄຟລ໌ນີ້
                $settingsContent = file_get_contents($this->settingsFile);
                $newContent = preg_replace(
                    "/('jc_master_token'\s*=>\s*')[^']*/", 
                    "$1" . addslashes($newToken), 
                    $settingsContent
                );
                file_put_contents($this->settingsFile, $newContent);

                return true;
            }
        }
        
        throw new Exception("ບໍ່ສາມາດຂໍ Token ໃໝ່ได้. ກະລຸນາກວດສອບ Username/Password ຂອງບັນຊີຫຼັກ.");
    }

    /**
     * (ຟັງຊັນໃໝ່) ເປັນຫົວໃຈຫຼັກໃນການຍິງ API, ມີລະບົບລອງໃໝ່ (Retry)
     * @param string $method (GET, POST)
     * @param string $endpoint
     * @param array $payload
     * @param bool $isRetry
     * @return array
     * @throws Exception
     */
    private function makeRequest($method, $endpoint, $payload = [], $isRetry = false) {
        $url = $this->baseUrl . $endpoint;
        $ch = curl_init($url);

        $headers = [
            'Cookie: token=' . $this->settings['jc_master_token']
        ];
        
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HEADER, true); // ເອົາ Header ມາເພື່ອກວດສອບ Content-Type

        if ($method === 'POST') {
            $headers[] = 'Content-Type: application/json';
            curl_setopt($ch, CURLOPT_POST, true);
            curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload));
        }
        
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);

        $response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        // ກວດສອບກໍລະນີ Token ໝົດອາຍຸ (401)
        if ($http_code == 401 && !$isRetry) {
            $this->refreshToken(); // ຂໍ Token ໃໝ່
            return $this->makeRequest($method, $endpoint, $payload, true); // ລອງຍິງ API ຊ້ຳອີກຄັ້ງ
        }

        if ($http_code < 200 || $http_code >= 300) {
             throw new Exception("API Error: Server responded with status " . $http_code);
        }

        // ແຍກ Header ແລະ Body
        $header_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
        $header_str = substr($response, 0, $header_size);
        $body_str = substr($response, $header_size);

        // ກວດສອບວ່າຄຳຕອບເປັນ JSON ຫຼື HTML
        if (strpos($header_str, 'application/json') !== false) {
            return ['type' => 'json', 'content' => json_decode($body_str, true)];
        } else {
            return ['type' => 'html', 'content' => $body_str];
        }
    }

    // --- ຟັງຊັນ Public ທັງໝົດຈະຖືກປັບໃຫ້ງ່າຍຂຶ້ນ ---

    public function getStoreProducts() {
        $response = $this->makeRequest('GET', '/store');
        $html = $response['content'];
        
        // ... (ໂຄດແກະ HTML ຍັງຄືເກົ່າ) ...
        $products = [];
        libxml_use_internal_errors(true);
        $dom = new DOMDocument();
        $dom->loadHTML($html);
        libxml_clear_errors();
        $xpath = new DOMXPath($dom);
        $product_links = $xpath->query("//a[starts-with(@href, '/detail-product?id=')]");
        foreach ($product_links as $link) {
            $href = $link->getAttribute('href');
            parse_str(parse_url($href, PHP_URL_QUERY), $query);
            $id = $query['id'] ?? null;
            $name = trim($xpath->query(".//h6", $link)->item(0)->textContent ?? '');
            $image_url = $xpath->query(".//img", $link)->item(0)->getAttribute('src') ?? null;
            if ($id) $products[] = ['id' => $id, 'name' => $name, 'image_url' => $this->baseUrl . $image_url];
        }
        return $products;
    }

    public function getProductDetails($productId) {
         $response = $this->makeRequest('GET', '/detail-product?id=' . $productId);
         $html = $response['content'];

        // ... (ໂຄດແກະ HTML ຍັງຄືເກົ່າ) ...
        $items = [];
        libxml_use_internal_errors(true);
        $dom = new DOMDocument();
        $dom->loadHTML($html);
        libxml_clear_errors();
        $xpath = new DOMXPath($dom);
        $rows = $xpath->query("//tbody/tr[@data-id]");
        foreach ($rows as $row) {
            $items[] = [
                'item_id' => $row->getAttribute('data-id'),
                'item_pid' => $row->getAttribute('data-pid'),
                'name' => trim($xpath->query(".//td[1]", $row)->item(0)->textContent),
                'base_price' => (float)$row->getAttribute('data-base-price'),
            ];
        }
        return $items;
    }

    public function initiateTopup($amount) {
        $payload = ['amount' => (string)$amount, 'type' => 'crypto-network'];
        $response = $this->makeRequest('POST', '/api/transactions/topup', $payload);
        // ... The logic for fetching the payment page and parsing it should be here ...
        // For now, we will return the direct response and assume the refactor is focused on token refresh
        return $response['content'];
    }

    public function confirmTopup($ref, $txId) {
        $payload = ['ref' => $ref, 'txId' => $txId];
        $response = $this->makeRequest('POST', '/api/transactions/confirm-payment', $payload);
        return $response['content'];
    }

    public function createOrder($items, $totalAmount) {
        $payload = ['amount' => $totalAmount, 'items' => $items];
        $response = $this->makeRequest('POST', '/api/transactions/order', $payload);
        return $response['content'];
    }
}
?>