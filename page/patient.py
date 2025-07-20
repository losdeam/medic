from utils import *
import pandas as pd
import streamlit as st
import datetime
from io import BytesIO

# 获取医师下拉列表
def get_doctor_options():
    db = create_connection()
    doctors = db['doctors'].find({}, {'_id': 0, 'doctor_id': 1, 'name': 1})
    return {f"{doctor['name']}": doctor['doctor_id'] for doctor in doctors}
def get_patients_options():
    db = create_connection()
    pipeline = [
    {"$project": {
        "_id": 0,
        "patient_id": 1,
        "name": 1,
        "gender" :{"$ifNull": ["$gender", ""]},
        "age": {"$ifNull": ["$age",20]},
        "phone": {"$ifNull": ["$phone",""]},
        "allergy": {"$ifNull": ["$allergy", ""]},  # 如果allergy字段不存在，则用空列表代替
        "attention_flag": {"$ifNull": ["$attention_flag", ""]}
    }}
    ]
    patients = list(db['patients'].aggregate(pipeline))
    return {f"{patient['name']}": (patient['patient_id'],patient['allergy'],patient["attention_flag"],patient["gender"],patient["age"],patient["phone"]) for patient in patients}
# 根据姓名和电话查询患者
def find_patient(name, phone):
    db = create_connection()
    patient = db['patients'].find_one({'name': name, 'phone': phone})
    return patient['patient_id'] if patient else None

# 添加患者
def add_patient(patient_id, name, gender, age, phone,allergy,attention_flag):
    db = create_connection()
    try:
        db['patients'].insert_one({
            'patient_id': patient_id, # 患者ID
            'name': name, # 患者姓名
            'gender': gender, # 患者性别
            'age': age, # 患者年龄
            'phone': phone,# 患者联系方式
            "allergy": allergy,#患者过敏
            "attention_flag":attention_flag#患者关注标志
        })
        return True
    except Exception:
        return False

# 添加病例记录
def add_record(patient_id, doctor_id, visit_date, department, symptoms, diagnosis, treatment, cost, notes):
    db = create_connection()
    db['records'].insert_one({
        'patient_id': patient_id,
        'doctor_id': doctor_id,
        'visit_date': visit_date,
        'department': department,
        'symptoms': symptoms,
        'diagnosis': diagnosis,
        'treatment': treatment,
        'cost': cost,
        'notes': notes
    })

# 获取所有病例记录
def get_all_records():
    db = create_connection()
    records = db['records'].aggregate([
        {
            '$lookup': {
                'from': 'patients',
                'localField': 'patient_id',
                'foreignField': 'patient_id',
                'as': 'patient_info'
            }
        },
        {
            '$lookup': {
                'from': 'doctors',
                'localField': 'doctor_id',
                'foreignField': 'doctor_id',
                'as': 'doctor_info'
            }
        },
        {
            '$unwind': '$patient_info'
        },
        {
            '$unwind': '$doctor_info'
        },
        {
            '$project': {
                'record_id': '$_id',
                'patient_id': 1,
                'patient_name': '$patient_info.name',
                'patient_gender': '$patient_info.gender',
                'patient_age': '$patient_info.age',
                'doctor_id': 1,
                'doctor_name': '$doctor_info.name',
                'doctor_department': '$doctor_info.department',
                'visit_date': 1,
                'symptoms': 1,
                'diagnosis': 1,
                'treatment': 1,
                'cost': 1,
                'notes': 1
            }
        },
        {
            '$sort': {
                'visit_date': -1
            }
        }
    ])
    df = pd.DataFrame(list(records))
    return df

