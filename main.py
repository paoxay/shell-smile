# -*- coding: utf-8 -*-
# main.py - FastAPI Web Server
import logging
import json
import bcrypt
from fastapi import FastAPI, Request, Response, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

# Import ໂມດູນຈາກໂປຣເຈັກເຮົາ
import database
import jc_service
from config import DB_CONFIG # ເພື່ອໃຊ້ໃນການກວດສອບ password

# --- Models ---
# ໃຊ້ກວດສອບຂໍ້ມູນທີ່ส่งมาจากໜ້າเว็บ
class LoginData(BaseModel):
    username: str
    password: str

class CreateMemberData(BaseModel):
    username: str
    password: str

class AdjustBalanceData(BaseModel):
    user_id: int
    amount: float
    remark: str | None = ""

class UpdateItemData(BaseModel):
    item_id: int
    markup_type: str
    markup_value: float
    is_active: bool

class UpdateProductData(BaseModel):
    product_id: int
    is_active: bool


# --- App Setup ---
app = FastAPI()

# ເພີ່ມ Middleware ສຳລັບจัดการ session (ຄືກັບ $_SESSION ใน PHP)
app.add_middleware(SessionMiddleware, secret_key="a_very_secret_key_change_me")

# --- Authentication ---
def get_current_admin(request: Request):
    if "admin_id" not in request.session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return request.session["admin_id"]

# --- API Endpoints ---

# 1. Authentication Endpoints (แทน login.php, logout.php)
@app.post("/api/login")
async def admin_login(data: LoginData, request: Request):
    conn = None
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s AND role = 'admin'", (data.username,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=401, detail="Username ຫຼື Password ບໍ່ຖືກຕ້ອງ")

        # ໃຊ້ bcrypt ກວດສອບລະຫັດຜ່ານ
        if bcrypt.checkpw(data.password.encode('utf-8'), user['password'].encode('utf-8')):
            request.session['admin_id'] = user['id']
            request.session['admin_username'] = user['username']
            return {"success": True}
        else:
            raise HTTPException(status_code=401, detail="Username ຫຼື Password ບໍ່ຖືກຕ້ອງ")
    finally:
        if conn and conn.is_connected():
            conn.close()

@app.get("/api/logout")
async def admin_logout(request: Request):
    request.session.clear()
    return {"success": True}

# 2. Dashboard Endpoints (แทน dashboard_stats.php, transactions.php)
@app.get("/api/dashboard_stats")
async def get_dashboard_stats(admin_id: int = Depends(get_current_admin)):
    conn = None
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(id) FROM users WHERE role = 'member'")
        total_members = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT SUM(balance) FROM users WHERE role = 'member'")
        total_balance = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'topup' AND status = 'success'")
        total_topup = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'purchase' AND status = 'success'")
        total_purchase = cursor.fetchone()[0] or 0
        
        stats = {
            'total_members': int(total_members),
            'total_balance': float(total_balance),
            'total_topup': float(total_topup),
            'total_purchase': abs(float(total_purchase))
        }
        return {'success': True, 'stats': stats}
    finally:
        if conn and conn.is_connected():
            conn.close()

