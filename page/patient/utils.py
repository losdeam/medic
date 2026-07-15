from utils import *
import pandas as pd
from io import BytesIO
import datetime
import json


def _row_to_dict(row):
    return dict(row) if row else None


def _rows_to_list(rows):
    return [dict(r) for r in rows]


def add_patient_record(patient_name, gender, age, phone, allergy, attention,
                       doctor_name, department, visit_date, symptoms,
                       diagnosis, treatment, cost, notes):
    conn = create_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM doctors WHERE name = ?", (doctor_name,))
    doctor = _row_to_dict(c.fetchone())
    if not doctor:
        conn.close()
        return "错误：医师不存在"

    c.execute("SELECT * FROM patients WHERE name = ? AND phone = ?", (patient_name, phone))
    patient = _row_to_dict(c.fetchone())

    if not patient:
        patient_id = generate_id("PAT")
        c.execute(
            "INSERT INTO patients (patient_id, name, gender, age, phone, allergy, attention_flag) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (patient_id, patient_name, gender, age, phone, allergy, 1 if attention else 0)
        )
    else:
        patient_id = patient['patient_id']
        c.execute(
            "UPDATE patients SET gender = ?, age = ?, allergy = ?, attention_flag = ? WHERE patient_id = ?",
            (gender, age, allergy, 1 if attention else 0, patient_id)
        )

    if isinstance(visit_date, datetime.datetime):
        visit_date_obj = visit_date
    elif isinstance(visit_date, float):
        visit_date_obj = datetime.datetime.fromtimestamp(visit_date)
    else:
        visit_date_obj = datetime.datetime.strptime(visit_date, "%Y-%m-%dT%H:%M:%S")

    c.execute(
        "INSERT INTO records (patient_id, doctor_id, visit_date, department, symptoms, diagnosis, treatment, cost, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (patient_id, doctor['doctor_id'], visit_date_obj.strftime('%Y-%m-%d %H:%M:%S'), department, symptoms, diagnosis, treatment, cost, notes)
    )
    conn.commit()
    conn.close()
    return "成功：病例记录已添加"


def update_record(record_id, patient_name, gender, age, phone, allergy, attention,
                  doctor_name, department, visit_date, symptoms, diagnosis, treatment, cost, notes):
    conn = create_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM doctors WHERE name = ?", (doctor_name,))
    doctor = _row_to_dict(c.fetchone())
    if not doctor:
        conn.close()
        return "错误：医师不存在"

    c.execute("SELECT * FROM records WHERE id = ?", (record_id,))
    record = _row_to_dict(c.fetchone())
    if not record:
        conn.close()
        return "错误：病例记录不存在"

    patient_id = record['patient_id']
    c.execute(
        "UPDATE patients SET name = ?, gender = ?, age = ?, phone = ?, allergy = ?, attention_flag = ? WHERE patient_id = ?",
        (patient_name, gender, age, phone, allergy, 1 if attention else 0, patient_id)
    )

    if isinstance(visit_date, datetime.datetime):
        visit_date_obj = visit_date
    elif isinstance(visit_date, float):
        visit_date_obj = datetime.datetime.fromtimestamp(visit_date)
    else:
        visit_date_obj = datetime.datetime.strptime(visit_date, "%Y-%m-%dT%H:%M:%S")

    c.execute(
        "UPDATE records SET doctor_id = ?, department = ?, visit_date = ?, symptoms = ?, diagnosis = ?, treatment = ?, cost = ?, notes = ? WHERE id = ?",
        (doctor['doctor_id'], department, visit_date_obj.strftime('%Y-%m-%d %H:%M:%S'), symptoms, diagnosis, treatment, cost, notes, record_id)
    )
    conn.commit()
    conn.close()
    return "成功：病例记录已更新"


