# streamlit_app.py
import requests
import streamlit as st

API_BASE = "https://emojihub.yurace.pro/api"


# --------- API helper functions ---------
def get_json(path: str, params: dict | None = None):
    url = f"{API_BASE}{path}"
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_random_emoji():
    return get_json("/random")


def get_categories():
    return get_json("/categories")  # ["smileys and people", ...]


def get_groups():
    return get_json("/groups")      # ["face positive", ...]


def get_random_by_category(category: str):
    # README 기준: /random/category/{category-name}  [oai_citation:0‡GitHub](https://github.com/cheatsnake/emojihub?utm_source=chatgpt.com)
    return get_json(f"/random/category/{category}")


def get_random_by_group(group: str):
    # README 기준: /random/group/{group-name}  [oai_citation:1‡GitHub](https://github.com/cheatsnake/emojihub?utm_source=chatgpt.com)
    return get_json(f"/random/group/{group}")


def search_emojis(query: str):
    # /search?q={query}  [oai_citation:2‡GitHub](https://github.com/cheatsnake/emojihub?utm_source=chatgpt.com)
    return get_json("/search", params={"q": query})


# --------- UI helpers ---------
def render_emoji_card(obj: dict):
    name = obj.get("name", "unknown")
    category = obj.get("category", "-")
    group = obj.get("group", "-")
    html_codes = obj.get("htmlCode", [])
    unicode_codes = obj.get("unicode", [])

    # htmlCode로 실제 이모지 렌더
    emoji_html = "".join(html_codes) if html_codes else ""
    st.markdown(
        f"<div style='font-size: 3rem;'>{emoji_html}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(f"**{name}**")
    st.caption(f"Category: {category} · Group: {group}")
    if unicode_codes:
        st.code(", ".join(unicode_codes), language="text")


# --------- Streamlit main ---------
def main():
    st.set_page_config(
        page_title="EmojiHub Explorer",
        layout="wide",
    )

    st.title("EmojiHub Explorer 😺")
    st.write(
        "cheatsnake의 **EmojiHub API**를 사용하는 간단한 데모입니다.  \n"
        "랜덤 이모지, 카테고리/그룹별 이모지, 이름 검색을 해볼 수 있어요."
    )

    # 사이드바: 모드 선택
    with st.sidebar:
        st.header("Mode")
        mode = st.radio(
            "기능 선택",
            ["Random", "Random by Category", "Random by Group", "Search by Name"],
        )

    # -------- Random --------
    if mode == "Random":
        st.subheader("🎲 Random Emoji")
        if st.button("Get random emoji"):
            try:
                obj = get_random_emoji()
                render_emoji_card(obj)
            except Exception as e:
                st.error(f"API 오류: {e}")

    # -------- Random by Category --------
    elif mode == "Random by Category":
        st.subheader("📁 Random Emoji by Category")

        try:
            categories = get_categories()
        except Exception as e:
            st.error(f"카테고리 목록을 가져오는 중 오류: {e}")
            return

        category = st.selectbox("Category", categories)
        if st.button("Get random emoji in this category"):
            try:
                obj = get_random_by_category(category)
                render_emoji_card(obj)
            except Exception as e:
                st.error(f"API 오류: {e}")

    # -------- Random by Group --------
    elif mode == "Random by Group":
        st.subheader("👥 Random Emoji by Group")

        try:
            groups = get_groups()
        except Exception as e:
            st.error(f"그룹 목록을 가져오는 중 오류: {e}")
            return

        group = st.selectbox("Group", groups)
        if st.button("Get random emoji in this group"):
            try:
                obj = get_random_by_group(group)
                render_emoji_card(obj)
            except Exception as e:
                st.error(f"API 오류: {e}")

    # -------- Search --------
    else:  # Search by Name
        st.subheader("🔍 Search Emojis by Name")

        query = st.text_input("검색어 (예: 'cat', 'heart', 'face')")
        if st.button("Search") and query.strip():
            try:
                results = search_emojis(query.strip())
            except Exception as e:
                st.error(f"API 오류: {e}")
                return

            if not results:
                st.warning("검색 결과가 없습니다.")
                return

            st.caption(f"Found {len(results)} result(s).")
            for obj in results:
                with st.container():
                    render_emoji_card(obj)
                    st.markdown("---")

        elif not query:
            st.info("이름 일부를 입력하고 Search 버튼을 눌러보세요.")


if __name__ == "__main__":
    main()