# 根据患者 ID 获取病例记录
def get_records_by_patient(patient_id):
    db = create_connection()
    records = db['records'].aggregate([
        {
            '$match': {
                'patient_id': patient_id
            }
        },
        {
            '$lookup': {
                'from': 'patients',
                'localField': 'patient_id',
                'foreignField': 'patient_id',
                'as': 'patient_info'
            }
        },
        {
            '$lookup': {
                'from': 'doctors',
                'localField': 'doctor_id',
                'foreignField': 'doctor_id',
                'as': 'doctor_info'
            }
        },
        {
            '$unwind': '$patient_info'
        },
        {
            '$unwind': '$doctor_info'
        },
        {
            '$project': {
                'record_id': '$_id',
                'patient_id': 1,
                'patient_name': '$patient_info.name',
                'patient_gender': '$patient_info.gender',
                'patient_age': '$patient_info.age',
                'doctor_id': 1,
                'doctor_name': '$doctor_info.name',
                'doctor_department': '$doctor_info.department',
                'visit_date': 1,
                'symptoms': 1,
                'diagnosis': 1,
                'treatment': 1,
                'notes': 1
            }
        },
        {
            '$sort': {
                'visit_date': -1
            }
        }
    ])
    df = pd.DataFrame(list(records))
    return df

# 根据医师 ID 获取病例记录
def get_records_by_doctor(doctor_id):
    db = create_connection()
    records = db['records'].aggregate([
        {
            '$match': {
                'doctor_id': doctor_id
            }
        },
        {
            '$lookup': {
                'from': 'patients',
                'localField': 'patient_id',
                'foreignField': 'patient_id',
                'as': 'patient_info'
            }
        },
        {
            '$lookup': {
                'from': 'doctors',
                'localField': 'doctor_id',
                'foreignField': 'doctor_id',
                'as': 'doctor_info'
            }
        },
        {
            '$unwind': '$patient_info'
        },
        {
            '$unwind': '$doctor_info'
        },
        {
            '$project': {
                'record_id': '$_id',
                'patient_id': 1,
                'patient_name': '$patient_info.name',
                'patient_gender': '$patient_info.gender',
                'patient_age': '$patient_info.age',
                'doctor_id': 1,
                'doctor_name': '$doctor_info.name',
                'doctor_department': '$doctor_info.department',
                'visit_date': 1,
                'symptoms': 1,
                'diagnosis': 1,
                'treatment': 1,
                'notes': 1
            }
        },
        {
            '$sort': {
                'visit_date': -1
            }
        }
    ])
    df = pd.DataFrame(list(records))
    return df

# 根据条件搜索病例
def search_records(option, query):
    db = create_connection()
    if option == "患者 ID":
        filter_condition = {'patient_id': query}
    elif option == "患者姓名":
        filter_condition = {'patient_info.name': {'$regex': query, '$options': 'i'}}
    elif option == "医师 ID":
        filter_condition = {'doctor_id': query}
    elif option == "医师姓名":
        filter_condition = {'doctor_info.name': {'$regex': query, '$options': 'i'}}
    elif option == "科室":
        filter_condition = {'department': {'$regex': query, '$options': 'i'}}
    elif option == "就诊日期":
        filter_condition = {'visit_date': {'$regex': query, '$options': 'i'}}
    records = db['records'].aggregate([
        {
            '$lookup': {
                'from': 'patients',
                'localField': 'patient_id',
                'foreignField': 'patient_id',
                'as': 'patient_info'
            }
        },
        {
            '$lookup': {
                'from': 'doctors',
                'localField': 'doctor_id',
                'foreignField': 'doctor_id',
                'as': 'doctor_info'
            }
        },
        {
            '$unwind': '$patient_info'
        },
        {
            '$unwind': '$doctor_info'
        },
        {
            '$match': filter_condition
        },
        {
            '$project': {
                'record_id': '$_id',
                'patient_id': 1,
                'patient_name': '$patient_info.name',
                'patient_gender': '$patient_info.gender',
                'patient_age': '$patient_info.age',
                'doctor_id': 1,
                'doctor_name': '$doctor_info.name',
                'doctor_department': '$doctor_info.department',
                'visit_date': 1,
                'symptoms': 1,
                'diagnosis': 1,
                'treatment': 1,
                'notes': 1
            }
        },
        {
            '$sort': {
                'visit_date': -1
            }
        }
    ])
    df = pd.DataFrame(list(records))
    return df

# 删除病例记录
def delete_record(record_id):
    db = create_connection()
    db['records'].delete_one({'_id': record_id})