def get_records_with_buttons(search_option=None, query=None):
    conn = create_connection()
    c = conn.cursor()

    sql = '''
    SELECT r.id AS record_id, p.name AS patient_name, p.gender AS patient_gender, p.age AS patient_age,
           d.name AS doctor_name, r.department, r.visit_date, r.symptoms, r.diagnosis, r.treatment, r.cost
    FROM records r
    JOIN patients p ON r.patient_id = p.patient_id
    JOIN doctors d ON r.doctor_id = d.doctor_id
    '''

    params = []
    if search_option and query:
        if search_option == "患者姓名":
            sql += " WHERE p.name LIKE ?"
            params.append(f"%{query}%")
        elif search_option == "医师姓名":
            sql += " WHERE d.name LIKE ?"
            params.append(f"%{query}%")
        elif search_option == "科室":
            sql += " WHERE r.department LIKE ?"
            params.append(f"%{query}%")
        elif search_option == "就诊日期":
            sql += " WHERE r.visit_date LIKE ?"
            params.append(f"%{query}%")

    sql += " ORDER BY r.visit_date DESC"

    c.execute(sql, params)
    records = _rows_to_list(c.fetchall())
    conn.close()

    df = pd.DataFrame(records)
    if df.empty:
        df = pd.DataFrame(columns=['患者姓名', '性别', '年龄', '医师', '科室', '就诊日期', '症状', '诊断', '治疗', '费用', '操作'])
    else:
        df['操作'] = df['record_id'].apply(lambda x: f"编辑_{x}")
        df = df.rename(columns={
            'patient_name': '患者姓名',
            'patient_gender': '性别',
            'patient_age': '年龄',
            'doctor_name': '医师',
            'department': '科室',
            'visit_date': '就诊日期',
            'symptoms': '症状',
            'diagnosis': '诊断',
            'treatment': '治疗',
            'cost': '费用'
        })[['患者姓名', '性别', '年龄', '医师', '科室', '就诊日期', '症状', '诊断', '治疗', '费用', '操作']]
    return df


def get_record_by_id(record_id):
    conn = create_connection()
    c = conn.cursor()
    c.execute('''
    SELECT r.*, p.name AS patient_name, p.gender AS patient_gender, p.age AS patient_age,
           p.phone AS patient_phone, p.allergy AS patient_allergy, p.attention_flag AS patient_attention,
           d.name AS doctor_name, d.doctor_id AS doc_doctor_id
    FROM records r
    JOIN patients p ON r.patient_id = p.patient_id
    JOIN doctors d ON r.doctor_id = d.doctor_id
    WHERE r.id = ?
    ''', (record_id,))
    row = _row_to_dict(c.fetchone())
    conn.close()

    if not row:
        return None

    return {
        'patient_info': {
            'name': row['patient_name'],
            'gender': row['patient_gender'],
            'age': row['patient_age'],
            'phone': row['patient_phone'],
            'allergy': row['patient_allergy'],
            'attention_flag': bool(row['patient_attention']),
        },
        'doctor_info': {
            'name': row['doctor_name'],
            'doctor_id': row['doc_doctor_id'],
        },
        'department': row['department'],
        'visit_date': row['visit_date'],
        'symptoms': row['symptoms'],
        'diagnosis': row['diagnosis'],
        'treatment': row['treatment'],
        'cost': row['cost'],
        'notes': row['notes'],
    }


def generate_id(prefix):
    return f"{prefix}_{str(uuid.uuid4())[:8]}"


def get_all_records():
    conn = create_connection()
    c = conn.cursor()
    c.execute('''
    SELECT r.id AS record_id, p.name AS patient_name, p.gender AS patient_gender, p.age AS patient_age,
           d.name AS doctor_name, r.department, r.visit_date, r.symptoms, r.diagnosis, r.treatment, r.cost
    FROM records r
    JOIN patients p ON r.patient_id = p.patient_id
    JOIN doctors d ON r.doctor_id = d.doctor_id
    ORDER BY r.visit_date DESC
    ''')
    records = _rows_to_list(c.fetchall())
    conn.close()

    df = pd.DataFrame(records)
    if df.empty:
        return pd.DataFrame(columns=['患者姓名', '性别', '年龄', '医师', '科室', '就诊日期', '症状', '诊断', '治疗', '费用'])
    return df[['patient_name', 'patient_gender', 'patient_age', 'doctor_name',
               'department', 'visit_date', 'symptoms', 'diagnosis', 'treatment', 'cost']].rename(
        columns={
            'patient_name': '患者姓名',
            'patient_gender': '性别',
            'patient_age': '年龄',
            'doctor_name': '医师',
            'department': '科室',
            'visit_date': '就诊日期',
            'symptoms': '症状',
            'diagnosis': '诊断',
            'treatment': '治疗',
            'cost': '费用'
        }
    )


