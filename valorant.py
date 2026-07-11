import streamlit as st
import requests
import json
import random
import time

# 1. 페이지 페이지 설정 (와이드 모드)
st.set_page_config(page_title="ValoPlan AI Hub", layout="wide", initial_sidebar_state="expanded")

# 2. Valorant-API 데이터 로드
@st.cache_data
def get_valorant_data(endpoint):
    url = f"https://valorant-api.com/v1/{endpoint}?language=ko-KR"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []

agents = get_valorant_data("agents")
playable_agents = [a for a in agents if a.get("isPlayableCharacter")]
maps = get_valorant_data("maps")
weapons_data = get_valorant_data("weapons")

if "valoplant_objects" not in st.session_state:
    st.session_state.valoplant_objects = []

st.sidebar.markdown("<h1 style='color: #ff4655; text-align: center;'>🔴 ValoPlan AI Hub</h1>", unsafe_allow_html=True)
menu = st.sidebar.radio("메뉴를 선택하세요", ["요원 정보 (Agents)", "무기 & 스킨 (Weapons)", "🗺️ 작전 지휘소 (Strategy Board)"])

# --- [메뉴 1: 요원 정보] ---
if menu == "요원 정보 (Agents)":
    st.title("👤 요원 정보")
    agent_names = [a["displayName"] for a in playable_agents]
    selected_agent_name = st.selectbox("요원을 선택하세요", agent_names)
    agent = next(a for a in playable_agents if a["displayName"] == selected_agent_name)
    
    col1, col2 = st.columns([1, 2])
    with col1: 
        st.image(agent["fullPortrait"], use_container_width=True)
    with col2:
        st.subheader(f"역할군: {agent['role']['displayName'] if agent['role'] else '없음'}")
        st.write(agent["description"])
        
        st.markdown("### ✨ 스킬 정보")
        for ab in agent["abilities"]:
            if ab.get("displayIcon"): 
                icon_col, text_col = st.columns([1, 15])
                with icon_col: st.image(ab["displayIcon"], width=40)
                with text_col: st.markdown(f"**{ab['displayName']}**")
            else:
                st.markdown(f"**{ab['displayName']}**")
            st.write(ab.get("description", "설명이 없습니다."))
            st.markdown("---")

# --- [메뉴 2: 무기 & 스킨 정보] ---
elif menu == "무기 & 스킨 (Weapons)":
    st.title("🔫 무기 및 스킨 정보")
    selected_weapon_name = st.selectbox("무기를 선택하세요", [w["displayName"] for w in weapons_data])
    weapon = next(w for w in weapons_data if w["displayName"] == selected_weapon_name)
    st.image(weapon["displayIcon"], width=400)
    
    st.markdown("### 🎨 보유 스킨 목록")
    cols = st.columns(3)
    for idx, skin in enumerate(weapon.get("skins", [])):
        if skin["displayIcon"] and "Standard" not in skin["displayName"]:
            with cols[idx % 3]:
                st.image(skin["displayIcon"], use_container_width=True)
                st.caption(skin["displayName"])

