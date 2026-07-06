import streamlit as st
import pandas as pd
import os
import qrcode
from PIL import Image
import io

# 页面基础全局配置
st.set_page_config(page_title="赣州富硒农产品产销便民服务平台", layout="wide")
st.title("赣州富硒农产品产销便民服务平台")

# 读取CSV，兼容Windows中文编码
df = pd.read_csv("data.csv", encoding="gbk")
st.success("数据加载完成，可切换下方板块查看对应内容")

# 左侧身份下拉选择
identity = st.selectbox("请选择您的身份", ["消费者（购买用户）", "经销商（收购商）", "农户（种植户）"])

# ---------------------- 1、消费者板块：表格保留 + 下方图文百科 ----------------------
if identity == "消费者（购买用户）":
    st.header("🛒 消费者产品选购专区")
    st.subheader("全部富硒农产品介绍与售价（完整数据表）")
    # 【保留原始完整表格，不删除】
    consumer_df = df[["产品名称", "产品分类", "产地", "单价", "富硒等级", "上市季节"]]
    st.dataframe(consumer_df, use_container_width=True)

    st.divider()
    st.subheader("📖 农产品百科图文详情（下方可查看单品图文介绍）")
    st.markdown("每条数据自动匹配对应产品图片，信息全部读取自表格")
    st.divider()

    # 循环读取CSV每一行数据，生成图文卡片
    for index, row in df.iterrows():
        product_name = row["产品名称"]
        # 拼接本地图片路径（你自己存放图片的文件夹）
        img_path = f"./product_img/{product_name}.jpg"

        col1, col2 = st.columns([1, 3])
        with col1:
            # 判断图片是否存在，不存在则展示默认占位图
            if os.path.exists(img_path):
                st.image(img_path, width=220, caption=product_name)
            else:
                st.image("https://img0.baidu.com/it/u=3511123102,3922111230&fm=253&fmt=auto&app=138&f=JPEG?w=800&h=800", width=220, caption="暂无自定义产品图")

        with col2:
            st.subheader(f"【{product_name}】产品详情")
            # 自动从表格读取所有数据，以文字展示
            st.markdown(f"""
            - 产品分类：{row['产品分类']}
            - 原产地：{row['产地']}
            - 零售单价：{row['单价']}
            - 富硒品质等级：{row['富硒等级']}
            - 最佳采购/上市时段：{row['上市季节']}
            """)
            st.info(f"选购说明：{product_name}产自赣州富硒土壤产区，天然富含硒元素，推荐在{row['上市季节']}采购，新鲜度更高。")
        st.divider()

# ---------------------- 2、经销商板块（原有表格完全不变） ----------------------
elif identity == "经销商（收购商）":
    st.header("🤝 经销商收购参考专区")
    st.subheader("全部富硒农产品产地、单价、供货销量明细")
    dealer_df = df[["产品名称", "产品分类", "产地", "单价", "月度销量"]]
    st.dataframe(dealer_df, use_container_width=True)
    

# ---------------------- 3、农户板块：县域筛选 + 溯源二维码智能体 ----------------------
elif identity == "农户（种植户）":
    st.header("👨‍🌾 农户种植参考专区")
    # 下拉选择种植县域
    all_county = df["产地"].unique()
    select_county = st.selectbox("请选择您的种植县城", all_county)
    # 筛选出当前县城所有产品数据
    county_all_product = df[df["产地"] == select_county]

    st.subheader(f"【{select_county}】全部种植产品明细")
    # 展示本县每一款产品完整信息（名称/分类/单价/销量）
    st.dataframe(county_all_product[["产品名称", "产品分类", "单价", "月度销量"]], use_container_width=True)

            # ========== 农产品溯源智能体（微信兼容最简文本版，无加载空白） ==========
    st.divider()
    st.header("🤖 农产品溯源智能体（包装打印专用）")
    st.markdown("功能说明：生成精简溯源二维码，扫码一键复制全部产品档案，无需跳转网页、无图片加载失败问题")

    # 仅展示当前县城产品
    trace_product = st.selectbox("选择需要生成溯源码的本县农产品", county_all_product["产品名称"].unique())
    trace_info = county_all_product[county_all_product["产品名称"] == trace_product].iloc[0]

    # 极致压缩单行文本，无换行、无多余符号，最大程度避免扫码解析崩溃
    trace_data = f"赣南富硒溯源｜品名:{trace_info['产品名称']};品类:{trace_info['产品分类']};产地:{trace_info['产地']};富硒等级:{trace_info['富硒等级']};上市季:{trace_info['上市季节']};单价:{trace_info['单价']}元/斤;月供货:{trace_info['月度销量']}斤;产地直供无中间商"

    # 低容量、大尺寸二维码，打印清晰识别稳定
    qr = qrcode.QRCode(version=1, box_size=14, border=5)
    qr.add_data(trace_data)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="#006400", back_color="white")

    buffer = io.BytesIO()
    qr_image.save(buffer, format="PNG")
    buffer.seek(0)

    col_qr, col_text = st.columns([1, 2])
    with col_qr:
        st.image(buffer, caption=f"{trace_product} 溯源二维码")
        st.download_button(
            label="下载二维码打印贴纸",
            data=buffer,
            file_name=f"{trace_info['产地']}_{trace_product}_溯源码.png",
            mime="image/png"
        )
    with col_text:
        st.subheader("消费者扫码操作步骤（无加载失败）")
        st.markdown("""
        1. 打开微信右上角「+」→ 扫一扫贴纸（不要长按相册识别）
        2. 页面底部点击【复制文本内容】
        3. 粘贴到微信对话框/备忘录，完整查看全部溯源信息
        """)
        st.warning("打印要求：贴纸边长≥3厘米，光线充足下扫码，不会出现加载空白、图片失效问题")
