import gradio as gr
from page.patient import page_patient
from page.doc import page_doc
from page.config.page_config import page_config
from page.dashboard import render_dashboard
from utils import init_tables

THEME_CSS = """
:root {
    --primary: #1a56db;
    --primary-dark: #1344b0;
    --primary-light: #e8effd;
    --success: #059669;
    --success-light: #ecfdf5;
    --warning: #d97706;
    --warning-light: #fffbeb;
    --danger: #dc2626;
    --danger-light: #fef2f2;
    --bg: #f1f5f9;
    --card: #ffffff;
    --text: #0f172a;
    --text-secondary: #475569;
    --border: #e2e8f0;
    --radius: 12px;
    --radius-sm: 8px;
    --shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
    --shadow-lg: 0 10px 25px rgba(0,0,0,0.08);
    --sidebar-w: 220px;
}

.gradio-container {
    max-width: 100% !important;
    background: var(--bg) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
    color: var(--text) !important;
}

/* ===== Sidebar ===== */
.sidebar-wrap {
    background: linear-gradient(180deg, #1a56db 0%, #1344b0 40%, #0f3a96 100%) !important;
    border-radius: 0 var(--radius) var(--radius) 0 !important;
    padding: 0 !important;
    min-height: 100vh !important;
    box-shadow: 4px 0 20px rgba(0,0,0,0.1) !important;
    position: sticky !important;
    top: 0 !important;
    display: flex !important;
    flex-direction: column !important;
}

.sidebar-brand {
    padding: 32px 20px 24px;
    text-align: center;
    border-bottom: 1px solid rgba(255,255,255,0.12);
}

.sidebar-brand .logo-icon {
    width: 48px;
    height: 48px;
    background: rgba(255,255,255,0.15);
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 12px;
    backdrop-filter: blur(4px);
}

.sidebar-brand h2 {
    color: #fff;
    font-size: 16px;
    font-weight: 600;
    margin: 0 0 4px;
    letter-spacing: 0.5px;
}

.sidebar-brand p {
    color: rgba(255,255,255,0.6);
    font-size: 12px;
    margin: 0;
}

.sidebar-nav {
    padding: 16px 12px;
    flex: 1;
}

.sidebar-nav .nav-label {
    color: rgba(255,255,255,0.4);
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 16px 12px 8px;
    display: block;
}

.nav-btn {
    background: transparent !important;
    color: rgba(255,255,255,0.8) !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
    margin: 2px 0 !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    text-align: left !important;
    width: 100% !important;
    justify-content: flex-start !important;
    box-shadow: none !important;
    transition: all 0.2s !important;
    gap: 10px !important;
}

.nav-btn:hover {
    background: rgba(255,255,255,0.12) !important;
    color: #fff !important;
    transform: translateX(3px) !important;
}

.nav-btn.gr-button-primary {
    background: rgba(255,255,255,0.18) !important;
    color: #fff !important;
    box-shadow: inset 3px 0 0 #fff !important;
}

.sidebar-footer {
    padding: 16px 12px;
    border-top: 1px solid rgba(255,255,255,0.08);
}

.sidebar-footer .nav-btn {
    font-size: 12px !important;
    padding: 10px 16px !important;
}

/* ===== Main Content ===== */
.main-content-wrap {
    padding: 0 !important;
}

.content-header {
    padding: 24px 32px 12px;
    background: var(--card);
    border-bottom: 1px solid var(--border);
}

.content-header h1 {
    font-size: 22px;
    font-weight: 700;
    color: var(--text);
    margin: 0;
}

.content-header p {
    font-size: 13px;
    color: var(--text-secondary);
    margin: 4px 0 0;
}

.content-body {
    padding: 20px 24px;
}

.content-panel {
    background: var(--card) !important;
    border-radius: var(--radius) !important;
    padding: 20px 24px !important;
    box-shadow: var(--shadow) !important;
}

/* ===== Section Title ===== */
.section-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 15px;
    font-weight: 600;
    color: var(--text);
    margin: 20px 0 12px;
    padding-bottom: 8px;
    border-bottom: 2px solid var(--primary-light);
}

.section-title svg {
    color: var(--primary);
    flex-shrink: 0;
}

/* ===== Stats Grid ===== */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 24px;
}

.stat-card {
    background: var(--card);
    border-radius: var(--radius);
    padding: 20px 24px;
    box-shadow: var(--shadow);
    border-left: 4px solid var(--primary);
    transition: transform 0.2s, box-shadow 0.2s;
    position: relative;
    overflow: hidden;
}

.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

.stat-card .stat-label {
    font-size: 13px;
    color: var(--text-secondary);
    margin: 0 0 6px;
    font-weight: 500;
}

.stat-card .stat-value {
    font-size: 30px;
    font-weight: 700;
    color: var(--text);
    margin: 0;
    line-height: 1.2;
}

.stat-card .stat-icon {
    position: absolute;
    top: 16px;
    right: 16px;
    opacity: 0.1;
    color: var(--primary);
}

.stat-card.patients { border-left-color: #1a56db; }
.stat-card.doctors { border-left-color: #059669; }
.stat-card.records { border-left-color: #7c3aed; }
.stat-card.today { border-left-color: #d97706; }
.stat-card.attention { border-left-color: #dc2626; }

/* ===== Gradio Tab Overrides ===== */
.tabs {
    border: none !important;
    background: transparent !important;
}

.tabs > .tab-nav {
    background: var(--bg) !important;
    border-bottom: 1px solid var(--border) !important;
    border-radius: 8px 8px 0 0 !important;
    padding: 0 4px !important;
    gap: 0 !important;
}

.tabs > .tab-nav button {
    background: transparent !important;
    border: none !important;
    color: var(--text-secondary) !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 10px 18px !important;
    margin: 4px 2px 0 !important;
    transition: all 0.2s !important;
    border-radius: 6px 6px 0 0 !important;
    position: relative !important;
}

.tabs > .tab-nav button:hover {
    color: var(--primary) !important;
    background: rgba(26, 86, 219, 0.06) !important;
}

.tabs > .tab-nav button.selected {
    color: var(--primary) !important;
    background: var(--card) !important;
    font-weight: 600 !important;
    box-shadow: 0 -1px 3px rgba(0,0,0,0.06) !important;
}

.tabs > .tab-body {
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
    padding: 20px 24px !important;
    background: var(--card) !important;
}

/* ===== Nested tabs (inside content-panel) ===== */
.content-panel .tabs > .tab-nav {
    margin: -20px -24px 0 !important;
    padding: 4px 24px 0 !important;
    border-radius: 0 !important;
}

.content-panel .tabs > .tab-nav button.selected {
    box-shadow: none !important;
}

.content-panel .tabs > .tab-body {
    margin: 0 -24px -20px !important;
    border-left: none !important;
    border-right: none !important;
    border-bottom: none !important;
    border-radius: 0 !important;
    padding: 20px 0 !important;
}

/* Form components */
label, .label-text, .gr-form-label, .label-wrap span {
    font-size: 13px !important;
    font-weight: 600 !important;
    color: var(--text) !important;
}

input, textarea, select, .dropdown, .input-wrap, .gr-input {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    font-size: 14px !important;
    padding: 8px 12px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
    background: var(--card) !important;
    color: var(--text) !important;
}

input:focus, textarea:focus, select:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 2px var(--primary-light) !important;
    outline: none !important;
}

/* Buttons */
button, .gr-button {
    border-radius: var(--radius-sm) !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 8px 20px !important;
    transition: all 0.2s !important;
    border: 1px solid var(--border) !important;
    background: var(--card) !important;
    color: var(--text) !important;
}

.gr-button-primary, button.gr-button-primary {
    background: var(--primary) !important;
    color: #fff !important;
    border: 1px solid var(--primary) !important;
}

.gr-button-primary:hover {
    background: var(--primary-dark) !important;
    box-shadow: 0 4px 12px rgba(26, 86, 219, 0.3) !important;
}

.gr-button-secondary {
    background: var(--card) !important;
    color: var(--text) !important;
}

.gr-button-secondary:hover {
    background: var(--bg) !important;
}

/* Dataframe / table */
table, .dataframe {
    border-collapse: separate !important;
    border-spacing: 0 !important;
    width: 100% !important;
    font-size: 13px !important;
}

.dataframe th, table th {
    background: var(--bg) !important;
    color: var(--text-secondary) !important;
    font-weight: 600 !important;
    font-size: 12px !important;
    letter-spacing: 0.3px !important;
    padding: 10px 12px !important;
    border-bottom: 2px solid var(--border) !important;
    text-align: left !important;
    white-space: nowrap !important;
}

.dataframe td, table td {
    padding: 9px 12px !important;
    border-bottom: 1px solid var(--border) !important;
    color: var(--text) !important;
}

.dataframe tr:hover td, table tr:hover td {
    background: var(--primary-light) !important;
}

/* Accordion */
.accordion {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    margin: 12px 0 !important;
}

.accordion > .accordion-header {
    background: var(--bg) !important;
    padding: 12px 16px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
}

/* Checkbox & Radio */
.gr-checkbox {
    accent-color: var(--primary) !important;
}

.gr-radio {
    accent-color: var(--primary) !important;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

::-webkit-scrollbar-track {
    background: transparent;
}

::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--text-secondary);
}

/* ===== Responsive ===== */
@media (max-width: 768px) {
    .stats-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    .content-body {
        padding: 16px;
    }
    .sidebar-wrap {
        min-height: auto !important;
    }
}

@media (max-width: 480px) {
    .stats-grid {
        grid-template-columns: 1fr;
    }
}

/* Success message styling */
.gr-success {
    background: var(--success-light) !important;
    color: var(--success) !important;
    border: 1px solid var(--success) !important;
    border-radius: var(--radius-sm) !important;
    padding: 12px 16px !important;
    font-weight: 500 !important;
}

"""


