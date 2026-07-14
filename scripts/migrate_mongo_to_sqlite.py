#!/usr/bin/env python3
"""MongoDB → SQLite 数据迁移脚本

将 MongoDB `medical_records` 数据库中的患者、医师、病例记录
迁移到 SQLite `medical_records.db` 中。

用法:
    python scripts/migrate_mongo_to_sqlite.py                    # 交互式确认
    python scripts/migrate_mongo_to_sqlite.py --yes              # 跳过确认
    python scripts/migrate_mongo_to_sqlite.py --dry-run          # 仅预览，不写入
    python scripts/migrate_mongo_to_sqlite.py --uri mongodb://...  # 指定 MongoDB 地址
    python scripts/migrate_mongo_to_sqlite.py --db-path /path/to/medical_records.db
"""

import argparse
import datetime
import os
import sqlite3
import sys
from collections import defaultdict

# 确保项目根目录在 sys.path 中，以便可导入 utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import init_tables, create_connection as create_sqlite_conn


def connect_mongo(uri):
    from pymongo import MongoClient
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.server_info()  # 探活
    return client['medical_records']


def read_mongo_collections(db):
    """读取 MongoDB 全部集合数据。"""
    collections = {}
    for name in ['patients', 'doctors', 'records']:
        collections[name] = list(db[name].find({}))
    return collections


def transform_patient(doc):
    return {
        'patient_id': doc['patient_id'],
        'name': doc['name'],
        'gender': doc['gender'],
        'age': int(doc['age']),
        'phone': doc.get('phone', ''),
        'allergy': doc.get('allergy', ''),
        'attention_flag': 1 if doc.get('attention_flag') else 0,
    }


def transform_doctor(doc):
    return {
        'doctor_id': doc['doctor_id'],
        'name': doc['name'],
        'department': doc.get('department', ''),
        'title': doc.get('title', ''),
        'phone': doc.get('phone', ''),
        'email': doc.get('email', ''),
    }


def transform_record(doc):
    visit_date = doc.get('visit_date')
    if isinstance(visit_date, datetime.datetime):
        visit_date = visit_date.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(visit_date, str):
        # 尝试归一化格式
        for fmt in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
            try:
                visit_date = datetime.datetime.strptime(visit_date, fmt).strftime('%Y-%m-%d %H:%M:%S')
                break
            except ValueError:
                continue
    return {
        'patient_id': doc.get('patient_id', ''),
        'doctor_id': doc.get('doctor_id', ''),
        'visit_date': visit_date or '',
        'department': doc.get('department', ''),
        'symptoms': doc.get('symptoms', ''),
        'diagnosis': doc.get('diagnosis', ''),
        'treatment': doc.get('treatment', ''),
        'cost': doc.get('cost', ''),
        'notes': doc.get('notes', ''),
    }


def migrate(collections, conn, dry_run=False):
    """将转换后的数据写入 SQLite。返回统计信息。"""
    c = conn.cursor()
    log = defaultdict(lambda: {'inserted': 0, 'updated': 0, 'skipped': 0})

    # 1) 患者
    for doc in collections.get('patients', []):
        row = transform_patient(doc)
        c.execute("SELECT patient_id FROM patients WHERE patient_id = ?", (row['patient_id'],))
        existing = c.fetchone()
        if existing:
            if not dry_run:
                c.execute(
                    "UPDATE patients SET name=?, gender=?, age=?, phone=?, allergy=?, attention_flag=? WHERE patient_id=?",
                    (row['name'], row['gender'], row['age'], row['phone'], row['allergy'], row['attention_flag'], row['patient_id'])
                )
            log['patients']['updated'] += 1
        else:
            if not dry_run:
                c.execute(
                    "INSERT INTO patients (patient_id, name, gender, age, phone, allergy, attention_flag) VALUES (?,?,?,?,?,?,?)",
                    (row['patient_id'], row['name'], row['gender'], row['age'], row['phone'], row['allergy'], row['attention_flag'])
                )
            log['patients']['inserted'] += 1

    # 2) 医师
    for doc in collections.get('doctors', []):
        row = transform_doctor(doc)
        c.execute("SELECT doctor_id FROM doctors WHERE doctor_id = ?", (row['doctor_id'],))
        existing = c.fetchone()
        if existing:
            if not dry_run:
                c.execute(
                    "UPDATE doctors SET name=?, department=?, title=?, phone=?, email=? WHERE doctor_id=?",
                    (row['name'], row['department'], row['title'], row['phone'], row['email'], row['doctor_id'])
                )
            log['doctors']['updated'] += 1
        else:
            if not dry_run:
                c.execute(
                    "INSERT INTO doctors (doctor_id, name, department, title, phone, email) VALUES (?,?,?,?,?,?)",
                    (row['doctor_id'], row['name'], row['department'], row['title'], row['phone'], row['email'])
                )
            log['doctors']['inserted'] += 1

    # 3) 病例
    for doc in collections.get('records', []):
        row = transform_record(doc)
        c.execute(
            "SELECT id FROM records WHERE patient_id=? AND doctor_id=? AND visit_date=? AND symptoms=?",
            (row['patient_id'], row['doctor_id'], row['visit_date'], row['symptoms'])
        )
        existing = c.fetchone()
        if existing:
            if not dry_run:
                c.execute(
                    "UPDATE records SET diagnosis=?, treatment=?, cost=?, notes=?, department=? WHERE id=?",
                    (row['diagnosis'], row['treatment'], row['cost'], row['notes'], row['department'], existing['id'])
                )
            log['records']['updated'] += 1
        else:
            if not dry_run:
                c.execute(
                    "INSERT INTO records (patient_id, doctor_id, visit_date, department, symptoms, diagnosis, treatment, cost, notes) VALUES (?,?,?,?,?,?,?,?,?)",
                    (row['patient_id'], row['doctor_id'], row['visit_date'], row['department'], row['symptoms'], row['diagnosis'], row['treatment'], row['cost'], row['notes'])
                )
            log['records']['inserted'] += 1

    if not dry_run:
        conn.commit()

    return dict(log)


