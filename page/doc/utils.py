from utils import *
import pandas as pd


def add_doctor(name, department, title, phone, email):
    if not name or not department:
        return "错误：姓名和科室为必填项"

    conn = create_connection()
    c = conn.cursor()

    c.execute("SELECT doctor_id FROM doctors WHERE name = ?", (name,))
    if c.fetchone():
        conn.close()
        return "错误：已存在同名医师"

    doctor_id = generate_id("DOC")
    try:
        c.execute(
            "INSERT INTO doctors (doctor_id, name, department, title, phone, email) VALUES (?, ?, ?, ?, ?, ?)",
            (doctor_id, name, department, title, phone, email)
        )
        conn.commit()
        conn.close()
        return f"成功：医师添加完成，ID: {doctor_id}"
    except Exception as e:
        conn.close()
        return f"错误：{str(e)}"


def get_all_doctors():
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM doctors")
    doctors = c.fetchall()
    conn.close()

    if not doctors:
        return pd.DataFrame(columns=['ID', '姓名', '科室', '职称', '电话', '邮箱'])

    df = pd.DataFrame([dict(r) for r in doctors])
    return df[['doctor_id', 'name', 'department', 'title', 'phone', 'email']].rename(
        columns={
            'doctor_id': 'ID',
            'name': '姓名',
            'department': '科室',
            'title': '职称',
            'phone': '电话',
            'email': '邮箱'
        }
    )


def update_doctor(doctor_id, name, department, title, phone, email):
    conn = create_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE doctors SET name = ?, department = ?, title = ?, phone = ?, email = ? WHERE doctor_id = ?",
        (name, department, title, phone, email, doctor_id)
    )
    conn.commit()
    conn.close()
    return "成功：医师信息已更新"


def delete_doctor(doctor_id):
    conn = create_connection()
    c = conn.cursor()
    c.execute("DELETE FROM records WHERE doctor_id = ?", (doctor_id,))
    c.execute("DELETE FROM doctors WHERE doctor_id = ?", (doctor_id,))
    conn.commit()
    conn.close()
    return "成功：医师信息已删除"
