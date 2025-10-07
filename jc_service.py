# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import config
import logging

_jc_master_token = None

def get_token():
    """ກວດສອບ ແລະ ຂໍ Master Token ໃໝ່ຖ້າຈຳເປັນ"""
    global _jc_master_token
    if _jc_master_token:
        return _jc_master_token
    logging.info("Requesting a new master token...")
    try:
        response = requests.post(
            'https://jcplaycoin.com/api/users/login',
            json={'username': config.JC_MASTER_USERNAME, 'password': config.JC_MASTER_PASSWORD},
            timeout=15, verify=False
        )
        response.raise_for_status()
        token = response.cookies.get('token')
        if not token: raise Exception("ບໍ່ພົບ Token ໃນ Cookie")
        _jc_master_token = token
        logging.info("Successfully obtained a new master token.")
        return token
    except requests.exceptions.RequestException as e:
        logging.error(f"Error getting token: {e}")
        raise Exception("ບໍ່ສາມາດຂໍ Master Token ໄດ້")

def _make_request(method, endpoint, payload=None, is_retry=False):
    """ฟังก์ชันกลางสำหรับยิง API พร้อมระบบ Retry"""
    try:
        token = get_token()
        cookies = {'token': token}
        url = f"https://jcplaycoin.com{endpoint}"
        if method.upper() == 'GET':
            response = requests.get(url, cookies=cookies, timeout=15, verify=False)
        elif method.upper() == 'POST':
            response = requests.post(url, cookies=cookies, json=payload, timeout=20, verify=False)
        else:
            raise ValueError("Unsupported HTTP method")
        if response.status_code in [401, 403, 302] and not is_retry:
            logging.warning(f"Request failed with {response.status_code}. Refreshing token...")
            global _jc_master_token
            _jc_master_token = None
            return _make_request(method, endpoint, payload, is_retry=True)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed for {endpoint}: {e}")
        return None

def getProductDetails(product_id):
    """ດຶງຂໍ້ມູນລາຍລະອຽດສິນຄ້າ (ແພັກເກັດຍ່ອຍ)"""
    response = _make_request('GET', f'/detail-product?id={product_id}')
    if not response: return None
    items = []
    soup = BeautifulSoup(response.text, 'lxml')
    rows = soup.select("tbody tr[data-id]")
    for row in rows:
        price_node = row.select_one("del.original-proposed-price")
        base_price = float(price_node['value']) if price_node and 'value' in price_node.attrs else 0.0
        original_price = float(row.get('data-disprice', 0.0))
        items.append({'item_id': row.get('data-id'), 'item_pid': row.get('data-pid'),'name': row.select_one("td").text.strip(),'base_price': base_price,'original_price': original_price})
    return items

def createOrder(items, total_amount):
    """ສ້າງຄຳສັ່ງຊື້"""
    payload = {'amount': 0, 'items': items}
    response = _make_request('POST', '/api/transactions/order', payload)
    return response.json() if response and 'application/json' in response.headers.get('Content-Type', '') else None

def getOrderDetailCode(ref_code):
    """ດຶງ Voucher Code ຈາກໜ້າລາຍລະອຽດ Order"""
    try:
        response = _make_request('GET', f'/detail-order?ref={ref_code}')
        if not response:
            return "ບໍ່ສາມາດດຶງຂໍ້ມູນ Code ໄດ້"
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # --- LOGIC ໃໝ່ທີ່ຖືກຕ້ອງ 100% ---
        # 1. ຊອກຫາປ້າຍ "Code"
        code_label = soup.find('p', class_='text-grey-custom', string=lambda text: text and 'Code' in text)
        
        if code_label:
            # 2. ຊອກຫາ div ທີ່ເປັນ container ຂອງ code ຕົວຈິງ
            code_row = code_label.find_next_sibling('div', class_='row')
            if code_row:
                # 3. ຊອກຫາ <p class="m-0"> ທີ່ຢູ່ຂ້າງໃນ
                code_tag = code_row.find('p', class_='m-0')
                if code_tag and code_tag.text.strip():
                    return code_tag.text.strip() # ສົ່ງຄືນ Code ທີ່ດຶງໄດ້
        
        return "ບໍ່ພົບ Code (ໂຄງສ້າງ HTML ອາດຈະປ່ຽນ)"
    except Exception as e:
        logging.error(f"Error parsing order detail page for code: {e}")
        return "ເກີດຂໍ້ຜິດພາດຕອນດຶງ Code"

def initiate_topup(amount):
    """ເລີ່ມຕົ້ນທຸລະກຳເຕີມເງິນ"""
    response_step1 = _make_request('POST', '/api/transactions/topup', {'amount': str(amount), 'type': 'crypto-network'})
    if not response_step1: return None
    data_step1 = response_step1.json()
    ref_code = data_step1.get('data', {}).get('ref')
    if not ref_code: return None
    response_step2 = _make_request('GET', f'/payment?ref={ref_code}')
    if not response_step2: return None
    soup = BeautifulSoup(response_step2.text, 'lxml')
    wallet_address = soup.find('input', {'id': 'cryptoNetworkId'}).get('value')
    network = soup.find('input', {'id': 'cryptoNetworkChannel'}).get('value')
    currency = soup.find('input', {'id': 'currency'}).get('value')
    final_amount = soup.find('input', {'id': 'amount'}).get('value')
    return {'ref': ref_code, 'amount': final_amount, 'wallet_address': wallet_address, 'network': network, 'currency': currency}

def confirm_topup(ref_code, txid):
    """ຢືນຢັນການເຕີມເງິນ"""
    payload = {'ref': ref_code, 'txId': txid}
    response = _make_request('POST', '/api/transactions/confirm-payment', payload)
    return response.json() if response and 'application/json' in response.headers.get('Content-Type', '') else None