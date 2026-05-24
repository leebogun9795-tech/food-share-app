import streamlit as st
from datetime import datetime, timedelta
import random
import folium
from streamlit_folium import st_folium

# ==========================================
# [PAGE CONFIG] 웹 브라우저 탭 설정 및 테마 분위기
# ==========================================
st.set_page_config(page_title="공유냉장고 : 우리 동네 소통 플랫폼", layout="wide", page_icon="🧺")

# ==========================================
# [SESSION STATE] 새로고침해도 데이터가 유지되도록 저장소 세팅
# ==========================================
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.my_location = "위치 미인증"
    st.session_state.is_authenticated = False
    st.session_state.total_carbon_saved = 0.0
    st.session_state.my_wishlist = []
    
    # 사용자별 매너 온도
    st.session_state.user_temperatures = {
        "나": 36.5, "신촌불주먹": 37.2, "노원지킴이": 36.0, "상계동주민": 40.5, "꿀팁요정": 38.0, "자취고수": 39.1
    }
    
    # 동네생활 게시글
    st.session_state.community_posts = [
        {"id": 1, "user": "꿀팁요정", "content": "1호 공유냉장고에 오늘 신선한 채소가 많이 들어왔네요!", "time": "10분 전"},
        {"id": 2, "user": "자취고수", "content": "역 앞 마트 오늘 타임세일 한대요. 참고하세요~", "time": "30분 전"}
    ]
    
    # 음식 데이터
    st.session_state.foods = [
        {
            "id": 1, "name": "감자 3알", "type": "무료나눔", 
            "exp_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"), 
            "user": "신촌불주먹", "carbon": 0.3, "status": "실온", "fridge": "상계 1호점",
            "desc": "요리하고 남았어요.", "cook_date": "2026-05-13", "storage": "서늘한 곳 보관"
        },
        {
            "id": 2, "name": "우유 500ml (미개봉)", "type": "무료나눔", 
            "exp_date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"), 
            "user": "노원지킴이", "carbon": 0.5, "status": "냉장", "fridge": "상계 2호점",
            "desc": "유통기한 임박해서 나눔합니다.", "cook_date": "안 했어요.", "storage": "냉장 보관"
        },
        {
            "id": 3, "name": "방울토마토 한 팩", "type": "물물교환", 
            "exp_date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"), 
            "user": "상계동주민", "carbon": 0.4, "status": "냉장", "fridge": "상계 3호점",
            "desc": "사과나 다른 과일이랑 바꾸고 싶어요!", "cook_date": "2026-05-14", "storage": "냉장 보관"
        }
    ]
    
    # 채팅방 및 모달 상태 관리 변수들
    st.session_state.chats = {}
    st.session_state.active_chat_id = None
    st.session_state.selected_user_profile = None

# 냉장고 고정 위치 정보
FRIDGE_LOCATIONS = {"상계 1호점": (200, 150), "상계 2호점": (500, 200), "상계 3호점": (350, 350)}


# ==========================================
# [HEADER] 상단 네비게이션 및 대시보드 정보
# ==========================================
st.title("🥦 우리 동네 공유냉장고 플랫폼")
st.caption("디자인과 로직이 결합된 지속 가능한 먹거리 나눔 네트워크")

head_col1, head_col2, head_col3, head_col4 = st.columns([2, 2, 2, 2])

with head_col1:
    if not st.session_state.is_authenticated:
        if st.button("📍 동네 인증하기", type="primary"):
            st.session_state.my_location = "서울시 노원구 상계동"
            st.session_state.is_authenticated = True
            st.success("✅ 상계동 커뮤니티 인증 완료!")
            st.rerun()
    else:
        st.success(f"📍 인증됨: {st.session_state.my_location}")

with head_col2:
    st.metric("🌱 나의 탄소 절감량", f"{st.session_state.total_carbon_saved:.2f} kg")

with head_col3:
    st.metric("🌡️ 나의 매너 온도", f"{st.session_state.user_temperatures['나']:.1f} ℃")

with head_col4:
    if st.session_state.my_wishlist:
        st.info(f"🔔 관심 키워드: {', '.join(st.session_state.my_wishlist)}")
    else:
        st.light_sidebar = "등록된 알림 키워드 없음"

st.write("---")


# ==========================================
# [SIDEBAR POPUP] 유저 프로필 보기 대용 (사이드바 활용)
# ==========================================
if st.session_state.selected_user_profile:
    user = st.session_state.selected_user_profile
    with st.sidebar:
        st.subheader(f"👤 {user}님의 프로필")
        temp = st.session_state.user_temperatures.get(user, 36.5)
        st.metric("🌡️ 매너 온도", f"{temp:.1f} ℃")
        
        st.write("**📋 올린 제품 목록**")
        user_items = [f['name'] for f in st.session_state.foods if f['user'] == user]
        if user_items:
            for item in user_items:
                st.write(f"- {item}")
        else:
            st.caption("등록된 제품이 없습니다.")
            
        st.write("**🤝 최근 거래 내역**")
        trades = ["사과 나눔 완료", "우유 교환 완료", "식빵 나눔 완료"] if user != "나" else ["진행 중인 내역이 없습니다."]
        for t in trades:
            st.write(f"✓ {t}")
            
        if st.button("프로필 닫기"):
            st.session_state.selected_user_profile = None
            st.rerun()


