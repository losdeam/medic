from .utils import *
import gradio as gr
def page_edit_doc():
    doc_ids = [d['doctor_id'] for d in create_connection()['doctors'].find()]
    edit_doc_id = gr.Dropdown(doc_ids, label="选择医师ID")
    edit_name = gr.Textbox(label="医师姓名")
    edit_dept = gr.Dropdown(["内科", "外科", "儿科", "妇科", "眼科", "口腔科", "皮肤科"], label="所属科室")
    edit_title = gr.Textbox(label="职称")
    edit_phone = gr.Textbox(label="联系电话")
    edit_email = gr.Textbox(label="电子邮箱")
    update_btn = gr.Button("保存修改")
    edit_status = gr.Textbox(label="状态", interactive=False)
    
    update_btn.click(
        update_doctor,
        inputs=[edit_doc_id, edit_name, edit_dept, edit_title, edit_phone, edit_email],
        outputs=edit_status
    )

    # 删除医师
    with gr.Tab("删除医师"):
        del_doc_id = gr.Dropdown(doc_ids, label="选择要删除的医师ID")
        del_btn = gr.Button("确认删除")
        del_status = gr.Textbox(label="状态", interactive=False)
        
        del_btn.click(
            delete_doctor,
            inputs=[del_doc_id],
            outputs=del_status
        )