def search_patients(name_prefix):
    if not name_prefix:
        return []
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM patients WHERE name LIKE ? LIMIT 3", (f"{name_prefix}%",))
    results = _rows_to_list(c.fetchall())
    conn.close()
    return results


def get_patient_by_name(name):
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM patients WHERE name = ?", (name,))
    row = _row_to_dict(c.fetchone())
    conn.close()
    return row


def fill_patient_info(selected_name):
    if not selected_name:
        return [None, None, None, None, False]
    patient = get_patient_by_name(selected_name)
    if not patient:
        return [None, None, None, None, False]
    return [
        patient.get('gender'),
        patient.get('age'),
        patient.get('phone'),
        patient.get('allergy'),
        bool(patient.get('attention_flag', False)),
    ]


def export_data():
    import tempfile
    import os

    conn = create_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM patients")
    patients = _rows_to_list(c.fetchall())
    c.execute("SELECT * FROM doctors")
    doctors = _rows_to_list(c.fetchall())
    c.execute("SELECT * FROM records")
    records = _rows_to_list(c.fetchall())
    conn.close()

    data = {
        'version': 1,
        'exported_at': datetime.datetime.now().isoformat(),
        'patients': patients,
        'doctors': doctors,
        'records': records,
    }

    fd, path = tempfile.mkstemp(suffix='.json', prefix='medic_export_')
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return path


def export_csv():
    import tempfile
    import os

    df = get_all_records()
    fd, path = tempfile.mkstemp(suffix='.csv', prefix='medic_export_')
    os.close(fd)
    df.to_csv(path, index=False, encoding='utf-8-sig')
    return path


def export_xlsx():
    import tempfile
    import os

    df = get_all_records()
    fd, path = tempfile.mkstemp(suffix='.xlsx', prefix='medic_export_')
    os.close(fd)
    with pd.ExcelWriter(path, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='病例记录')
        worksheet = writer.sheets['病例记录']
        for i, col in enumerate(df.columns):
            max_width = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, min(max_width, 40))
    return path


def _find_or_create_patient(c, name, gender, age):
    c.execute("SELECT * FROM patients WHERE name = ?", (name,))
    patient = c.fetchone()
    if patient:
        c.execute("UPDATE patients SET gender=?, age=? WHERE patient_id=?", (gender, age, patient['patient_id']))
        return patient['patient_id']
    pid = generate_id("PAT")
    c.execute(
        "INSERT INTO patients (patient_id, name, gender, age, phone, allergy, attention_flag) VALUES (?,?,?,?,?,?,?)",
        (pid, name, gender, age, '', '', 0)
    )
    return pid


def _find_or_create_doctor(c, name, department):
    c.execute("SELECT * FROM doctors WHERE name = ?", (name,))
    doctor = c.fetchone()
    if doctor:
        return doctor['doctor_id']
    did = generate_id("DOC")
    c.execute(
        "INSERT INTO doctors (doctor_id, name, department, title, phone, email) VALUES (?,?,?,?,?,?)",
        (did, name, department, '', '', '')
    )
    return did


