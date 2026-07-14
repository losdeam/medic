from utils import *
import pandas as pd
from io import BytesIO
import datetime
import gradio as gr

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

    if isinstance(visit_date, float):
        # 旧版本Gradio：float是Unix时间戳（秒），转换为datetime
        visit_date_obj = datetime.datetime.fromtimestamp(visit_date)
    else:
        # 新版本Gradio：字符串格式，按ISO格式解析（兼容处理）
        visit_date_obj = datetime.datetime.strptime(visit_date, "%Y-%m-%dT%H:%M:%S")
    # 添加病例记录
    db['records'].insert_one({
        'patient_id': patient_id,
        'doctor_id': doctor['doctor_id'],
        'visit_date': visit_date_obj,
        'department': department,
        'symptoms': symptoms,
        'diagnosis': diagnosis,
        'treatment': treatment,
        'cost': cost,
        'notes': notes
    })
    return "成功：病例记录已添加"

def update_record(record_id, patient_name, gender, age, phone, allergy, attention,
                  doctor_name, department, visit_date, symptoms, diagnosis, treatment, cost, notes):
    """更新病例记录"""
    db = create_connection()
    
    # 验证医师存在
    doctor = db['doctors'].find_one({'name': doctor_name})
    if not doctor:
        return "错误：医师不存在"
    
    # 获取原始记录
    record = db['records'].find_one({'_id': record_id})
    if not record:
        return "错误：病例记录不存在"
    
    patient_id = record['patient_id']
    
    # 更新患者信息
    db['patients'].update_one(
        {'patient_id': patient_id},
        {'$set': {
            'name': patient_name,
            'gender': gender,
            'age': age,
            'phone': phone,
            'allergy': allergy,
            'attention_flag': attention
        }}
    )
    if isinstance(visit_date, float):
        # 旧版本Gradio：float是Unix时间戳（秒），转换为datetime
        visit_date_obj = datetime.datetime.fromtimestamp(visit_date)
    else:
        # 新版本Gradio：字符串格式，按ISO格式解析（兼容处理）
        visit_date_obj = datetime.datetime.strptime(visit_date, "%Y-%m-%dT%H:%M:%S")
    
    # 更新病例信息
    db['records'].update_one(
        {'_id': record_id},
        {'$set': {
            'doctor_id': doctor['doctor_id'],
            'department': department,
            'visit_date': visit_date_obj,
            'symptoms': symptoms,
            'diagnosis': diagnosis,
            'treatment': treatment,
            'cost': cost,
            'notes': notes
        }}
    )
    
    return "成功：病例记录已更新"

# 构建整合后的病例列表（含编辑按钮）
def get_records_with_buttons(search_option=None, query=None):
    """获取病例列表，包含编辑按钮"""
    db = create_connection()
    
    # 基础聚合查询
    pipeline = [
        {'$lookup': {'from': 'patients', 'localField': 'patient_id', 'foreignField': 'patient_id', 'as': 'patient_info'}},
        {'$lookup': {'from': 'doctors', 'localField': 'doctor_id', 'foreignField': 'doctor_id', 'as': 'doctor_info'}},
        {'$unwind': '$patient_info'},
        {'$unwind': '$doctor_info'},
        {'$project': {
            'record_id': '$_id',
            'patient_name': '$patient_info.name',
            'patient_gender': '$patient_info.gender',
            'patient_age': '$patient_info.age',
            'doctor_name': '$doctor_info.name',
            'department': '$department',
            'visit_date': 1,
            'symptoms': 1,
            'diagnosis': 1,
            'treatment': 1,
            'cost': 1
        }},
        {'$sort': {'visit_date': -1}}
    ]
    
    # 处理搜索条件
    if search_option and query:
        match_condition = {}
        if search_option == "患者姓名":
            match_condition = {'patient_info.name': {'$regex': query, '$options': 'i'}}
        elif search_option == "医师姓名":
            match_condition = {'doctor_info.name': {'$regex': query, '$options': 'i'}}
        elif search_option == "科室":
            match_condition = {'department': {'$regex': query, '$options': 'i'}}
        elif search_option == "就诊日期":
            match_condition = {'visit_date': {'$regex': query, '$options': 'i'}}
        pipeline.insert(3, {'$match': match_condition})
    
    records = list(db['records'].aggregate(pipeline))
    df = pd.DataFrame(records)
    
    if df.empty:
        df = pd.DataFrame(columns=['患者姓名', '性别', '年龄', '医师', '科室', '就诊日期', '症状', '诊断', '治疗', '费用', '操作'])
    else:
        # 添加编辑按钮列（使用record_id作为按钮标识）
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

# gradio中未实现
# def export_records():
#     df = get_all_records()
#     output = BytesIO()
#     # 使用ExcelWriter将DataFrame写入BytesIO对象
#     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
#         df.to_excel(writer, index=False, sheet_name='Sheet1')
#     output.seek(0)
#     excel_data = output.getvalue()  # 获取bytes数据
#     output.close()  # 关闭BytesIO对象
#     return excel_data

