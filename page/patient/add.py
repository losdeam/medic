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
def page_add_patient():
    with gr.Row():
        with gr.Column(scale=1):
            patient_name = gr.Textbox(label="患者姓名*")
            gender = gr.Radio(["男", "女"], label="性别")
            age = gr.Number(label="年龄", value=30)
            phone = gr.Textbox(label="联系电话")
            allergy = gr.Textbox(label="过敏史")
            attention = gr.Checkbox(label="重点关注")
        
        with gr.Column(scale=1):
            print([d for d in create_connection()['doctors'].find()])
            doctors = {item['name']: item for item in create_connection()['doctors'].find()}
            doctor_name = gr.Dropdown(doctors.keys(), label="接诊医师*",value=list(doctors.keys())[0])
            def update_department(doctor_name):
                """根据选择的医生更新科室信息"""
                if doctor_name and doctor_name in doctors:
                    return doctors[doctor_name]['department']
                return ""
            def get_initial_department():
                """获取初始科室信息"""
                if doctors:
                    first_doctor = list(doctors.keys())[0]
                    return doctors[first_doctor]['department']
                return "暂无科室信息"
            # print(list(doctors.keys())[0])
            # print(doctors,doctor_name)
            # print(doctors[doctor_name])
            department = gr.Textbox(interactive=False ,label="科室",
                value=get_initial_department()  # 这里正确初始化
            )
            visit_date = gr.DateTime (label="就诊日期*", value=datetime.datetime.now())
        # 关键部分：绑定医生选择变化事件
    doctor_name.change(
        fn=update_department,
        inputs=doctor_name,
        outputs=department
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

    # gr刷新
    