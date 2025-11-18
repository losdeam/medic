import gradio as gr
from .utils import *
import datetime
def signal():
    gr.Success("处理成功！",2)
def page_init():
    return [
        "",  # patient_name 清空
        None,  # gender 重置
        30,  # age 默认值
        "",  # phone 清空
        "",  # allergy 清空
        False,  # attention 未勾选
        None,  # doctor_name 重置
        None,  # department 重置
        datetime.datetime.now(),  # visit_date 当前时间
        "",  # symptoms 清空
        "",  # diagnosis 清空
        "",  # treatment 清空
        "",  # cost 清空
        ""  # notes 清空
    ]
def update_patient_suggestions(input_text):
    matched_patients = search_patients(input_text) if input_text else []
    results = matched_patients[:3]
    num_results = len(results)
    
    # 修正：用 value 设置按钮文本
    btn1_value = results[0]['name'] if num_results >=1 else ""
    btn1_visible = num_results >=1
    btn2_value = results[1]['name'] if num_results >=2 else ""
    btn2_visible = num_results >=2
    btn3_value = results[2]['name'] if num_results >=3 else ""
    btn3_visible = num_results >=3
    
    row_visible = num_results > 0
    
    return [
        gr.update(visible=row_visible),  # 按钮组可见性
        gr.update(value=btn1_value, visible=btn1_visible),  # 按钮1文本（用value）
        gr.update(value=btn2_value, visible=btn2_visible),  # 按钮2文本
        gr.update(value=btn3_value, visible=btn3_visible)   # 按钮3文本
    ]
def page_add_patient():
    with gr.Row():
        with gr.Column(scale=1):
            # 修改为普通Textbox用于输入
            patient_name = gr.Textbox(label="患者姓名*", placeholder="输入患者姓名")
            # 修正：按钮用 value 控制显示文本，初始化时为空
            with gr.Row(visible=False) as suggestion_row:
                patient_btn1 = gr.Button(value="", visible=False)  # 用 value 而非 label
                patient_btn2 = gr.Button(value="", visible=False)
                patient_btn3 = gr.Button(value="", visible=False)
            
            gender = gr.Radio(["男", "女"], label="性别")
            age = gr.Number(label="年龄", value=30)
            phone = gr.Textbox(label="联系电话")
            allergy = gr.Textbox(label="过敏史")
            attention = gr.Checkbox(label="重点关注")
        
        with gr.Column(scale=1):
            doctors = {item['name']: item for item in create_connection()['doctors'].find()}
            doctor_name = gr.Dropdown(doctors.keys(), label="接诊医师*", value=list(doctors.keys())[0] if doctors else None)
            
            def update_department(doctor_name):
                if doctor_name and doctor_name in doctors:
                    return doctors[doctor_name]['department']
                return ""
            
            def get_initial_department():
                if doctors:
                    first_doctor = list(doctors.keys())[0]
                    return doctors[first_doctor]['department']
                return "暂无科室信息"
            
            department = gr.Textbox(
                interactive=False, 
                label="科室",
                value=get_initial_department()
            )
            visit_date = gr.DateTime(label="就诊日期*", value=datetime.datetime.now())
    
    doctor_name.change(
        fn=update_department,
        inputs=doctor_name,
        outputs=department
    )
    
    patient_name.change(
        fn=update_patient_suggestions,
        inputs=patient_name,
        outputs=[suggestion_row, patient_btn1, patient_btn2, patient_btn3]
    )
    
    # 按钮1点击事件：填充信息
    patient_btn1.click(
        fn=fill_patient_info,
        inputs=patient_btn1,  # 传入按钮文本（患者姓名）
        outputs=[gender, age, phone, allergy, attention]
    ).then(
        # 同步姓名到输入框，并隐藏按钮组
        fn=lambda name: [gr.update(value=name), gr.update(visible=False)],
        inputs=patient_btn1,
        outputs=[patient_name, suggestion_row]
    )
    
    # 按钮2点击事件（与按钮1逻辑一致）
    patient_btn2.click(
        fn=fill_patient_info,
        inputs=patient_btn2,
        outputs=[gender, age, phone, allergy, attention]
    ).then(
        fn=lambda name: [gr.update(value=name), gr.update(visible=False)],
        inputs=patient_btn2,
        outputs=[patient_name, suggestion_row]
    )
    
    # 按钮3点击事件（与按钮1逻辑一致）
    patient_btn3.click(
        fn=fill_patient_info,
        inputs=patient_btn3,
        outputs=[gender, age, phone, allergy, attention]
    ).then(
        fn=lambda name: [gr.update(value=name), gr.update(visible=False)],
        inputs=patient_btn3,
        outputs=[patient_name, suggestion_row]
    )
    
    cost = gr.Textbox(label="费用") 
    symptoms = gr.Textbox(label="症状*", lines=3)
    diagnosis = gr.Textbox(label="诊断结果*", lines=3)
    treatment = gr.Textbox(label="治疗方案", lines=3)
    notes = gr.Textbox(label="备注", lines=2)
    
    add_record_btn = gr.Button("保存病例")
    record_status = gr.Textbox(label="状态", interactive=False)

    add_record_btn.click(
        fn=add_patient_record,
        inputs=[patient_name, gender, age, phone, allergy, attention,
                doctor_name, department, visit_date, symptoms,
                diagnosis, treatment, cost, notes],
        outputs=record_status
    ).then(
        fn=signal,
        inputs=[],
        outputs=[]
    ).then(
        fn=page_init,
        outputs=[
                patient_name, gender, age, phone, allergy, attention,
                doctor_name, department, visit_date,
                symptoms, diagnosis, treatment, cost, notes
            ]
    ).then(
        fn=None,
        js="() => window.scrollTo({ top: 0, behavior: 'smooth' })"
    )