import streamlit as st
import pandas as pd

st.set_page_config(page_title="斑尾月例 提出状況", layout="wide")

st.title("斑尾月例 提出状況")

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYHHQG26M-80wf7IgIr2-CbD36XAfPJG37P_WkE0K3QCGNHZz4Na4hR6w-2w7qMWItObLlY2KA0Vpi/pub?gid=911658908&single=true&output=csv"

df = pd.read_csv(CSV_URL)
df = df.dropna(how="all")

st.subheader("提出バンド一覧")

member_cols = [col for col in df.columns if "出演者" in col or "メンバー" in col]

for _, row in df.iterrows():
    band_name = row["バンド名(正式名称)"]

    members = []
    for col in member_cols:
        if pd.notna(row[col]) and str(row[col]).strip() != "":
            members.append(str(row[col]).strip())

    st.markdown(f"{band_name}")

    for member in members:
        st.markdown(f"- {member}")

    st.divider()

st.subheader("個人ごとの提出数")

all_members = []

for _, row in df.iterrows():
    for col in member_cols:
        if pd.notna(row[col]) and str(row[col]).strip() != "":
            all_members.append(str(row[col]).strip())

member_count_df = pd.DataFrame(all_members, columns=["名前"])
member_count_df = member_count_df["名前"].value_counts().reset_index()
member_count_df.columns = ["名前", "提出数"]

st.dataframe(member_count_df, use_container_width=True, hide_index=True)
