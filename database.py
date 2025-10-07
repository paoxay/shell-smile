# -*- coding: utf-8 -*-
import mysql.connector
import config

def get_db_connection():
    """ສ້າງ ແລະ ສົ່ງຄືນ connection ຂອງຖານຂໍ້ມູນ"""
    try:
        connection = mysql.connector.connect(**config.DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None