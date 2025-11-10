# -*- coding: utf-8 -*-
# FINAL COMPLETE VERSION: QUANTITY + FREE NAV + UNLIMITED PRODUCT CLICK
import logging
import mysql.connector
import json
from decimal import Decimal, ROUND_HALF_UP 
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler,
)

import config
import jc_service

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

(SELECT_ITEM, SELECT_QUANTITY, CONFIRM_PURCHASE, EXECUTE_PURCHASE) = range(4)
(GET_AMOUNT, GET_TXID) = range(4, 6)

# --- Common Filters ---
FILTER_STORE = filters.Regex('^🛒 ร้านค้า \(Store\)$')
FILTER_TOPUP = filters.Regex('^💰 เติมเงิน \(Top-up\)$')
FILTER_BALANCE = filters.Regex('^💵 ยอดเงิน \(Balance\)$')
FILTER_HISTORY = filters.Regex('^📜 ประวัติ \(History\)$')

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    telegram_id = user.id
    username = user.username or f"user_{telegram_id}"
    db_connection = None
    try:
        db_connection = mysql.connector.connect(**config.DB_CONFIG)
        cursor = db_connection.cursor()
        cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (telegram_id,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO users (telegram_id, username, password, role) VALUES (%s, %s, %s, %s)",(telegram_id, username, 'telegram_user', 'member'))
            db_connection.commit()
            welcome_text = f"สวัสดี, {user.first_name}!\nยินดีต้อนรับสู่ Smile Panel. บัญชีของคุณถูกสร้างสำเร็จแล้ว"
        else:
            welcome_text = f"ยินดีต้อนรับกลับมา, {user.first_name}!"
        keyboard = [['🛒 ร้านค้า (Store)', '💰 เติมเงิน (Top-up)'], ['💵 ยอดเงิน (Balance)', '📜 ประวัติ (History)']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    except mysql.connector.Error as err:
        logging.error(f"Database Error on start: {err}")
        await update.message.reply_text("เกิดข้อผิดพลาดในการเชื่อมต่อฐานข้อมูล")
    finally:
        if db_connection and db_connection.is_connected():
            db_connection.close()

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    db_connection = None
    try:
        db_connection = mysql.connector.connect(**config.DB_CONFIG)
        cursor = db_connection.cursor()
        cursor.execute("SELECT balance FROM users WHERE telegram_id = %s", (telegram_id,))
        result = cursor.fetchone()
        if result:
            balance = Decimal(str(result[0])).quantize(Decimal('0.0001'))
            reply_text = f"💵 ยอดเงินคงเหลือของคุณคือ:\n\n<b>${balance} USD</b>"
        else:
            reply_text = "ไม่พบบัญชีของคุณ กรุณาพิมพ์ /start"
        await update.message.reply_text(reply_text, parse_mode='HTML')
    except mysql.connector.Error as err:
        logging.error(f"Database Error on balance check: {err}")
        await update.message.reply_text("เกิดข้อผิดพลาดในการตรวจสอบยอดเงิน")
    finally:
        if db_connection and db_connection.is_connected():
            db_connection.close()
    return ConversationHandler.END

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    db_connection = None
    try:
        db_connection = mysql.connector.connect(**config.DB_CONFIG)
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
        user = cursor.fetchone()
        if not user:
            await update.message.reply_text("ไม่พบบัญชีของคุณ กรุณาพิมพ์ /start")
            return ConversationHandler.END
        cursor.execute("SELECT * FROM transactions WHERE user_id = %s ORDER BY created_at DESC LIMIT 10", (user['id'],))
        transactions = cursor.fetchall()
        if not transactions:
            await update.message.reply_text("📜 คุณยังไม่มีประวัติการทำธุรกรรม")
            return ConversationHandler.END
        reply_text = "📜 **ປະຫວັດທຸລະກຳ 10 ລາຍການຫຼ້າສຸດ:**\n\n"
        for tx in transactions:
            date = tx['created_at'].strftime('%Y-%m-%d %H:%M')
            amount = Decimal(str(tx['amount'])).quantize(Decimal('0.0001'))
            tx_type = tx['type'].capitalize()
            if tx_type == 'Topup': tx_type = 'เติมเงิน'
            elif tx_type == 'Purchase': tx_type = 'สั่งซื้อ'
            elif tx_type == 'Adjustment': tx_type = 'Admin ปรับยอด'
            if amount > 0:
                reply_text += f"🗓️ {date}\n✅ {tx_type}: `+${amount}`\n\n"
            else:
                reply_text += f"🗓️ {date}\n🛒 {tx_type}: `-${abs(amount)}`\n\n"
        await update.message.reply_text(reply_text, parse_mode='Markdown')
    except mysql.connector.Error as err:
        logging.error(f"Database Error on history: {err}")
        await update.message.reply_text("เกิดข้อผิดพลาดในการโหลดประวัติ")
    finally:
        if db_connection and db_connection.is_connected():
            db_connection.close()
    return ConversationHandler.END

async def store_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # เคลียร์ state เก่าถ้ามี
    context.user_data.clear()
    db_connection = None
    try:
        db_connection = mysql.connector.connect(**config.DB_CONFIG)
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute("SELECT id, external_id, name FROM products WHERE is_active = 1 ORDER BY name ASC")
        products = cursor.fetchall()
        if not products:
            await update.message.reply_text("ขออภัย, ตอนนี้ยังไม่มีสินค้าวางขาย")
            return ConversationHandler.END
        keyboard = [[InlineKeyboardButton(p['name'], callback_data=f"product_{p['external_id']}")] for p in products]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("กรุณาเลือกหมวดหมู่สินค้า:", reply_markup=reply_markup)
        return SELECT_ITEM
    except Exception as e:
        logging.error(f"Error in store_start: {e}")
        return ConversationHandler.END
    finally:
        if db_connection and db_connection.is_connected(): db_connection.close()

async def select_product_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    product_external_id = query.data.split('_')[1]
    
    # ถ้ามาจากการกดเปลี่ยนหมวดสินค้า, ให้แก้ไขข้อความเดิมแทนที่จะส่งใหม่
    try:
        await query.edit_message_text("กำลังโหลดราคาล่าสุด...")
    except Exception:
        # กรณีข้อความเก่าแก้ไขไม่ได้ (อาจจะเกิดขึ้นได้น้อย)
        pass

    db_connection = None
    try:
        real_time_items = jc_service.getProductDetails(product_external_id)
        if not real_time_items:
            await query.edit_message_text("ขออภัย, ไม่สามารถดึงข้อมูลราคาสินค้าได้")
            return ConversationHandler.END
        
        db_connection = mysql.connector.connect(**config.DB_CONFIG)
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute("SELECT id, external_item_id, name, markup_type, markup_value FROM product_items WHERE product_id = (SELECT id FROM products WHERE external_id = %s) AND is_active = 1", (product_external_id,))
        db_items = cursor.fetchall()

        if not db_items:
            await query.edit_message_text("ขออภัย, ไม่มีแพ็กเกจสำหรับสินค้านี้")
            return ConversationHandler.END
        keyboard = []
        real_time_prices = {item['item_id']: item['base_price'] for item in real_time_items}
        for item in db_items:
            cost_price = real_time_prices.get(item['external_item_id'])
            if cost_price is None: 
                continue
            selling_price = Decimal(str(cost_price))
            if item['markup_type'] == 'percentage':
                selling_price += selling_price * (Decimal(str(item['markup_value'])) / Decimal('100'))
            else:
                selling_price += Decimal(str(item['markup_value']))
            selling_price_formatted = selling_price.quantize(Decimal('0.0001'))
            button_text = f"{item['name']} - ${selling_price_formatted}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"item_{item['id']}")])
        
        if not keyboard:
             await query.edit_message_text("ขออภัย, คำนวณราคาไม่ได้")
             return ConversationHandler.END
        
        # เพิ่มปุ่มกลับไปหน้าเลือกหมวด (Optional, แต่ใส่ไว้ก็ดี)
        # keyboard.append([InlineKeyboardButton("🔙 กลับ", callback_data="back_to_store")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("กรุณาเลือกแพ็กเกจที่ต้องการซื้อ:", reply_markup=reply_markup)
        # CHANGED: ไปที่ State SELECT_QUANTITY แต่เรายังอยู่ในหน้าเลือก item,
        # ดังนั้น return SELECT_QUANTITY เพื่อรอการกด item_
        return SELECT_QUANTITY 
    except Exception as e:
        logging.error(f"Error in select_product_item: {e}")
        try:
            await query.edit_message_text("เกิดข้อผิดพลาดโหลดรายการ.")
        except:
            pass
        return ConversationHandler.END
    finally:
        if db_connection and db_connection.is_connected(): db_connection.close()

async def ask_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    item_id = int(query.data.split('_')[1])
    context.user_data['selected_item_id'] = item_id
    
    keyboard = [
        [InlineKeyboardButton("1", callback_data="qty_1"), InlineKeyboardButton("2", callback_data="qty_2"), InlineKeyboardButton("3", callback_data="qty_3")],
        [InlineKeyboardButton("4", callback_data="qty_4"), InlineKeyboardButton("5", callback_data="qty_5"), InlineKeyboardButton("10", callback_data="qty_10")],
        [InlineKeyboardButton("❌ ยกเลิก", callback_data="cancel_buy")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("กรุณาเลือกจำนวนที่ต้องการซื้อ:", reply_markup=reply_markup)
    return CONFIRM_PURCHASE

async def confirm_purchase_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    quantity = int(query.data.split('_')[1])
    item_id = context.user_data.get('selected_item_id')
    context.user_data['selected_quantity'] = quantity

    if not item_id:
        await query.edit_message_text("เกิดข้อผิดพลาด: ไม่พบข้อมูลรายการนี้ กรุณาลองใหม่อีกครั้ง")
        return ConversationHandler.END

    telegram_id = query.from_user.id
    db_connection = None
    try:
        db_connection = mysql.connector.connect(**config.DB_CONFIG)
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute("SELECT balance FROM users WHERE telegram_id = %s", (telegram_id,))
        user = cursor.fetchone()
        cursor.execute("SELECT pi.*, p.external_id FROM products p JOIN product_items pi ON p.id = pi.product_id WHERE pi.id = %s", (item_id,))
        item = cursor.fetchone()
        
        real_time_item_data = jc_service.getProductDetails(item['external_id'])
        cost_price = next((i['base_price'] for i in real_time_item_data if i['item_id'] == item['external_item_id']), '0.0')
        
        unit_price = Decimal(str(cost_price))
        if item['markup_type'] == 'percentage':
            unit_price += unit_price * (Decimal(str(item['markup_value'])) / Decimal('100'))
        else:
            unit_price += Decimal(str(item['markup_value']))
        unit_price = unit_price.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
        
        total_price = (unit_price * Decimal(quantity)).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
        user_balance = Decimal(str(user['balance']))
        
        if user_balance < total_price:
            await query.edit_message_text(f"❌ ยอดเงินในบัญชีของคุณไม่เพียงพอ! คุณต้องการจ่าย ${total_price} สำหรับ {quantity} รายการนี้, แต่มีเพียง ${user_balance.quantize(Decimal('0.0001'))}")
            return ConversationHandler.END
            
        keyboard = [[InlineKeyboardButton("✅ ยืนยันการสั่งซื้อ", callback_data="confirm_buy"), InlineKeyboardButton("❌ ยกเลิกการสั่งซื้อ", callback_data="cancel_buy")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"ยืนยันการสั่งซื้อ:\n\n📦 สินค้า: {item['name']}\n🔢 จำนวน: {quantity}\n💰 ราคารวม: ${total_price} USD\n\nต้องการดำเนินการหรือไม่?", reply_markup=reply_markup)
        return EXECUTE_PURCHASE
    except Exception as e:
        logging.error(f"Error in confirm_purchase_prompt: {e}")
        await query.edit_message_text("เกิดข้อผิดพลาดในการคำนวณราคา กรุณาลองใหม่อีกครั้ง")
        return ConversationHandler.END
    finally:
        if db_connection and db_connection.is_connected(): db_connection.close()

async def execute_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'cancel_buy':
        await query.edit_message_text("ยกเลิกการสั่งซื้อแล้ว")
        return ConversationHandler.END

    await query.edit_message_text("กำลังดำเนินการสั่งซื้อ...")
    item_id = context.user_data.get('selected_item_id')
    quantity = context.user_data.get('selected_quantity', 1)

    telegram_id = query.from_user.id
    db_connection = None
    try:
        db_connection = mysql.connector.connect(**config.DB_CONFIG)
        cursor = db_connection.cursor(dictionary=True)
        db_connection.start_transaction()
        cursor.execute("SELECT * FROM users WHERE telegram_id = %s FOR UPDATE", (telegram_id,))
        user = cursor.fetchone()
        cursor.execute("SELECT pi.*, p.external_id as product_external_id FROM product_items pi JOIN products p ON pi.product_id = p.id WHERE pi.id = %s", (item_id,))
        item = cursor.fetchone()
        
        real_time_item_data = jc_service.getProductDetails(item['product_external_id'])
        real_time_details = next((i for i in real_time_item_data if i['item_id'] == item['external_item_id']), None)

        if not real_time_details:
            await query.edit_message_text("❌ ขออภัย, ไม่พบข้อมูลรายการนี้แล้ว กรุณาลองใหม่อีกครั้ง")
            db_connection.rollback()
            return ConversationHandler.END
        
        cost_price = real_time_details['base_price']
        item_pid = real_time_details['item_pid']
        
        unit_price = Decimal(str(cost_price))
        if item['markup_type'] == 'percentage':
            unit_price += unit_price * (Decimal(str(item['markup_value'])) / Decimal('100'))
        else:
            unit_price += Decimal(str(item['markup_value']))
        unit_price = unit_price.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
        
        total_selling_price = (unit_price * Decimal(quantity)).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
        user_balance = Decimal(str(user['balance']))

        if user_balance < total_selling_price:
            await query.edit_message_text("❌ ขออภัย, ยอดเงินของคุณไม่เพียงพอ")
            db_connection.rollback()
            return ConversationHandler.END
            
        items_for_api = [{'productId': item['product_external_id'],'itemsId': item['external_item_id'],'itemsPid': item_pid,'quantity': quantity}]
        order_result = jc_service.createOrder(items_for_api, total_selling_price)

        if not order_result:
            await query.edit_message_text("❌ การสั่งซื้อล้มเหลว\n\n(สาเหตุที่เป็นไปได้: ยอดเงินในบัญชีหลักในระบบอาจหมด กรุณาติดต่อแอดมิน paoxayyasan)")
            db_connection.rollback()
            return ConversationHandler.END
        
        if not order_result.get('success'):
            await query.edit_message_text(f"❌ การสั่งซื้อล้มเหลว: {order_result.get('message', 'Unknown error')}")
            db_connection.rollback()
            return ConversationHandler.END
        
        ref_code = order_result['data']['ref']
        await query.edit_message_text("สั่งซื้อสำเร็จ! กำลังเตรียม Voucher Code...")
        voucher_code = jc_service.getOrderDetailCode(ref_code)
        
        balance_before = user_balance
        balance_after = balance_before - total_selling_price
        cursor.execute("UPDATE users SET balance = %s WHERE id = %s", (balance_after, user['id']))
        cursor.execute("INSERT INTO transactions (user_id, ref_code, type, amount, status, details, balance_before, balance_after) VALUES (%s, %s, 'purchase', %s, 'success', %s, %s, %s)",(user['id'], ref_code, -total_selling_price, json.dumps(order_result['data']), balance_before, balance_after))
        db_connection.commit()

        await query.edit_message_text(f"✅ การสั่งซื้อสำเร็จ!\n\n📦 สินค้า: {item['name']} (x{quantity})\n📜 Voucher Code:\n<code>{voucher_code}</code>\n\n💵 ยอดเงินปัจจุบัน: ${balance_after.quantize(Decimal('0.0001'))} USD", parse_mode='HTML')
        return ConversationHandler.END
    except Exception as e:
        if db_connection and db_connection.is_connected(): db_connection.rollback()
        logging.error(f"Error during purchase execution: {e}")
        await query.edit_message_text("เกิดข้อผิดพลาดร้ายแรงขณะทำการสั่งซื้อ")
        return ConversationHandler.END
    finally:
        if db_connection and db_connection.is_connected(): db_connection.close()

async def topup_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("กรุณาพิมพ์จำนวนเงิน (USD) ที่คุณต้องการโอนเข้าบัญชี Smile one:")
    return GET_AMOUNT

async def get_amount_and_initiate_topup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        amount = float(update.message.text)
        if amount <= 0: raise ValueError()
    except ValueError:
        await update.message.reply_text("จำนวนเงินไม่ถูกต้อง กรุณาพิมพ์อีกครั้ง")
        return GET_AMOUNT
    context.user_data['topup_original_amount'] = amount
    await update.message.reply_text("กำลังสร้างรายการเติมเงิน...")
    details = jc_service.initiate_topup(amount)
    if details:
        context.user_data['topup_ref'] = details['ref']
        telegram_id = update.effective_user.id
        db_connection = None
        try:
            db_connection = mysql.connector.connect(**config.DB_CONFIG)
            cursor = db_connection.cursor()
            cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
            user_record = cursor.fetchone()
            if not user_record:
                await update.message.reply_text("เกิดข้อผิดพลาด: ไม่พบบัญชีของคุณในระบบ")
                return ConversationHandler.END
            user_id = user_record[0]
            details_json = json.dumps(details)
            cursor.execute("INSERT INTO transactions (user_id, ref_code, type, amount, status, details) VALUES (%s, %s, 'topup', %s, 'pending', %s)", (user_id, details['ref'], details['amount'], details_json))
            db_connection.commit()
        except mysql.connector.Error as err:
            logging.error(f"Database error on initiate_topup: {err}")
            await update.message.reply_text("เกิดข้อผิดพลาดในการบันทึกข้อมูล")
            return ConversationHandler.END
        finally:
            if db_connection and db_connection.is_connected(): db_connection.close()
        reply_text = (f"✅ สร้างรายการสำเร็จ!\nกรุณาโอนเงินตามรายละเอียดด้านล่างนี้:\n\n<b>จำนวนที่ต้องโอน:</b> {details['amount']} {details['currency']}\n<b>เครือข่าย:</b> {details['network']}\n<b>ที่อยู่กระเป๋า (Address):</b> <code>{details['wallet_address']}</code>\n\n⚠️ เมื่อโอนสำเร็จ, กรุณาส่ง TxID มาที่นี่เพื่อยืนยันการโอนเงิน")
        await update.message.reply_text(reply_text, parse_mode='HTML')
        return GET_TXID
    else:
        await update.message.reply_text("❌ เกิดข้อผิดพลาด ไม่สามารถสร้างรายการเติมเงินได้")
        return ConversationHandler.END

async def get_txid_and_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    txid = update.message.text
    ref_code = context.user_data.get('topup_ref')
    original_amount = context.user_data.get('topup_original_amount', 0)
    if not ref_code or original_amount == 0:
        await update.message.reply_text("เกิดข้อผิดพลาด ไม่พบรายการเติมเงิน กรุณาเริ่มใหม่อีกครั้ง")
        return ConversationHandler.END
    await update.message.reply_text("ได้รับ TxID แล้ว 🔄 กำลังส่งไปยืนยัน...\n⏳ ขั้นตอนนี้อาจใช้เวลา 30–60 วินาที...")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    confirmation = jc_service.confirm_topup(ref_code, txid)
    if confirmation and confirmation.get('success'):
        amount_to_credit = original_amount
        telegram_id = update.effective_user.id
        db_connection = None
        try:
            db_connection = mysql.connector.connect(**config.DB_CONFIG)
            cursor = db_connection.cursor()
            cursor.execute("SELECT balance, id FROM users WHERE telegram_id = %s FOR UPDATE", (telegram_id,))
            user_record = cursor.fetchone()
            balance_before = user_record[0]
            user_id = user_record[1]
            balance_after = Decimal(str(balance_before)) + Decimal(str(amount_to_credit))
            cursor.execute("UPDATE users SET balance = %s WHERE id = %s", (balance_after, user_id))
            confirmation_json = json.dumps(confirmation)
            cursor.execute("UPDATE transactions SET status = 'success', details = %s, balance_before = %s, balance_after = %s WHERE ref_code = %s", (confirmation_json, balance_before, balance_after, ref_code))
            db_connection.commit()
            await update.message.reply_text(f"✅ ยืนยันการเติมเงินสำเร็จ!\nยอดเงินของคุณได้เพิ่มขึ้นแล้ว ${Decimal(str(amount_to_credit)).quantize(Decimal('0.0001'))} USD\nยอดเงินปัจจุบันคือ ${balance_after.quantize(Decimal('0.0001'))} USD")
        except mysql.connector.Error as err:
            logging.error(f"Database Error on confirm: {err}")
            await update.message.reply_text("ยืนยันสำเร็จ แต่เกิดข้อผิดพลาดในการอัปเดตยอดเงิน")
        finally:
            if db_connection and db_connection.is_connected(): db_connection.close()
        context.user_data.clear()
        return ConversationHandler.END
    else:
        await update.message.reply_text("❌ การยืนยันไม่สำเร็จ\nรอสักครู่อีก 1-2 นาที แล้วส่ง TxID เดิมอีกครั้ง\nหรือพิมพ์ /cancel เพื่อยกเลิกรายการนี้")
        return GET_TXID

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text("ยกเลิกรายการแล้ว")
    else:
        await update.message.reply_text("ยกเลิกรายการแล้ว")
    return ConversationHandler.END

def main():
    application = Application.builder().token(config.TELEGRAM_TOKEN).build()
    
    common_fallbacks = [
        CommandHandler('cancel', cancel),
        MessageHandler(FILTER_STORE, store_start),
        MessageHandler(FILTER_BALANCE, balance_command),
        MessageHandler(FILTER_HISTORY, history_command),
    ]

    topup_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(FILTER_TOPUP, topup_start)],
        states={
            GET_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~FILTER_STORE & ~FILTER_BALANCE & ~FILTER_HISTORY, get_amount_and_initiate_topup)],
            GET_TXID: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~FILTER_STORE & ~FILTER_BALANCE & ~FILTER_HISTORY, get_txid_and_confirm)],
        },
        fallbacks=common_fallbacks,
        allow_reentry=True
    )

    # --- UPDATED: Store Conversation with Unlimited Product Navigation ---
    store_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(FILTER_STORE, store_start)],
        states={
            # ทุกๆ state สามารถรับคำสั่ง `product_` ได้ เพื่อให้กดเปลี่ยนหมวดได้ตลอด
            SELECT_ITEM: [
                CallbackQueryHandler(select_product_item, pattern='^product_')
            ],
            SELECT_QUANTITY: [
                CallbackQueryHandler(ask_quantity, pattern='^item_'),
                CallbackQueryHandler(select_product_item, pattern='^product_') # <-- เพิ่มตรงนี้
            ],
            CONFIRM_PURCHASE: [
                CallbackQueryHandler(confirm_purchase_prompt, pattern='^qty_'),
                CallbackQueryHandler(select_product_item, pattern='^product_') # <-- เพิ่มตรงนี้
            ],
            EXECUTE_PURCHASE: [
                CallbackQueryHandler(execute_purchase, pattern='^(confirm_buy|cancel_buy)$'),
                 # ปกติขั้นตอนนี้ไม่ควรเปลี่ยนสินค้าแล้ว เพราะกำลังซื้อ, แต่ถ้าอยากให้เปลี่ยนได้ก็เพิ่มใส่ได้
                 # แต่ในกรณีนี้มันเป็นเพียง State ชั่วคราวที่รอ confirm/cancel เท่านั้น
                 CallbackQueryHandler(select_product_item, pattern='^product_') # <-- เพิ่มตรงนี้ (Optional, ถ้าอยากให้เปลี่ยนใจวินาทีสุดท้าย)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel), CallbackQueryHandler(cancel, pattern='^cancel_buy$')] + common_fallbacks, # เพิ่ม common_fallbacks ใส่นี้ด้วย
        allow_reentry=True
    )

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(FILTER_BALANCE, balance_command))
    application.add_handler(MessageHandler(FILTER_HISTORY, history_command))
    application.add_handler(topup_conv_handler)
    application.add_handler(store_conv_handler)
    
    logging.info("Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()
