from .utils import *
import gradio as gr
    
def page_search_doc():
    doctors_df = gr.Dataframe(get_all_doctors(), max_height=500)
    refresh_docs = gr.Button("刷新列表")
    refresh_docs.click(get_all_doctors, outputs=doctors_df)