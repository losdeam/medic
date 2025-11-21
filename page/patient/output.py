import gradio as gr
from .utils import *

def page_output_patient():
    export_btn = gr.Button("导出为Excel")
    export_file = gr.File(label="下载文件")
    # export_btn.click(export_records, outputs=export_file)