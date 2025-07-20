import streamlit as st
from utils import *
import pandas as pd

# 添加医师
def add_doctor(doctor_id, name, department, title, phone, email):
    db = create_connection()
    try:
        db['doctors'].insert_one({
            'doctor_id': doctor_id,
            'name': name,
            'department': department,
            'title': title,
            'phone': phone,
            'email': email
        })
        return True
    except Exception:
        return False

# 更新医师信息
def update_doctor(doctor_id, name, department, title, phone, email):
    db = create_connection()
    db['doctors'].update_one(
        {'doctor_id': doctor_id},
        {'$set': {
            'name': name,
            'department': department,
            'title': title,
            'phone': phone,
            'email': email
        }}
    )

# 检查医师是否存在
def exsit_doctor(name):
    db = create_connection()
    doctor = db['doctors'].find_one({'name': name})
    return doctor

# 删除医师
def delete_doctor(doctor_id):
    db = create_connection()
    # 先删除关联的病例记录
    db['records'].delete_many({'doctor_id': doctor_id})
    # 再删除医师
    db['doctors'].delete_one({'doctor_id': doctor_id})

# 获取所有医师
def get_all_doctors():
    db = create_connection()
    doctors = db['doctors'].find()
    df = pd.DataFrame(list(doctors))
    return df

def page_doc(page):
    if page == "添加医师":
        st.subheader("添加新医师")

        name = st.text_input("医师姓名*", placeholder="输入医师姓名")
        department = st.selectbox("所属科室*", ["内科", "外科", "儿科", "妇科", "眼科", "口腔科", "皮肤科"])
        title = st.text_input("职称", placeholder="输入医师职称")
        phone = st.text_input("联系电话", placeholder="输入手机号码")
        email = st.text_input("电子邮箱", placeholder="输入电子邮箱")

        if st.button("添加医师"):
            if not name or not department:
                st.error("带*的字段为必填项，请确保填写完整。")
            else:
                if exsit_doctor(name):
                    st.error("已存在同名医师，请检查输入。")
                doctor_id = generate_id("DOC")
                if add_doctor(doctor_id, name, department, title, phone, email):
                    st.success(f"新医师已添加，ID: {doctor_id}")
                    st.rerun()
                else:
                    st.error("添加医师失败，请检查输入。")

    elif page == "查看医师":
        st.subheader("医师列表")

        doctors_df = get_all_doctors()

        if doctors_df.empty:
            st.info("暂无医师信息，请先添加医师。")
        else:
            st.dataframe(doctors_df, use_container_width=True)

    elif page == "编辑医师":
        st.subheader("编辑医师信息")

        doctors_df = get_all_doctors()

        if doctors_df.empty:
            st.info("暂无医师信息，请先添加医师。")
        else:
            doctor_id = st.selectbox("选择要编辑的医师", doctors_df['doctor_id'].tolist())

            # 获取当前医师信息
            doctor_info = doctors_df[doctors_df['doctor_id'] == doctor_id].iloc[0]

            name = st.text_input("医师姓名", doctor_info['name'])
            department = st.selectbox("所属科室", ["内科", "外科", "儿科", "妇科", "眼科", "口腔科", "皮肤科"],
                                      ["内科", "外科", "儿科", "妇科", "眼科", "口腔科", "皮肤科"].index(
                                          doctor_info['department']))
            title = st.text_input("职称", doctor_info['title'])
            phone = st.text_input("联系电话", doctor_info['phone'])
            email = st.text_input("电子邮箱", doctor_info['email'])

            if st.button("保存修改"):
                update_doctor(doctor_id, name, department, title, phone, email)
                st.success("医师信息已更新！")
                st.experimental_rerun()

    elif page == "删除医师":
        st.subheader("删除医师")

        doctors_df = get_all_doctors()

        if doctors_df.empty:
            st.info("暂无医师信息，请先添加医师。")
        else:
            doctor_id = st.selectbox("选择要删除的医师", doctors_df['doctor_id'].tolist())

            if st.button("确认删除"):
                delete_doctor(doctor_id)
                st.success("医师信息已删除！")
                st.experimental_rerun()