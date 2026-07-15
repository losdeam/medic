import gradio as gr
from utils import create_connection, init_tables
import datetime
import pandas as pd


def get_dashboard_stats():
    conn = create_connection()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM patients")
    patient_count = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM doctors")
    doctor_count = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM records")
    record_count = c.fetchone()[0]

    today = datetime.datetime.now().strftime('%Y-%m-%d')
    c.execute("SELECT COUNT(*) FROM records WHERE visit_date LIKE ?", (f"{today}%",))
    today_count = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM patients WHERE attention_flag = 1")
    attention_count = c.fetchone()[0]

    conn.close()

    return patient_count, doctor_count, record_count, today_count, attention_count


def render_stats_html():
    pc, dc, rc, tc, ac = get_dashboard_stats()
    html = f'''
    <div class="stats-grid">
        <div class="stat-card patients">
            <div class="stat-icon">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="8.5" cy="7" r="4"/><path d="M20 8v6M23 11h-6"/></svg>
            </div>
            <p class="stat-label">患者总数</p>
            <p class="stat-value">{pc}</p>
        </div>
        <div class="stat-card doctors">
            <div class="stat-icon">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21v-2a4 4 0 00-4-4H9a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/><path d="M12 3v8M8 7h8"/></svg>
            </div>
            <p class="stat-label">医师总数</p>
            <p class="stat-value">{dc}</p>
        </div>
        <div class="stat-card records">
            <div class="stat-icon">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
            </div>
            <p class="stat-label">病例总数</p>
            <p class="stat-value">{rc}</p>
        </div>
        <div class="stat-card today">
            <div class="stat-icon">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/><circle cx="12" cy="16" r="1"/></svg>
            </div>
            <p class="stat-label">今日就诊</p>
            <p class="stat-value">{tc}</p>
        </div>
    </div>
    <div class="stats-grid" style="grid-template-columns: repeat(1, 1fr);">
        <div class="stat-card attention" style="border-left-color: #dc3545;{'' if ac == 0 else 'background: #fff5f5;'}">
            <div class="stat-icon">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            </div>
            <p class="stat-label">重点关注患者</p>
            <p class="stat-value" style="color: #dc3545;">{ac}</p>
        </div>
    </div>
    '''
    return html


def get_recent_records(limit=8):
    conn = create_connection()
    c = conn.cursor()
    c.execute('''
    SELECT r.id, p.name AS patient_name, p.attention_flag,
           d.name AS doctor_name, r.department, r.visit_date, r.diagnosis
    FROM records r
    JOIN patients p ON r.patient_id = p.patient_id
    JOIN doctors d ON r.doctor_id = d.doctor_id
    ORDER BY r.visit_date DESC
    LIMIT ?
    ''', (limit,))
    rows = c.fetchall()
    conn.close()

    if not rows:
        return pd.DataFrame(columns=['患者姓名', '医师', '科室', '就诊日期', '诊断'])

    records = []
    for r in rows:
        records.append({
            '患者姓名': r['patient_name'],
            '医师': r['doctor_name'],
            '科室': r['department'],
            '就诊日期': r['visit_date'],
            '诊断': r['diagnosis'][:30] + '...' if len(r['diagnosis']) > 30 else r['diagnosis'],
        })
    return pd.DataFrame(records)


def render_dashboard():
    init_tables()

    stats_html = gr.HTML(render_stats_html())
    gr.HTML('<div class="section-title"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg> 最近病例记录</div>')
    recent_df = gr.Dataframe(get_recent_records(), max_height=320, show_label=False)

    refresh_btn = gr.Button("🔄 刷新数据", variant="secondary")
    refresh_btn.click(
        fn=render_stats_html,
        outputs=stats_html
    ).then(
        fn=get_recent_records,
        outputs=recent_df
    )

__all__ = ['render_dashboard', 'get_dashboard_stats']
