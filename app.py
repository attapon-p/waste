import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# 1. PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Waste Management Dashboard",
    page_icon="♻️",
    layout="wide"
)


# ============================================================
# 2. LOAD DATA
# ============================================================

@st.cache_data
def load_data():
    df = pd.read_excel("waste.xlsx")

    # ลำดับเดือนภาษาไทย
    month_order = [
        "มกราคม",
        "กุมภาพันธ์",
        "มีนาคม",
        "เมษายน",
        "พฤษภาคม",
        "มิถุนายน",
        "กรกฎาคม",
        "สิงหาคม",
        "กันยายน",
        "ตุลาคม",
        "พฤศจิกายน",
        "ธันวาคม"
    ]

    df["เดือน"] = pd.Categorical(
        df["เดือน"],
        categories=month_order,
        ordered=True
    )

    return df


df = load_data()


# ============================================================
# 3. TITLE
# ============================================================

st.title("♻️ Waste Management Dashboard")

st.markdown(
    """
    **Dashboard การจัดการขยะ**
    
    ใช้สำหรับวิเคราะห์ปริมาณขยะ การนำขยะไปใช้ประโยชน์
    และปริมาณขยะที่ส่งกำจัด โดยสามารถกรองข้อมูลตามปี
    สังกัด หน่วยงาน และเดือนได้
    """
)


# ============================================================
# 4. FILTER
# ============================================================

st.sidebar.header("🔎 Filter ข้อมูล")

# ปี
year_list = sorted(df["ปี"].dropna().unique())

selected_year = st.sidebar.multiselect(
    "ปี",
    options=year_list,
    default=year_list
)

# สังกัด
affiliation_list = sorted(df["สังกัด"].dropna().unique())

selected_affiliation = st.sidebar.multiselect(
    "สังกัด",
    options=affiliation_list,
    default=affiliation_list
)

# หน่วยงาน
agency_list = sorted(df["หน่วยงาน"].dropna().unique())

selected_agency = st.sidebar.multiselect(
    "หน่วยงาน",
    options=agency_list,
    default=agency_list
)

# เดือน
month_list = [
    "มกราคม",
    "กุมภาพันธ์",
    "มีนาคม",
    "เมษายน",
    "พฤษภาคม",
    "มิถุนายน",
    "กรกฎาคม",
    "สิงหาคม",
    "กันยายน",
    "ตุลาคม",
    "พฤศจิกายน",
    "ธันวาคม"
]

available_months = [
    m for m in month_list
    if m in df["เดือน"].astype(str).unique()
]

selected_month = st.sidebar.multiselect(
    "เดือน",
    options=available_months,
    default=available_months
)


# ============================================================
# 5. FILTER DATA
# ============================================================

filtered_df = df[
    (df["ปี"].isin(selected_year)) &
    (df["สังกัด"].isin(selected_affiliation)) &
    (df["หน่วยงาน"].isin(selected_agency)) &
    (df["เดือน"].astype(str).isin(selected_month))
].copy()


# ============================================================
# 6. CHECK DATA
# ============================================================

if filtered_df.empty:

    st.warning("ไม่พบข้อมูลตามเงื่อนไขที่เลือก")

    st.stop()


# ============================================================
# 7. KPI
# ============================================================

total_waste = filtered_df["ขยะที่เกิดขึ้น (กก.)"].sum()

total_reuse = filtered_df["นำไปใช้ประโยชน์ (กก.)"].sum()

total_disposal = filtered_df["ขยะที่ส่งกำจัด (กก.)"].sum()

avg_reduction = filtered_df["ร้อยละขยะส่งกำจัดลดลง"].mean()

total_foam = filtered_df["โฟมบรรจุอาหาร (ใบ)"].sum()


# ============================================================
# KPI CARDS
# ============================================================

st.subheader("📊 สรุปข้อมูล")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "ขยะที่เกิดขึ้น",
        f"{total_waste:,.2f} กก."
    )

with col2:
    st.metric(
        "นำไปใช้ประโยชน์",
        f"{total_reuse:,.2f} กก."
    )

with col3:
    st.metric(
        "ขยะที่ส่งกำจัด",
        f"{total_disposal:,.2f} กก."
    )

with col4:
    st.metric(
        "เฉลี่ยขยะส่งกำจัดลดลง",
        f"{avg_reduction:,.2f}%"
    )

with col5:
    st.metric(
        "โฟมบรรจุอาหาร",
        f"{total_foam:,.0f} ใบ"
    )


st.divider()


# ============================================================
# 8. MONTHLY WASTE TREND
# ============================================================

st.subheader("📈 ปริมาณขยะรายเดือน")

monthly_df = (
    filtered_df
    .groupby("เดือน", observed=False)[
        [
            "ขยะที่เกิดขึ้น (กก.)",
            "นำไปใช้ประโยชน์ (กก.)",
            "ขยะที่ส่งกำจัด (กก.)"
        ]
    ]
    .sum()
    .reset_index()
)

monthly_df["เดือน"] = pd.Categorical(
    monthly_df["เดือน"],
    categories=month_list,
    ordered=True
)

monthly_df = monthly_df.sort_values("เดือน")

monthly_long = monthly_df.melt(
    id_vars="เดือน",
    value_vars=[
        "ขยะที่เกิดขึ้น (กก.)",
        "นำไปใช้ประโยชน์ (กก.)",
        "ขยะที่ส่งกำจัด (กก.)"
    ],
    var_name="ประเภท",
    value_name="ปริมาณ (กก.)"
)

