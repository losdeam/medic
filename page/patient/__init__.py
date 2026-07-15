import gradio as gr
from .add import page_add_patient
from .edit import page_edit_patient
from .output import page_output_patient
def page_patient():
    with gr.Tabs():
        with gr.Tab("📝 添加病例"):
            page_add_patient()
        with gr.Tab("🔍 病例查询与编辑"):
            page_edit_patient()
        with gr.Tab("📦 导入/导出数据"):
            page_output_patient()
