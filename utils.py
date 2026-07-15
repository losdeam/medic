import uuid
import sqlite3
import sys
import json
import os
import shutil


def _get_app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


CONFIG_FILE = os.path.join(_get_app_dir(), 'config.json')


def _load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_config(config):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise RuntimeError(f"无法保存配置文件: {e}")


def get_db_path():
    config = _load_config()
    db_path = config.get('db_path', 'medical_records.db')
    if not os.path.isabs(db_path):
        db_path = os.path.join(_get_app_dir(), db_path)
    return db_path


def set_db_path(path):
    if not path:
        raise ValueError("数据库路径不能为空")
    config = _load_config()
    config['db_path'] = path
    _save_config(config)


def create_connection():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def generate_id(prefix):
    return f"{prefix}_{str(uuid.uuid4())[:8]}"


def _create_tables(conn):
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        patient_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        gender TEXT NOT NULL,
        age INTEGER NOT NULL,
        phone TEXT,
        allergy TEXT,
        attention_flag INTEGER DEFAULT 0
    )
    ''')
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
    c.execute('''
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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


def init_tables():
    conn = create_connection()
    _create_tables(conn)
    conn.close()


def migrate_db(old_path, new_path):
    if old_path == new_path:
        return "新旧路径相同，无需迁移"

    if not os.path.exists(old_path):
        return f"原数据库文件不存在: {old_path}"

    old_conn = sqlite3.connect(old_path)
    old_conn.row_factory = sqlite3.Row
    old_c = old_conn.cursor()

    new_conn = sqlite3.connect(new_path)
    new_c = new_conn.cursor()

    _create_tables(new_conn)

    tables = ['patients', 'doctors', 'records']
    summary = {}

    for table in tables:
        old_c.execute(f"SELECT * FROM {table}")
        rows = old_c.fetchall()
        if not rows:
            summary[table] = 0
            continue

        columns = [desc[0] for desc in old_c.description]
        placeholders = ','.join('?' for _ in columns)
        column_names = ','.join(f'"{c}"' for c in columns)

        count = 0
        for row in rows:
            values = [row[c] for c in columns]
            try:
                new_c.execute(
                    f"INSERT OR IGNORE INTO {table}({column_names}) VALUES({placeholders})",
                    values
                )
                if new_c.rowcount > 0:
                    count += 1
            except Exception as e:
                pass

        summary[table] = count

    new_conn.commit()
    new_conn.close()
    old_conn.close()

    parts = [f"{cn}: {n} 条" for cn, n in summary.items() if n > 0]
    total = sum(summary.values())
    parts.append(f"共 {total} 条")
    return "迁移完成: " + ', '.join(parts)


_REG_KEY = r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run"
_REG_NAME = "简易病例记录系统"


def _try_reg(*args):
    try:
        import subprocess
        return subprocess.run(
            ['reg'] + list(args),
            capture_output=True, timeout=10
        )
    except Exception:
        return None


def is_autostart_enabled():
    result = _try_reg('query', _REG_KEY, '/v', _REG_NAME)
    return result is not None and result.returncode == 0


def enable_autostart():
    if not getattr(sys, 'frozen', False):
        return "仅支持打包后的 exe 文件"
    result = _try_reg('add', _REG_KEY, '/v', _REG_NAME, '/t', 'REG_SZ', '/d', sys.executable, '/f')
    if result is not None and result.returncode == 0:
        return "已启用开机自启"
    return f"设置失败 (error={result.returncode if result is not None else 'reg not found'})"


def disable_autostart():
    result = _try_reg('delete', _REG_KEY, '/v', _REG_NAME, '/f')
    if result is not None and result.returncode == 0:
        return "已禁用开机自启"
    if result is not None and result.returncode == 1:
        return "未设置开机自启"
    return f"禁用失败 (error={result.returncode if result is not None else 'reg not found'})"