def import_csv(file_obj):
    if file_obj is None:
        return "请选择要导入的文件"

    df = pd.read_csv(file_obj, encoding='utf-8-sig')
    expected_cols = ['患者姓名', '性别', '年龄', '医师', '科室', '就诊日期']
    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        return f"缺少必要列: {', '.join(missing)}"

    conn = create_connection()
    c = conn.cursor()
    new_records = updated_records = 0

    for _, row in df.iterrows():
        try:
            patient_id = _find_or_create_patient(c, str(row['患者姓名']).strip(), str(row.get('性别', '')).strip(), int(row.get('年龄', 0)))
            doctor_id = _find_or_create_doctor(c, str(row['医师']).strip(), str(row.get('科室', '')).strip())
            visit_date = str(row.get('就诊日期', '')).strip()
            symptoms = str(row.get('症状', '')).strip()
            diagnosis = str(row.get('诊断', '')).strip()
            treatment = str(row.get('治疗', '')).strip() if pd.notna(row.get('治疗')) else ''
            cost = str(row.get('费用', '')).strip() if pd.notna(row.get('费用')) else ''
            notes = str(row.get('备注', '')).strip() if pd.notna(row.get('备注')) else ''

            c.execute(
                "SELECT id FROM records WHERE patient_id=? AND doctor_id=? AND visit_date=? AND symptoms=?",
                (patient_id, doctor_id, visit_date, symptoms)
            )
            existing = c.fetchone()
            if existing:
                c.execute(
                    "UPDATE records SET department=?, diagnosis=?, treatment=?, cost=?, notes=? WHERE id=?",
                    (str(row.get('科室', '')).strip(), diagnosis, treatment, cost, notes, existing['id'])
                )
                updated_records += 1
            else:
                c.execute(
                    "INSERT INTO records (patient_id, doctor_id, visit_date, department, symptoms, diagnosis, treatment, cost, notes) VALUES (?,?,?,?,?,?,?,?,?)",
                    (patient_id, doctor_id, visit_date, str(row.get('科室', '')).strip(), symptoms, diagnosis, treatment, cost, notes)
                )
                new_records += 1
        except Exception:
            continue

    conn.commit()
    conn.close()
    return f"导入完成：新增 {new_records} 条病例，更新 {updated_records} 条"


def import_xlsx(file_obj):
    if file_obj is None:
        return "请选择要导入的文件"

    df = pd.read_excel(file_obj, engine='openpyxl')
    expected_cols = ['患者姓名', '性别', '年龄', '医师', '科室', '就诊日期']
    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        return f"缺少必要列: {', '.join(missing)}"

    conn = create_connection()
    c = conn.cursor()
    new_records = updated_records = 0

    for _, row in df.iterrows():
        try:
            patient_id = _find_or_create_patient(c, str(row['患者姓名']).strip(), str(row.get('性别', '')).strip(), int(row.get('年龄', 0)))
            doctor_id = _find_or_create_doctor(c, str(row['医师']).strip(), str(row.get('科室', '')).strip())
            visit_date = str(row.get('就诊日期', '')).strip()
            symptoms = str(row.get('症状', '')).strip()
            diagnosis = str(row.get('诊断', '')).strip()
            treatment = str(row.get('治疗', '')).strip() if pd.notna(row.get('治疗')) else ''
            cost = str(row.get('费用', '')).strip() if pd.notna(row.get('费用')) else ''
            notes = str(row.get('备注', '')).strip() if pd.notna(row.get('备注')) else ''

            c.execute(
                "SELECT id FROM records WHERE patient_id=? AND doctor_id=? AND visit_date=? AND symptoms=?",
                (patient_id, doctor_id, visit_date, symptoms)
            )
            existing = c.fetchone()
            if existing:
                c.execute(
                    "UPDATE records SET department=?, diagnosis=?, treatment=?, cost=?, notes=? WHERE id=?",
                    (str(row.get('科室', '')).strip(), diagnosis, treatment, cost, notes, existing['id'])
                )
                updated_records += 1
            else:
                c.execute(
                    "INSERT INTO records (patient_id, doctor_id, visit_date, department, symptoms, diagnosis, treatment, cost, notes) VALUES (?,?,?,?,?,?,?,?,?)",
                    (patient_id, doctor_id, visit_date, str(row.get('科室', '')).strip(), symptoms, diagnosis, treatment, cost, notes)
                )
                new_records += 1
        except Exception:
            continue

    conn.commit()
    conn.close()
    return f"导入完成：新增 {new_records} 条病例，更新 {updated_records} 条"


