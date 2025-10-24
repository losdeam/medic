from utils import *
import pandas as pd
import streamlit as st
import datetime
from io import BytesIO
import time 
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

#
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
    if db['records'].find_one({'_id': record_id}) is None:
        print("记录不存在")
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
        last_record_botton = ""
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
                if all_patients[name][1] or all_patients[name][2]:
                    allergy_ = all_patients[name][1]
                    attention_flag = all_patients[name][2]
                    show_remind_alert("请注意")
                gender = st.text_input("性别*",value=all_patients[name][3],disabled=True)
                age = st.text_input("年龄",value=all_patients[name][4],disabled=True,key="age")
                phone = st.text_input("联系电话", value=all_patients[name][5],disabled=True,key="phone")
                last_record_botton = st.button("填充上次病例")
            else:
                gender = st.selectbox("性别", ["男", "女", "其他"])
                age = st.number_input("年龄", min_value=0, max_value=150, step=1,key="age")
                phone = st.text_input("联系电话", placeholder="输入手机号码",key="phone")
                
        with col2:
            date = st.date_input("就诊日期", datetime.date.today())
            department = st.selectbox("科室", ["骨科","内科", "外科", "儿科", "妇科", "眼科", "口腔科", "皮肤科"])

            # 获取医师列表
            doctor_options = get_doctor_options()
            if not doctor_options:
                st.warning("请先添加医师！")
                st.stop()

            doctor_selection = st.selectbox("主治医生", list(doctor_options.keys()))
            doctor_id = doctor_options[doctor_selection]
        symptoms = st.text_area("症状描述", placeholder="详细描述患者症状",key = "symptoms")
        diagnosis = st.text_area("诊断结果", placeholder="填写诊断结果",key = "diagnosis")
        treatment = st.text_area("治疗方案", placeholder="填写治疗方案",key = "treatment")
        allergy = st.text_area("过敏史", placeholder="填写过敏史",key = "allergy")
        attention_flag =st.checkbox("特殊标记",value= True if attention_flag else False,key = "attention_flag")
        notes = st.text_area("备注", placeholder="填写其他需要记录的信息",key ="notes" )
        if last_record_botton:
            patient_record = get_records_by_patient(all_patients[name][0]).iloc[-1].to_dict()
            st.session_state.symptoms = patient_record["symptoms"]
            st.session_state.diagnosis = patient_record["diagnosis"]
            st.session_state.treatment = patient_record["treatment"]
            st.session_state.allergy = allergy_
            st.session_state.attention_flag =  True if attention_flag else False
            st.session_state.notes = patient_record["notes"]

        cost = 0
        # 保存按钮
        if st.button("保存病例"):
            if not name:
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
                time.sleep(1)
                st.session_state.clear()
                st.session_state.symptoms = ""
                st.session_state.diagnosis = ""
                st.session_state.treatment = ""
                st.session_state.allergy = ""
                st.session_state.attention_flag =  False
                st.session_state.phone = ""
                st.session_state.patient_input = ""
                st.session_state.notes = ""
                st.rerun()
    elif page == "查看病例":
        st.subheader("病例记录列表")
        
        # 获取所有记录
        records_df = get_all_records()
        del(records_df["patient_id"])
        del(records_df["doctor_id"])
        del(records_df["record_id"])
        key_mapping = {
            "patient_name": "患者姓名",
            "gender": "性别",
            "age": "年龄",
            "phone": "联系电话",
            "symptoms": "症状描述",
            "diagnosis": "诊断结果",
            "treatment": "治疗方案",
            "cost": "费用",
            "notes": "备注",
            "visit_date": "就诊日期",
            "department": "科室",
            "doctor_name": "主治医生",

        }

        if records_df.empty:
            st.info("暂无病例记录，请先添加病例。")
        else:
            records_df = records_df.rename(columns={
                "_id":"病例编号",
             'patient_name': '患者姓名',
            'patient_gender': '性别',
            'patient_age': '年龄',
            'doctor_name': '主治医生',
            'visit_date': '就诊日期',
            'symptoms': '症状描述',
            'diagnosis': '诊断结果',
            "cost": "费用",
            "doctor_department": "科室",
            "notes": "备注",
            'treatment': '治疗方案'
        })
            # # 显示记录表格
            # st.dataframe(records_df, use_container_width=True)
            
            # 分页显示
            records_per_page = 10
            total_pages = len(records_df) // records_per_page + (1 if len(records_df) % records_per_page != 0 else 0)
            
            if total_pages > 1:
                col1, col2, col3 = st.columns([1, 1, 1])
                current_page = col2.number_input("页码", min_value=1, max_value=total_pages, value=1)
                
                start_idx = (current_page - 1) * records_per_page
                end_idx = min(start_idx + records_per_page, len(records_df))
                
                st.dataframe(records_df.iloc[start_idx:end_idx], use_container_width=True)
            
            # 删除功能
            st.subheader("删除病例记录")
            record_id = st.number_input("输入要删除的记录ID",min_value=0,max_value=len(records_df))
            if st.button("删除记录"):
                record_id = records_df['_id'][record_id]
                delete_record(record_id)
                st.success(f"记录ID {record_id} 已删除！")
                time.sleep(1)
                st.rerun()
    
    elif page == "搜索病例":
        st.subheader("搜索病例记录")
        
        search_option = st.selectbox("搜索条件", ["患者姓名","患者ID",  "医师ID", "医师姓名", "科室", "就诊日期"])
        search_query = st.text_input(f"输入{search_option}")
        
        if st.button("搜索"):
            # if not search_query:
            #     st.warning("请输入搜索内容。")
            # else:
            results_df = search_records(search_option, search_query)
            
            if results_df.empty:
                st.info(f"未找到符合条件的病例记录。")
            else:
                st.success(f"找到 {len(results_df)} 条记录")
                st.dataframe(results_df, use_container_width=True)
    
    elif page == "导出数据":
        st.subheader("导出病例数据")
        
        # 获取所有记录
        records_df = get_all_records()
        
        if records_df.empty:
            st.info("暂无病例记录，无法导出。")
        else:
            # 导出为CSV
            csv = records_df.to_csv(sep='\t', na_rep='nan')
            st.download_button(
                label="下载CSV文件",
                data=csv,
                file_name="病例记录.csv",
                mime="text/csv"
            )
            
            # 创建Excel文件
            def to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='病例记录', index=False)
                output.seek(0)
                return output
            
            excel_file = to_excel(records_df)
            st.download_button(
                label="下载Excel文件",
                data=excel_file,
                file_name="病例记录.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            