import gradio as gr
from .add import page_add_doc
from .search import page_search_doc
from .edit import page_edit_doc   
def page_doc():
    with gr.Tabs():
        # 添加医师
        with gr.Tab("添加医师"):
            page_add_doc()
        
        # 查看医师
        with gr.Tab("查看医师"):
            page_search_doc()
            
        # 编辑医师
        with gr.Tab("编辑医师"):
            page_edit_doc()