fig_month = px.line(
    monthly_long,
    x="เดือน",
    y="ปริมาณ (กก.)",
    color="ประเภท",
    markers=True,
    title="แนวโน้มปริมาณขยะรายเดือน"
)

fig_month.update_layout(
    xaxis_title="เดือน",
    yaxis_title="ปริมาณ (กก.)",
    legend_title="ประเภทขยะ",
    hovermode="x unified"
)

st.plotly_chart(
    fig_month,
    use_container_width=True
)


# ============================================================
# 9. AGENCY WASTE
# ============================================================

st.subheader("🏢 ปริมาณขยะตามหน่วยงาน")

agency_df = (
    filtered_df
    .groupby("หน่วยงาน", as_index=False)[
        [
            "ขยะที่เกิดขึ้น (กก.)",
            "นำไปใช้ประโยชน์ (กก.)",
            "ขยะที่ส่งกำจัด (กก.)"
        ]
    ]
    .sum()
)

agency_long = agency_df.melt(
    id_vars="หน่วยงาน",
    value_vars=[
        "ขยะที่เกิดขึ้น (กก.)",
        "นำไปใช้ประโยชน์ (กก.)",
        "ขยะที่ส่งกำจัด (กก.)"
    ],
    var_name="ประเภท",
    value_name="ปริมาณ (กก.)"
)

fig_agency = px.bar(
    agency_long,
    x="หน่วยงาน",
    y="ปริมาณ (กก.)",
    color="ประเภท",
    barmode="group",
    title="เปรียบเทียบปริมาณขยะตามหน่วยงาน"
)

fig_agency.update_layout(
    xaxis_title="หน่วยงาน",
    yaxis_title="ปริมาณ (กก.)",
    xaxis_tickangle=-45
)

st.plotly_chart(
    fig_agency,
    use_container_width=True
)


# ============================================================
# 10. WASTE MANAGEMENT COMPOSITION
# ============================================================

st.subheader("♻️ การจัดการขยะ")

reuse_total = filtered_df["นำไปใช้ประโยชน์ (กก.)"].sum()

disposal_total = filtered_df["ขยะที่ส่งกำจัด (กก.)"].sum()

management_df = pd.DataFrame({
    "ประเภท": [
        "นำไปใช้ประโยชน์",
        "ส่งกำจัด"
    ],
    "ปริมาณ": [
        reuse_total,
        disposal_total
    ]
})

col_left, col_right = st.columns(2)

with col_left:

    fig_pie = px.pie(
        management_df,
        names="ประเภท",
        values="ปริมาณ",
        hole=0.45,
        title="สัดส่วนการจัดการขยะ"
    )

    st.plotly_chart(
        fig_pie,
        use_container_width=True
    )


with col_right:

    # Top 10 หน่วยงานที่มีขยะสูงสุด
    top_agency = (
        agency_df
        .sort_values(
            "ขยะที่เกิดขึ้น (กก.)",
            ascending=False
        )
        .head(10)
    )

    fig_top = px.bar(
        top_agency,
        x="ขยะที่เกิดขึ้น (กก.)",
        y="หน่วยงาน",
        orientation="h",
        title="10 หน่วยงานที่มีขยะเกิดขึ้นสูงสุด"
    )

    fig_top.update_layout(
        yaxis={
            "categoryorder": "total ascending"
        }
    )

    st.plotly_chart(
        fig_top,
        use_container_width=True
    )


# ============================================================
# 11. PEOPLE AND WORKING DAYS
# ============================================================

st.subheader("👥 คนเฉลี่ยและวันทำงาน")

people_df = (
    filtered_df
    .groupby("เดือน", observed=False)[
        ["คนเฉลี่ย", "วันทำงาน"]
    ]
    .mean()
    .reset_index()
)

people_df["เดือน"] = pd.Categorical(
    people_df["เดือน"],
    categories=month_list,
    ordered=True
)

people_df = people_df.sort_values("เดือน")

fig_people = px.bar(
    people_df,
    x="เดือน",
    y="คนเฉลี่ย",
    title="จำนวนคนเฉลี่ยรายเดือน"
)

fig_people.update_layout(
    xaxis_title="เดือน",
    yaxis_title="คนเฉลี่ย"
)

st.plotly_chart(
    fig_people,
    use_container_width=True
)


# ============================================================
# 12. DATA TABLE
# ============================================================

st.subheader("📋 รายละเอียดข้อมูล")

display_columns = [
    "ปี",
    "สังกัด",
    "หน่วยงาน",
    "เดือน",
    "คนเฉลี่ย",
    "วันทำงาน",
    "โฟมบรรจุอาหาร (ใบ)",
    "ขยะที่เกิดขึ้น (กก.)",
    "นำไปใช้ประโยชน์ (กก.)",
    "ขยะที่ส่งกำจัด (กก.)",
    "ร้อยละขยะส่งกำจัดลดลง"
]

st.dataframe(
    filtered_df[display_columns],
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 13. DOWNLOAD FILTERED DATA
# ============================================================

st.subheader("⬇️ Download")

csv_data = filtered_df[display_columns].to_csv(
    index=False,
    encoding="utf-8-sig"
)

st.download_button(
    label="ดาวน์โหลดข้อมูลที่กรองแล้ว (CSV)",
    data=csv_data,
    file_name="filtered_waste_data.csv",
    mime="text/csv"
)


# ============================================================
# 14. FOOTER
# ============================================================

st.divider()

st.caption(
    "Waste Management Dashboard | Developed with Streamlit + Pandas + Plotly"
)