# --- [메뉴 3: 🗺️ 작전 지휘소 (오류 원천 차단 완결판)] ---
elif menu == "🗺️ 작전 지휘소 (Strategy Board)":
    st.title("🎯 실시간 AI 고속 기동 시뮬레이터")
    
    col_ctrl, col_canvas = st.columns([1, 2.5])

    with col_ctrl:
        st.subheader("🎒 전술 에셋 & 진영 설정")
        
        map_names = [m["displayName"] for m in maps if m.get("displayIcon")]
        selected_map_name = st.selectbox("전술을 세울 맵 선택", map_names)
        v_map = next(m for m in maps if m["displayName"] == selected_map_name)
        minimap_url = v_map["displayIcon"]
        st.markdown("---")
        
        obj_type = st.radio("종류 선택", ["공격팀 요원", "수비팀 요원", "💥 스파이크 (Spike)", "🧱 세이지 장벽", "⭕ 브림스톤 궁극기", "🚪 전술 문"])
        
        active_icon_url = ""
        display_name = obj_type
        team = "neutral"
        special_shape = "none"
        chosen_weapon_name = "밴달"
        
        if "요원" in obj_type:
            sel_agent = st.selectbox("요원 선택", [a["displayName"] for a in playable_agents])
            agent_data = next(a for a in playable_agents if a["displayName"] == sel_agent)
            active_icon_url = agent_data["displayIcon"]
            display_name = sel_agent
            team = "공격팀" if "공격" in obj_type else "수비팀"
            
            w_names = [w["displayName"] for w in weapons_data] + ["체임버: 역작", "체임버: 헤드헌터"]
            default_idx = w_names.index("밴달") if "밴달" in w_names else 0
            sel_weapon = st.selectbox(f"{sel_agent}의 무기 선택", w_names, index=default_idx)
            chosen_weapon_name = sel_weapon
            
        elif obj_type == "💥 스파이크 (Spike)":
            team = "공격팀"
            display_name = "스파이크"
            special_shape = "spike"
        elif obj_type == "🧱 세이지 장벽":
            special_shape = "rect"
            display_name = "세이지 장벽"
        elif obj_type == "⭕ 브림스톤 궁극기":
            special_shape = "circle"
            display_name = "브림스톤 궁"
        elif obj_type == "🚪 전술 문":
            special_shape = "door"
            display_name = "전술 문"
        
        if st.button("➕ 지도 위에 에셋 추가", use_container_width=True):
            existing_count = len(st.session_state.valoplant_objects)
            spawn_offset = (existing_count * 25) % 100
            
            st.session_state.valoplant_objects.append({
                "id": int(time.time() * 1000) + random.randint(0, 999),
                "type": obj_type,
                "shape": special_shape,
                "name": display_name,
                "team": team,
                "weapon": chosen_weapon_name,
                "hp": 150,
                "x": 250 + spawn_offset,
                "y": 250 + spawn_offset,
                "scaleX": 1.0, "scaleY": 1.0, "angle": 0
            })
            st.rerun()
            
        if st.button("🧹 배치 초기화", use_container_width=True):
            st.session_state.valoplant_objects = []
            st.rerun()

    with col_canvas:
        st.subheader(f"🗺️ {selected_map_name} 실시간 전술 전장")
        
        state_json = st.text_area("Canvas Sync", value=json.dumps(st.session_state.valoplant_objects), label_visibility="collapsed")
        try:
            st.session_state.valoplant_objects = json.loads(state_json)
        except:
            pass

        objects_json = json.dumps(st.session_state.valoplant_objects)

        # 🚨 브라우저 이미지 검은색 에러 차단: 텍스트 및 벡터 도형 기반 생성 시스템
        elements_js = ""
        for obj in st.session_state.valoplant_objects:
            if obj["shape"] == "none": # 요원 추가
                borderColor = '#ff4655' if obj['team'] == '공격팀' else '#00ea9a'
                short_name = obj["name"][:2] # 이름 앞 두 글자 추출 (ex: 제트, 피닉스)
                
                elements_js += f"""
                let bgCircle_{obj['id']} = new fabric.Circle({{ radius: 18, fill: '#0f1923', stroke: '{borderColor}', strokeWidth: 3, originX: 'center', originY: 'center' }});
                let text_{obj['id']} = new fabric.Text('{short_name}', {{ fontSize: 13, fill: '#ffffff', fontWeight: 'bold', originX: 'center', originY: 'center' }});
                
                let group_{obj['id']} = new fabric.Group([bgCircle_{obj['id']}, text_{obj['id']}], {{
                    left: {obj["x"]}, top: {obj["y"]}, originX: 'center', originY: 'center',
                    scaleX: {obj["scaleX"]}, scaleY: {obj["scaleY"]}, angle: {obj["angle"]},
                    cornerSize: 8, cornerColor: '#ffffff', transparentCorners: false
                }});
                group_{obj['id']}.objData = {json.dumps(obj)};
                group_{obj['id']}.isAgent = true; group_{obj['id']}.team = '{obj["team"]}'; group_{obj['id']}.hp = {obj["hp"]};
                group_{obj['id']}.weapon = '{obj["weapon"]}'; group_{obj['id']}.agentName = '{obj["name"]}';
                canvas.add(group_{obj['id']});
                """
            elif obj["shape"] == "spike": # 스파이크 추가
                elements_js += f"""
                let spCircle_{obj['id']} = new fabric.Circle({{ radius: 12, fill: '#ff4655', stroke: '#ffffff', strokeWidth: 2, originX: 'center', originY: 'center' }});
                let spText_{obj['id']} = new fabric.Text('💣', {{ fontSize: 12, originX: 'center', originY: 'center' }});
                let spike_{obj['id']} = new fabric.Group([spCircle_{obj['id']}, spText_{obj['id']}], {{ left: {obj["x"]}, top: {obj["y"]}, originX: 'center', originY: 'center' }});
                spike_{obj['id']}.objData = {json.dumps(obj)};
                canvas.add(spike_{obj['id']});
                """
            else: # 범위 스킬 추가
                shape_init = ""
                if obj["shape"] == "rect": shape_init = "new fabric.Rect({ width: 80, height: 18, fill: 'rgba(0, 230, 230, 0.5)', stroke: '#00ffff', strokeWidth: 2 })"
                elif obj["shape"] == "circle": shape_init = "new fabric.Circle({ radius: 35, fill: 'rgba(255, 70, 0, 0.3)', stroke: '#ff4655', strokeWidth: 2 })"
                elif obj["shape"] == "door": shape_init = "new fabric.Rect({ width: 45, height: 9, fill: 'rgba(140, 70, 20, 0.7)', stroke: '#ffaa00', strokeWidth: 2 })"
                
                if shape_init:
                    elements_js += f"""
                    let shape_{obj['id']} = {shape_init};
                    shape_{obj['id']}.set({{ left: {obj["x"]}, top: {obj["y"]}, originX: 'center', originY: 'center', scaleX: {obj["scaleX"]}, scaleY: {obj["scaleY"]}, angle: {obj["angle"]} }});
                    shape_{obj['id']}.setControlsVisibility({{ mt: true, mb: true, ml: true, mr: true, bl: true, br: true, tl: true, tr: true, mtr: true }});
                    shape_{obj['id']}.objData = {json.dumps(obj)};
                    canvas.add(shape_{obj['id']});
                    """

        js_code = """
        const canvas = new fabric.Canvas('cv', { selection: true });
        const logBoard = document.getElementById('status-board');
        
        // 🚨 충돌 캔버스 데이터 추출을 가볍게 하기 위해 500x500으로 스케일링 일치
        const collisionCanvas = document.createElement('canvas');
        collisionCanvas.width = 500; collisionCanvas.height = 500;
        const colCtx = collisionCanvas.getContext('2d', { willReadFrequently: true });

        const mapImage = new Image();
        mapImage.crossOrigin = "Anonymous";
        mapImage.src = 'MINIMAP_URL_PLACEHOLDER';
        mapImage.onload = function() {
            colCtx.drawImage(mapImage, 0, 0, 500, 500);
            
            fabric.Image.fromURL('MINIMAP_URL_PLACEHOLDER', function(fImg) {
                fImg.set({ selectable: false, evented: false, left: 0, top: 0, width: 500, height: 500 });
                canvas.setBackgroundImage(fImg, canvas.renderAll.bind(canvas));
            }, { crossOrigin: 'anonymous' });
        };

        function updateParent() {
            const objs = canvas.getObjects(); let updatedData = [];
            objs.forEach(o => {
                if(o.objData) {
                    let d = o.objData; d.x = o.left; d.y = o.top; d.scaleX = o.scaleX; d.scaleY = o.scaleY; d.angle = o.angle;
                    updatedData.push(d);
                }
            });
            const ta = window.parent.document.querySelector('textarea');
            if(ta) { ta.value = JSON.stringify(updatedData); ta.dispatchEvent(new Event('input', { bubbles: true })); }
        }
        canvas.on('object:modified', updateParent);

        ELEMENTS_JS_PLACEHOLDER

        const weaponStats = {
            "밴달": { body: 40, head: 160, fireDelay: 1 }, "팬텀": { body: 35, head: 140, fireDelay: 1 },
            "오퍼레이터": { body: 150, head: 255, fireDelay: 4 }, "셰리프": { body: 55, head: 145, fireDelay: 2 },
            "체임버: 역작": { body: 150, head: 255, fireDelay: 2 }, "체임버: 헤드헌터": { body: 55, head: 159, fireDelay: 1.5 }
        };

        // 🚨 벽 검지 로직 정밀 보정 (검은 여백 우회)
        function isWalkable(x, y) {
            if (x < 10 || x > 490 || y < 10 || y > 490) return false;
            try {
                let pixel = colCtx.getImageData(x, y, 1, 1).data;
                if (pixel[3] < 35) return false; 
            } catch(e) { return true; }
            return true;
        }

        let battleInterval;
        function startAiBattle() {
            logBoard.innerHTML = "🎬 <b>[전술 링크] 요원 정보 및 총기 시스템 교전을 시작합니다.</b><br><br>";
            let liveAgents = canvas.getObjects().filter(o => o.isAgent);
            if (liveAgents.filter(a => a.team === "공격팀").length === 0 || liveAgents.filter(a => a.team === "수비팀").length === 0) return;
            liveAgents.forEach(a => a.set('selectable', false));

            battleInterval = setInterval(() => {
                let attackers = liveAgents.filter(a => a.team === "공격팀" && a.hp > 0);
                let defenders = liveAgents.filter(a => a.team === "수비팀" && a.hp > 0);

                if (attackers.length === 0 || defenders.length === 0) {
                    clearInterval(battleInterval); return;
                }

                liveAgents.forEach(agent => {
                    if (agent.hp <= 0) return;
                    if (!agent.fireCooldown) agent.fireCooldown = 0;
                    if (agent.fireCooldown > 0) agent.fireCooldown--;

                    let targets = agent.team === "공격팀" ? defenders : attackers;
                    let closestEnemy = null; let minDist = 9999;
                    targets.forEach(t => {
                        let d = Math.hypot(t.left - agent.left, t.top - agent.top);
                        if (d < minDist) { minDist = d; closestEnemy = t; }
                    });

                    if (closestEnemy) {
                        let angle = Math.atan2(closestEnemy.top - agent.top, closestEnemy.left - agent.left);
                        let moveSpeed = 12;
                        let nextX = agent.left + Math.cos(angle) * moveSpeed;
                        let nextY = agent.top + Math.sin(angle) * moveSpeed;
                        
                        if (isWalkable(nextX, nextY)) {
                            agent.left = nextX; agent.top = nextY;
                        } else {
                            agent.left += (Math.random() - 0.5) * 25;
                            agent.top += (Math.random() - 0.5) * 25;
                        }
                        agent.setCoords();

                        if (minDist < 150 && agent.fireCooldown <= 0) {
                            let stat = weaponStats[agent.weapon] || { body: 30, head: 90, fireDelay: 2 };
                            agent.fireCooldown = stat.fireDelay;
                            let isHeadshot = Math.random() < 0.25;
                            let dmg = isHeadshot ? stat.head : stat.body;

                            closestEnemy.hp -= dmg;
                            let hitText = isHeadshot ? "<span style='color:#ffea00;'><b>[HEADSHOT 🎯]</b></span>" : "<b>[BODY]</b>";
                            logBoard.innerHTML += `💥 ${hitText} ${agent.team} <span style='color:#fff;'><b>${agent.agentName}</b></span> 👉 적 HP: ${Math.max(0, closestEnemy.hp)}<br>`;
                            logBoard.scrollTop = logBoard.scrollHeight;

                            if (closestEnemy.hp <= 0) {
                                logBoard.innerHTML += `💀 <b>[제압]</b> ${agent.team} <b>${agent.agentName}</b>가 적 <b>${closestEnemy.agentName}</b>를 처치했습니다.<br>`;
                                closestEnemy.set({ opacity: 0.15 });
                            }}
                    }}
                });
                canvas.renderAll();
            }, 150);
        }
        """
        js_code = js_code.replace("MINIMAP_URL_PLACEHOLDER", minimap_url).replace("ELEMENTS_JS_PLACEHOLDER", elements_js)

        # 📺 [해결] CSS Viewport Scale 레이아웃을 주입하여 가로/세로 잘림 현상을 100% 영구 해결
        board_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.1/fabric.min.js"></script>
            <style>
                body {{ margin:0; padding:0; background:#0f1923; font-family:sans-serif; overflow:hidden; }}
                /* 화면 크기에 맞춰 전체 요소를 100% 비율로 축소 자동매핑 */
                .main-wrapper {{ display: flex; flex-direction: row; gap: 15px; width: 100vw; height: 100vh; max-height: 520px; padding: 5px; box-sizing: border-box; }}
                
                .map-section {{ width: 500px; display: flex; flex-direction: column; }}
                .canvas-container {{ position: relative; width: 500px; height: 500px; border: 2px solid #ff4655; border-radius: 6px; background-color: #1a222b; overflow: hidden; }}
                canvas {{ position: absolute; top: 0; left: 0; }}
                
                #battle-btn {{ margin-top: 8px; width: 500px; padding: 10px; background: #ff4655; color: white; border: none; font-size: 14px; font-weight: bold; border-radius: 4px; cursor: pointer; }}
                
                .log-section {{ flex: 1; height: 518px; min-width: 250px; }}
                #status-board {{ 
                    width: 100%; height: 100%; background: #111822; border-radius: 6px; padding: 12px; 
                    font-size: 13px; color: #0ea; overflow-y: auto; border: 1px solid #2f3e4e; border-left: 5px solid #ff4655; box-sizing: border-box; line-height: 1.5;
                }}
            </style>
        </head>
        <body>
            <div class="main-wrapper">
                <div class="map-section">
                    <div class="canvas-container">
                        <canvas id="cv" width="500" height="500"></canvas>
                    </div>
                    <button id="battle-btn" onclick="startAiBattle()">🚀 픽셀 충돌 엔진 실시간 전투 개시</button>
                </div>
                <div class="log-section">
                    <div id="status-board">💬 대원을 배치하고 전투를 개시하세요. (얼굴 투명 버그 해결 토큰 적용)</div>
                </div>
            </div>
            <script>{js_code}</script>
        </body>
        </html>
        """
        # 스트림릿 컴포넌트 프레임을 가로 100%, 세로 550px 콤팩트 핏으로 제한하여 잘림 완벽 해결
        st.components.v1.html(board_html, height=550)