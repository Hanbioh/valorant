import streamlit as st
import requests
import urllib.parse
import base64
import hashlib

# 0. 세션 상태 초기화 (이벤트 제어용)
for key in ["event_lightning", "event_ruby", "event_champions", "event_jett", "event_gold", "event_unknown"]:
    if key not in st.session_state:
        st.session_state[key] = False

st.set_page_config(layout="wide", page_title="VALORANT - VCT Special Edition")

# 이미지 로컬 -> Base64 변환 헬퍼 함수
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return ""

jett_base64 = get_base64_image("jett_champions.png")

# 이벤트 기반 동적 CSS 설정
bg_css = ""
if st.session_state.event_ruby:
    bg_css = """
    .stApp {
        background: radial-gradient(circle at center, #3d060f 0%, #150205 100%) !important;
        color: #ECE8E1 !important;
    }
    h1, h2, h3, h4, h5, h6, .stSubheader, .cyber-header {
        color: #FF4655 !important;
        text-shadow: 0 0 10px rgba(255, 70, 85, 0.8) !important;
    }
    """
elif st.session_state.event_champions:
    bg_css = """
    .stApp {
        background: radial-gradient(circle at center, #1b160a 0%, #080703 100%) !important;
    }
    h1, h2, h3, h4, h5, h6, .stSubheader, .cyber-header {
        color: #D4AF37 !important;
        text-shadow: 0 0 10px rgba(212, 175, 55, 0.8) !important;
    }
    """

# 1. 미래지향적 사이버네틱 CSS 스타일링 적용
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;600;700&family=Outfit:wght@300;400;600;800&display=swap');

.stApp {{
    background-color: #060a0f !important;
    background-image: 
        radial-gradient(circle at center, rgba(16, 25, 36, 0.85) 0%, #060a0f 100%),
        linear-gradient(rgba(0, 240, 255, 0.015) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 240, 255, 0.015) 1px, transparent 1px) !important;
    background-size: 100% 100%, 35px 35px, 35px 35px !important;
    color: #ECE8E1 !important;
    font-family: 'Outfit', sans-serif !important;
}}

[data-testid="stSidebar"] {{
    background-color: #f5f7fa !important;
    border-right: 3px solid #00F0FF !important;
    box-shadow: 0 0 20px rgba(0, 240, 255, 0.25) !important;
}}
[data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {{
    color: #0f1923 !important;
}}

h1, h2, h3, h4, h5, h6, .stSubheader {{
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 800 !important;
    color: #ffffff !important;
    text-shadow: 0 0 10px rgba(0, 240, 255, 0.8) !important;
}}

div[data-baseweb="select"], input, textarea, div[data-baseweb="input"] {{
    background-color: #ffffff !important;
    color: #0f1923 !important;
    border: 2px solid #00F0FF !important;
    border-radius: 8px !important;
}}

button, .stButton button, .stLinkButton a {{
    background: linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%) !important;
    color: #0f1923 !important;
    border: 2px solid #00F0FF !important;
    border-radius: 8px !important;
    font-weight: 800 !important;
}}

.agent-info-card, .abilities-container, .weapon-display-panel, .map-frame {{
    background: rgba(10, 19, 29, 0.7);
    border: 1px solid rgba(0, 240, 255, 0.2);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
}}

.skin-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
}}
.skin-card {{
    background: rgba(10, 19, 29, 0.5);
    border: 1px solid rgba(0, 240, 255, 0.15);
    border-radius: 10px;
    padding: 15px;
    text-align: center;
}}

