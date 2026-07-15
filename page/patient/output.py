import gradio as gr
from .utils import export_data, export_csv, export_xlsx, import_data, import_csv, import_xlsx


def page_output_patient():
    with gr.Tabs():
        with gr.Tab("📄 CSV 导入/导出"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 导出为 CSV 文件")
                    csv_btn = gr.Button("导出 CSV", variant="primary")
                    csv_file = gr.File(label="下载 CSV 文件")
                    csv_btn.click(fn=export_csv, outputs=csv_file)

                with gr.Column():
                    gr.Markdown("### 从 CSV 文件导入")
                    csv_input = gr.File(label="选择 CSV 文件", file_types=[".csv"])
                    csv_import_btn = gr.Button("导入 CSV", variant="primary")
                    csv_result = gr.Textbox(label="导入结果")
                    csv_import_btn.click(fn=import_csv, inputs=csv_input, outputs=csv_result)

        with gr.Tab("📊 Excel 导入/导出"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 导出为 Excel 文件")
                    xlsx_btn = gr.Button("导出 XLSX", variant="primary")
                    xlsx_file = gr.File(label="下载 XLSX 文件")
                    xlsx_btn.click(fn=export_xlsx, outputs=xlsx_file)

                with gr.Column():
                    gr.Markdown("### 从 Excel 文件导入")
                    xlsx_input = gr.File(label="选择 XLSX 文件", file_types=[".xlsx"])
                    xlsx_import_btn = gr.Button("导入 XLSX", variant="primary")
                    xlsx_result = gr.Textbox(label="导入结果")
                    xlsx_import_btn.click(fn=import_xlsx, inputs=xlsx_input, outputs=xlsx_result)

        with gr.Tab("📦 JSON 完整备份"):
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