# ==========================================
# [MAIN TABS] 메인 기능 탭 구성 (피그마 디자인 구조화)
# ==========================================
tab_list, tab_chat, tab_community, tab_map, tab_reg, tab_settings = st.tabs([
    "🍲 음식 공유", "💬 1:1 채팅방", "🏡 동네생활", "📍 냉장고 지도", "✍️ 나눔 등록", "⚙️ 설정"
])

# --- 1. 음식 공유 탭 ---
with tab_list:
    st.subheader("🍲 동네 냉장고에 올라온 음식")
    for food in st.session_state.foods:
        with st.container(border=True):
            c1, c2, c3 = st.columns([5, 2, 2])
            with c1:
                st.markdown(f"### **[{food['status']}] {food['name']}**")
                st.caption(f"📍 보관 장소: {food['fridge']} | 🤝 거래 방식: {food['type']}")
                st.write(f"⏱️ 유통기한: {food['exp_date']} | 🍳 조리상태: {food['cook_date']} | 📦 상세보관: {food['storage']}")
            with c2:
                # 닉네임 클릭 시 프로필 오픈
                if st.button(f"👤 {food['user']}", key=f"prof_{food['id']}"):
                    st.session_state.selected_user_profile = food['user']
                    st.rerun()
            with c3:
                if food['user'] == "나":
                    st.info("내가 올린 글")
                else:
                    if st.button("💬 채팅하기", key=f"chatbtn_{food['id']}", type="primary"):
                        fid = food['id']
                        if fid not in st.session_state.chats:
                            st.session_state.chats[fid] = {"food": food, "messages": []}
                        st.session_state.active_chat_id = fid
                        st.info("채팅방 탭으로 이동해서 대화를 확인해 보세요!")

# --- 2. 1:1 채팅방 탭 ---
with tab_chat:
    st.subheader("💬 진행 중인 거래 채팅")
    if not st.session_state.chats:
        st.caption("진행 중인 채팅방이 없습니다. '음식 공유' 탭에서 대화를 신청해 보세요.")
    else:
        chat_options = {fid: f"👤 {data['food']['user']}님과의 대화 ({data['food']['name']})" for fid, data in st.session_state.chats.items()}
        selected_chat = st.selectbox("대화방 선택", options=list(chat_options.keys()), format_func=lambda x: chat_options[x])
        
        if selected_chat:
            chat_data = st.session_state.chats[selected_chat]
            food = chat_data["food"]
            
            # 채팅방 타임라인 출력
            st.write("---")
            st.caption(f"📢 '{food['name']}' 거래를 위한 안전 안내: 개인정보에 유의하세요.")
            
            for msg in chat_data["messages"]:
                if msg["sender"] == "나":
                    st.chat_message("user").write(msg["text"])
                else:
                    st.chat_message("assistant").write(f"**[{msg['sender']}]** {msg['text']}")
            
            # 메시지 입력창
            if user_msg := st.chat_input("메시지를 입력하세요", key="chat_input_unique"):
                chat_data["messages"].append({"sender": "나", "text": user_msg})
                
                # 심플 자동 응답 봇 로직 구현
                if "안녕하세요" in user_msg:
                    reply = "안녕하세요! 거래 가능합니다."
                else:
                    reply = random.choice(["지금 바로 갈 수 있어요!", "감사합니다!", "어디서 뵐까요?", "좋은 나눔 감사드립니다!"])
                chat_data["messages"].append({"sender": food['user'], "text": reply})
                st.rerun()
                
            # 거래 완료 및 평가하기
            st.write("---")
            st.write("💡 거래가 완료되셨나요?")
            c_win, c_lose = st.columns(2)
            with c_win:
                if st.button("👍 최고예요! (+0.1℃)", key="eval_up"):
                    st.session_state.user_temperatures[food['user']] = round(st.session_state.user_temperatures[food['user']] + 0.1, 1)
                    st.success(f"{food['user']}님의 온도가 올랐습니다!")
            with c_lose:
                if st.button("👎 별로예요 (-0.1℃)", key="eval_down"):
                    st.session_state.user_temperatures[food['user']] = round(st.session_state.user_temperatures[food['user']] - 0.1, 1)
                    st.warning(f"{food['user']}님의 온도가 차감되었습니다.")

