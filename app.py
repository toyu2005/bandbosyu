import streamlit as st
import pandas as pd
import html


# ==================================================
# ページ設定
# ==================================================
st.set_page_config(
    page_title="斑尾月例 提出状況",
    layout="wide"
)

st.title("斑尾月例 提出状況")


# ==================================================
# 更新ボタン
# ==================================================
refresh_clicked = st.button(
    "🔄 最新の提出状況に更新"
)


# ==================================================
# Googleスプレッドシートの公開CSV
# ==================================================
CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vTCWJVhUD05P7Ikx-uq5kGN9gt0dFK-tcUWG2X5uqs1spACMS9oLPJOQ-mGrmwSiCDZH2pQULRQHLa-/"
    "pub?gid=631960825&single=true&output=csv"
)


# キャッシュ防止用
cache_buster = pd.Timestamp.now().timestamp()


# スプレッドシートを読み込む
try:

    df = pd.read_csv(
        CSV_URL + "&t=" + str(cache_buster)
    )

except Exception as error:

    st.error(
        "スプレッドシートを読み込めませんでした。"
        "公開設定やURLを確認してください。"
    )

    st.exception(error)
    st.stop()


# すべて空欄の行を削除
df = df.dropna(how="all")


# 読み込み時刻
loaded_at = pd.Timestamp.now(
    tz="Asia/Tokyo"
).strftime("%Y年%m月%d日 %H:%M:%S")


if refresh_clicked:
    st.success("最新の提出状況に更新しました。")


st.caption(f"最終更新：{loaded_at}")


# ==================================================
# 名簿シートの公開CSV
# ==================================================
MEMBER_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vTCWJVhUD05P7Ikx-uq5kGN9gt0dFK-tcUWG2X5uqs1spACMS9oLPJOQ-mGrmwSiCDZH2pQULRQHLa-/"
    "pub?gid=673348774&single=true&output=csv"
)


# 名簿を読み込む
try:
    member_df = pd.read_csv(
        MEMBER_CSV_URL
        + "&t="
        + str(pd.Timestamp.now().timestamp())
    )

except Exception as error:
    st.error(
        "名簿シートを読み込めませんでした。"
        "公開設定やURLを確認してください。"
    )
    st.exception(error)
    st.stop()


# 「名前」列があるか確認
if "名前" not in member_df.columns:
    st.error(
        "名簿シートに「名前」列がありません。"
        "A1セルを「名前」にしてください。"
    )
    st.stop()


# 空欄を除いて名簿を作成
ALL_MEMBERS = (
    member_df["名前"]
    .dropna()
    .astype(str)
    .str.strip()
)

ALL_MEMBERS = [
    name
    for name in ALL_MEMBERS
    if name != ""
]


# ==================================================
# 名前を統一する関数
# 半角・全角スペース・改行などを無視
# ==================================================
def normalize_name(name):

    if pd.isna(name):
        return ""

    return "".join(str(name).split())


# ==================================================
# 提出日時を画像のような形式にする関数
# ==================================================
def format_relative_time(timestamp):

    if pd.isna(timestamp):
        return ""

    now = pd.Timestamp.now(
        tz="Asia/Tokyo"
    )

    timestamp = pd.Timestamp(timestamp)


    # タイムゾーンがない場合は日本時間として扱う
    if timestamp.tzinfo is None:

        timestamp = timestamp.tz_localize(
            "Asia/Tokyo"
        )

    else:

        timestamp = timestamp.tz_convert(
            "Asia/Tokyo"
        )


    diff = now - timestamp


    month_day = (
        f"{timestamp.month}/{timestamp.day}"
    )

    hour_minute = (
        f"{timestamp.hour}:{timestamp.minute:02d}"
    )


    # 未来の日時になっている場合
    if diff.total_seconds() < 0:

        return f"{month_day} {hour_minute}"


    minutes = int(
        diff.total_seconds() // 60
    )

    hours = int(
        diff.total_seconds() // 3600
    )

    days = diff.days


    if minutes < 1:

        return "たった今"


    elif minutes < 60:

        return f"{minutes}分前"


    elif hours < 24:

        return f"{hours}時間前"


    elif days < 7:

        return f"{days}日前 {hour_minute}"


    else:

        return f"{month_day} {hour_minute}"


