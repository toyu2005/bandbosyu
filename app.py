import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="斑尾月例 提出状況",
    layout="wide"
)

st.title("斑尾月例 提出状況")

# Googleスプレッドシート(CSV)のURL
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYHHQG26M-80wf7IgIr2-CbD36XAfPJG37P_WkE0K3QCGNHZz4Na4hR6w-2w7qMWItObLlY2KA0Vpi/pub?gid=911658908&single=true&output=csv"

# データ読込
df = pd.read_csv(CSV_URL)
df = df.dropna(how="all")

####################################
# 提出一覧
####################################

st.header("提出一覧")

show_columns = [
    "バンド名(正式名称)",
    "出演者1",
    "出演者2",
    "出演者3",
    "出演者4",
    "出演者5",
    "出演者6",
    "出演者7",
    "出演者8",
    "出演者9",
]

exist_columns = [c for c in show_columns if c in df.columns]

st.dataframe(
    df[exist_columns],
    use_container_width=True,
    hide_index=True,
)

####################################
# 個人ごとの提出数
####################################

st.header("個人ごとの提出数")

member_columns = [c for c in df.columns if c.startswith("出演者")]

members = []

for col in member_columns:
    for name in df[col].dropna():

        name = str(name).strip()

        if name != "":
            members.append(name)

member_df = (
    pd.DataFrame({"名前": members})
    .value_counts()
    .reset_index(name="提出数")
    .sort_values("提出数", ascending=False)
)

st.dataframe(
    member_df,
    use_container_width=True,
    hide_index=True,
)