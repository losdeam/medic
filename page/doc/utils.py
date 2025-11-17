from utils import *
import pandas as pd

    # 医师管理相关函数
def add_doctor(name, department, title, phone, email):
    if not name or not department:
        return "错误：姓名和科室为必填项"
    
    db = create_connection()
    if db['doctors'].find_one({'name': name}):
        return "错误：已存在同名医师"
    
    doctor_id = generate_id("DOC")
    try:
        db['doctors'].insert_one({
            'doctor_id': doctor_id,
            'name': name,
            'department': department,
            'title': title,
            'phone': phone,
            'email': email
        })
        return f"成功：医师添加完成，ID: {doctor_id}"
    except Exception as e:
        return f"错误：{str(e)}"

def get_all_doctors():
    db = create_connection()
    doctors = list(db['doctors'].find())
    if not doctors:
        return pd.DataFrame(columns=['ID', '姓名', '科室', '职称', '电话', '邮箱'])
    
    df = pd.DataFrame(doctors)
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
    db = create_connection()
    db['doctors'].update_one(
        {'doctor_id': doctor_id},
        {'$set': {
            'name': name,
            'department': department,
            'title': title,
            'phone': phone,
            'email': email
        }}
    )
    return "成功：医师信息已更新"

def delete_doctor(doctor_id):
    db = create_connection()
    db['records'].delete_many({'doctor_id': doctor_id})
    db['doctors'].delete_one({'doctor_id': doctor_id})
    return "成功：医师信息已删除"

# 病例管理相关函数
def add_patient_record(patient_name, gender, age, phone, allergy, attention, 
                      doctor_name, department, visit_date, symptoms, 
                      diagnosis, treatment, cost, notes):
    db = create_connection()
    
    # 获取医生ID
    doctor = db['doctors'].find_one({'name': doctor_name})
    if not doctor:
        return "错误：医师不存在"
    
    # 创建或获取患者
    patient = db['patients'].find_one({'name': patient_name, 'phone': phone})
    if not patient:
        patient_id = generate_id("PAT")
        db['patients'].insert_one({
            'patient_id': patient_id,
            'name': patient_name,
            'gender': gender,
            'age': age,
            'phone': phone,
            'allergy': allergy,
            'attention_flag': attention
        })
    else:
        patient_id = patient['patient_id']
        # 更新患者信息
        db['patients'].update_one(
            {'patient_id': patient_id},
            {'$set': {
                'gender': gender,
                'age': age,
                'allergy': allergy,
                'attention_flag': attention
            }}
        )
    
    # 添加病例记录
    db['records'].insert_one({
        'patient_id': patient_id,
        'doctor_id': doctor['doctor_id'],
        'visit_date': visit_date.strftime('%Y-%m-%d'),
        'department': department,
        'symptoms': symptoms,
        'diagnosis': diagnosis,
        'treatment': treatment,
        'cost': cost,
        'notes': notes
    })
    
    return "成功：病例记录已添加"