# ==================================================
# デザイン
# ==================================================
st.markdown(
    """
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

    .submitted-time {
        color: #777777;
        font-size: 13px;
        margin-top: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==================================================
# 列を取得
# ==================================================
band_column = "バンド名(正式名称)"


member_cols = [
    col
    for col in df.columns
    if "出演者" in str(col)
    or "メンバー" in str(col)
]


# ==================================================
# 必要な列があるか確認
# ==================================================
if band_column not in df.columns:

    st.error(
        f"「{band_column}」という列が見つかりません。"
        "スプレッドシートの列名を確認してください。"
    )

    st.stop()


if len(member_cols) == 0:

    st.error(
        "「出演者」または「メンバー」を含む列が見つかりません。"
        "スプレッドシートの列名を確認してください。"
    )

    st.stop()


# ==================================================
# 提出日時の列を探す
# ==================================================
timestamp_column = None


timestamp_candidates = [
    "タイムスタンプ",
    "提出日時",
    "送信日時",
    "回答日時",
    "日時",
    "Timestamp"
]


# 完全一致で探す
for candidate in timestamp_candidates:

    if candidate in df.columns:

        timestamp_column = candidate
        break


# 部分一致で探す
if timestamp_column is None:

    for col in df.columns:

        normalized_column = (
            normalize_name(col).lower()
        )

        if any(
            normalize_name(candidate).lower()
            in normalized_column
            for candidate in timestamp_candidates
        ):

            timestamp_column = col
            break


# 日時として変換
if timestamp_column is not None:

    df["_submitted_at"] = pd.to_datetime(
        df[timestamp_column],
        errors="coerce"
    )


# ==================================================
# 提出バンド一覧
# ==================================================
st.subheader("提出バンド一覧")


with st.expander(
    "提出バンド一覧を表示・非表示",
    expanded=True
):

    search = st.text_input(
        "バンド名・出演者で検索",
        placeholder="名前またはバンド名を入力"
    )


    display_df = df.copy()


    # ==================================================
    # 検索処理
    # ==================================================
    if search:

        search_text = (
            normalize_name(search).lower()
        )

        mask = (
            display_df
            .fillna("")
            .astype(str)
            .apply(
                lambda row:
                search_text
                in normalize_name(
                    " ".join(row.values)
                ).lower(),
                axis=1
            )
        )

        display_df = display_df[mask]


    st.caption(
        f"表示中の提出数：{len(display_df)}件"
    )


    # ==================================================
    # バンドカードを表示
    # ==================================================
    for _, row in display_df.iterrows():

        band_name = row[band_column]


        if (
            pd.isna(band_name)
            or str(band_name).strip() == ""
        ):

            band_name = "バンド名未入力"


        safe_band_name = html.escape(
            str(band_name).strip()
        )


        # メンバーを取得
        members = []


        for col in member_cols:

            member = row[col]


            if (
                pd.notna(member)
                and str(member).strip() != ""
            ):

                members.append(
                    str(member).strip()
                )


        # 改行や余分なインデントを入れずHTMLを作る
        member_html = "".join(
            f"<p class='member-line'>{html.escape(member)}</p>"
            for member in members
        )


        if not member_html:

            member_html = (
                "<p class='member-line'>"
                "メンバー未入力"
                "</p>"
            )


        # ==================================================
        # 提出日時
        # ==================================================
        submitted_time_html = ""


        if timestamp_column is not None:

            parsed_time = row["_submitted_at"]


            if pd.notna(parsed_time):

                submitted_time = (
                    format_relative_time(
                        parsed_time
                    )
                )


                submitted_time_html = (
                    "<div class='submitted-time'>"
                    f"{html.escape(submitted_time)}"
                    "</div>"
                )


            elif (
                pd.notna(row[timestamp_column])
                and str(
                    row[timestamp_column]
                ).strip() != ""
            ):

                original_time = html.escape(
                    str(
                        row[timestamp_column]
                    ).strip()
                )


                submitted_time_html = (
                    "<div class='submitted-time'>"
                    f"{original_time}"
                    "</div>"
                )


        # ==================================================
        # カード全体
        # ==================================================
        card_html = (
            "<div class='band-card'>"
            f"<div class='band-title'>{safe_band_name}</div>"
            f"{member_html}"
            f"{submitted_time_html}"
            "</div>"
        )


        st.markdown(
            card_html,
            unsafe_allow_html=True
        )


# ==================================================
# 個人ごとの提出数
# ==================================================
st.subheader("個人ごとの提出数")


submitted_members = []


# 全バンドから出演者を取得
for _, row in df.iterrows():

    for col in member_cols:

        member = row[col]


        if (
            pd.notna(member)
            and str(member).strip() != ""
        ):

            submitted_members.append(
                str(member).strip()
            )


# 名前を統一
normalized_submitted_members = [
    normalize_name(member)
    for member in submitted_members
]


# 提出数を計算
submitted_counts = pd.Series(
    normalized_submitted_members,
    dtype="object"
).value_counts()


# 名簿59人を基準に表を作成
member_count_df = pd.DataFrame({
    "名前": ALL_MEMBERS
})


# 各部員の提出数
member_count_df["提出数"] = (
    member_count_df["名前"]
    .apply(normalize_name)
    .map(submitted_counts)
    .fillna(0)
    .astype(int)
)


# 順位を計算
member_count_df["順位"] = (
    member_count_df["提出数"]
    .rank(
        method="min",
        ascending=False
    )
    .astype(int)
)


# 提出数が多い順に並べる
member_count_df = member_count_df.sort_values(
    by=[
        "提出数",
        "名前"
    ],
    ascending=[
        False,
        True
    ]
).reset_index(drop=True)


# 順位を左側にする
member_count_df = member_count_df[
    [
        "順位",
        "名前",
        "提出数"
    ]
]


st.markdown("#### 全員の提出数")


st.dataframe(
    member_count_df,
    use_container_width=True,
    hide_index=True,
    column_config={

        "順位": st.column_config.NumberColumn(
            "順位",
            format="%d位",
            width="small"
        ),

        "名前": st.column_config.TextColumn(
            "名前"
        ),

        "提出数": st.column_config.NumberColumn(
            "提出数",
            format="%d"
        )
    }
)


# ==================================================
# 名簿にない名前を確認
# ==================================================
registered_normalized_names = {
    normalize_name(name)
    for name in ALL_MEMBERS
}


unknown_members = []


for member in submitted_members:

    normalized_member = (
        normalize_name(member)
    )


    if (
        normalized_member
        not in registered_normalized_names
    ):

        unknown_members.append(member)


# 重複を削除
unknown_members = list(
    dict.fromkeys(unknown_members)
)


if len(unknown_members) > 0:

    st.warning(
        "名簿に登録されていない名前があります。"
        "入力ミスや表記の違いがないか確認してください。"
    )


    unknown_member_df = pd.DataFrame({
        "名簿にない名前": unknown_members
    })


    st.dataframe(
        unknown_member_df,
        use_container_width=True,
        hide_index=True
    )
