# -*- coding: utf-8 -*-
# FINAL COMPLETE VERSION
import logging
import mysql.connector
import json
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

(SELECT_ITEM, CONFIRM_PURCHASE, EXECUTE_PURCHASE) = range(3)
(GET_AMOUNT, GET_TXID) = range(3, 5)


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
            welcome_text = f"ສະບາຍດີ, {user.first_name}!\nຍິນດີຕ້ອນຮັບສູ່ Smile Panel. ບັນຊີຂອງທ່ານຖືກສ້າງສຳເລັດແລ້ວ."
        else:
            welcome_text = f"ຍິນດີຕ້ອນຮັບກັບມາ, {user.first_name}!"
        keyboard = [['🛒 ຮ້ານຄ້າ (Store)', '💰 ເຕີມເງິນ (Top-up)'], ['💵 ຍອດເງິນ (Balance)', '📜 ປະຫວັດ (History)']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    except mysql.connector.Error as err:
        logging.error(f"Database Error on start: {err}")
        await update.message.reply_text("ເກີດຂໍ້ຜິດພາດໃນການເຊື່ອມຕໍ່ຖານຂໍ້ມູນ.")
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
            reply_text = f"💵 ຍອດເງິນຄົງເຫຼືອຂອງທ່ານແມ່ນ:\n\n<b>${result[0]:.4f} USD</b>"
        else:
            reply_text = "ບໍ່ພົບບັນຊີຂອງທ່ານ. ກະລຸນາພິມ /start."
        await update.message.reply_text(reply_text, parse_mode='HTML')
    except mysql.connector.Error as err:
        logging.error(f"Database Error on balance check: {err}")
        await update.message.reply_text("ເກີດຂໍ້ຜິດພາດໃນການກວດສອບຍອດເງິນ.")
    finally:
        if db_connection and db_connection.is_connected():
            db_connection.close()

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    db_connection = None
    try:
        db_connection = mysql.connector.connect(**config.DB_CONFIG)
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
        user = cursor.fetchone()
        if not user:
            await update.message.reply_text("ບໍ່ພົບບັນຊີຂອງທ່ານ. ກະລຸນາພິມ /start.")
            return
        cursor.execute("SELECT * FROM transactions WHERE user_id = %s ORDER BY created_at DESC LIMIT 10", (user['id'],))
        transactions = cursor.fetchall()
        if not transactions:
            await update.message.reply_text("📜 ທ່ານຍັງບໍ່ມີປະຫວັດທຸລະກຳ.")
            return
        reply_text = "📜 **ປະຫວັດທຸລະກຳ 10 ລາຍການຫຼ້າສຸດ:**\n\n"
        for tx in transactions:
            date = tx['created_at'].strftime('%Y-%m-%d %H:%M')
            amount = float(tx['amount'])
            tx_type = tx['type'].capitalize()
            if tx_type == 'Topup': tx_type = 'ເຕີມເງິນ'
            elif tx_type == 'Purchase': tx_type = 'ສັ່ງຊື້'
            elif tx_type == 'Adjustment': tx_type = 'Admin ປັບຍອດ'
            if amount > 0:
                reply_text += f"🗓️ {date}\n✅ {tx_type}: `+${amount:.4f}`\n\n"
            else:
                reply_text += f"🗓️ {date}\n🛒 {tx_type}: `-${abs(amount):.4f}`\n\n"
        await update.message.reply_text(reply_text, parse_mode='Markdown')
    except mysql.connector.Error as err:
        logging.error(f"Database Error on history: {err}")
        await update.message.reply_text("ເກີດຂໍ້ຜິດພາດໃນການໂຫຼດປະຫວັດ.")
    finally:
        if db_connection and db_connection.is_connected():
            db_connection.close()

async def store_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    db_connection = None
    try:
        db_connection = mysql.connector.connect(**config.DB_CONFIG)
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute("SELECT id, external_id, name FROM products WHERE is_active = 1 ORDER BY name ASC")
        products = cursor.fetchall()
        if not products:
            await update.message.reply_text("ຂໍອະໄພ, ຕອນນີ້ຍັງບໍ່ມີສິນຄ້າວາງຂາຍ.")
            return ConversationHandler.END
        keyboard = [[InlineKeyboardButton(p['name'], callback_data=f"product_{p['external_id']}")] for p in products]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("ກະລຸນາເລືອກໝວດໝູ່ສິນຄ້າ:", reply_markup=reply_markup)
        return SELECT_ITEM
    finally:
        if db_connection and db_connection.is_connected(): db_connection.close()

async def select_product_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    product_external_id = query.data.split('_')[1]
    await query.edit_message_text("ກຳລັງໂຫຼດລາຄາຫຼ້າສຸດ...")
    db_connection = None
    try:
        real_time_items = jc_service.getProductDetails(product_external_id)
        if not real_time_items:
            await query.edit_message_text("ຂໍອະໄພ, ບໍ່ສາມາດດຶງຂໍ້ມູນລາຄາສິນຄ້າໄດ້.")
            return ConversationHandler.END
        db_connection = mysql.connector.connect(**config.DB_CONFIG)
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute("SELECT id, external_item_id, name, markup_type, markup_value FROM product_items WHERE product_id = (SELECT id FROM products WHERE external_id = %s) AND is_active = 1", (product_external_id,))
        db_items = cursor.fetchall()
        if not db_items:
            await query.edit_message_text("ຂໍອະໄພ, ບໍ່ມີແພັກເກັດສຳລັບສິນຄ້ານີ້.")
            return ConversationHandler.END
        keyboard = []
        real_time_prices = {item['item_id']: item['base_price'] for item in real_time_items}
        for item in db_items:
            cost_price = real_time_prices.get(item['external_item_id'])
            if cost_price is None: continue
            selling_price = float(cost_price)
            if item['markup_type'] == 'percentage':
                selling_price += selling_price * (float(item['markup_value']) / 100)
            else:
                selling_price += float(item['markup_value'])
            button_text = f"{item['name']} - ${selling_price:.4f}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"item_{item['id']}")])
        if not keyboard:
             await query.edit_message_text("ຂໍອະໄພ, ບໍ່ສາມາດຄຳນວນລາຄາສິນຄ້າໄດ້.")
             return ConversationHandler.END
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("ກະລຸນາເລືອກແພັກເກັດ:", reply_markup=reply_markup)
        return CONFIRM_PURCHASE
    except Exception as e:
        logging.error(f"Error in select_product_item: {e}")
        await query.edit_message_text("ເກີດຂໍ້ຜິດພາດໃນການໂຫຼດລາຍການ.")
        return ConversationHandler.END
    finally:
        if db_connection and db_connection.is_connected(): db_connection.close()

async def confirm_purchase_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    item_id = int(query.data.split('_')[1])
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
        cost_price = next((i['base_price'] for i in real_time_item_data if i['item_id'] == item['external_item_id']), float(item['base_price']))
        selling_price = float(cost_price)
        if item['markup_type'] == 'percentage':
            selling_price += selling_price * (float(item['markup_value']) / 100)
        else:
            selling_price += float(item['markup_value'])
        if float(user['balance']) < selling_price:
            await query.edit_message_text(f"❌ ຍອດເງິນບໍ່ພຽງພໍ! ທ່ານຕ້ອງການ ${selling_price:.4f}, ແຕ່ມີພຽງ ${float(user['balance']):.4f}.")
            return ConversationHandler.END
        keyboard = [[InlineKeyboardButton("✅ ຢືນຢັນການຊື້", callback_data=f"buy_{item_id}"), InlineKeyboardButton("❌ ຍົກເລີກ", callback_data="cancel_buy")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"ທ່ານຕ້ອງການຊື້ '{item['name']}' ໃນລາຄາ ${selling_price:.4f} USD ແທ້ບໍ່?", reply_markup=reply_markup)
        return EXECUTE_PURCHASE
    finally:
        if db_connection and db_connection.is_connected(): db_connection.close()

async def execute_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("ກຳລັງດຳເນີນການສັ່ງຊື້...")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    item_id = int(query.data.split('_')[1])
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
        cost_price = next((i['base_price'] for i in real_time_item_data if i['item_id'] == item['external_item_id']), float(item['base_price']))
        selling_price = float(cost_price)
        if item['markup_type'] == 'percentage':
            selling_price += selling_price * (float(item['markup_value']) / 100)
        else:
            selling_price += float(item['markup_value'])
        if float(user['balance']) < selling_price:
            await query.edit_message_text("❌ ຂໍອະໄພ, ຍອດເງິນຂອງທ່ານບໍ່ພຽງພໍແລ້ວ.")
            db_connection.rollback()
            return ConversationHandler.END
        items_for_api = [{'productId': item['product_external_id'],'itemsId': item['external_item_id'],'itemsPid': '1','quantity': 1}]
        order_result = jc_service.createOrder(items_for_api, selling_price)
        if not order_result or not order_result.get('success'):
            await query.edit_message_text(f"❌ ການສັ່ງຊື້ລົ້ມເຫຼວ: {order_result.get('message', 'Unknown error')}")
            db_connection.rollback()
            return ConversationHandler.END
        
        ref_code = order_result['data']['ref']
        await query.edit_message_text("ສັ່ງຊື້ສຳເລັດ, ກຳລັງດຶງ Voucher Code...")
        voucher_code = jc_service.getOrderDetailCode(ref_code)
        
        balance_before = float(user['balance'])
        balance_after = balance_before - selling_price
        cursor.execute("UPDATE users SET balance = %s WHERE id = %s", (balance_after, user['id']))
        cursor.execute("INSERT INTO transactions (user_id, ref_code, type, amount, status, details, balance_before, balance_after) VALUES (%s, %s, 'purchase', %s, 'success', %s, %s, %s)",(user['id'], ref_code, -selling_price, json.dumps(order_result['data']), balance_before, balance_after))
        db_connection.commit()

        await query.edit_message_text(f"✅ ການສັ່ງຊື້ສຳເລັດ!\n\n📜 Voucher Code:\n<code>{voucher_code}</code>\n\n💵 ຍອດເງິນຄົງເຫຼືອ: ${balance_after:.4f} USD", parse_mode='HTML')
        return ConversationHandler.END
    except Exception as e:
        if db_connection and db_connection.is_connected(): db_connection.rollback()
        logging.error(f"Error during purchase execution: {e}")
        await query.edit_message_text("ເກີດຂໍ້ຜິດພາດຮ້າຍແຮງຂະນະສັ່ງຊື້.")
        return ConversationHandler.END
    finally:
        if db_connection and db_connection.is_connected(): db_connection.close()

# --- Top-up Conversation ---
async def topup_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("ກະລຸນາໃສ່ຈຳນວນເງິນ (USD) ທີ່ທ່ານຕ້ອງການເຕີມ:")
    return GET_AMOUNT

async def get_amount_and_initiate_topup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        amount = float(update.message.text)
        if amount <= 0: raise ValueError()
    except ValueError:
        await update.message.reply_text("ຈຳນວນເງິນບໍ່ຖືກຕ້ອງ, ກະລຸນາລອງໃໝ່.")
        return GET_AMOUNT
    context.user_data['topup_original_amount'] = amount
    await update.message.reply_text("ກຳລັງສ້າງລາຍການເຕີມເງິນ...")
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
                await update.message.reply_text("ເກີດຂໍ້ຜິດພາດ: ບໍ່ພົບບັນຊີຂອງທ່ານ.")
                return ConversationHandler.END
            user_id = user_record[0]
            details_json = json.dumps(details)
            cursor.execute("INSERT INTO transactions (user_id, ref_code, type, amount, status, details) VALUES (%s, %s, 'topup', %s, 'pending', %s)", (user_id, details['ref'], details['amount'], details_json))
            db_connection.commit()
        except mysql.connector.Error as err:
            logging.error(f"Database error on initiate_topup: {err}")
            await update.message.reply_text("ເກີດຂໍ້ຜິດພາດໃນການບັນທຶກຂໍ້ມູນ.")
            return ConversationHandler.END
        finally:
            if db_connection and db_connection.is_connected(): db_connection.close()
        reply_text = (f"✅ ສ້າງລາຍການສຳເລັດ!\nກະລຸນາໂອນເງິນຕາມລາຍລະອຽດລຸ່ມນີ້:\n\n<b>ຈຳນວນທີ່ຕ້ອງໂອນ:</b> {details['amount']} {details['currency']}\n<b>ເຄືອຂ່າຍ:</b> {details['network']}\n<b>ທີ່ຢູ່ກະເປົາ (Address):</b> <code>{details['wallet_address']}</code>\n\n⚠️ ເມື່ອໂອນສຳເລັດ, ກະລຸນາສົ່ງ TxID ມາທີ່ນີ້ເພື່ອຢືນຢັນ.")
        await update.message.reply_text(reply_text, parse_mode='HTML')
        return GET_TXID
    else:
        await update.message.reply_text("❌ ເກີດຂໍ້ຜິດພາດ, ບໍ່ສາມາດສ້າງລາຍການເຕີມເງິນໄດ້.")
        return ConversationHandler.END

async def get_txid_and_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    txid = update.message.text
    ref_code = context.user_data.get('topup_ref')
    original_amount = context.user_data.get('topup_original_amount', 0)
    if not ref_code or original_amount == 0:
        await update.message.reply_text("ເກີດຂໍ້ຜິດພາດ, ບໍ່ພົບລາຍການເຕີມເງິນ. ກະລຸນາເລີ່ມໃໝ່.")
        return ConversationHandler.END
    await update.message.reply_text("ໄດ້ຮັບ TxID ແລ້ວ. ກຳລັງສົ່ງໄປຢືນຢັນ...\n⏳ ຂັ້ນຕອນນີ້ອາດຈະໃຊ້ເວລາ 30-60 ວິນາທີ...")
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
            balance_after = float(balance_before) + float(amount_to_credit)
            cursor.execute("UPDATE users SET balance = %s WHERE id = %s", (balance_after, user_id))
            confirmation_json = json.dumps(confirmation)
            cursor.execute("UPDATE transactions SET status = 'success', details = %s, balance_before = %s, balance_after = %s WHERE ref_code = %s", (confirmation_json, balance_before, balance_after, ref_code))
            db_connection.commit()
            await update.message.reply_text(f"✅ ຢືນຢັນການເຕີມເງິນສຳເລັດ!\nຍອດເງິນຂອງທ່ານໄດ້ເພີ່ມຂຶ້ນ ${amount_to_credit:.4f} USD.\nຍອດເງິນປັດຈຸບັນແມ່ນ ${balance_after:.4f} USD")
        except mysql.connector.Error as err:
            logging.error(f"Database Error on confirm: {err}")
            await update.message.reply_text("ຢືນຢັນສຳເລັດ, ແຕ່ເກີດຂໍ້ຜິດພາດໃນການອັບເດດຍອດເງິນ.")
        finally:
            if db_connection and db_connection.is_connected(): db_connection.close()
        context.user_data.clear()
        return ConversationHandler.END
    else:
        await update.message.reply_text("❌ ການຢືນຢັນຍັງບໍ່ສຳເລັດ.\nກະລຸນາລໍຖ້າອີກ 1-2 ນາທີ ແລ້ວລອງ **ສົ່ງ TxID ເດີມຊ້ຳອີກຄັ້ງ**,\nຫຼື ພິມ /cancel ເພື່ອຍົກເລີກ.")
        return GET_TXID

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ຍົກເລີກການສົນທະນາ"""
    context.user_data.clear()
    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text("ຍົກເລີກການສັ່ງຊື້ແລ້ວ.")
    else:
        await update.message.reply_text("ຍົກເລີກລາຍການແລ້ວ.")
    return ConversationHandler.END


def main():
    """ຟັງຊັນຫຼັກໃນການເລີ່ມຕົ້ນບອທ"""
    application = Application.builder().token(config.TELEGRAM_TOKEN).build()
    
    topup_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^💰 ເຕີມເງິນ \(Top-up\)$'), topup_start)],
        states={
            GET_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_amount_and_initiate_topup)],
            GET_TXID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_txid_and_confirm)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    store_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^🛒 ຮ້ານຄ້າ \(Store\)$'), store_start)],
        states={
            SELECT_ITEM: [CallbackQueryHandler(select_product_item, pattern='^product_')],
            CONFIRM_PURCHASE: [CallbackQueryHandler(confirm_purchase_prompt, pattern='^item_')],
            EXECUTE_PURCHASE: [CallbackQueryHandler(execute_purchase, pattern='^buy_')]
        },
        fallbacks=[CommandHandler('cancel', cancel), CallbackQueryHandler(cancel, pattern='^cancel_buy$')],
    )

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.Regex('^💵 ຍອດເງິນ \(Balance\)$'), balance_command))
    application.add_handler(MessageHandler(filters.Regex('^📜 ປະຫວັດ \(History\)$'), history_command))
    application.add_handler(topup_conv_handler)
    application.add_handler(store_conv_handler)
    
    logging.info("Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()