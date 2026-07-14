import gradio as gr
from .add import page_add_patient
from .edit import page_edit_patient
from .output import page_output_patient
def page_patient():
    with gr.Tabs():
        # 添加病例
        with gr.Tab("添加病例"):
            page_add_patient()
        # 整合后的查看/搜索/编辑病例
        with gr.Tab("病例查询与编辑"):
            page_edit_patient()
        with gr.Tab("导入/导出数据"):
            page_output_patient()
