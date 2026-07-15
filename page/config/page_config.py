import gradio as gr
import os
from utils import get_db_path, set_db_path, migrate_db, is_autostart_enabled, enable_autostart, disable_autostart


def _migrate_and_switch(new_path):
    new_path = new_path.strip().strip('"').strip("'")
    if not new_path:
        return "请输入有效的数据库路径"

    abs_path = os.path.abspath(new_path)
    current_path = get_db_path()

    try:
        result = migrate_db(current_path, abs_path)
        set_db_path(abs_path)
        return result
    except Exception as e:
        return f"操作失败: {e}"


def page_config():
    """配置页面"""
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## 界面配置")

            with gr.Group():
                font_size_slider = gr.Slider(
                    minimum=16,
                    maximum=48,
                    value=16,
                    step=1,
                    label="字体大小",
                    elem_id="font_size_slider"
                )

                apply_btn = gr.Button("应用配置")
                reset_btn = gr.Button("恢复默认")

                status_text = gr.Textbox(label="", interactive=False)

            apply_btn.click(
                None,
                inputs=[font_size_slider],
                outputs=None,
                js="""
                (fontSize) => {
                    document.documentElement.style.setProperty('--text-md', fontSize + 'px');
                    document.body.style.fontSize = fontSize + 'px';
                    return "配置已应用！";
                }
                """
            )

            reset_btn.click(
                None,
                inputs=[],
                outputs=[font_size_slider, status_text],
                js="""
                () => {
                    const fontSlider = document.querySelector('#font_size_slider input');
                    if (fontSlider) {
                        fontSlider.value = 16;
                        fontSlider.dispatchEvent(new Event('input'));
                    }
                    document.documentElement.style.setProperty('--text-md', '16px');
                    document.body.style.fontSize = '16px';
                    return [16, "已恢复默认配置！"];
                }
                """
            )

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## 开机自启")

            with gr.Group():
                autostart_cb = gr.Checkbox(
                    value=is_autostart_enabled(),
                    label="开机时自动启动此系统"
                )
                autostart_status = gr.Textbox(label="", interactive=False)

                def _toggle_autostart(enabled):
                    if enabled:
                        return enable_autostart()
                    else:
                        return disable_autostart()

                autostart_cb.change(
                    fn=_toggle_autostart,
                    inputs=[autostart_cb],
                    outputs=[autostart_status]
                )

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## 数据存储")

            with gr.Group():
                current_db = gr.Textbox(
                    value=get_db_path(),
                    label="当前数据库路径",
                    interactive=False
                )

                new_db_path = gr.Textbox(
                    value=get_db_path(),
                    label="新数据库路径",
                    placeholder="输入新的 .db 文件路径，支持绝对或相对路径"
                )

                switch_btn = gr.Button("切换并迁移数据", variant="primary")

                db_status = gr.Textbox(label="", interactive=False)

            switch_btn.click(
                fn=_migrate_and_switch,
                inputs=[new_db_path],
                outputs=[db_status]
            ).then(
                fn=lambda: get_db_path(),
                inputs=None,
                outputs=[current_db]
            )


__all__ = ['page_config']
