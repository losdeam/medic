import streamlit as st
import pandas as pd
import datetime

import os
from io import BytesIO
from utils import init_tables
from page import page_doc,page_patient
import streamlit.web.cli as stcli
import sys
# 确保中文显示正常
st.set_page_config(page_title="病例记录系统", layout="wide")


init_tables()

# 页面标题和描述
st.title("简易病例记录系统")
st.markdown("这是一个用于记录和管理患者病例的简单系统，支持添加、查看、搜索和导出病例记录。")

# 侧边栏 - 功能选择
with st.sidebar:
    st.header("功能导航")
    module = st.radio("选择模块:", ["病例管理", "医师管理"])
    
    if module == "病例管理":
        page = st.radio("请选择功能:", ["添加病例", "查看病例", "搜索病例", "导出数据"])
    else:
        page = st.radio("请选择功能:", ["添加医师", "查看医师", "编辑医师", "删除医师"])

# 主页面内容
if module == "病例管理":
    page_patient(page)
else:  # 医师管理模块
    page_doc(page)