def print_summary(source_counts, log, dry_run):
    tag = " [DRY-RUN 预览]" if dry_run else ""
    print(f"\n{'='*60}")
    print(f"迁移结果{tag}")
    print(f"{'='*60}")

    for table in ['patients', 'doctors', 'records']:
        src = source_counts.get(table, 0)
        ins = log.get(table, {}).get('inserted', 0)
        upd = log.get(table, {}).get('updated', 0)
        print(f"  {table}: 源 {src} 条 → 新增 {ins}, 更新 {upd}")

    total_src = sum(source_counts.values())
    total_ins = sum(v.get('inserted', 0) for v in log.values())
    total_upd = sum(v.get('updated', 0) for v in log.values())
    print(f"  合计: 源 {total_src} 条 → 新增 {total_ins}, 更新 {total_upd}")

    if dry_run:
        print("\n  提示: 使用 --yes 参数正式执行迁移。")


def main():
    parser = argparse.ArgumentParser(description='MongoDB → SQLite 数据迁移')
    parser.add_argument('--yes', '-y', action='store_true', help='跳过确认，直接迁移')
    parser.add_argument('--dry-run', '-n', action='store_true', help='仅预览，不写入 SQLite')
    parser.add_argument('--uri', default='mongodb://localhost:27017/', help='MongoDB 连接串')
    parser.add_argument('--db-path', default='medical_records.db', help='SQLite 数据库路径')
    args = parser.parse_args()

    # 连接 MongoDB
    try:
        mongo_db = connect_mongo(args.uri)
    except Exception as e:
        print(f"错误: 无法连接 MongoDB ({args.uri}): {e}")
        sys.exit(1)
    print(f"MongoDB 已连接: {args.uri}")

    # 读取源数据
    collections = read_mongo_collections(mongo_db)
    source_counts = {name: len(docs) for name, docs in collections.items()}
    total = sum(source_counts.values())
    if total == 0:
        print("MongoDB 中无数据，无需迁移。")
        mongo_db.client.close()
        return

    print(f"源数据统计: 患者 {source_counts['patients']} 条, 医师 {source_counts['doctors']} 条, 病例 {source_counts['records']} 条, 共 {total} 条")

    if args.dry_run:
        print("\n>>> DRY-RUN 模式 — 仅预览，不写入 SQLite <<<")
    elif not args.yes:
        answer = input("\n确认迁移? [y/N] ").strip().lower()
        if answer not in ('y', 'yes'):
            print("已取消。")
            mongo_db.client.close()
            return

    # 初始化 SQLite 表结构
    init_tables()
    conn = create_sqlite_conn()

    # 执行迁移
    log = migrate(collections, conn, dry_run=args.dry_run)

    # 输出摘要
    print_summary(source_counts, log, args.dry_run)

    # 验证
    if not args.dry_run:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM patients")
        pt = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM doctors")
        dr = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM records")
        rc = c.fetchone()[0]
        print(f"\n验证: SQLite 现有 患者 {pt} 条, 医师 {dr} 条, 病例 {rc} 条")

    conn.close()
    mongo_db.client.close()


if __name__ == '__main__':
    main()