# 更新患者信息
def update_patient(patient_id, name, gender, age, phone,allergy,attention_flag):
    db = create_connection()
    db['patients'].update_one(
        {'patient_id': patient_id},
        {'$set': {
            'name': name,
            'gender': gender,
            'age': age,
            'phone': phone,
            "allergy": allergy,#患者过敏
            "attention_flag":attention_flag#患者关注标志
        }}
    )

def page_patient(page):
    if page == "添加病例":
        st.subheader("添加新病例")

        # 表单布局
        col1, col2 = st.columns(2)
        # 初始化，后续获取到的话进行更新
        allergy = ""
        attention_flag =""

        with col1:
            all_patients = get_patients_options()
            container = st.container()
                # 用于存储用户输入
            if "patient_input" not in st.session_state:
                st.session_state.patient_input = ""
            name = container.text_input("患者姓名*", key="patient_input", placeholder="输入患者姓名")

            # 模糊搜索匹配的患者
            matched_patients = []
            if name:
                matched_patients = [p for p in all_patients if name.lower() in p.lower()]
            # 如果有匹配结果，显示为可点击的选项
            if matched_patients:
                container.markdown("**匹配的患者**")
                for patient in matched_patients:
                    def update_patient_input():
                        st.session_state.patient_input = patient
                    container.button(patient,on_click=update_patient_input, key=f"btn_{patient}")
            if name in all_patients :
                if all_patients[name][1]:
                    show_remind_alert("患者有过敏史,请注意")
                    allergy = all_patients[name][1]
                if all_patients[name][2]:
                    attention_flag = all_patients[name][2]
                    show_remind_alert("患者被标记为需要特别注意,请注意")
                gender = st.text_input("性别*",value=all_patients[name][3],disabled=True)
                age = st.text_input("年龄*",value=all_patients[name][4],disabled=True)
                phone = st.text_input("联系电话", value=all_patients[name][5],disabled=True)
            else:
                gender = st.selectbox("性别*", ["男", "女", "其他"])
                age = st.number_input("年龄*", min_value=0, max_value=150, step=1)
                phone = st.text_input("联系电话", placeholder="输入手机号码")
                
        with col2:
            date = st.date_input("就诊日期*", datetime.date.today())
            department = st.selectbox("科室*", ["内科", "外科", "儿科", "妇科", "眼科", "口腔科", "皮肤科"])

            # 获取医师列表
            doctor_options = get_doctor_options()
            if not doctor_options:
                st.warning("请先添加医师！")
                st.stop()

            doctor_selection = st.selectbox("主治医生*", list(doctor_options.keys()))
            doctor_id = doctor_options[doctor_selection]

        symptoms = st.text_area("症状描述*", placeholder="详细描述患者症状")
        diagnosis = st.text_area("诊断结果*", placeholder="填写诊断结果")
        treatment = st.text_area("治疗方案", placeholder="填写治疗方案")
        allergy = st.text_area("过敏史", placeholder="填写过敏史")
        attention_flag =st.checkbox("特殊标记",value= True if attention_flag else False)
        notes = st.text_area("备注", placeholder="填写其他需要记录的信息")
        cost = 0
        # 保存按钮
        if st.button("保存病例"):
            if not name or not gender or age == 0 or not symptoms or not diagnosis:
                st.error("带*的字段为必填项，请确保填写完整。")
            else:
                # 检查患者是否已存在
                patient_id = find_patient(name, phone)

                if not patient_id:
                    # 患者不存在，生成新的患者 ID
                    patient_id = generate_id("PAT")
                    add_patient(patient_id, name, gender, age, phone,allergy,attention_flag)
                    st.info(f"已为新患者创建 ID: {patient_id}")
                else:
                    # 患者已存在，更新患者信息
                    update_patient(patient_id, name, gender, age, phone,allergy,attention_flag)
                    st.info(f"找到现有患者，ID: {patient_id}")

                # 添加病例记录
                visit_date = date.strftime("%Y-%m-%d")
                add_record(patient_id, doctor_id, visit_date, department, symptoms, diagnosis, treatment, cost, notes)
                show_success_alert("病例保存成功！")