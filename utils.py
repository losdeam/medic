import uuid
from pymongo import MongoClient
# 在 utils.py 中添加（复用性更高）
import streamlit as st
def show_remind_alert(message):
    """显示可关闭的重点提示弹窗"""
    st.toast(message, icon="⭐")
def show_success_alert(message):
    """显示可关闭的成功弹窗"""
    st.toast(message, icon="✅")
# 生成唯一的 ID
def generate_id(prefix):
    return f"{prefix}_{str(uuid.uuid4())[:8]}"

# 连接 MongoDB 数据库
def create_connection():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['medical_records']
    return db

# 初始化 MongoDB 集合
def init_tables():
    global patients
    global doctors
    global records
    db = create_connection()
    # 创建患者集合
    patients = db['patients']
    # 创建医师集合
    doctors = db['doctors']
    # 创建病例集合
    records = db['records']
    return db
# 初始化数据库表
# def init_tables():
#     conn = create_connection()
#     c = conn.cursor()
    
#     # 创建患者表
#     c.execute('''
#     CREATE TABLE IF NOT EXISTS patients (
#         patient_id TEXT PRIMARY KEY,
#         name TEXT NOT NULL,
#         gender TEXT NOT NULL,
#         age INTEGER NOT NULL,
#         phone TEXT
#     )
#     ''')
    
#     # 创建医师表
#     c.execute('''
#     CREATE TABLE IF NOT EXISTS doctors (
#         doctor_id TEXT PRIMARY KEY,
#         name TEXT NOT NULL,
#         department TEXT NOT NULL,
#         title TEXT,
#         phone TEXT,
#         email TEXT
#     )
#     ''')
    
#     # 创建病例表，关联患者ID和医师ID
#     c.execute('''
#     CREATE TABLE IF NOT EXISTS records (
#         record_id INTEGER PRIMARY KEY AUTOINCREMENT,
#         patient_id TEXT NOT NULL,
#         doctor_id TEXT NOT NULL,
#         visit_date TEXT NOT NULL,
#         department TEXT NOT NULL,
#         symptoms TEXT NOT NULL,
#         diagnosis TEXT NOT NULL,
#         treatment TEXT,
#         cost TEXT,
#         notes TEXT,
#         FOREIGN KEY (patient_id) REFERENCES patients (patient_id),
#         FOREIGN KEY (doctor_id) REFERENCES doctors (doctor_id)
#     )
#     ''')
    
#     conn.commit()
#     conn.close()


