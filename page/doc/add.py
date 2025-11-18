from .utils import *
import gradio as gr

def page_add_doc():
    doc_name = gr.Textbox(label="医师姓名*")
    doc_dept = gr.Dropdown(["骨科","内科", "外科", "儿科", "妇科", "眼科", "口腔科", "皮肤科"], label="所属科室*")
    doc_title = gr.Textbox(label="职称")
    doc_phone = gr.Textbox(label="联系电话")
    doc_email = gr.Textbox(label="电子邮箱")
    add_doc_btn = gr.Button("添加医师")
    doc_status = gr.Textbox(label="状态", interactive=False)
    
    add_doc_btn.click(
        add_doctor, 
        inputs=[doc_name, doc_dept, doc_title, doc_phone, doc_email],
        outputs=doc_status
    )