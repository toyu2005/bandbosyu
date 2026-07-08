import streamlit as st
import pandas as pd

st.set_page_config(page_title="斑尾月例 提出状況", layout="wide")

st.title("斑尾月例 提出状況")

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTCWJVhUD05P7Ikx-uq5kGN9gt0dFK-tcUWG2X5uqs1spACMS9oLPJOQ-mGrmwSiCDZH2pQULRQHLa-/pub?gid=631960825&single=true&output=csv"
df = pd.read_csv(CSV_URL + "&t=" + str(pd.Timestamp.now().timestamp()))
df = df.dropna(how="all")

if df.empty:
    st.info("まだ提出はありません。例として以下のように表示されます。")

    example_df = pd.DataFrame({
        "バンド名(正式名称)": ["ヨルシカ", "back number"],
        "出演者1": ["田中", "佐藤"],
        "出演者2": ["鈴木", "山田"],
        "出演者3": ["高橋", ""],
    })

    df = example_df

st.markdown("""
<style>
.band-card {
    background-color: #f2f2f2;
    border-radius: 18px;
    padding: 12px 16px;
    margin: 8px 0 14px 0;
    width: fit-content;
    max-width: 90%;
    line-height: 1.35;
}
.band-title {
    font-weight: bold;
    font-size: 18px;
    margin-bottom: 6px;
}
.member-line {
    font-size: 16px;
    margin: 0;
}
</style>
""", unsafe_allow_html=True)

st.subheader("提出バンド一覧")

search = st.text_input("バンド名・出演者で検索")

display_df = df.copy()

if search:
    mask = display_df.fillna("").astype(str).agg(" ".join, axis=1).str.contains(search, case=False, na=False)
    display_df = display_df[mask]

st.caption(f"提出数：{len(display_df)}件")

member_cols = [col for col in df.columns if "出演者" in col or "メンバー" in col]

for _, row in display_df.iterrows():
    band_name = row["バンド名(正式名称)"]

    members = []
    for col in member_cols:
        if pd.notna(row[col]) and str(row[col]).strip() != "":
            members.append(str(row[col]).strip())

    member_html = "".join([f"<p class='member-line'>{m}</p>" for m in members])

    st.markdown(f"""
    <div class="band-card">
        <div class="band-title">{band_name}</div>
        {member_html}
    </div>
    """, unsafe_allow_html=True)

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
