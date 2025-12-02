import gradio as gr

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
            
            # 使用Gradio的JS API来动态更新样式
            apply_btn.click(
                None,
                inputs=[font_size_slider],
                outputs=None,
                js="""
                (fontSize) => {
                    // 更新CSS变量
                    document.documentElement.style.setProperty('--text-md', fontSize + 'px');

                    // 更新body字体大小
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
                    // 重置滑块值
                    const fontSlider = document.querySelector('#font_size_slider input');
                    
                    // 触发输入事件以更新值
                    if (fontSlider) {
                        fontSlider.value = 16;
                        fontSlider.dispatchEvent(new Event('input'));
                    }

                    
                    // 重置CSS变量
                    document.documentElement.style.setProperty('--text-md', '16px');

                    // 重置body字体大小
                    document.body.style.fontSize = '16px';
                    
                    // 重置容器尺寸
                    const containers = document.querySelectorAll('.gradio-container');

                    
                    return [16, "已恢复默认配置！"];
                }
                """
            )

# 导出页面函数
__all__ = ['page_config']