import base64
import streamlit as st
import requests
import re
import time
from PIL import Image
import os
from pathlib import Path

# đảm bảo luôn có URL mặc định
if "BACKEND_URL" not in st.session_state or not st.session_state["BACKEND_URL"]:
    st.session_state["BACKEND_URL"] = https://ai-congdanso-backend.onrender.com/"http://127.0.0.1:8000"

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

st.markdown("### 🚀 Nào, hãy cùng bắt đầu chương trình huấn luyện!")

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
    
    # TASK MODE: Trạm 1,2,4,5 (indices 0,1,3,4)
    with col_left:
        gen_key = f"gen_{i}"
        
        # --- Nút bấm sinh nhiệm vụ ---
        if st.button(f"🎲 Sinh nhiệm vụ tại Trạm {i+1}", key=gen_key):
            st.session_state[f"feedback_{i}"] = ""
            st.session_state[f"displayed_task_{i}"] = ""
            try:
                with st.spinner("CHIRON26 đang tạo nhiệm vụ..."):
                    res = requests.post(
                        f"{BACKEND_URL}/api/{endpoint}",
                        json={"mode": "generate_task"},
                        timeout=60
                    )
                    if res.status_code == 200:
                        raw = res.json().get("response", "")
                        
                        # [QUAN TRỌNG] Bước làm sạch dữ liệu để cắt bỏ Đáp án/Giải thích
                        clean = preprocess_task_text(raw) 
                        
                        st.session_state[f"task_{i}"] = clean
                    else:
                        st.error(f"❌ Lỗi API: {res.status_code}")
                        st.session_state[f"task_{i}"] = ""
            except Exception as e:
                st.error("⚠️ Không thể kết nối backend.")
                st.session_state[f"task_{i}"] = ""

        # --- Hiển thị nhiệm vụ ---
        current_task = st.session_state.get(f"task_{i}", "")
        
        if current_task:
            st.markdown("### 🧩 Nhiệm vụ của bạn:")

            st.markdown("<div class='task-box'>", unsafe_allow_html=True)

            # [QUAN TRỌNG] Thay hàm display_static_task cũ bằng hàm làm đẹp HTML mới
            # Hàm này sẽ chuyển text thô thành HTML đẹp, in đậm tiêu đề, in hoa...
            formatted_html = generate_formatted_html(current_task)
            
            st.markdown(formatted_html, unsafe_allow_html=True)
            
            # Lưu trạng thái
            st.session_state[f"displayed_task_{i}"] = current_task

            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<div class='small-note'>Gợi ý: Nhập đáp án ở khung phải (mỗi đáp án một dòng).</div>", unsafe_allow_html=True)

    # RIGHT COLUMN: answer input and submit
    with col_right:
        st.markdown("<div class='answer-sticky'><div class='answer-box'>", unsafe_allow_html=True)

        # separate widget key (for the textarea) and storage key (answer_value_{i})
        answer_storage_key = f"answer_value_{i}"
        answer_widget_key = f"ans_widget_{i}"

        # init storage
        if answer_storage_key not in st.session_state:
            st.session_state[answer_storage_key] = ""

        # ensure widget reflects stored value (so switching stations keeps text)
        # Use value through session_state to avoid conflict
        answer_text = st.text_area(
            "✏️ Nhập câu trả lời (vd: 1A)",
            value=st.session_state.get(answer_storage_key, ""),
            key=answer_widget_key,
            height=150
        )

        # keep storage in sync with widget
        st.session_state[answer_storage_key] = answer_text

        # Submit button
        submit_key = f"submit_{i}"
        if st.button("📤 Nộp bài", key=submit_key):
            if not answer_text.strip():
                st.warning("Bạn chưa nhập đáp án!")
            else:
                task_text = st.session_state.get(f"task_{i}", "")
                try:
                    res = requests.post(
                        f"{BACKEND_URL}/api/{endpoint}",
                        json={"mode": "evaluate", "answer": answer_text, "task": task_text},
                        timeout=60
                    )
                    if res.status_code == 200:
                        fb = res.json().get("feedback", "Không có phản hồi.")
                    else:
                        fb = f"⚠️ Lỗi backend: {res.status_code}"
                except Exception as e:
                    fb = "⚠️ Lỗi kết nối backend."

                # store feedback and keep user's answers
                st.session_state[f"feedback_{i}"] = fb
                st.session_state[answer_storage_key] = answer_text

        # show feedback if exists
        if st.session_state.get(f"feedback_{i}"):
            st.markdown("### 📢 Phản hồi:")
            st.success(st.session_state[f"feedback_{i}"])

        st.markdown("</div></div>", unsafe_allow_html=True)


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