{bg_css}
</style>
""", unsafe_allow_html=True)

# API 로드
@st.cache_data
def get_data(endpoint):
    try:
        url = f"https://valorant-api.com/v1/{endpoint}?language=ko-KR"
        res = requests.get(url, verify=False, timeout=10)
        return res.json().get("data", []) if res.status_code == 200 else []
    except Exception:
        return []

agents = get_data("agents")
maps = get_data("maps")
weapons = get_data("weapons")

@st.cache_data(ttl=1800)
def get_user_gemini_models(api_key_str):
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key_str)
        models = []
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                clean_name = m.name.replace("models/", "")
                disp = m.display_name if m.display_name else clean_name
                models.append((f"✨ {disp}", clean_name))
        
        # 모델의 가벼움(속도) 기준 정렬: 8b(가장 가벼움) -> flash -> pro
        def get_model_priority(item):
            name = item[1].lower()
            if "8b" in name:
                return 1
            elif "flash" in name:
                return 2
            elif "pro" in name:
                return 3
            return 4
            
        models.sort(key=get_model_priority)
        return models
    except Exception:
        return []

# 사이드바 설정
st.sidebar.markdown("""
<div style='background:linear-gradient(135deg,#0f1923,#1a2a3a);border:1px solid #00F0FF;border-radius:10px;padding:12px;margin-bottom:8px;text-align:center;'>
    <div style='font-family:Orbitron,sans-serif;font-size:13px;font-weight:900;color:#00F0FF;'>⚡ VCT EVENT SYSTEM</div>
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("메뉴", ["요원 상세 정보", "무기 & 스킨", "🗺️ 맵 정보", "📊 전적 검색", "🤖 AI 스킨 추천"])

