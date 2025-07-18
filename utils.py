import uuid
import sqlite3
# 生成唯一的ID
def generate_id(prefix):
    return f"{prefix}_{str(uuid.uuid4())[:8]}"

# 连接SQLite数据库
def create_connection():
    conn = sqlite3.connect("medical_records.db")
    return conn


# 初始化数据库表
def init_tables():
    conn = create_connection()
    c = conn.cursor()
    
    # 创建患者表
    c.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        patient_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        gender TEXT NOT NULL,
        age INTEGER NOT NULL,
        phone TEXT
    )
    ''')
    
    # 创建医师表
    c.execute('''
    CREATE TABLE IF NOT EXISTS doctors (
        doctor_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        title TEXT,
        phone TEXT,
        email TEXT
    )
    ''')
    
    # 创建病例表，关联患者ID和医师ID
    c.execute('''
    CREATE TABLE IF NOT EXISTS records (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT NOT NULL,
        doctor_id TEXT NOT NULL,
        visit_date TEXT NOT NULL,
        department TEXT NOT NULL,
        symptoms TEXT NOT NULL,
        diagnosis TEXT NOT NULL,
        treatment TEXT,
        cost TEXT,
        notes TEXT,
        FOREIGN KEY (patient_id) REFERENCES patients (patient_id),
        FOREIGN KEY (doctor_id) REFERENCES doctors (doctor_id)
    )
    ''')
    
    conn.commit()
    conn.close()