def import_data(file_obj):
    if file_obj is None:
        return "请选择要导入的文件"

    with open(file_obj, 'r', encoding='utf-8') as f:
        data = json.load(f)

    version = data.get('version', 0)
    if version != 1:
        return "不支持的数据格式版本"

    conn = create_connection()
    c = conn.cursor()

    counts = {}
    for table_name in ['patients', 'doctors', 'records']:
        docs = data.get(table_name, [])
        if not docs:
            counts[table_name] = "0"
            continue

        new_count = update_count = 0
        for doc in docs:
            if table_name == 'patients':
                c.execute("SELECT patient_id FROM patients WHERE patient_id = ?", (doc['patient_id'],))
                existing = c.fetchone()
                if existing:
                    c.execute(
                        "UPDATE patients SET name=?, gender=?, age=?, phone=?, allergy=?, attention_flag=? WHERE patient_id=?",
                        (doc['name'], doc['gender'], doc['age'], doc.get('phone', ''), doc.get('allergy', ''), doc.get('attention_flag', 0), doc['patient_id'])
                    )
                    update_count += 1
                else:
                    c.execute(
                        "INSERT INTO patients (patient_id, name, gender, age, phone, allergy, attention_flag) VALUES (?,?,?,?,?,?,?)",
                        (doc['patient_id'], doc['name'], doc['gender'], doc['age'], doc.get('phone', ''), doc.get('allergy', ''), doc.get('attention_flag', 0))
                    )
                    new_count += 1
            elif table_name == 'doctors':
                c.execute("SELECT doctor_id FROM doctors WHERE doctor_id = ?", (doc['doctor_id'],))
                existing = c.fetchone()
                if existing:
                    c.execute(
                        "UPDATE doctors SET name=?, department=?, title=?, phone=?, email=? WHERE doctor_id=?",
                        (doc['name'], doc['department'], doc.get('title', ''), doc.get('phone', ''), doc.get('email', ''), doc['doctor_id'])
                    )
                    update_count += 1
                else:
                    c.execute(
                        "INSERT INTO doctors (doctor_id, name, department, title, phone, email) VALUES (?,?,?,?,?,?)",
                        (doc['doctor_id'], doc['name'], doc['department'], doc.get('title', ''), doc.get('phone', ''), doc.get('email', ''))
                    )
                    new_count += 1
            else:
                c.execute(
                    "SELECT id FROM records WHERE patient_id=? AND doctor_id=? AND visit_date=? AND symptoms=?",
                    (doc['patient_id'], doc['doctor_id'], doc['visit_date'], doc['symptoms'])
                )
                existing = c.fetchone()
                if existing:
                    c.execute(
                        "UPDATE records SET patient_id=?, doctor_id=?, visit_date=?, department=?, symptoms=?, diagnosis=?, treatment=?, cost=?, notes=? WHERE id=?",
                        (doc['patient_id'], doc['doctor_id'], doc['visit_date'], doc['department'], doc['symptoms'], doc['diagnosis'], doc.get('treatment', ''), doc.get('cost', ''), doc.get('notes', ''), existing['id'])
                    )
                    update_count += 1
                else:
                    c.execute(
                        "INSERT INTO records (patient_id, doctor_id, visit_date, department, symptoms, diagnosis, treatment, cost, notes) VALUES (?,?,?,?,?,?,?,?,?)",
                        (doc['patient_id'], doc['doctor_id'], doc['visit_date'], doc['department'], doc['symptoms'], doc['diagnosis'], doc.get('treatment', ''), doc.get('cost', ''), doc.get('notes', ''))
                    )
                    new_count += 1

        counts[table_name] = f"{new_count} 新增, {update_count} 更新"

    conn.commit()
    conn.close()

    return (
        f"导入完成：患者 {counts.get('patients', 0)}，"
        f"医师 {counts.get('doctors', 0)}，"
        f"病例 {counts.get('records', 0)}"
    )