# 1. 요원 상세 정보
if menu == "요원 상세 정보":
    st.title("👤 요원 검색 및 정보")
    query = st.text_input("요원 이름을 입력하세요 (예: 제트, 바이퍼 등)")
    filtered_agents = [a for a in agents if a.get("isPlayableCharacter") and (not query or query.lower() in a["displayName"].lower())]
    
    if filtered_agents:
        sel_agent = st.selectbox("조회할 요원을 선택하세요", [a["displayName"] for a in filtered_agents])
        agent = next((a for a in filtered_agents if a["displayName"] == sel_agent), None)
        
        if agent:
            col1, col2 = st.columns([1.2, 2])
            with col1:
                st.image(agent['fullPortrait'], use_container_width=True)
            with col2:
                st.markdown(f"""
                <div class="agent-info-card">
                    <h3>{agent['displayName'].upper()}</h3>
                    <p><b>역할군:</b> {agent['role']['displayName'] if agent['role'] else '없음'}</p>
                    <p>{agent['description']}</p>
                </div>
                """, unsafe_allow_html=True)

            # 스킬 정보 표시
            st.markdown("<br><h3>⚡ 보유 스킬 정보</h3>", unsafe_allow_html=True)
            abilities = agent.get("abilities", [])
            if abilities:
                slot_map = {
                    "Grenade": "C 스킬 (기본/구매)",
                    "Ability1": "Q 스킬 (전술/유틸)",
                    "Ability2": "E 스킬 (시그니처/무료)",
                    "Ultimate": "X 스킬 (궁극기/필살기)",
                    "Passive": "패시브 (지속 효과)"
                }
                
                # 유효한 스킬만 필터링 (이름이 존재하고 Passive가 아닌 기본 스킬들 우선 배치)
                valid_abilities = [ab for ab in abilities if ab.get("displayName") and ab.get("slot") != "Passive"]
                passives = [ab for ab in abilities if ab.get("slot") == "Passive" and ab.get("displayName")]
                valid_abilities.extend(passives)

                def get_skill_effect_tag(d_name, d_desc):
                    text = (d_name + " " + d_desc).lower()
                    if any(k in text for k in ["연막", "구체", "차단", "장벽", "연막탄", "시야"]):
                        return "🌫️ 연막/차단"
                    elif any(k in text for k in ["이동", "돌진", "순풍", "순간이동", "점프", "도약", "날아"]):
                        return "⚡ 이동/기동"
                    elif any(k in text for k in ["탐지", "정찰", "위치", "추적", "드론", "화살"]):
                        return "👁️ 적 탐지"
                    elif any(k in text for k in ["실명", "섬광", "눈가림", "맹목"]):
                        return "💫 섬광/실명"
                    elif any(k in text for k in ["치유", "회복", "체력", "부활"]):
                        return "💚 치유/부활"
                    elif any(k in text for k in ["속박", "둔화", "제압", "기절", "진동", "무력화"]):
                        return "🛑 제압/디버프"
                    elif any(k in text for k in ["피해", "폭발", "화염", "수류탄", "사격", "칼", "포탄"]):
                        return "💥 데미지/공격"
                    return "🔮 전술 효과"

                def get_simple_action_summary(d_name, d_desc):
                    if not d_desc:
                        return d_name
                    clean = d_desc
                    prefixes = ["장착합니다. ", "장착합니다 ", "즉시 ", "발사하면 ", "스킬 키를 누르면 ", "조준하고 발사하여 "]
                    for p in prefixes:
                        if clean.startswith(p):
                            clean = clean[len(p):]
                    first = clean.split('. ')[0].strip()
                    if first.endswith('.'):
                        first = first[:-1]
                    if len(first) > 42:
                        first = first[:39] + "..."
                    return first

                if valid_abilities:
                    cols = st.columns(len(valid_abilities))
                    for idx, ab in enumerate(valid_abilities):
                        slot_name = slot_map.get(ab.get("slot"), ab.get("slot", ""))
                        icon_url = ab.get("displayIcon")
                        img_tag = f'<img src="{icon_url}" style="width: 50px; height: 50px; margin-bottom: 10px; filter: drop-shadow(0 0 5px #00F0FF);"/>' if icon_url else '<div style="height:60px;"></div>'
                        
                        desc = ab.get('description', '')
                        effect_tag = get_skill_effect_tag(ab.get('displayName', ''), desc)
                        short_desc = get_simple_action_summary(ab.get('displayName', ''), desc)

                        with cols[idx]:
                            st.markdown(f"""
                            <div class="abilities-container" style="text-align:center; height:100%; border: 1px solid rgba(0, 240, 255, 0.25); border-radius:10px; padding:15px; background:rgba(10, 19, 29, 0.55); display: flex; flex-direction: column; align-items: center; justify-content: flex-start;">
                                {img_tag}
                                <div style="font-weight: 800; font-size: 15px; color:#ffffff; font-family:\'Orbitron\', sans-serif;">{ab.get('displayName')}</div>
                                <div style="font-size: 11px; background: rgba(0, 240, 255, 0.15); color: #00F0FF; border: 1px solid rgba(0, 240, 255, 0.3); border-radius: 12px; padding: 2px 8px; margin: 4px 0 8px 0; font-weight: 700;">{effect_tag}</div>
                                <div style="font-size: 11.5px; color:#a0aec0; margin-bottom: 8px; font-weight: 600;">{slot_name}</div>
                                <div style="font-size: 12.5px; color:#ece8e1; text-align: left; line-height: 1.4; word-break: keep-all;">{short_desc}</div>
                            </div>
                            """, unsafe_allow_html=True)

                    # 스킬 카드 하단에 1줄 핵심 직관 요약 리스트 및 스킬 효과 안내 패널 표시
                    summary_html = "<div style='background:rgba(0, 240, 255, 0.05); border:1px dashed rgba(0, 240, 255, 0.4); border-radius:10px; padding:16px; margin-top:20px;'>"
                    summary_html += "<div style='font-size:15px; font-weight:800; color:#00F0FF; margin-bottom:6px;'>💡 요원 스킬 구성 & 효과 요약</div>"
                    summary_html += "<div style='font-size:12px; color:#a0aec0; margin-bottom:12px;'>* <b>C</b>: 구매형 보조 | <b>Q</b>: 전술 유틸 | <b>E</b>: 시그니처 | <b>X</b>: 궁극기</div>"
                    summary_html += "<ul style='margin:0; padding-left:20px; color:#ece8e1; font-size:13.5px; line-height:1.7;'>"
                    
                    for ab in valid_abilities:
                        s_name = slot_map.get(ab.get("slot"), ab.get("slot", ""))
                        d_name = ab.get("displayName", "")
                        raw_desc = ab.get("description", "")
                        eff_tag = get_skill_effect_tag(d_name, raw_desc)
                        clean_action = get_simple_action_summary(d_name, raw_desc)
                        summary_html += f"<li><b>[{s_name}] {d_name}</b> <span style='color:#00F0FF; font-size:12px;'>[{eff_tag}]</span> : {clean_action}</li>"
                    
                    summary_html += "</ul></div>"
                    st.markdown(summary_html, unsafe_allow_html=True)

