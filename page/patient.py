from utils import *
import pandas as pd
import streamlit as st
import datetime
from io import BytesIO
# 获取医师下拉列表
def get_doctor_options():
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT doctor_id, name FROM doctors")
    doctors = c.fetchall()
    conn.close()
    return {f"{name} ({doctor_id})": doctor_id for doctor_id, name in doctors}

# 根据姓名和电话查询患者
def find_patient(name, phone):
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT patient_id FROM patients WHERE name = ? AND phone = ?", (name, phone))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# 添加患者
def add_patient(patient_id, name, gender, age, phone):
    conn = create_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO patients VALUES (?, ?, ?, ?, ?)", 
                 (patient_id, name, gender, age, phone))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
# 添加病例记录
def add_record(patient_id, doctor_id, visit_date, department, symptoms, diagnosis, treatment,cost, notes):
    conn = create_connection()
    c = conn.cursor()
    c.execute("INSERT INTO records (patient_id, doctor_id, visit_date, department, symptoms, diagnosis, treatment,cost, notes) VALUES (?, ?, ?, ?, ?, ?, ?,?, ?)", 
             (patient_id, doctor_id, visit_date, department, symptoms, diagnosis, treatment,cost, notes))
    conn.commit()
    conn.close()

# 获取所有病例记录
def get_all_records():
    conn = create_connection()
    query = """
    SELECT r.record_id, p.patient_id, p.name AS patient_name, p.gender, p.age,
           d.doctor_id, d.name AS doctor_name, d.department,
           r.visit_date, r.symptoms, r.diagnosis, r.treatment, r.cost,r.notes
    FROM records r
    JOIN patients p ON r.patient_id = p.patient_id
    JOIN doctors d ON r.doctor_id = d.doctor_id
    ORDER BY r.visit_date DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# 根据患者ID获取病例记录
def get_records_by_patient(patient_id):
    conn = create_connection()
    query = """
    SELECT r.record_id, p.patient_id, p.name AS patient_name, p.gender, p.age,
           d.doctor_id, d.name AS doctor_name, d.department,
           r.visit_date, r.symptoms, r.diagnosis, r.treatment, r.notes
    FROM records r
    JOIN patients p ON r.patient_id = p.patient_id
    JOIN doctors d ON r.doctor_id = d.doctor_id
    WHERE r.patient_id = ?
    ORDER BY r.visit_date DESC
    """
    df = pd.read_sql_query(query, conn, params=(patient_id,))
    conn.close()
    return df

# 根据医师ID获取病例记录
def get_records_by_doctor(doctor_id):
    conn = create_connection()
    query = """
    SELECT r.record_id, p.patient_id, p.name AS patient_name, p.gender, p.age,
           d.doctor_id, d.name AS doctor_name, d.department,
           r.visit_date, r.symptoms, r.diagnosis, r.treatment, r.notes
    FROM records r
    JOIN patients p ON r.patient_id = p.patient_id
    JOIN doctors d ON r.doctor_id = d.doctor_id
    WHERE r.doctor_id = ?
    ORDER BY r.visit_date DESC
    """
    df = pd.read_sql_query(query, conn, params=(doctor_id,))
    conn.close()
    return df

# 根据条件搜索病例
def search_records(option, query):
    print(option, query)
    conn = create_connection()
    if option == "患者ID":
        sql = """
        SELECT r.record_id, p.patient_id, p.name AS patient_name, p.gender, p.age,
               d.doctor_id, d.name AS doctor_name, d.department,
               r.visit_date, r.symptoms, r.diagnosis, r.treatment, r.notes
        FROM records r
        JOIN patients p ON r.patient_id = p.patient_id
        JOIN doctors d ON r.doctor_id = d.doctor_id
        WHERE r.patient_id = ?
        ORDER BY r.visit_date DESC
        """
        df = pd.read_sql_query(sql, conn, params=(query,))
    
    elif option == "患者姓名":
        sql = """
        SELECT r.record_id, p.patient_id, p.name AS patient_name, p.gender, p.age,
               d.doctor_id, d.name AS doctor_name, d.department,
               r.visit_date, r.symptoms, r.diagnosis, r.treatment, r.notes
        FROM records r
        JOIN patients p ON r.patient_id = p.patient_id
        JOIN doctors d ON r.doctor_id = d.doctor_id
        WHERE p.name LIKE ?
        ORDER BY r.visit_date DESC
        """
        df = pd.read_sql_query(sql, conn, params=(f"%{query}%",))
    
    elif option == "医师ID":
        sql = """
        SELECT r.record_id, p.patient_id, p.name AS patient_name, p.gender, p.age,
               d.doctor_id, d.name AS doctor_name, d.department,
               r.visit_date, r.symptoms, r.diagnosis, r.treatment, r.notes
        FROM records r
        JOIN patients p ON r.patient_id = p.patient_id
        JOIN doctors d ON r.doctor_id = d.doctor_id
        WHERE r.doctor_id = ?
        ORDER BY r.visit_date DESC
        """
        df = pd.read_sql_query(sql, conn, params=(query,))
    
    elif option == "医师姓名":
        sql = """
        SELECT r.record_id, p.patient_id, p.name AS patient_name, p.gender, p.age,
               d.doctor_id, d.name AS doctor_name, d.department,
               r.visit_date, r.symptoms, r.diagnosis, r.treatment, r.notes
        FROM records r
        JOIN patients p ON r.patient_id = p.patient_id
        JOIN doctors d ON r.doctor_id = d.doctor_id
        WHERE d.name LIKE ?
        ORDER BY r.visit_date DESC
        """
        df = pd.read_sql_query(sql, conn, params=(f"%{query}%",))
    
    elif option == "科室":
        sql = """
        SELECT r.record_id, p.patient_id, p.name AS patient_name, p.gender, p.age,
               d.doctor_id, d.name AS doctor_name, d.department,
               r.visit_date, r.symptoms, r.diagnosis, r.treatment, r.notes
        FROM records r
        JOIN patients p ON r.patient_id = p.patient_id
        JOIN doctors d ON r.doctor_id = d.doctor_id
        WHERE r.department LIKE ?
        ORDER BY r.visit_date DESC
        """
        df = pd.read_sql_query(sql, conn, params=(f"%{query}%",))
    
    elif option == "就诊日期":
        sql = """
        SELECT r.record_id, p.patient_id, p.name AS patient_name, p.gender, p.age,
               d.doctor_id, d.name AS doctor_name, d.department,
               r.visit_date, r.symptoms, r.diagnosis, r.treatment, r.notes
        FROM records r
        JOIN patients p ON r.patient_id = p.patient_id
        JOIN doctors d ON r.doctor_id = d.doctor_id
        WHERE r.visit_date LIKE ?
        ORDER BY r.visit_date DESC
        """
        df = pd.read_sql_query(sql, conn, params=(f"%{query}%",))
    
    conn.close()
    return df

# 删除病例记录
def delete_record(record_id):
    conn = create_connection()
    c = conn.cursor()
    c.execute("DELETE FROM records WHERE record_id = ?", (record_id,))
    conn.commit()
    conn.close()

# 更新患者信息
def update_patient(patient_id, name, gender, age, phone):
    conn = create_connection()
    c = conn.cursor()
    c.execute("""
    UPDATE patients 
    SET name = ?, gender = ?, age = ?, phone = ?
    WHERE patient_id = ?
    """, (name, gender, age, phone, patient_id))
    conn.commit()
    conn.close()

def page_patient(page):
    if page == "添加病例":
        st.subheader("添加新病例")
        
        # 表单布局
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("患者姓名*", placeholder="输入患者姓名")
            gender = st.selectbox("性别*", ["男", "女", "其他"])
            age = st.number_input("年龄*", min_value=0, max_value=150, step=1)
            phone = st.text_input("联系电话", placeholder="输入手机号码")
            
            
        with col2:
            date = st.date_input("就诊日期*", datetime.date.today())
            department = st.selectbox("科室*", ["内科", "外科", "儿科", "妇科", "眼科", "口腔科", "皮肤科"])
            
            # 获取医师列表
            doctor_options = get_doctor_options()
            if not doctor_options:
                st.warning("请先添加医师！")
                st.stop()
                
            doctor_selection = st.selectbox("主治医生*", list(doctor_options.keys()))
            doctor_id = doctor_options[doctor_selection]
        
        symptoms = st.text_area("症状描述*", placeholder="详细描述患者症状")
        diagnosis = st.text_area("诊断结果*", placeholder="填写诊断结果")
        treatment = st.text_area("治疗方案", placeholder="填写治疗方案")
        cost = st.text_input("收费", placeholder="请输入费用")
        notes = st.text_area("备注", placeholder="填写其他需要记录的信息")
        
        # 保存按钮
        if st.button("保存病例"):
            if not name or not gender or age == 0  or not symptoms or not diagnosis:
                st.error("带*的字段为必填项，请确保填写完整。")
            else:
                # 检查患者是否已存在
                patient_id = find_patient(name, phone)
                
                if not patient_id:
                    # 患者不存在，生成新的患者ID
                    patient_id = generate_id("PAT")
                    add_patient(patient_id, name, gender, age, phone)
                    st.info(f"已为新患者创建ID: {patient_id}")
                else:
                    # 患者已存在，更新患者信息
                    update_patient(patient_id, name, gender, age, phone)
                    st.info(f"找到现有患者，ID: {patient_id}")
                
                # 添加病例记录
                visit_date = date.strftime("%Y-%m-%d")
                add_record(patient_id, doctor_id, visit_date, department, symptoms, diagnosis, treatment, cost,notes)
                
                st.success("病例记录已保存！")
                
                # 显示患者ID和记录详情
                st.subheader("记录详情")
                st.write(f"患者ID: {patient_id}")
                st.write(f"患者姓名: {name}")
                st.write(f"医师ID: {doctor_id}")
                st.write(f"医师姓名: {doctor_selection.split(' ')[0]}")
                st.write(f"就诊日期: {visit_date}")
    
    elif page == "查看病例":
        st.subheader("病例记录列表")
        
        # 获取所有记录
        records_df = get_all_records()
        
        if records_df.empty:
            st.info("暂无病例记录，请先添加病例。")
        else:
            # 显示记录表格
            st.dataframe(records_df, use_container_width=True)
            
            # 分页显示
            records_per_page = 10
            total_pages = len(records_df) // records_per_page + (1 if len(records_df) % records_per_page != 0 else 0)
            
            if total_pages > 1:
                col1, col2, col3 = st.columns([1, 1, 1])
                current_page = col2.number_input("页码", min_value=1, max_value=total_pages, value=1)
                
                start_idx = (current_page - 1) * records_per_page
                end_idx = min(start_idx + records_per_page, len(records_df))
                
                st.dataframe(records_df.iloc[start_idx:end_idx], use_container_width=True)
            
            # 删除功能
            st.subheader("删除病例记录")
            record_id = st.number_input("输入要删除的记录ID", min_value=1)
            
            if st.button("删除记录"):
                delete_record(record_id)
                st.success(f"记录ID {record_id} 已删除！")
                st.experimental_rerun()
    
    elif page == "搜索病例":
        st.subheader("搜索病例记录")
        
        search_option = st.selectbox("搜索条件", ["患者姓名","患者ID",  "医师ID", "医师姓名", "科室", "就诊日期"])
        search_query = st.text_input(f"输入{search_option}")
        
        if st.button("搜索"):
            # if not search_query:
            #     st.warning("请输入搜索内容。")
            # else:
            results_df = search_records(search_option, search_query)
            
            if results_df.empty:
                st.info(f"未找到符合条件的病例记录。")
            else:
                st.success(f"找到 {len(results_df)} 条记录")
                st.dataframe(results_df, use_container_width=True)
    
    elif page == "导出数据":
        st.subheader("导出病例数据")
        
        # 获取所有记录
        records_df = get_all_records()
        
        if records_df.empty:
            st.info("暂无病例记录，无法导出。")
        else:
            # 导出为CSV
            csv = records_df.to_csv(sep='\t', na_rep='nan')
            st.download_button(
                label="下载CSV文件",
                data=csv,
                file_name="病例记录.csv",
                mime="text/csv"
            )
            
            # 创建Excel文件
            def to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='病例记录', index=False)
                output.seek(0)
                return output
            
            excel_file = to_excel(records_df)
            st.download_button(
                label="下载Excel文件",
                data=excel_file,
                file_name="病例记录.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            # 数据统计
            # st.subheader("数据统计")
            
            # col1, col2, col3 = st.columns(3)
            # col1.metric("总病例数", len(records_df))
            
            # # 性别分布
            # patients_df = get_all_patients()
            # if not patients_df.empty:
            #     gender_distribution = patients_df['gender'].value_counts().to_dict()
            #     col2.metric("性别分布", ", ".join([f"{k}: {v}" for k, v in gender_distribution.items()]))
            
            # # 科室分布
            # if not records_df['department'].empty:
            #     department_distribution = records_df['department'].value_counts().to_dict()
            #     col3.metric("科室分布", ", ".join([f"{k}: {v}" for k, v in department_distribution.items()]))
            
            # # 图表展示
            # st.subheader("数据可视化")
            
            # # 性别分布饼图
            # if not patients_df.empty and not patients_df['gender'].empty:
            #     st.pyplot(patients_df['gender'].value_counts().plot(kind='pie', autopct='%1.1f%%', title='性别分布').figure)
            
            # # 科室分布柱状图
            # if not records_df['department'].empty:
            #     st.pyplot(records_df['department'].value_counts().plot(kind='bar', title='科室分布').figure)
            
            # # 年龄分布直方图
            # if not patients_df.empty and not patients_df['age'].empty:
            #     st.pyplot(patients_df['age'].plot(kind='hist', bins=10, title='年龄分布').figure)