def get_record_by_id(record_id):
    """通过记录ID获取完整病例信息"""
    db = create_connection()
    record = db['records'].aggregate([
        {'$match': {'_id': record_id}},
        {'$lookup': {'from': 'patients', 'localField': 'patient_id', 'foreignField': 'patient_id', 'as': 'patient_info'}},
        {'$lookup': {'from': 'doctors', 'localField': 'doctor_id', 'foreignField': 'doctor_id', 'as': 'doctor_info'}},
        {'$unwind': '$patient_info'},
        {'$unwind': '$doctor_info'}
    ])
    return list(record)[0] if record else None
def generate_id(prefix):
    return f"{prefix}_{str(uuid.uuid4())[:8]}"


def get_all_records():
    db = create_connection()
    records = db['records'].aggregate([
        {'$lookup': {
            'from': 'patients',
            'localField': 'patient_id',
            'foreignField': 'patient_id',
            'as': 'patient_info'
        }},
        {'$lookup': {
            'from': 'doctors',
            'localField': 'doctor_id',
            'foreignField': 'doctor_id',
            'as': 'doctor_info'
        }},
        {'$unwind': '$patient_info'},
        {'$unwind': '$doctor_info'},
        {'$project': {
            'record_id': '$_id',
            'patient_name': '$patient_info.name',
            'patient_gender': '$patient_info.gender',
            'patient_age': '$patient_info.age',
            'doctor_name': '$doctor_info.name',
            'department': '$department',
            'visit_date': 1,
            'symptoms': 1,
            'diagnosis': 1,
            'treatment': 1,
            'cost': 1
        }},
        {'$sort': {'visit_date': -1}}
    ])
    
    df = pd.DataFrame(list(records))
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


# 在文件末尾添加
def search_patients(name_prefix):
    """根据姓名前缀搜索病人，返回匹配的前3个结果"""
    db = create_connection()
    if not name_prefix:
        return []
    
    # 模糊匹配姓名（不区分大小写），限制返回3条
    patients = db['patients'].find(
        {'name': {'$regex': f'^{name_prefix}', '$options': 'i'}},
        {'name': 1, 'gender': 1, 'age': 1, 'phone': 1, 'allergy': 1, 'attention_flag': 1}
    ).limit(3)
    
    return list(patients)

def get_patient_by_name(name):
    """根据姓名获取病人详细信息"""
    db = create_connection()
    return db['patients'].find_one({'name': name})

# 新增：更新病人建议列表
def update_patient_suggestions(input_text):
    if not input_text:
        return gr.update(choices=[], visible=False)
    
    matched_patients = search_patients(input_text)
    if not matched_patients:
        return gr.update(choices=[], visible=False)
    
    choices = [p['name'] for p in matched_patients]
    return gr.update(choices=choices, visible=True)

# 新增：填充选中的病人信息
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
        patient.get('attention_flag', False)
    ]


def export_data():
    from bson import json_util
    import tempfile, os

    db = create_connection()
    data = {
        'version': 1,
        'exported_at': datetime.datetime.now().isoformat(),
        'collections': {
            'patients': list(db['patients'].find({})),
            'doctors': list(db['doctors'].find({})),
            'records': list(db['records'].find({})),
        }
    }

    fd, path = tempfile.mkstemp(suffix='.json', prefix='medic_export_')
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        json_util.dump(data, f, ensure_ascii=False, indent=2)

    return path


def export_csv():
    import tempfile, os

    df = get_all_records()
    fd, path = tempfile.mkstemp(suffix='.csv', prefix='medic_export_')
    os.close(fd)
    df.to_csv(path, index=False, encoding='utf-8-sig')
    return path


def export_xlsx():
    import tempfile, os

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


def import_data(file_obj):
    from bson import json_util

    if file_obj is None:
        return "请选择要导入的文件"

    with open(file_obj, 'r', encoding='utf-8') as f:
        data = json_util.load(f)

    version = data.get('version', 0)
    if version != 1:
        return "不支持的数据格式版本"

    collections = data.get('collections', {})
    db = create_connection()

    counts = {}
    for coll_name in ['patients', 'doctors', 'records']:
        docs = collections.get(coll_name, [])
        if not docs:
            counts[coll_name] = "0"
            continue

        new_count = update_count = 0
        for doc in docs:
            doc.pop('_id', None)
            if coll_name == 'patients':
                existing = db['patients'].find_one({'patient_id': doc['patient_id']})
                if existing:
                    db['patients'].replace_one({'patient_id': doc['patient_id']}, doc)
                    update_count += 1
                else:
                    db['patients'].insert_one(doc)
                    new_count += 1
            elif coll_name == 'doctors':
                existing = db['doctors'].find_one({'doctor_id': doc['doctor_id']})
                if existing:
                    db['doctors'].replace_one({'doctor_id': doc['doctor_id']}, doc)
                    update_count += 1
                else:
                    db['doctors'].insert_one(doc)
                    new_count += 1
            else:  # records
                existing = db['records'].find_one({
                    'patient_id': doc['patient_id'],
                    'doctor_id': doc['doctor_id'],
                    'visit_date': doc['visit_date'],
                    'symptoms': doc['symptoms'],
                })
                if existing:
                    db['records'].replace_one({'_id': existing['_id']}, doc)
                    update_count += 1
                else:
                    db['records'].insert_one(doc)
                    new_count += 1

        counts[coll_name] = f"{new_count} 新增, {update_count} 更新"

    return (
        f"导入完成：患者 {counts.get('patients', 0)}，"
        f"医师 {counts.get('doctors', 0)}，"
        f"病例 {counts.get('records', 0)}"
    )