import datetime
import gradio as gr
from .utils import *

def page_edit_patient():
    # 搜索区域
    with gr.Row():
        search_option = gr.Dropdown(["患者姓名", "医师姓名", "科室", "就诊日期"], label="搜索选项")
        search_query = gr.Textbox(label="搜索内容")
        search_btn = gr.Button("搜索")
        refresh_btn = gr.Button("刷新列表")
    
    # 病例列表（含编辑按钮）
    records_df = gr.Dataframe(get_records_with_buttons(), max_height=500, interactive=False)
    # 编辑弹窗
    with gr.Accordion("编辑病例记录") as edit_modal:
        record_id = gr.Textbox(visible=False)  # 存储当前编辑的记录ID
        
        with gr.Row():
            with gr.Column(scale=1):
                edit_patient_name = gr.Textbox(label="患者姓名*")
                edit_gender = gr.Radio(["男", "女"], label="性别")
                edit_age = gr.Number(label="年龄")
                edit_phone = gr.Textbox(label="联系电话")
                edit_allergy = gr.Textbox(label="过敏史")
                edit_attention = gr.Checkbox(label="重点关注")
            
            with gr.Column(scale=1):
                conn = create_connection()
                c = conn.cursor()
                c.execute("SELECT name FROM doctors")
                doctors_list = [r['name'] for r in c.fetchall()]
                conn.close()
                edit_doctor_name = gr.Dropdown(doctors_list, label="接诊医师*")
                edit_department = gr.Dropdown(["骨科","内科", "外科", "儿科", "妇科", "眼科", "口腔科", "皮肤科"], label="科室*")
                edit_visit_date = gr.DateTime(label="就诊日期*")
            
        edit_cost = gr.Textbox(label="费用")
        edit_symptoms = gr.Textbox(label="症状*", lines=3)
        edit_diagnosis = gr.Textbox(label="诊断结果*", lines=3)
        edit_treatment = gr.Textbox(label="治疗方案", lines=3)
        edit_notes = gr.Textbox(label="备注", lines=2)
        
        with gr.Row():
            save_edit_btn = gr.Button("保存修改")
            cancel_edit_btn = gr.Button("取消")
        
        edit_status = gr.Textbox(label="编辑状态", interactive=False)
    
    # 按钮事件绑定
    def handle_search(search_opt, query):
        return get_records_with_buttons(search_opt, query)
    
    search_btn.click(handle_search, inputs=[search_option, search_query], outputs=records_df)
    refresh_btn.click(lambda: get_records_with_buttons(), outputs=records_df)
    
    # 处理编辑按钮点击
    def open_edit_modal(event: gr.SelectData):
        try:
            if isinstance(event.value,str)  and event.value.startswith("编辑_"):
                rid = event.value.split("_")[1]
                record = get_record_by_id(int(rid))
                if record:
                    v = record['visit_date']
                    if isinstance(v, datetime.datetime):
                        object_visit_date = v
                    elif isinstance(v, (int, float)):
                        object_visit_date = datetime.datetime.fromtimestamp(v)
                    else:
                        object_visit_date = datetime.datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
                    return (
                        gr.update(visible=True),  # edit_modal
                        gr.update(value=rid),     # record_id
                        gr.update(value=record['patient_info']['name']),      # edit_patient_name
                        gr.update(value=record['patient_info']['gender']),    # edit_gender
                        gr.update(value=record['patient_info']['age']),       # edit_age
                        gr.update(value=record['patient_info']['phone']),     # edit_phone
                        gr.update(value=record['patient_info']['allergy']),   # edit_allergy
                        gr.update(value=record['patient_info']['attention_flag']),  # edit_attention
                        gr.update(value=record['doctor_info']['name']),       # edit_doctor_name
                        gr.update(value=record['department']),                # edit_department
                        gr.update(value=object_visit_date),  # edit_visit_date
                        gr.update(value=record['symptoms']),                  # edit_symptoms
                        gr.update(value=record['diagnosis']),                 # edit_diagnosis
                        gr.update(value=record['treatment']),                 # edit_treatment
                        gr.update(value=record['cost']),                      # edit_cost
                        gr.update(value=record.get('notes', '')),             # edit_notes
                        gr.update(value="")                                   # edit_status
                    )
            return [gr.update()] * 17
        except Exception as e:
            return [gr.update()] * 16 + [gr.update(value=f"打开编辑失败: {e}")]
    
    records_df.select(open_edit_modal, outputs=[edit_modal, record_id, edit_patient_name, edit_gender,
                                                edit_age, edit_phone, edit_allergy, edit_attention,
                                                edit_doctor_name, edit_department, edit_visit_date,
                                                edit_symptoms, edit_diagnosis, edit_treatment,
                                                edit_cost, edit_notes, edit_status])
    
    # 保存修改
    def save_edit(rid, pname, gender, age, phone, allergy, attention, dname, dept, vdate, symp, diag, treat, cost, notes):
        result = update_record(int(rid), pname, gender, age, phone, allergy, attention,
                                dname, dept, vdate, symp, diag, treat, cost, notes)
        return {
            edit_status: result,
            records_df: get_records_with_buttons(),
            edit_modal: gr.update(visible=False) if "成功" in result else gr.update(visible=True)
        }
    
    save_edit_btn.click(save_edit, inputs=[record_id, edit_patient_name, edit_gender, edit_age,
                                            edit_phone, edit_allergy, edit_attention, edit_doctor_name,
                                            edit_department, edit_visit_date, edit_symptoms,
                                            edit_diagnosis, edit_treatment, edit_cost, edit_notes],
                        outputs=[edit_status, records_df, edit_modal])
    
    # 取消编辑
    cancel_edit_btn.click(lambda: {edit_modal: gr.update(visible=False)}, outputs=edit_modal)

