import streamlit as st
import pandas as pd

st.set_page_config(page_title="斑尾月例 提出状況", layout="wide")

st.title("斑尾月例 提出状況")

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYHHQG26M-80wf7IgIr2-CbD36XAfPJG37P_WkE0K3QCGNHZz4Na4hR6w-2w7qMWItObLlY2KA0Vpi/pub?gid=911658908&single=true&output=csv"

df = pd.read_csv(CSV_URL)
df = df.dropna(how="all")

st.subheader("提出バンド一覧")

show_columns = ["バンド名", "メンバー"]

if all(col in df.columns for col in show_columns):
    st.dataframe(df[show_columns], use_container_width=True, hide_index=True)
else:
    st.error("列名が合っていません。1行目を「バンド名」「メンバー」にしてください。")

st.subheader("個人ごとの提出数")

if "メンバー" in df.columns:
    members = []

    for member_text in df["メンバー"].dropna():
        member_text = str(member_text)
        member_text = member_text.replace("，", ",")
        member_text = member_text.replace("、", ",")
        member_text = member_text.replace("/", ",")
        member_text = member_text.replace("・", ",")

        for name in member_text.split(","):
            name = name.strip()
            if name != "":
                members.append(name)

    member_count_df = pd.DataFrame(members, columns=["名前"])
    member_count_df = member_count_df["名前"].value_counts().reset_index()
    member_count_df.columns = ["名前", "提出数"]

    st.dataframe(member_count_df, use_container_width=True, hide_index=True)