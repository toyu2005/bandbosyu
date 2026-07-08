import streamlit as st
import pandas as pd

st.title("斑尾月例 提出状況")

# GoogleスプレッドシートのCSV用URLを入れる
csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYHHQG26M-80wf7IgIr2-CbD36XAfPJG37P_WkE0K3QCGNHZz4Na4hR6w-2w7qMWItObLlY2KA0Vpi/pub?gid=911658908&single=true&output=csv"

df = pd.read_csv(csv_url)

st.subheader("提出一覧")
st.dataframe(df, use_container_width=True)

st.subheader("バンド名一覧")
if "バンド名" in df.columns:
    st.dataframe(df["バンド名"].value_counts().reset_index())
