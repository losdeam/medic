import gradio as gr
from page.patient import page_patient
from page.doc import page_doc
from page.config.page_config import page_config
from utils import init_tables

# 静态 CSS - 在页面加载时就应用
static_css = """
:root {
    --text-md: 1rem; /* 16px */
}

.gradio-container {
    font-family: 'Microsoft YaHei', '微软雅黑', Arial, sans-serif !important;
    max-width: var(--container-width) !important;
    min-height: var(--container-height) !important;
}

body {
    font-size: var(--font-size) !important;
}
"""

# 构建Gradio界面（修改后）
def create_interface():
    init_tables()
    with gr.Blocks(css=static_css, title="简易病例记录系统") as app:
        gr.Markdown("# 简易病例记录系统")
        gr.Markdown("这是一个用于记录和管理患者病例的简单系统，支持添加、查看、搜索、编辑和导出病例记录。")
        
        with gr.Tabs():
            # 病例管理标签页
            with gr.Tab("病例管理"):
                page_patient()
            # 医师管理标签页
            with gr.Tab("医师管理"):
                page_doc()
            # 系统配置标签页
            with gr.Tab("系统配置"):
                page_config()
    
    return app

# 启动应用
if __name__ == "__main__":
    app = create_interface()
    app.launch(server_name="0.0.0.0", server_port=8501, debug=True)