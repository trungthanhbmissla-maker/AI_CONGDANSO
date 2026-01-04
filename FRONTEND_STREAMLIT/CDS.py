import base64
import streamlit as st
import requests
import re
import time
from PIL import Image
import os
from pathlib import Path
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components 


# đảm bảo luôn có URL mặc định
if "BACKEND_URL" not in st.session_state or not st.session_state["BACKEND_URL"]:
    #st.session_state["BACKEND_URL"] = "http://127.0.0.1:8000"#Chạy local thì thay lại
    st.session_state["BACKEND_URL"] = "https://ai-congdanso-backend.onrender.com/" #Chạy Online
    
# ===================== CẤU HÌNH TRANG =====================
PRIMARY_COLOR = "#004A8F"
ACCENT_COLOR = "#0064C8"
CARD_BG = "#E8F3FF"

st.set_page_config(
    page_title="CHIRON 26",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================
# 🏫 LOGO & TIÊU ĐỀ
# ================================
def load_logo_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None

possible_paths = [
    Path(__file__).parent / "assets" / "logo.png",
    Path("assets/logo.png"),
    Path("logo.png"),
]
logo_b64 = next((load_logo_base64(p) for p in possible_paths if p.exists()), None)

if logo_b64:
    st.markdown(f"""
        <div style="text-align: center; margin-bottom: 5px; margin-top: -50px;">
            <img src="data:image/png;base64,{logo_b64}" width="150">
        </div>
    """, unsafe_allow_html=True)

# ===================== CSS =====================
st.markdown("""
<style>
.banner {
    background: #002a4d;
    padding: 20px 22px;
    border-radius: 10px;
    color: white;
    margin-bottom: 16px;
}
.banner-title {
    font-size: 30px;
    font-weight: 800;
}
.banner-sub {
    font-size: 16px;
    opacity: 0.95;
}

/* Card */
.card {
    background: """ + CARD_BG + """;
    padding: 14px 16px;
    border-radius: 10px;
    color: """ + PRIMARY_COLOR + """;
}

/* Chat */
.chat-user {
    background: #d4e8ff;
    padding: 10px;
    margin: 6px 0;
    border-radius: 8px;
    text-align: right;
}
.chat-assistant {
    background: #f5f5f5;
    padding: 10px;
    margin: 6px 0;
    border-radius: 8px;
}

/* Answer box */
.answer-box {
    background: #ffffff;
    padding: 12px;
    border-radius: 10px;
    border: 1px solid #d9d9d9;
    box-shadow: 0 1px 6px rgba(0,0,0,0.04);
}
.answer-sticky {
    position: sticky;
    top: 80px;
}

.task-box {
    max-height: 420px;
    overflow-y: auto;
    padding-right: 10px;
}
.small-note {
    font-size: 13px;
    color: #666;
}
</style>
""", unsafe_allow_html=True)

# ===================== SIDEBAR =====================
with st.sidebar:
    st.image(str(Path("assets/logo.png")), width=80)
    st.subheader("📚 Chọn trạm")
    station_choice = st.radio("Trạm:", [
        "1️⃣ Trạm 1 - Khai thác dữ liệu & thông tin",
        "2️⃣ Trạm 2 - Giao tiếp & hợp tác",
        "3️⃣ Trạm 3 - Sáng tạo nội dung số",
        "4️⃣ Trạm 4 - Bảo mật & an toàn",
        "5️⃣ Trạm 5 - Giải quyết vấn đề",
        "6️⃣ Trạm 6 - Ứng dụng trí tuệ nhân tạo"
    ], index=0)

    st.markdown("---")
    st.subheader("📘 Hướng dẫn sử dụng")
    st.markdown("""
- Trạm 1, 2, 4, 5: CHIRON26 sẽ sinh nhiệm vụ, các bạn sẽ trả lời bằng cách nhập đáp án vào ô đáp án. Định dạng đáp án: 1A, 2B.... CHIRON26 chấm và hỗ trợ phân tích đáp án.
- Trạm 3 & 6: Bạn sẽ tương tác với CHIRON26 để xây dựng ý tưởng sáng tạo nội dung; thảo luận các nội dung liên quan đến ứng dụng trí tuệ nhân tạo đạt hiệu quả.
""")

    st.markdown("---")
    st.markdown("**Liên hệ nhóm tác giả:** <br> "
    "**Trần Gia Bảo - Lò Anh Khang** <br> "
    "**BINH MINH INTERNAL SCHOOL**",
    unsafe_allow_html=True
    )
    backend_input = st.text_input(
        "Backend URL",
        value=st.session_state.get('BACKEND_URL', "https://ai-congdanso-backend.onrender.com/")
    )
    if backend_input:
        st.session_state['BACKEND_URL'] = backend_input

# ===================== BANNER =====================
st.markdown("""
<style>
.banner {
    width: 100%;
    display: flex;
    justify-content: center;   /* Căn giữa ngang */
    text-align: center;        /* Căn giữa chữ */
}

.banner-title {
    font-size: 26px;
    font-weight: 700;
    color: #FFFFFF !important;
    text-shadow: 0px 2px 6px rgba(0,0,0,0.35);
}

.banner-sub {
    font-size: 16px;
    margin-top: 4px;
    color: #FFFFFF !important;
}
</style>

<div class='banner'>
  <div>
    <div class='banner-title'>HỆ THỐNG HUẤN LUYỆN NĂNG LỰC SỐ CHO HỌC SINH PHỔ THÔNG</div>
    <div class='banner-sub'>Bảo vệ mình  •  Tôn trọng người  •  An toàn trên không gian mạng</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("### 🚀 Nào, hãy cùng CHIRON26 bắt đầu chương trình huấn luyện!")

# ===================== FIX: GỘP preprocess=====================
def preprocess_task_text(text: str):
    if not text:
        return ""
    
    lines = text.split('\n')
    cleaned_lines = []
    
    # 1. Cờ đánh dấu để bỏ qua phần Lời chào đầu tiên (nếu có)
    # Chúng ta chỉ bắt đầu lấy nội dung khi gặp "Tình huống" hoặc "Câu..."
    found_start = False
    
    # Danh sách từ khóa báo hiệu kết thúc bài (Đáp án/Giải thích)
    stop_markers = ["đáp án", "giải thích", "hướng dẫn trả lời", "gợi ý đáp án"]

    for line in lines:
        stripped = line.strip().lower()
        
        # --- LOGIC CẮT PHẦN ĐUÔI (ĐÁP ÁN) ---
        # Kiểm tra xem dòng này có bắt đầu bằng từ khóa cấm không (bỏ qua dấu * - •)
        # VD: "**Đáp án:** A" hoặc "Giải thích chi tiết:"
        clean_start = re.sub(r"^[\*\-\•\s]+", "", stripped) # Gọt sạch đầu dòng
        
        is_stop = False
        for marker in stop_markers:
            # Chỉ cắt nếu từ khóa nằm ngay đầu câu
            if clean_start.startswith(marker):
                is_stop = True
                break
        
        if is_stop:
            break # Gặp đáp án là dừng ngay, không lấy dòng này và các dòng sau nữa

        # --- LOGIC CẮT PHẦN ĐẦU (LỜI CHÀO) ---
        # Nếu chưa tìm thấy điểm bắt đầu, hãy kiểm tra xem dòng này có phải Tình huống/Câu hỏi không
        if not found_start:
            # Nếu dòng này chứa "Tình huống" hoặc "Câu 1", đánh dấu đã bắt đầu
            if "tình huống" in stripped or re.match(r"^câu\s*\d+", stripped):
                found_start = True
            else:
                # Nếu dòng này chỉ là lời chào luyên thuyên thì bỏ qua (không append)
                # Tuy nhiên, để an toàn (tránh cắt nhầm), nếu dòng quá dài (>50 ký tự) cứ giữ lại
                if len(line) < 50: 
                    continue 

        # Nếu đã qua các cửa ải trên -> Giữ lại dòng này
        cleaned_lines.append(line)
    
    # Ghép lại thành văn bản
    result = "\n".join(cleaned_lines).strip()
    
    # Fallback: Nếu cắt xong mà rỗng tuếch (do AI định dạng lạ), trả về text gốc
    if not result:
        return text
        
    return result
# ===================== HTML =====================
def generate_formatted_html(text):
    lines = text.split("\n")
    html = ""

    for raw in lines:
        line = raw.rstrip()
        if not line:
            html += "<div style='height:6px'></div>"
            continue
            
        # Làm sạch các ký tự đầu dòng để nhận diện (bỏ **, •, -, khoảng trắng)
        clean_check = re.sub(r"^[\s\*\-\•]+", "", line).replace("**", "")
        
        # --- 1. XỬ LÝ CÁC LOẠI TIÊU ĐỀ ---

        # CÂU 1, CÂU 2... (Giữ nguyên in hoa toàn bộ vì nó ngắn)
        if re.match(r"^Câu\s*\d+", clean_check, re.IGNORECASE):
            html += f"<div style='font-size:17px;font-weight:700;margin-top:10px'>{clean_check.upper()}</div>"
            continue

        # TÌNH HUỐNG... (Sửa đổi logic tại đây)
        if clean_check.lower().startswith("tình huống"):
            # Regex tách: (Chữ Tình huống + số) (dấu : hoặc .) (Nội dung phía sau)
            match = re.match(r"^(tình huống[\s\d]*)([:\.]?)\s*(.*)", clean_check, re.IGNORECASE)
            
            if match:
                label = match.group(1).upper() # VD: TÌNH HUỐNG 1
                sep = match.group(2)           # Dấu :
                content = match.group(3)       # Nội dung chính (Giữ nguyên hoa/thường)
                
                # Nếu có nội dung phía sau -> In hoa tiêu đề, nội dung in đậm thường
                if content:
                    html += (
                        f"<div style='margin-top:8px;color:#2c3e50'>"
                        f"<span style='font-weight:800'>{label}{sep}</span> " 
                        f"<span style='font-weight:600'>{content}</span>"     
                        f"</div>"
                    )
                else:
                    # Nếu dòng chỉ có tiêu đề (VD: Tình huống 1) -> In hoa hết
                    html += f"<div style='margin-top:8px;font-weight:700;color:#2c3e50'>{label}</div>"
            else:
                # Fallback nếu regex không bắt được (ít xảy ra)
                html += f"<div style='margin-top:8px;font-weight:700;color:#2c3e50'>{clean_check.upper()}</div>"
            continue

        # CÂU HỎI... (Áp dụng logic tương tự Tình huống)
        if clean_check.lower().startswith("câu hỏi"):
            match = re.match(r"^(câu hỏi)([:\.]?)\s*(.*)", clean_check, re.IGNORECASE)
            if match:
                label = match.group(1).upper() # CÂU HỎI
                sep = match.group(2)
                content = match.group(3)
                
                if content:
                    html += (
                        f"<div style='margin-top:8px;color:#2c3e50'>"
                        f"<span style='font-weight:800'>{label}{sep}</span> "
                        f"<span style='font-weight:600'>{content}</span>"
                        f"</div>"
                    )
                else:
                    html += f"<div style='margin-top:8px;font-weight:700;color:#2c3e50'>{label}</div>"
            continue

        # --- 2. XỬ LÝ ĐÁP ÁN ---
        m = re.match(r"^[\s\*\-\•]*([A-D])[\.\):]\s*(.*)", line)
        if m:
            label = m.group(1)
            content = m.group(2).strip()
            content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', content)
            html += (
                "<div style='margin-left:16px;margin-top:4px'>"
                f"<b>{label}.</b> {content}"
                "</div>"
            )
            continue

        # --- 3. XỬ LÝ GẠCH ĐẦU DÒNG THƯỜNG ---
        if line.strip().startswith(("* ", "- ", "• ")):
            content = re.sub(r"^[\*\-\•]\s*", "", line.strip())
            content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', content)
            html += (
                "<div style='margin-left:14px;margin-top:3px'>• "
                f"{content}</div>"
            )
            continue

        # --- 4. VĂN BẢN THƯỜNG ---
        formatted_line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
        html += f"<div style='margin-top:4px'>{formatted_line}</div>"

    return html

# ===================== STATIC TASK =====================
def display_static_task(text):
    html = generate_formatted_html(text)
    st.markdown(
        f"<div class='card' style='font-size:15px; line-height:1.45'>{html}</div>",
        unsafe_allow_html=True
    )

# ===================== PHẦN 2 — RENDER TRẠM + ROUTER + FOOTER =====================

# Ensure BACKEND_URL is read from session_state (can be changed in sidebar)
BACKEND_URL = st.session_state.get('BACKEND_URL', "http://127.0.0.1:8000")

stations = [
    ("station1-info-literacy", "🔍 Rèn luyện năng lực khai thác dữ liệu & thông tin."),
    ("station2-digital-collab", "🤝 Giao tiếp & hợp tác hiệu quả trong môi trường số."),
    ("station3-content-creation", "🎨 Sáng tạo nội dung số an toàn & có trách nhiệm."),
    ("station4-safety", "🛡️ Bảo vệ dữ liệu & phòng tránh rủi ro trực tuyến."),
    ("station5-problem-solving", "🧩 Ứng dụng công nghệ để giải quyết vấn đề."),
    ("station6-ai-ethics", "⚖️ Ứng dụng trí tuệ nhân tạo.")
]

def render_station(i, endpoint, desc):
    st.subheader(f"🏁 Trạm {i+1}")
    st.info(desc)

    col_left, col_right = st.columns([3, 1])

    # =========================
    # TRẠM 3 & 6 — CHAT AI
    # =========================
    if i in (2, 5):
        with col_left:
            session_key = f"messages_{i}"
            form_key = f"chat_form_{i}"

            # Khởi tạo lịch sử chat
            if session_key not in st.session_state:
                st.session_state[session_key] = []

            # Hiển thị lịch sử chat
            for msg in st.session_state[session_key]:
                role = msg["role"]
                content = msg["content"]
                bubble = "chat-user" if role == "user" else "chat-assistant"
                st.markdown(f"<div class='{bubble}'>{content}</div>", unsafe_allow_html=True)

            st.markdown("---")

            # Form gửi chat, clear_on_submit=True tự reset ô nhập
            with st.form(key=form_key, clear_on_submit=True):
                chat_input = st.text_area("💬 Nhập tin nhắn cho CHIRON26", height=120)
                submitted = st.form_submit_button("📩 Gửi tin nhắn")

                if submitted and chat_input.strip():
                    # 1. Lưu user message
                    st.session_state[session_key].append({"role": "user", "content": chat_input})

                    # 2. Gửi backend
                    try:
                        # Thêm spinner cho đẹp để người dùng biết đang xử lý
                        with st.spinner("CHIRON đang trả lời..."):
                            res = requests.post(
                                f"{BACKEND_URL}/api/{endpoint}",
                                json={"message": chat_input},
                                timeout=60
                            )
                            reply = res.json().get("response", "🤖CHIRON26 hiện không thể trả lời.")
                    except:
                        reply = "⚠️ Không thể kết nối backend."

                    # 3. Lưu assistant message
                    st.session_state[session_key].append({"role": "assistant", "content": reply})
                    
                    # 4. QUAN TRỌNG: Ép chạy lại trang để hiển thị ngay lập tức
                    st.rerun()

        # Cột phải bỏ trống
        with col_right:
            st.empty()
        return
    
# ================= TASK MODE: Trạm 1,2,4,5 =================
    # ================= ⏱️ TÍNH TOÁN THỜI GIAN =================
    start_time = st.session_state.get(f"start_time_{i}")
    TOTAL_TIME = 300  # 5 phút
    
    # Kiểm tra xem đã nộp bài chưa
    is_submitted = st.session_state.get(f"result_{i}") is not None

    if start_time and not is_submitted:
        # Nếu đang làm bài: Tính thời gian trôi qua
        elapsed = int(time.time() - start_time)
        remaining = max(0, TOTAL_TIME - elapsed)
        time_up = remaining == 0
    elif is_submitted:
        # Nếu đã nộp bài: Dừng thời gian tại thời điểm nộp (Hoặc chỉ cần hiện 0 để báo xong)
        # Ở đây ta set time_up = True để khóa các nút, nhưng không hiện màu đỏ cảnh báo
        remaining = 0 
        time_up = False 
    else:
        remaining = TOTAL_TIME
        time_up = False

    # ================= BẮT ĐẦU GIAO DIỆN =================
    
    # --- CỘT TRÁI: ĐỀ BÀI ---
    with col_left:
        gen_key = f"gen_{i}"
        
        # Nút sinh nhiệm vụ
        # Nếu đang làm (chưa nộp và chưa hết giờ) thì không được sinh lại để tránh reset giờ
        disable_gen = (start_time is not None and not time_up and not is_submitted)
        
        if st.button(f"🎲 Sinh nhiệm vụ tại Trạm {i+1}", key=gen_key, disabled=disable_gen, type="primary"):
            st.session_state[f"feedback_{i}"] = ""
            st.session_state[f"result_{i}"] = None
            # Reset lựa chọn radio
            st.session_state[f"q1_{i}"] = "A" 
            st.session_state[f"q2_{i}"] = "A"
            
            try:
                with st.spinner("Đang tạo đề bài..."):
                    res = requests.post(
                        f"{BACKEND_URL}/api/{endpoint}",
                        json={"mode": "generate_task"},
                        timeout=60
                    )
                if res.status_code == 200:
                    raw = res.json().get("response", "")
                    clean = preprocess_task_text(raw)
                    st.session_state[f"task_{i}"] = clean
                    st.session_state[f"start_time_{i}"] = time.time()
                    st.rerun()
                else:
                    st.error("Lỗi API.")
            except Exception:
                st.error("Lỗi kết nối.")

        # Hiển thị nội dung
        current_task = st.session_state.get(f"task_{i}")
        if current_task:
            st.markdown("### 🧩 Nhiệm vụ của bạn:")
            st.markdown(generate_formatted_html(current_task), unsafe_allow_html=True)

    # --- CỘT PHẢI: ĐỒNG HỒ & TRẮC NGHIỆM ---
 
    with col_right:
        
        # 1. ĐỒNG HỒ
        if st.session_state.get(f"task_{i}"):
            if is_submitted:
                st.markdown(
                    """
                    <div style="background:#e5e7eb; color:#374151; padding:10px; border-radius:8px; text-align:center; font-weight:bold; margin-bottom:15px;">
                        ⏹️ Đã nộp bài
                    </div>
                    """, unsafe_allow_html=True
                )
            elif time_up:
                st.markdown(
                    """
                    <div style="background:#ef4444; color:white; padding:10px; border-radius:8px; text-align:center; font-weight:bold; margin-bottom:15px;">
                        🛑 HẾT GIỜ
                    </div>
                    """, unsafe_allow_html=True
                )
            else:
                timer_html_code = f"""
                <div id="timer-box" style="background-color: #004A8F; color: white; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; font-family: sans-serif; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <span id="timer-display">⏱️ Loading...</span>
                </div>
                <script>
                    var timeleft = {remaining};
                    function updateTimer() {{
                        if(timeleft <= 0){{
                            document.getElementById("timer-display").innerHTML = "🛑 HẾT GIỜ";
                            document.getElementById("timer-box").style.backgroundColor = "#ef4444";
                        }} else {{
                            var m = Math.floor(timeleft / 60);
                            var s = timeleft % 60;
                            var mStr = m < 10 ? "0" + m : m;
                            var sStr = s < 10 ? "0" + s : s;
                            document.getElementById("timer-display").innerHTML = "⏱️ " + mStr + ":" + sStr;
                            timeleft -= 1;
                        }}
                    }}
                    updateTimer();
                    setInterval(updateTimer, 1000);
                </script>
                """
                components.html(timer_html_code, height=50)
        else:
            st.empty()

        # 2. KHUNG TRẢ LỜI (RADIO BUTTON)
        if st.session_state.get(f"task_{i}"):
            with st.container():
                st.markdown("#### ✏️ Chọn đáp án:")
                
                c1, c2 = st.columns(2)
                disable_input = time_up or is_submitted
                
                with c1:
                    st.markdown("**Câu 1:**")
                    ans1 = st.radio("Câu 1", ["A", "B"], key=f"q1_{i}", horizontal=True, label_visibility="collapsed", disabled=disable_input)
                
                with c2:
                    st.markdown("**Câu 2:**")
                    ans2 = st.radio("Câu 2", ["A", "B"], key=f"q2_{i}", horizontal=True, label_visibility="collapsed", disabled=disable_input)

                final_answer_text = f"1{ans1}, 2{ans2}"

                # 3. NÚT NỘP BÀI
                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                
                if not is_submitted:
                    if st.button("📤 Nộp bài", key=f"submit_{i}", disabled=disable_input, type="primary"):
                        should_rerun = False 
                        
                        with st.spinner("Đang chấm..."):
                            try:
                                res = requests.post(
                                    f"{BACKEND_URL}/api/{endpoint}",
                                    json={"mode": "evaluate", "answer": final_answer_text, "task": current_task},
                                    timeout=60
                                )
                                fb = res.json().get("feedback", "")
                                
                                # --- LOGIC CHẤM ĐIỂM NGHIÊM NGẶT (CHỈ DÙNG SCORE) ---
                                is_perfect = False
                                
                                # 1. Tìm dòng SCORE: x/y (Ví dụ: SCORE: 0/2, SCORE: 2/2)
                                score_match = re.search(r"SCORE:\s*(\d+)/(\d+)", fb, re.IGNORECASE)
                                
                                if score_match:
                                    num_correct = int(score_match.group(1)) # Số câu đúng
                                    total = int(score_match.group(2))       # Tổng số câu
                                    
                                    # Chỉ Đạt khi đúng Tuyệt đối (ví dụ 2/2)
                                    if num_correct == total and total > 0:
                                        is_perfect = True
                                    
                                    # Xóa dòng SCORE khô khan khỏi nội dung hiển thị
                                    display_feedback = re.sub(r"SCORE:.*\n?", "", fb, flags=re.IGNORECASE).strip()
                                else:
                                    # 2. TRƯỜNG HỢP KHẨN CẤP: AI không trả về SCORE
                                    # Mặc định là FALSE (Chưa đạt) để an toàn, không cho pass bừa.
                                    is_perfect = False 
                                    display_feedback = fb
                                    # Có thể thêm dòng cảnh báo nếu muốn
                                    # display_feedback = "⚠️ Lỗi định dạng chấm điểm.\n\n" + fb
                                
                                st.session_state[f"result_{i}"] = {
                                    "passed": is_perfect, 
                                    "feedback": display_feedback
                                }
                                should_rerun = True
                                
                            except Exception as e:
                                st.error(f"Lỗi kết nối: {e}")
                        
                        if should_rerun:
                            st.rerun()

        # 4. HIỂN THỊ KẾT QUẢ
        result = st.session_state.get(f"result_{i}")
        if result:
            st.markdown("---")
            if result["passed"]:
                st.markdown(
                    """
                    <div style="background-color:#dcfce7; color:#166534; padding:12px; border-radius:8px; border:1px solid #22c55e; text-align:center;">
                        🎉 <b>XUẤT SẮC! (ĐÚNG 100%)</b>
                    </div>
                    """, unsafe_allow_html=True
                )
            else:
                st.markdown(
                    """
                    <div style="background-color:#fee2e2; color:#991b1b; padding:12px; border-radius:8px; border:1px solid #ef4444; text-align:center;">
                        ⚠️ <b>CHƯA ĐẠT</b><br>
                        <span style="font-size:13px;">(Cần đúng 100% mới được tính là Đạt)</span>
                    </div>
                    """, unsafe_allow_html=True
                )
            
           
            st.markdown(
                f"""
                <div style='margin-top:10px; font-size:14px; color:#065f46; background:#f0fff4; padding:15px; border-radius:8px; border: 1px solid #bbf7d0;'>
                    <b>🤖 Để CHIRON26 gợi ý thêm cho bạn nhé:</b><br>{result['feedback']}
                </div>
                """,
                unsafe_allow_html=True
            )

# ===================== ROUTER: lấy trạm được chọn ở sidebar =====================
selected_label = station_choice
mapping = {
    "1️⃣ Trạm 1 - Khai thác dữ liệu & thông tin": 0,
    "2️⃣ Trạm 2 - Giao tiếp & hợp tác": 1,
    "3️⃣ Trạm 3 - Sáng tạo nội dung số": 2,
    "4️⃣ Trạm 4 - Bảo mật & an toàn": 3,
    "5️⃣ Trạm 5 - Giải quyết vấn đề": 4,
    "6️⃣ Trạm 6 - Ứng dụng trí tuệ nhân tạo": 5
}
idx = mapping.get(selected_label, 0)
endpoint, desc = stations[idx]
render_station(idx, endpoint, desc)

# ===================== FOOTER =====================
st.markdown("---")
st.caption("Chiron 26 - Hệ thống huấn luyện năng lực số cho học sinh phổ thông")