@app.get("/api/transactions")
async def get_transactions(admin_id: int = Depends(get_current_admin)):
    conn = None
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT t.id, t.type, t.amount, t.status, t.created_at, u.username, t.balance_before, t.balance_after 
            FROM transactions t JOIN users u ON t.user_id = u.id
            ORDER BY t.created_at DESC LIMIT 20
        """
        cursor.execute(query)
        transactions = cursor.fetchall()
        for tx in transactions: # Format datetime for JSON
            tx['created_at'] = tx['created_at'].isoformat()
        return {'success': True, 'transactions': transactions}
    finally:
        if conn and conn.is_connected():
            conn.close()

# 3. Members Endpoints (แทน members.php, create.php, adjust_balance.php)
@app.get("/api/members")
async def list_members(admin_id: int = Depends(get_current_admin)):
    conn = None
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username, balance, created_at FROM users WHERE role = 'member' ORDER BY id DESC")
        members = cursor.fetchall()
        for member in members:
            member['created_at'] = member['created_at'].isoformat()
        return {'success': True, 'members': members}
    finally:
        if conn and conn.is_connected():
            conn.close()

@app.post("/api/members/create")
async def create_member(data: CreateMemberData, admin_id: int = Depends(get_current_admin)):
    conn = None
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username = %s", (data.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="Username ນີ້ມີຜູ້ໃຊ້ງານແລ້ວ")
        
        hashed_password = bcrypt.hashpw(data.password.encode('utf-8'), bcrypt.gensalt())
        
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, 'member')", (data.username, hashed_password.decode('utf-8')))
        conn.commit()
        
        return {'success': True, 'message': 'ສ້າງຜູ້ໃຊ້ໃໝ່ສຳເລັດ!'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn and conn.is_connected():
            conn.close()
            
@app.post("/api/members/adjust_balance")
async def adjust_balance(data: AdjustBalanceData, request: Request, admin_id: int = Depends(get_current_admin)):
    conn = None
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        conn.start_transaction()
        
        cursor.execute("SELECT balance FROM users WHERE id = %s", (data.user_id,))
        balance_before = cursor.fetchone()[0]
        
        balance_after = float(balance_before) + data.amount
        
        cursor.execute("UPDATE users SET balance = %s WHERE id = %s", (balance_after, data.user_id))
        
        details = json.dumps({'remark': data.remark, 'admin_id': request.session.get('admin_id')})
        
        cursor.execute(
            "INSERT INTO transactions (user_id, type, amount, status, details, balance_before, balance_after) VALUES (%s, 'adjustment', %s, 'success', %s, %s, %s)",
            (data.user_id, data.amount, details, balance_before, balance_after)
        )
        conn.commit()
        return {'success': True, 'message': 'ປັບປຸງຍອດເງິນສຳເລັດ'}
    except Exception as e:
        if conn: conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn and conn.is_connected():
            conn.close()

# 4. Products Endpoints (แทน list.php, sync.php, update.php, etc.)
@app.get("/api/products/list")
async def list_products(admin_id: int = Depends(get_current_admin)):
    conn = None
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT p.id as product_id, p.name as product_name, p.external_id as product_external_id, p.is_active as product_is_active,
                   pi.id as item_id, pi.external_item_id, pi.name as item_name, pi.markup_type, pi.markup_value, pi.is_active as item_is_active
            FROM products p
            LEFT JOIN product_items pi ON p.id = pi.product_id
            ORDER BY p.name, pi.id
        """
        cursor.execute(query)
        db_results = cursor.fetchall()
        
        products_from_db = {}
        for row in db_results:
            if row['product_id'] not in products_from_db:
                products_from_db[row['product_id']] = {
                    'product_id': row['product_id'],
                    'product_name': row['product_name'],
                    'product_external_id': row['product_external_id'],
                    'product_is_active': row['product_is_active'],
                    'items': []
                }
            if row['item_id']:
                products_from_db[row['product_id']]['items'].append(row)

        final_products = []
        for product_id, product_data in products_from_db.items():
            real_time_items = jc_service.getProductDetails(product_data['product_external_id'])
            
            updated_items = []
            if real_time_items:
                real_time_prices = {rt_item['item_id']: {'base_price': rt_item['base_price'], 'original_price': rt_item['original_price']} for rt_item in real_time_items}

                for db_item in product_data['items']:
                    if db_item['external_item_id'] in real_time_prices:
                        db_item['base_price'] = real_time_prices[db_item['external_item_id']]['base_price']
                        db_item['original_price'] = real_time_prices[db_item['external_item_id']]['original_price']
                        updated_items.append(db_item)
            product_data['items'] = updated_items
            final_products.append(product_data)
        
        return {'success': True, 'products': final_products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn and conn.is_connected():
            conn.close()

@app.post("/api/products/update")
async def update_product_item(data: UpdateItemData, admin_id: int = Depends(get_current_admin)):
    conn = None
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE product_items SET markup_type = %s, markup_value = %s, is_active = %s WHERE id = %s",
            (data.markup_type, data.markup_value, data.is_active, data.item_id)
        )
        conn.commit()
        return {'success': True, 'message': 'ອັບເດດຂໍ້ມູນສຳເລັດ'}
    finally:
        if conn and conn.is_connected():
            conn.close()

@app.post("/api/products/update_product")
async def update_product_status(data: UpdateProductData, admin_id: int = Depends(get_current_admin)):
    conn = None
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        conn.start_transaction()
        is_active_int = 1 if data.is_active else 0
        cursor.execute("UPDATE products SET is_active = %s WHERE id = %s", (is_active_int, data.product_id))
        cursor.execute("UPDATE product_items SET is_active = %s WHERE product_id = %s", (is_active_int, data.product_id))
        conn.commit()
        return {'success': True, 'message': 'ອັບເດດສະຖານະໝວດສິນຄ້າສຳເລັດ'}
    except Exception as e:
        if conn: conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn and conn.is_connected():
            conn.close()

@app.get("/api/products/sync")
async def sync_products(admin_id: int = Depends(get_current_admin)):
    conn = None
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        products_from_api = jc_service.getStoreProducts()
        
        product_count = 0
        item_count = 0
        conn.start_transaction()
        for product_data in products_from_api:
            # Not implemented in python jc_service, so skipping image_url
            # image_url = product_data.get('image_url', '') 

            cursor.execute("SELECT id FROM products WHERE external_id = %s", (product_data['id'],))
            existing_product = cursor.fetchone()
            
            if existing_product:
                product_id = existing_product[0]
                cursor.execute("UPDATE products SET name = %s WHERE id = %s", (product_data['name'], product_id))
            else:
                cursor.execute("INSERT INTO products (external_id, name) VALUES (%s, %s)", (product_data['id'], product_data['name']))
                product_id = cursor.lastrowid
            product_count += 1

            items_from_api = jc_service.getProductDetails(product_data['id'])
            for item_data in items_from_api:
                # Using INSERT ... ON DUPLICATE KEY UPDATE
                query = """
                    INSERT INTO product_items (product_id, external_item_id, name, base_price) 
                    VALUES (%s, %s, %s, %s) 
                    ON DUPLICATE KEY UPDATE name = VALUES(name), base_price = VALUES(base_price)
                """
                cursor.execute(query, (product_id, item_data['item_id'], item_data['name'], item_data['base_price']))
                item_count += 1
        
        conn.commit()
        return {'success': True, 'message': f"Sync ສຳເລັດ! ພົບ {product_count} ໝວດສິນຄ້າ ແລະ {item_count} ລາຍການ."}
    except Exception as e:
        if conn: conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn and conn.is_connected():
            conn.close()


# --- Serve Static Files ---
# ໃຫ້ FastAPI ເປັນໂຕເປີດໄຟລ໌ໜ້າเว็บ (HTML, JS) ຈາກໂຟເດີ admin
app.mount("/", StaticFiles(directory="admin", html=True), name="admin")