# --- 3. 동네생활 탭 ---
with tab_community:
    st.subheader("🏡 우리 동네 실시간 정보통")
    if not st.session_state.is_authenticated:
        st.warning("🔒 동네 인증을 완료해야 열람 및 작성이 가능합니다.")
    else:
        with st.form("community_form", clear_on_submit=True):
            post_text = st.text_input("동네 주민들과 나누고 싶은 소식을 적어보세요", placeholder="예: 3호점에 간식 기부 완료했습니다!")
            if st.form_submit_button("올리기"):
                if post_text:
                    st.session_state.community_posts.insert(0, {"id": len(st.session_state.community_posts)+1, "user": "나", "content": post_text, "time": "방금 전"})
                    st.rerun()
                    
        for post in st.session_state.community_posts:
            with st.container(border=True):
                col_p1, col_p2 = st.columns([1, 6])
                with col_p1:
                    if st.button(f"👤 {post['user']}", key=f"post_user_{post['id']}_{random.randint(0,1000)}"):
                        st.session_state.selected_user_profile = post['user']
                        st.rerun()
                with col_p2:
                    st.write(post['content'])
                    st.caption(post['time'])

# --- 4. 지도 탭 ---
with tab_map:
    st.subheader("📍 상계동 공유 냉장고 현황 지도")
    m = folium.Map(
    location=[37.6658, 127.0670],
    zoom_start=14,
    tiles="CartoDB positron"
)

    folium.CircleMarker(
         location=[37.6658, 127.0670],
        radius=12,
        color="#FF4B91",
        fill=True,
        fill_color="#FF4B91",
        popup="""
        <div style="
            font-size:14px;
            padding:8px;
        ">
        🥔 감자 3알
        </div>
        """
    ).add_to(m)

    st.markdown("""
    <style>
    iframe {
     border-radius: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    st_folium(m, width=900, height=400)

    # 지도를 흉내 낸 시각적인 대시보드 카드 배치
map_col1, map_col2, map_col3 = st.columns(3)
for name, pos in FRIDGE_LOCATIONS.items():
        count = len([f for f in st.session_state.foods if f['fridge'] == name])
        if name == "상계 1호점":
            with map_col1: st.info(f"🟢 **{name}**\n\n현재 보관 중인 보존 식품: **{count}개**")
        elif name == "상계 2호점":
            with map_col2: st.success(f"🟢 **{name}**\n\n현재 보관 중인 보존 식품: **{count}개**")
        else:
            with map_col3: st.warning(f"🟢 **{name}**\n\n현재 보관 중인 보존 식품: **{count}개**")

# --- 5. 나눔 등록 탭 ---
with tab_reg:
    st.subheader("✍️ 내 주방의 남는 음식 나눔하기")
    with st.form("register_form", clear_on_submit=True):
        r_name = st.text_input("음식명")
        r_fridge = st.selectbox("보관할 공유냉장고 위치", list(FRIDGE_LOCATIONS.keys()))
        r_type = st.selectbox("거래 방식", ["무료나눔", "물물교환", "소액판매"])
        r_status = st.selectbox("보관 상태", ["냉장", "냉동", "실온"])
        r_exp = st.text_input("유통기한", datetime.now().strftime("%Y-%m-%d"))
        r_cook = st.text_input("조리/구매 날짜", datetime.now().strftime("%Y-%m-%d"))
        r_storage = st.text_input("상세 보관방법 가이드")
        
        if st.form_submit_button("냉장고에 등록 완료하기"):
            if not r_name:
                st.error("음식 이름을 정확히 입력해 주세요.")
            else:
                new_food = {
                    "id": len(st.session_state.foods) + 1, "name": r_name, "type": r_type,
                    "exp_date": r_exp, "status": r_status, "user": "나", "fridge": r_fridge,
                    "carbon": 0.45, "storage": r_storage, "cook_date": r_cook
                }
                st.session_state.foods.append(new_food)
                st.session_state.total_carbon_saved += 0.45
                st.success(f"🎉 '{r_name}' 아이템이 {r_fridge}에 정상 등록되었으며, 탄소 배출을 줄였습니다!")
                st.rerun()

# --- 6. 설정 탭 ---
with tab_settings:
    st.subheader("⚙️ 알림 및 서비스 키워드 세팅")
    wish_input = st.text_input("관심 있는 상시 품목 키워드를 추가해 두세요. (알람 연동용)", placeholder="예: 우유, 사과, 계란")
    if st.button("키워드 등록"):
        if wish_input and wish_input not in st.session_state.my_wishlist:
            st.session_state.my_wishlist.append(wish_input)
            st.success(f"📌 '{wish_input}' 키워드 구독 신청이 정상 처리되었습니다.")
            st.rerun()
            
    if st.session_state.my_wishlist:
        st.write("현재 내 구독 리스트:")
        for idx, w in enumerate(st.session_state.my_wishlist):
            st.code(f"알림 항목 {idx+1}: {w}")
            
st.sidebar.title("👤 사용자 정보")

nickname = st.sidebar.text_input("닉네임")
location = st.sidebar.selectbox(
    "지역 선택",
    ["상계동", "중계동", "하계동"]
)