def create_interface():
    init_tables()

    with gr.Blocks(css=THEME_CSS, title="医疗病例管理系统", theme=gr.themes.Soft()) as app:
        active_view = gr.State(0)

        with gr.Row(equal_height=False, elem_classes="app-layout"):
            # ===== Sidebar =====
            with gr.Column(scale=1, elem_classes="sidebar-wrap", min_width=200):
                gr.HTML('''
                <div class="sidebar-brand">
                    <div class="logo-icon">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                            <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
                        </svg>
                    </div>
                    <h2>MedicSys</h2>
                    <p>医疗病例管理系统</p>
                </div>
                <div class="sidebar-nav">
                    <span class="nav-label">导航菜单</span>
                ''')

                dashboard_btn = gr.Button("📊 数据概览", elem_classes="nav-btn", elem_id="nav-dashboard")
                patient_btn = gr.Button("📋 病例管理", elem_classes="nav-btn", elem_id="nav-patient", variant="primary")
                doctor_btn = gr.Button("👨‍⚕️ 医师管理", elem_classes="nav-btn", elem_id="nav-doctor")
                config_btn = gr.Button("⚙️ 系统配置", elem_classes="nav-btn", elem_id="nav-config")

                gr.HTML('</div>')

            # ===== Main Content =====
            with gr.Column(scale=4, elem_classes="main-content-wrap"):
                # Header area
                header_html = gr.HTML('''
                <div class="content-header">
                    <h1>病例管理</h1>
                    <p>管理患者病例记录 · 添加 / 查询 / 编辑 / 导入导出</p>
                </div>
                ''')

                body_html_container = gr.Column(elem_classes="content-body")

                with body_html_container:
                    dashboard_view = gr.Column(visible=False, elem_classes="content-panel")
                    with dashboard_view:
                        render_dashboard()

                    patient_view = gr.Column(visible=True, elem_classes="content-panel")
                    with patient_view:
                        page_patient()

                    doctor_view = gr.Column(visible=False, elem_classes="content-panel")
                    with doctor_view:
                        page_doc()

                    config_view = gr.Column(visible=False, elem_classes="content-panel")
                    with config_view:
                        page_config()

        # ===== Navigation Events =====
        def switch_view(view_num):
            headers = [
                ("数据概览", "医疗病例管理系统 · 仪表盘"),
                ("病例管理", "管理患者病例记录 · 添加 / 查询 / 编辑 / 导入导出"),
                ("医师管理", "管理医师信息 · 添加 / 查询 / 编辑 / 删除"),
                ("系统配置", "系统设置 · 界面 / 数据存储 / 开机自启"),
            ]
            title, desc = headers[view_num]
            header = f'<div class="content-header"><h1>{title}</h1><p>{desc}</p></div>'
            vis = [gr.update(visible=(i == view_num)) for i in range(4)]
            return [header, *vis]

        nav_btns = [dashboard_btn, patient_btn, doctor_btn, config_btn]

        for btn, idx in [(dashboard_btn, 0), (patient_btn, 1), (doctor_btn, 2), (config_btn, 3)]:
            btn.click(
                fn=lambda v=idx: switch_view(v),
                outputs=[header_html, dashboard_view, patient_view, doctor_view, config_view]
            ).then(
                fn=lambda v=idx: [
                    gr.update(variant="primary" if i == v else "secondary")
                    for i in range(4)
                ],
                outputs=nav_btns
            )

    return app


if __name__ == "__main__":
    for port in range(8501, 8601):
        try:
            app = create_interface()
            print(f"[*] 启动服务: http://localhost:{port}")
            app.launch(server_name="0.0.0.0", server_port=port, debug=True)
            break
        except OSError:
            print(f"[!] 端口 {port} 被占用，尝试下一个...")
            continue
    else:
        print("[错误] 8501-8600 端口均被占用")
