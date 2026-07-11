import streamlit as st
import requests
import urllib.parse

st.set_page_config(layout="wide", page_title="VALORANT - ION Edition")

# 1. 아이온(Ion) 테마 미래지향적 CSS 스타일링 적용
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

/* 전체 다크 스페이스 배경 */
.stApp {
    background: radial-gradient(circle at center, #101924 0%, #060a0f 100%) !important;
    color: #ECE8E1 !important;
    font-family: 'Outfit', sans-serif !important;
}

/* 사이드바 - 아이온 화이트 메탈 케이스 느낌 */
[data-testid="stSidebar"] {
    background-color: #f5f7fa !important;
    border-right: 3px solid #00F0FF !important;
    box-shadow: 0 0 20px rgba(0, 240, 255, 0.25) !important;
}
[data-testid="stSidebar"] * {
    color: #0f1923 !important;
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {
    color: #0f1923 !important;
    font-weight: 800 !important;
}

/* 미래지향적 헤더 네온 발광 효과 */
h1, h2, h3, h4, h5, h6, .stSubheader {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 800 !important;
    color: #ffffff !important;
    text-shadow: 0 0 10px rgba(0, 240, 255, 0.8), 0 0 20px rgba(0, 240, 255, 0.3) !important;
    letter-spacing: 1px;
}

/* 입력 필드 및 선택 박스 스타일 - 화이트 티타늄 질감 + 하늘색 테두리 */
div[data-baseweb="select"], input, textarea, div[data-baseweb="input"] {
    background-color: #ffffff !important;
    color: #0f1923 !important;
    border: 2px solid #00F0FF !important;
    border-radius: 8px !important;
    box-shadow: 0 0 10px rgba(0, 240, 255, 0.15) !important;
    font-weight: 600 !important;
}
div[data-baseweb="select"] *, input *, textarea * {
    color: #0f1923 !important;
}

/* 버튼 - 아이온 에너지 코어 발광 효과 */
button, .stButton button, .stLinkButton a {
    background: linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%) !important;
    color: #0f1923 !important;
    border: 2px solid #00F0FF !important;
    border-radius: 8px !important;
    font-weight: 800 !important;
    text-transform: uppercase;
    box-shadow: 0 0 12px rgba(0, 240, 255, 0.3) !important;
    transition: all 0.3s ease !important;
}
button:hover, .stButton button:hover, .stLinkButton a:hover {
    background: #00F0FF !important;
    color: #0f1923 !important;
    box-shadow: 0 0 25px rgba(0, 240, 255, 0.8) !important;
    transform: translateY(-2px);
}

/* 아코디언/익스팬더 - 사이버 글래스 모피즘 패널 */
.streamlit-expanderHeader {
    background-color: rgba(255, 255, 255, 0.07) !important;
    border: 1px solid rgba(0, 240, 255, 0.3) !important;
    border-radius: 8px !important;
    color: #ffffff !important;
    box-shadow: 0 0 8px rgba(0, 240, 255, 0.1) !important;
}
.streamlit-expanderContent {
    background-color: rgba(10, 18, 28, 0.85) !important;
    border-left: 1px solid rgba(0, 240, 255, 0.3) !important;
    border-right: 1px solid rgba(0, 240, 255, 0.3) !important;
    border-bottom: 1px solid rgba(0, 240, 255, 0.3) !important;
    border-radius: 0 0 8px 8px !important;
    color: #ece8e1 !important;
}
</style>
""", unsafe_allow_html=True)

# API 로드
@st.cache_data
def get_data(endpoint):
    url = f"https://valorant-api.com/v1/{endpoint}?language=ko-KR"
    res = requests.get(url)
    return res.json().get("data", []) if res.status_code == 200 else []

agents = get_data("agents")
maps = get_data("maps")
weapons = get_data("weapons")

menu = st.sidebar.radio("메뉴", ["요원 상세 정보", "무기 & 스킨", "🗺️ 맵 정보", "📊 전적 검색", "✈️ ION 비행기 게임"])

# 1. 요원 상세 정보 (검색 기능)
if menu == "요원 상세 정보":
    st.title("👤 요원 검색 및 정보")
    query = st.text_input("요원 이름을 입력하세요 (예: 제트, 바이퍼 등)")
    filtered_agents = [a for a in agents if a.get("isPlayableCharacter") and (not query or query.lower() in a["displayName"].lower())]
    
    for agent in filtered_agents:
        with st.expander(f"{agent['displayName']}"):
            col1, col2 = st.columns([1, 4])
            col1.image(agent['fullPortrait'], width=150)
            for ab in agent['abilities']:
                col2.markdown(f"**{ab['displayName']}**: {ab.get('description', '')}")

# 2. 무기 및 스킨 (val-skins.com 연동)
elif menu == "무기 & 스킨":
    st.title("🔫 무기 및 스킨")
    st.link_button("🌐 val-skins.com에서 스킨 확인하기", "https://www.val-skins.com/?view=skins&filter=Vandal")
    
    sel_w = st.selectbox("무기 선택", [w["displayName"] for w in weapons])
    weapon = next(w for w in weapons if w["displayName"] == sel_w)
    for skin in weapon.get("skins", []):
        if skin["displayIcon"] and "Standard" not in skin["displayName"]:
            st.image(skin["displayIcon"], width=150)
            st.write(skin["displayName"])

# 3. 맵 정보
elif menu == "🗺️ 맵 정보":
    st.title("🗺️ 발로란트 맵 상세")
    sel_map = st.selectbox("맵 선택", [m["displayName"] for m in maps if m.get("displayIcon")])
    m_data = next(m for m in maps if m["displayName"] == sel_map)
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("### 📍 전체 지도")
        st.image(m_data["displayIcon"], use_container_width=True)
    with col2:
        st.write("### 📸 맵 상세 사진")
        if m_data.get("splash"):
            st.image(m_data["splash"], use_container_width=True)
        else:
            st.write("상세 사진을 불러올 수 없습니다.")

# 4. 전적 확인
elif menu == "📊 전적 검색":
    st.title("📊 전적 확인")
    player_name = st.text_input("닉네임#태그를 입력하세요")
    if st.button("전적 조회") and player_name:
        if "#" in player_name:
            name_part, tag_part = player_name.split("#")
            url = f"https://tracker.gg/valorant/profile/riot/{urllib.parse.quote(name_part)}%23{tag_part}/overview"
            st.link_button("🔗 Tracker.gg에서 확인하기", url)
        else:
            st.error("닉네임#태그 형식으로 입력해주세요.")

# 5. 미니 비행기 게임 (아이온 스타파이터)
elif menu == "✈️ ION 비행기 게임":
    st.title("⚡ ION STARFIGHTER: 미니 비행기 게임")
    st.markdown("마우스를 움직여 **아이온 전투기**를 조종하세요. 에너지 레이저가 **자동으로 발사**됩니다!")
    st.markdown("날아오는 **에너지 노드(적)**를 모두 파괴하고 아이온 실드를 보호해 전장을 정복하세요.")

    # HTML5 Canvas + Web Audio API 사운드 게임 구현
    game_html = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <style>
            body {
                margin: 0;
                padding: 0;
                background: #080d14;
                color: #ffffff;
                font-family: sans-serif;
                overflow: hidden;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            #gameCanvas {
                border: 3px solid #00F0FF;
                border-radius: 12px;
                box-shadow: 0 0 25px rgba(0, 240, 255, 0.4);
                background: radial-gradient(circle at center, #101924 0%, #060a0f 100%);
                cursor: none; /* 실제 마우스 포인터 가리고 비행기로 대체 */
            }
        </style>
    </head>
    <body>
        <canvas id="gameCanvas" width="800" height="500"></canvas>
        <script>
            const canvas = document.getElementById("gameCanvas");
            const ctx = canvas.getContext("2d");

            let player = {
                x: 400,
                y: 400,
                size: 20,
                shield: 100,
                maxShield: 100
            };

            let bullets = [];
            let enemies = [];
            let particles = [];
            let stars = [];
            let score = 0;
            let gameOver = false;
            let gameStarted = false;
            let lastShotTime = 0;
            let fireRate = 180; // 발사 속도 (ms)

            // 우주 배경의 별들 세팅
            for (let i = 0; i < 50; i++) {
                stars.push({
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height,
                    size: Math.random() * 2 + 1,
                    speed: Math.random() * 3 + 1
                });
            }

            // 마우스 움직임 동기화
            canvas.addEventListener("mousemove", (e) => {
                const rect = canvas.getBoundingClientRect();
                player.x = e.clientX - rect.left;
                player.y = e.clientY - rect.top;
                
                if (player.x < 20) player.x = 20;
                if (player.x > canvas.width - 20) player.x = canvas.width - 20;
                if (player.y < 20) player.y = 20;
                if (player.y > canvas.height - 20) player.y = canvas.height - 20;
            });

            // 화면 클릭하여 시작 및 재시작
            canvas.addEventListener("click", () => {
                if (gameOver) {
                    resetGame();
                } else if (!gameStarted) {
                    gameStarted = true;
                    if (audioCtx.state === 'suspended') {
                        audioCtx.resume();
                    }
                }
            });

            // Web Audio API 기반 효과음 생성 시스템
            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            function playSound(freq, duration, type = 'sawtooth', endFreq = null) {
                try {
                    let osc = audioCtx.createOscillator();
                    let gain = audioCtx.createGain();
                    osc.connect(gain);
                    gain.connect(audioCtx.destination);
                    osc.type = type;
                    osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
                    if (endFreq) {
                        osc.frequency.exponentialRampToValueAtTime(endFreq, audioCtx.currentTime + duration);
                    }
                    gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
                    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
                    osc.start();
                    osc.stop(audioCtx.currentTime + duration);
                } catch(e) {}
            }

            function resetGame() {
                player.shield = 100;
                bullets = [];
                enemies = [];
                particles = [];
                score = 0;
                gameOver = false;
                gameStarted = true;
            }

            function spawnEnemy() {
                if (Math.random() < 0.045) {
                    enemies.push({
                        x: Math.random() * (canvas.width - 40) + 20,
                        y: -20,
                        speed: Math.random() * 2.5 + 2,
                        size: Math.random() * 12 + 10,
                        hp: 1,
                        color: 'hsl(' + (Math.random() * 40 + 340) % 360 + ', 90%, 50%)' // 에너지 코어 적
                    });
                }
            }

            function checkCollision(r1, r2) {
                let dist = Math.hypot(r1.x - r2.x, r1.y - r2.y);
                return dist < (r1.size || 20) + (r2.size || 20);
            }

            function createExplosion(x, y, color) {
                for (let i = 0; i < 15; i++) {
                    particles.push({
                        x: x,
                        y: y,
                        vx: (Math.random() - 0.5) * 8,
                        vy: (Math.random() - 0.5) * 8,
                        size: Math.random() * 3 + 1,
                        alpha: 1,
                        decay: Math.random() * 0.03 + 0.015,
                        color: color
                    });
                }
            }

            function update() {
                // 우주 배경 스크롤링
                stars.forEach(star => {
                    star.y += star.speed;
                    if (star.y > canvas.height) {
                        star.y = 0;
                        star.x = Math.random() * canvas.width;
                    }
                });

                if (gameStarted && !gameOver) {
                    // 무기 발사 (자동)
                    let now = Date.now();
                    if (now - lastShotTime > fireRate) {
                        // 아이온 특유의 듀얼 레이저 발사
                        bullets.push({ x: player.x - 15, y: player.y - 10, vy: -12, size: 3 });
                        bullets.push({ x: player.x + 15, y: player.y - 10, vy: -12, size: 3 });
                        playSound(650, 0.09, 'triangle', 180);
                        lastShotTime = now;
                    }

                    // 투사체 이동
                    bullets.forEach((b, index) => {
                        b.y += b.vy;
                        if (b.y < -10) bullets.splice(index, 1);
                    });

                    // 적 스폰
                    spawnEnemy();

                    // 적 이동 및 충돌
                    enemies.forEach((e, eIndex) => {
                        e.y += e.speed;
                        
                        // 아군 비행기와 충돌
                        if (checkCollision(player, e)) {
                            createExplosion(e.x, e.y, '#FF0055');
                            createExplosion(player.x, player.y, '#00F0FF');
                            enemies.splice(eIndex, 1);
                            player.shield -= 20;
                            playSound(120, 0.25, 'sawtooth', 35);
                            
                            if (player.shield <= 0) {
                                player.shield = 0;
                                gameOver = true;
                                playSound(50, 0.7, 'sawtooth', 10);
                            }
                            return;
                        }

                        // 레이저와 충돌
                        bullets.forEach((b, bIndex) => {
                            let dist = Math.hypot(e.x - b.x, e.y - b.y);
                            if (dist < e.size + b.size) {
                                createExplosion(e.x, e.y, '#00F0FF');
                                playSound(480, 0.12, 'sine', 700);
                                enemies.splice(eIndex, 1);
                                bullets.splice(bIndex, 1);
                                score += 100;
                            }
                        });

                        if (e.y > canvas.height + 20) enemies.splice(eIndex, 1);
                    });

                    // 파티클 이동
                    particles.forEach((p, index) => {
                        p.x += p.vx;
                        p.y += p.vy;
                        p.alpha -= p.decay;
                        if (p.alpha <= 0) particles.splice(index, 1);
                    });
                }
            }

            function draw() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                // 별들 그리기
                ctx.fillStyle = "rgba(255, 255, 255, 0.6)";
                stars.forEach(star => {
                    ctx.fillRect(star.x, star.y, star.size, star.size);
                });

                // 사이버네틱 무한 그리드 격자 (아이온 테마)
                ctx.strokeStyle = "rgba(0, 240, 255, 0.05)";
                ctx.lineWidth = 1;
                for (let x = 0; x < canvas.width; x += 40) {
                    ctx.beginPath();
                    ctx.moveTo(x, 0);
                    ctx.lineTo(x, canvas.height);
                    ctx.stroke();
                }
                let offset = (Date.now() / 25) % 40;
                for (let y = offset; y < canvas.height; y += 40) {
                    ctx.beginPath();
                    ctx.moveTo(0, y);
                    ctx.lineTo(canvas.width, y);
                    ctx.stroke();
                }

                // 대기(시작) 화면
                if (!gameStarted) {
                    ctx.textAlign = "center";
                    ctx.fillStyle = "#ffffff";
                    ctx.font = "bold 28px sans-serif";
                    ctx.shadowColor = "#00F0FF";
                    ctx.shadowBlur = 15;
                    ctx.fillText("ION STARFIGHTER", canvas.width / 2, canvas.height / 2 - 40);
                    
                    ctx.font = "16px sans-serif";
                    ctx.shadowBlur = 0;
                    ctx.fillStyle = "#8ba2b5";
                    ctx.fillText("마우스로 조종하면 에너지가 자동 발사됩니다.", canvas.width / 2, canvas.height / 2 + 10);
                    ctx.fillStyle = "#00F0FF";
                    ctx.fillText("미션을 개시하려면 화면을 클릭하세요", canvas.width / 2, canvas.height / 2 + 50);
                    return;
                }

                // 탄환 그리기
                bullets.forEach(b => {
                    ctx.shadowColor = "#00F0FF";
                    ctx.shadowBlur = 10;
                    ctx.fillStyle = "#00F0FF";
                    ctx.beginPath();
                    ctx.arc(b.x, b.y, b.size, 0, Math.PI * 2);
                    ctx.fill();
                });
                ctx.shadowBlur = 0;

                // 파티클 그리기
                particles.forEach(p => {
                    ctx.fillStyle = p.color;
                    ctx.globalAlpha = p.alpha;
                    ctx.fillRect(p.x, p.y, p.size, p.size);
                });
                ctx.globalAlpha = 1.0;

                // 에너지 코어 (적) 그리기
                enemies.forEach(e => {
                    ctx.save();
                    ctx.translate(e.x, e.y);
                    
                    ctx.shadowColor = "#FF0055";
                    ctx.shadowBlur = 8;
                    ctx.fillStyle = e.color;
                    
                    ctx.beginPath();
                    for (let i = 0; i < 8; i++) {
                        ctx.rotate(Math.PI / 4);
                        ctx.lineTo(e.size, 0);
                        ctx.lineTo(e.size / 2, e.size / 2);
                    }
                    ctx.closePath();
                    ctx.fill();
                    
                    // 중앙 핵
                    ctx.fillStyle = "#ffffff";
                    ctx.beginPath();
                    ctx.arc(0, 0, e.size / 3.5, 0, Math.PI * 2);
                    ctx.fill();
                    
                    ctx.restore();
                });
                ctx.shadowBlur = 0;

                // 아이온 테마 전전투기 (Sleek White + Glowing Cyan Core)
                if (!gameOver) {
                    ctx.save();
                    ctx.translate(player.x, player.y);

                    // 엔진 플레임 (하늘색 불꽃)
                    ctx.shadowColor = "#00F0FF";
                    ctx.shadowBlur = 12;
                    ctx.fillStyle = "#00F0FF";
                    ctx.beginPath();
                    ctx.moveTo(-5, 14);
                    ctx.lineTo(0, 24 + Math.random() * 8);
                    ctx.lineTo(5, 14);
                    ctx.closePath();
                    ctx.fill();

                    // 티타늄 화이트 전방향 날개 본체
                    ctx.shadowColor = "rgba(0, 240, 255, 0.2)";
                    ctx.shadowBlur = 5;
                    ctx.fillStyle = "#FFFFFF";
                    ctx.beginPath();
                    ctx.moveTo(0, -22); 
                    ctx.lineTo(-18, 14); 
                    ctx.lineTo(-5, 7);   
                    ctx.lineTo(0, 11);   
                    ctx.lineTo(5, 7);    
                    ctx.lineTo(18, 14);  
                    ctx.closePath();
                    ctx.fill();

                    // 아이온 특유의 다크 코어 캐노피
                    ctx.fillStyle = "#0a121c";
                    ctx.beginPath();
                    ctx.moveTo(0, -10);
                    ctx.lineTo(-3, 0);
                    ctx.lineTo(0, 3);
                    ctx.lineTo(3, 0);
                    ctx.closePath();
                    ctx.fill();

                    // 중앙의 빛나는 청록색 아이온 에너지 구체 (Energy Core)
                    ctx.shadowColor = "#00F0FF";
                    ctx.shadowBlur = 15;
                    ctx.fillStyle = "#00F0FF";
                    ctx.beginPath();
                    ctx.arc(0, 0, 5.5, 0, Math.PI * 2);
                    ctx.fill();

                    // 에너지 코어 화이트 스파크
                    ctx.fillStyle = "#FFFFFF";
                    ctx.beginPath();
                    ctx.arc(0, 0, 2.5, 0, Math.PI * 2);
                    ctx.fill();

                    ctx.restore();
                    ctx.shadowBlur = 0;
                }

                // HUD 인터페이스
                ctx.textAlign = "left";
                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 13px sans-serif";
                ctx.fillText("ION SHIELD: ", 20, 30);
                
                // 실드 바 구조
                ctx.fillStyle = "rgba(255, 255, 255, 0.1)";
                ctx.fillRect(110, 18, 150, 14);
                
                ctx.fillStyle = player.shield > 30 ? "#00F0FF" : "#FF0055";
                ctx.fillRect(110, 18, (player.shield / player.maxShield) * 150, 14);
                
                ctx.fillStyle = "#ffffff";
                ctx.fillText(player.shield + "%", 270, 30);

                // 스코어
                ctx.textAlign = "right";
                ctx.fillText("SCORE: " + score, canvas.width - 20, 30);

                // 게임 종료 화면
                if (gameOver) {
                    ctx.fillStyle = "rgba(8, 13, 20, 0.85)";
                    ctx.fillRect(0, 0, canvas.width, canvas.height);

                    ctx.textAlign = "center";
                    ctx.fillStyle = "#FF0055";
                    ctx.font = "bold 32px sans-serif";
                    ctx.shadowColor = "#FF0055";
                    ctx.shadowBlur = 15;
                    ctx.fillText("ION SHIELD DEPLETED", canvas.width / 2, canvas.height / 2 - 20);
                    
                    ctx.fillStyle = "#00F0FF";
                    ctx.font = "bold 20px sans-serif";
                    ctx.shadowColor = "#00F0FF";
                    ctx.fillText("FINAL SCORE: " + score, canvas.width / 2, canvas.height / 2 + 20);
                    
                    ctx.fillStyle = "#ffffff";
                    ctx.font = "14px sans-serif";
                    ctx.shadowBlur = 0;
                    ctx.fillText("미션을 다시 수행하려면 클릭하세요", canvas.width / 2, canvas.height / 2 + 70);
                }
            }

            function loop() {
                update();
                draw();
                requestAnimationFrame(loop);
            }

            loop();
        </script>
    </body>
    </html>
    """
    st.components.v1.html(game_html, height=520)