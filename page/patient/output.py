import gradio as gr
from .utils import export_data, export_csv, export_xlsx, import_data

def page_output_patient():
    with gr.Tabs():
        with gr.Tab("📄 导出病例 CSV"):
            gr.Markdown("### 导出全部病例记录为 CSV 文件\n适合 Excel / WPS 打开或导入其他系统。")
            csv_btn = gr.Button("导出 CSV", variant="primary")
            csv_file = gr.File(label="下载 CSV 文件")
            csv_btn.click(fn=export_csv, outputs=csv_file)

        with gr.Tab("📊 导出病例 Excel"):
            gr.Markdown("### 导出全部病例记录为 Excel (XLSX) 文件\n包含格式化表格，适合查看与打印。")
            xlsx_btn = gr.Button("导出 XLSX", variant="primary")
            xlsx_file = gr.File(label="下载 XLSX 文件")
            xlsx_btn.click(fn=export_xlsx, outputs=xlsx_file)

        with gr.Tab("📦 导出/导入 JSON (完整备份)"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 导出全部数据为 JSON 文件\n包含所有患者、医师和病例记录。可在其他实例中导入。")
                    export_btn = gr.Button("导出 JSON", variant="primary")
                    export_file = gr.File(label="下载导出文件")
                    export_btn.click(fn=export_data, outputs=export_file)

                with gr.Column():
                    gr.Markdown("### 从 JSON 文件导入数据\n上传之前导出的 JSON 文件进行恢复/迁移。已存在的记录会被更新，新记录会被添加。")
                    import_input = gr.File(label="选择 JSON 文件", file_types=[".json"])
                    import_btn = gr.Button("导入数据", variant="primary")
                    import_output = gr.Textbox(label="导入结果")
                    import_btn.click(fn=import_data, inputs=import_input, outputs=import_output)