# 2. 무기 및 스킨
elif menu == "무기 & 스킨":
    st.title("🔫 무기 및 스킨")
    if weapons:
        sel_w = st.selectbox("무기 선택", [w["displayName"] for w in weapons])
        weapon = next((w for w in weapons if w["displayName"] == sel_w), None)
        if weapon:
            st.image(weapon.get("displayIcon", ""), width=400)
            st.write(f"### 🎨 {weapon['displayName']} 스킨 목록")
            skins = [s for s in weapon.get("skins", []) if s.get("displayIcon")]
            
            cols = st.columns(3)
            for idx, skin in enumerate(skins):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="skin-card">
                        <img src="{skin['displayIcon']}" style="max-width:100%; height:100px; object-fit:contain;"/>
                        <p><b>{skin['displayName']}</b></p>
                    </div>
                    """, unsafe_allow_html=True)

# 3. 맵 정보
elif menu == "🗺️ 맵 정보":
    st.title("🗺️ 발로란트 맵 상세")
    map_list = [m["displayName"] for m in maps if m.get("displayIcon")]
    if map_list:
        sel_map = st.selectbox("맵 선택", map_list)
        m_data = next((m for m in maps if m["displayName"] == sel_map), None)
        if m_data:
            st.image(m_data.get("displayIcon", ""), use_container_width=True)

# 4. 전적 검색
elif menu == "📊 전적 검색":
    st.markdown("""
    <div style='background:rgba(10,19,29,0.8);border:1px solid #00F0FF;border-radius:10px;padding:24px;text-align:center;'>
        <h2 style='color:#00F0FF;margin-bottom:10px;'>📊 빠르고 정확한 전적 검색</h2>
        <p style='color:#ece8e1;font-size:15px;'>라이엇 공식 OP.GG 전적 검색을 지원합니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    player_name = st.text_input("닉네임#태그를 입력하세요 (예: FAKER#KR1)", "")
    
    if player_name.strip():
        if "#" in player_name:
            name_part, tag_part = player_name.strip().split("#", 1)
            opgg_url = f"https://valorant.op.gg/profile/{urllib.parse.quote(name_part)}-{urllib.parse.quote(tag_part)}"
            st.markdown(f'<a href="{opgg_url}" target="_blank"><button style="padding:10px 20px; font-weight:bold; cursor:pointer;">OP.GG에서 전적 보기 🔗</button></a>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("<div style='background:rgba(10,19,29,0.8);padding:15px;border-radius:8px;'><b>K/DA 비율</b><br><h2 style='color:#00F0FF;'>1.25</h2></div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div style='background:rgba(10,19,29,0.8);padding:15px;border-radius:8px;'><b>헤드샷 비율</b><br><h2 style='color:#00F0FF;'>24.5%</h2></div>", unsafe_allow_html=True)
        with col3:
            st.markdown("<div style='background:rgba(10,19,29,0.8);padding:15px;border-radius:8px;'><b>평균 딜량</b><br><h2 style='color:#ff4655;'>150.0</h2></div>", unsafe_allow_html=True)

# 5. 🤖 AI 대화형 스킨 추천 기능 (Gemini AI API 채팅 구현)
elif menu == "🤖 AI 스킨 추천":
    st.title("🤖 Gemini AI와 대화하는 발로란트 스킨 추천")
    st.write("발로란트 전문 AI 컨설턴트와 채팅하며 내 취향과 손맛에 딱 맞는 스킨을 찾아보세요!")
    
    # 사이드바 하단에서 Gemini API 키 입력
    api_key = st.sidebar.text_input("🔑 Gemini API Key 입력", type="password", help="aistudio.google.com에서 무료 발급")

    if not api_key:
        st.warning("💡 대화를 시작하려면 왼쪽 사이드바 맨 밑에 **Gemini API Key**를 입력해 주세요!")
        st.info("👉 API Key는 [Google AI Studio](https://aistudio.google.com/)에서 10초 만에 무료로 발급받을 수 있습니다.")
    else:
        # 내 계정/키에서 실제 사용 가능한 모델 동적 조회
        fetched_models = get_user_gemini_models(api_key)
        
        model_options = {}
        if fetched_models:
            for disp_name, code in fetched_models:
                model_options[disp_name] = code
            model_options["🔄 자동 탐색 (Auto Fallback)"] = "auto"
        else:
            model_options = {
                "⚡ Gemini 1.5 Flash 8B (가장 가벼움/속도 극대화)": "gemini-1.5-flash-8b",
                "⚡ Gemini 1.5 Flash Latest": "gemini-1.5-flash-latest",
                "🧠 Gemini 1.5 Pro Latest": "gemini-1.5-pro-latest",
                "🔄 자동 탐색 (Auto Fallback)": "auto"
            }

        selected_model_label = st.sidebar.selectbox("🤖 Gemini 모델 선택", list(model_options.keys()))
        selected_model_code = model_options[selected_model_label]

        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            # AI에 페르소나(전문가 역할) 부여
            system_instruction = """
            당신은 발로란트(VALORANT) 스킨 전문가이자 유저 맞춤형 컨설턴트입니다.
            사용자가 원하는 타격감(사운드), 느낌(SF, 묵직함, 경쾌함, 깔끔함 등), 주조색, 무기 종류, 예산(VP)에 맞춰 친구처럼 편하게 이야기하세요.
            사용자가 질문하면 발로란트 스킨 1~2개를 명확히 추천하고, 해당 스킨의 사운드 특징, 변형 애니메이션, 피니시 모션 등의 장점을 친절하고 재미있게 대화로 설명해 주세요.
            """

            # API Key 또는 선택된 모델 변경 감지 및 세션 초기화
            if st.session_state.get("current_api_key") != api_key or st.session_state.get("current_model_code") != selected_model_code:
                st.session_state.current_api_key = api_key
                st.session_state.current_model_code = selected_model_code
                st.session_state.pop("chat_session", None)
                st.session_state.pop("messages", None)

            # 메시지 목록 초기화
            if "messages" not in st.session_state:
                st.session_state.messages = [
                    {"role": "assistant", "content": f"반갑습니다, 요원님! 🎯 현재 **[{selected_model_label}]** 모델이 적용되었습니다. 찾으시는 스킨의 타격감이나 무기 종류, 선호하는 느낌을 편하게 적어주세요!"}
                ]

            # 기존 대화 내역 출력
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

            # 채팅 입력창 및 대화 처리
            if user_input := st.chat_input("원하는 스킨 느낌이나 질문을 적어보세요... (예: 둔탁한 소리가 나는 1티어 밴달 추천해줘)"):
                st.session_state.messages.append({"role": "user", "content": user_input})
                with st.chat_message("user"):
                    st.write(user_input)

                with st.chat_message("assistant"):
                    # 실제 내 API Key에서 검증된 모델 목록 기반 후보군 설정
                    available_codes = [code for _, code in fetched_models if code != "auto"] if fetched_models else ["gemini-1.5-flash-8b", "gemini-1.5-flash-latest", "gemini-1.5-pro-latest"]
                    
                    if selected_model_code == "auto":
                        candidates = available_codes
                    else:
                        candidates = [selected_model_code] + [m for m in available_codes if m != selected_model_code]

                    # 성공적으로 호출 완료되었던 작동 모델이 있다면 최우선 순위로 지정하여 직행
                    working_model = st.session_state.get("working_model")
                    if working_model and working_model in candidates:
                        candidates = [working_model] + [m for m in candidates if m != working_model]

                    ai_reply = None
                    last_err = None

                    # 성공할 때까지 후보 모델들로 시도
                    for model_name in candidates:
                        try:
                            if "chat_session" not in st.session_state:
                                # 이전 메시지가 있다면 최근 6개 대화만 추려서 컨텍스트 크기 경량화 및 응답 속도 최적화
                                raw_history = []
                                if "messages" in st.session_state:
                                    for msg in st.session_state.messages[-6:]:
                                        role = "model" if msg["role"] == "assistant" else "user"
                                        raw_history.append({"role": role, "parts": [msg["content"]]})

                                model = genai.GenerativeModel(
                                    model_name=model_name,
                                    system_instruction=system_instruction
                                )
                                st.session_state.chat_session = model.start_chat(history=raw_history)
                            
                            # 스트리밍 방식 적용하여 실시간 출력
                            response = st.session_state.chat_session.send_message(user_input, stream=True)
                            
                            def stream_generator():
                                for chunk in response:
                                    if chunk.text:
                                        yield chunk.text

                            ai_reply = st.write_stream(stream_generator)
                            
                            # 성공적으로 동작한 모델 정보 기억
                            st.session_state.working_model = model_name
                            last_err = None
                            break
                        except Exception as ex:
                            last_err = ex
                            st.session_state.pop("chat_session", None)

                    if ai_reply:
                        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                    else:
                        st.error(f"Gemini AI 호출 실패: {last_err}")

        except Exception as e:
            st.error(f"Gemini AI 호출 실패: {e}")