<?php

class JcApiService {
    private $baseUrl = 'https://jcplaycoin.com';
    private $settings;

    public function __construct() {
        if (session_status() === PHP_SESSION_NONE) {
            session_start();
        }
        $this->settings = require __DIR__ . '/../config/settings.php';
    }

    private function getToken() {
        if (isset($_SESSION['jc_master_token']) && !empty($_SESSION['jc_master_token'])) {
            return $_SESSION['jc_master_token'];
        }

        $ch = curl_init($this->baseUrl . '/api/users/login');
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HEADER, true);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
        curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
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
                $_SESSION['jc_master_token'] = $newToken;
                return $newToken;
            }
        }
        
        throw new Exception("ບໍ່ສາມາດຂໍ Master Token ໄດ້. ກະລຸນາກວດສອບ Username/Password ຂອງບັນຊີຫຼັກ.");
    }

    private function makeRequest($method, $endpoint, $payload = []) {
        $token = $this->getToken();
        $url = $this->baseUrl . $endpoint;
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
        curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
        $headers = ['Cookie: token=' . $token];
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HEADER, true);

        if ($method === 'POST') {
            $headers[] = 'Content-Type: application/json';
            curl_setopt($ch, CURLOPT_POST, true);
            curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload));
        }
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        $response = curl_exec($ch);

        if ($response === false) {
            $error = curl_error($ch);
            curl_close($ch);
            throw new Exception("cURL Error: " . $error);
        }
        
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        
        if ($http_code == 401 || $http_code == 302) {
             unset($_SESSION['jc_master_token']);
             curl_close($ch);
             throw new Exception("Authentication failed (Token might be expired). Please try again.");
        }
        
        $header_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
        $header = substr($response, 0, $header_size);
        $body = substr($response, $header_size);
        curl_close($ch);

        if ($http_code < 200 || $http_code >= 300) {
             throw new Exception("API Error: Server responded with status " . $http_code);
        }
        
        if (strpos($header, 'application/json') !== false) {
            return json_decode($body, true);
        } else {
            return $body;
        }
    }

    public function getStoreProducts() {
        $html = $this->makeRequest('GET', '/store');
        $products = [];
        libxml_use_internal_errors(true); 
        $dom = new DOMDocument(); 
        @$dom->loadHTML($html); 
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
         $html = $this->makeRequest('GET', '/detail-product?id=' . $productId);
        $items = [];
        libxml_use_internal_errors(true); 
        $dom = new DOMDocument(); 
        @$dom->loadHTML($html); 
        libxml_clear_errors();
        $xpath = new DOMXPath($dom);
        $rows = $xpath->query("//tbody/tr[@data-id]");
        foreach ($rows as $row) {
            $priceNode = $xpath->query(".//del[contains(@class, 'original-proposed-price')]", $row)->item(0);
            $base_price = $priceNode ? (float)$priceNode->getAttribute('value') : 0;
            $original_price = (float)$row->getAttribute('data-disprice');

            $items[] = [
                'item_id' => $row->getAttribute('data-id'),
                'item_pid' => $row->getAttribute('data-pid'),
                'name' => trim($xpath->query(".//td[1]", $row)->item(0)->textContent),
                'base_price' => $base_price,
                'original_price' => $original_price,
            ];
        }
        return $items;
    }

    public function initiateTopup($amount) {
        $payload = ['amount' => (string)$amount, 'type' => 'crypto-network'];
        $result1 = $this->makeRequest('POST', '/api/transactions/topup', $payload);
        $ref_code = $result1['data']['ref'] ?? null;
        if (!$ref_code) return null;
        $htmlResponse = $this->makeRequest('GET', '/payment?ref=' . $ref_code);
        $dom = new DOMDocument(); @$dom->loadHTML($htmlResponse);
        $xpath = new DOMXPath($dom);
        $wallet_address = $xpath->query("//input[@id='cryptoNetworkId']")->item(0)->getAttribute('value') ?? null;
        $network = $xpath->query("//input[@id='cryptoNetworkChannel']")->item(0)->getAttribute('value') ?? null;
        $currency = $xpath->query("//input[@id='currency']")->item(0)->getAttribute('value') ?? null;
        $final_data = $result1['data'];
        $final_data['payment_details'] = ['wallet_address' => $wallet_address, 'network' => $network, 'currency' => $currency];
        return ['success' => true, 'data' => $final_data];
    }
    
    public function confirmTopup($ref, $txId) {
        $payload = ['ref' => $ref, 'txId' => $txId];
        return $this->makeRequest('POST', '/api/transactions/confirm-payment', $payload);
    }

    public function createOrder($items, $totalAmount) {
        $payload = ['amount' => $totalAmount, 'items' => $items];
        return $this->makeRequest('POST', '/api/transactions/order', $payload);
    }
}
?>
