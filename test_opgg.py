import hashlib
import urllib.parse
import streamlit as st

# 1. 페이지 기본 설정 (가장 상단에 위치)
st.set_page_config(page_title="Valorant Stats Viewer", layout="wide")

# 2. 필요한 변수 기본값 초기화 (Unknown Name / UnboundLocalError 방지)
wins = 0
seed = "default_seed"
kda_ratio = 1.25
head_pct = 24.5
leg_pct = 5.0

# 3. Streamlit UI 및 HTML/CSS 렌더링
st.title("발로란트 전적 및 통계")

# HTML/CSS는 반드시 멀티라인 문자열("""...""")로 감싸서 st.markdown에 전달해야 함
html_content = f"""
<div style="background-color: #1f2937; padding: 20px; border-radius: 10px; color: white;">
    <h3 style="color: #ff4655;">플레이어 통계 요약</h3>
    <p><b>승리 횟수:</b> {wins}회</p>
    <p><b>K/DA 비율:</b> {kda_ratio}</p>
    <p><b>헤드샷 비율:</b> {head_pct}%</p>
    <p><b>다리 명중률:</b> {leg_pct}%</p>
</div>
"""

# HTML 안전 렌더링 옵션 적용
st.markdown(html_content, unsafe_allow_html=True)

# 4. 시드값 기반 해시 연산 예시 (기능 로직)
hashed_seed = hashlib.sha256(seed.encode()).hexdigest()
st.caption(f"시드 해시값: {hashed_seed}")