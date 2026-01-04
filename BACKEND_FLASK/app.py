import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

# ====================================================
# 1️⃣ Cấu hình ban đầu
# ====================================================
load_dotenv()

app = Flask(__name__)
CORS(app)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY or GOOGLE_API_KEY.strip() == "":
    GOOGLE_API_KEY = "AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxx" #Đưa lên onrender cần thay đổi để không lộ key
    print("⚠️ Không tìm thấy GOOGLE_API_KEY trong .env → đang dùng key dự phòng trong code.")

if not GOOGLE_API_KEY:
    raise ValueError("❌ Không tìm thấy GOOGLE_API_KEY. Vui lòng đặt trong file .env hoặc trong code fallback.")

try:
    genai.configure(api_key=GOOGLE_API_KEY)
    print("✅ Cấu hình Gemini API thành công.")
except Exception as e:
    print(f"❌ Lỗi khi cấu hình Gemini API: {e}")
    raise

MODELS_TO_TRY = [
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash-lite-001",
    "gemini-2.5-pro-preview-tts",
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash-lite-preview-09-2025",
    "gemini-2.5-computer-use-preview-10-2025"
    "gemini-3-flash-preview",
    "gemini-3-pro-preview"
]

# ====================================================
# 2️⃣ Hàm gọi Gemini an toàn
# ====================================================
'''def generate_text(prompt, safety_settings=None, generation_config=None):
    """
    Gọi Gemini an toàn với nhiều fallback:
    - hỗ trợ response.candidates[*].content.parts (cũ)
    - hỗ trợ response.text hoặc response.output_text (mới)
    - luôn trả về string (không trả None) — nếu không có nội dung sẽ trả message thông báo
    """
    safety_settings = safety_settings or []
    generation_config = generation_config or {"max_output_tokens": 300, "temperature": 0.8}

    last_error = None
    for model_name in MODELS_TO_TRY:
        try:
            print(f"🔄 Thử model: {model_name}")
            model = genai.GenerativeModel(model_name=model_name)
            response = model.generate_content(
                prompt,
                safety_settings=safety_settings,
                generation_config=generation_config,
            )

            # 1) Nếu đối tượng response có thuộc tính 'candidates' kiểu cũ
            try:
                if hasattr(response, "candidates") and response.candidates:
                    candidate = response.candidates[0]
                    # candidate.content.parts (trường hợp bạn dùng trước)
                    if hasattr(candidate, "content") and candidate.content:
                        parts = getattr(candidate.content, "parts", None)
                        if parts:
                            text = "".join([getattr(p, "text", "") for p in parts if getattr(p, "text", None)])
                            if text and text.strip():
                                print(f"✅ Thành công (candidates.parts) với {model_name}")
                                return text.strip()

                    # fallback: candidate may have text directly
                    if hasattr(candidate, "text") and candidate.text:
                        t = candidate.text.strip()
                        if t:
                            print(f"✅ Thành công (candidate.text) với {model_name}")
                            return t

            except Exception as e:
                # không dừng, thử các dạng khác
                print(f"⚠️ Không lấy được từ candidates: {e}")

            # 2) Nếu response có .text hoặc .output_text (một số SDK trả text trực tiếp)
            if hasattr(response, "text") and response.text:
                t = response.text.strip()
                if t:
                    print(f"✅ Thành công (response.text) với {model_name}")
                    return t

            if hasattr(response, "output_text") and response.output_text:
                t = response.output_text.strip()
                if t:
                    print(f"✅ Thành công (response.output_text) với {model_name}")
                    return t

            # 3) Một số API trả dict-like trong str form; cố parse fallback
            try:
                # Convert to string and return non-empty
                s = str(response)
                if s and len(s) > 20:  # tránh trả các chuỗi ngắn vô nghĩa
                    print(f"✅ Thành công (str(response)) với {model_name}")
                    return s.strip()
            except Exception:
                pass

            # nếu đến đây: response không chứa text rõ ràng, tiếp tục model khác
            last_error = f"No text in response for model {model_name}"
            print(f"⚠️ {last_error}")

        except ResourceExhausted:
            print(f"⚠️ Model {model_name} hết quota, thử model khác...")
            last_error = f"ResourceExhausted:{model_name}"
            continue
        except Exception as e:
            print(f"❌ Lỗi gọi model {model_name}: {e}")
            last_error = str(e)
            continue

    # Nếu không có model nào trả về nội dung hợp lệ -> trả fallback rõ ràng
    fallback_msg = ("⚠️ Hệ thống AI hiện không trả nội dung rõ ràng. "
                    "Xin thử lại sau hoặc liên hệ quản trị viên. "
                    "Chi tiết lỗi: " + (last_error or "unknown"))
    print(fallback_msg)
    return fallback_msg'''
def generate_text(prompt, safety_settings=None, generation_config=None):
    #raise RuntimeError("🔥 ĐANG VÀO generate_text MỚI 🔥")
    safety_settings = safety_settings or []
    generation_config = generation_config or {
        "max_output_tokens": 300,
        "temperature": 0.8
    }

    last_error = None

    for model_name in MODELS_TO_TRY:
        print(f"🔄 ĐANG THỬ MODEL: {model_name}")

        try:
            model = genai.GenerativeModel(model_name=model_name)
            response = model.generate_content(
                prompt,
                safety_settings=safety_settings,
                generation_config=generation_config,
            )

            # ===== LẤY TEXT =====
            if hasattr(response, "text") and response.text:
                print(f"✅ OK: response.text từ {model_name}")
                return response.text.strip()

            if hasattr(response, "candidates") and response.candidates:
                c = response.candidates[0]
                if hasattr(c, "content") and hasattr(c.content, "parts"):
                    text = "".join(p.text for p in c.content.parts if hasattr(p, "text"))
                    if text.strip():
                        print(f"✅ OK: candidates.parts từ {model_name}")
                        return text.strip()

            raise ValueError("Không có text hợp lệ trong response")

        except ResourceExhausted as e:
            print(f"⚠️ QUOTA HẾT tại {model_name}: {e}")
            last_error = f"ResourceExhausted:{model_name}"
            continue

        except Exception as e:
            print(f"❌ MODEL {model_name} LỖI: {type(e).__name__} | {e}")
            last_error = f"{model_name}:{e}"
            continue

    return (
        "⚠️ Hệ thống AI hiện không khả dụng.\n"
        "Vui lòng thử lại sau.\n"
        f"Chi tiết lỗi cuối: {last_error}"
    )
# ====================================================
# 🛰️ TRẠM 1 – KHAI THÁC DỮ LIỆU & THÔNG TIN
# ====================================================
@app.route("/api/station1-info-literacy", methods=["POST"])
def station1_info_literacy():
    try:
        data = request.get_json(silent=True) or {}
        mode = data.get("mode", "generate_task")
        answer = data.get("answer", "")
        task = data.get("task", "")
        topic = data.get("topic", "tin giả về trường học")

        if mode == "generate_task":
            prompt = f"""
            Bạn là AI giáo dục CHIRON26 giúp học sinh rèn luyện kỹ năng xác thực thông tin.
            Hãy tạo **2 câu hỏi trắc nghiệm A/B** xoay quanh chủ đề "{topic}" (tin giả, thông tin sai lệch).
            
            Cấu trúc bắt buộc:
            TÌNH HUỐNG 1: [Mô tả ngắn gọn về một tin đồn/tin giả]
            CÂU HỎI: [Câu hỏi về hành động nên làm]
            A. [Hành động sai/thiếu kiểm chứng]
            B. [Hành động đúng/kiểm chứng nguồn tin]
            
            (Tương tự cho Tình huống 2)
            
            QUAN TRỌNG: KHÔNG được kèm theo đáp án đúng hay lời giải thích ở cuối (để học sinh tự làm).
            """
            result = generate_text(prompt, generation_config={"max_output_tokens": 2048, "temperature": 0.8})
            return jsonify({"station": 1, "response": result})

        elif mode == "evaluate":
            prompt = f"""
            Bạn là giám khảo chấm thi trắc nghiệm kỹ năng thông tin.
            
            1. ĐỀ BÀI:
            {task}

            2. HỌC SINH CHỌN:
            {answer}

            3. YÊU CẦU CHẤM:
            - Xác định đáp án đúng của từng tình huống (Đáp án đúng là hành động kiểm chứng thông tin, tìm nguồn chính thống).
            - So sánh với lựa chọn của học sinh.
            - Tính tổng số câu đúng (trên 2 câu).

            4. ĐỊNH DẠNG TRẢ LỜI BẮT BUỘC (Dòng đầu tiên):
            SCORE: x/2
            
            (Trong đó x là số câu đúng. Ví dụ: SCORE: 0/2, SCORE: 1/2, SCORE: 2/2).
            
            Sau dòng SCORE mới được viết giải thích chi tiết vì sao đúng/sai.
            """
            
            # Giảm temperature xuống 0.5 để chấm điểm chính xác, không "văn vở"
            result = generate_text(prompt, generation_config={"max_output_tokens": 2048, "temperature": 0.5})
            return jsonify({"station": 1, "feedback": result})

        else:
            return jsonify({"error": "Invalid mode"}), 400

    except Exception as e:
        print("❌ Lỗi trạm 1:", e)
        return jsonify({"error": str(e)}), 500


# ====================================================
# 💬 TRẠM 2 – GIAO TIẾP & HỢP TÁC SỐ
# ====================================================
@app.route("/api/station2-digital-collab", methods=["POST"])
def station2_digital_collab():
    try:
        data = request.get_json(silent=True) or {}
        mode = data.get("mode", "generate_task")
        answer = data.get("answer", "")
        task = data.get("task", "")

        if mode == "generate_task":
            prompt = """
            Bạn là AI giáo dục CHIRON26 giúp học sinh huấn luyện kỹ năng giao tiếp & hợp tác trong môi trường số.
            Hãy tạo **2 tình huống ngắn (2–3 câu)** về học sinh làm việc nhóm trực tuyến,
            mỗi tình huống có **một câu hỏi trắc nghiệm A/B** để học sinh chọn cách ứng xử đúng.
            """
            result = generate_text(prompt, generation_config={"max_output_tokens": 2048, "temperature": 0.85})
            return jsonify({"station": 2, "response": result})

        elif mode == "evaluate":
            prompt = f"""
            Nhiệm vụ:
            {task}

            Câu trả lời của học sinh:
            {answer}

            Hãy chấm và phản hồi ngắn gọn, nêu điểm mạnh/yếu trong hợp tác số.
            """
            result = generate_text(prompt, generation_config={"max_output_tokens": 2048, "temperature": 0.75})
            return jsonify({"station": 2, "feedback": result})

        else:
            return jsonify({"error": "Invalid mode"}), 400

    except Exception as e:
        print("❌ Lỗi trạm 2:", e)
        return jsonify({"error": str(e)}), 500


# ====================================================
# 🎨 TRẠM 3 – SÁNG TẠO NỘI DUNG SỐ (chat)
# ====================================================

@app.route("/api/station3-content-creation", methods=["POST"])
def station3_content_creation():
    try:
        data = request.get_json(silent=True) or {}
        user_message = data.get("message", "")
        if not user_message:
            user_message = "Xin chào, tôi muốn tạo nội dung số an toàn và sáng tạo."

        prompt = f"""
        Bạn là AI giáo dục CHIRON26 giúp học sinh huấn luyện năng lực sáng tạo nội dung số.
        Học sinh nói: "{user_message}"
        Hãy phản hồi như cố vấn sáng tạo, gợi ý ý tưởng (bài đăng, video, poster)
        và nhấn mạnh đạo đức, bản quyền, trách nhiệm khi sáng tạo nội dung.
        Không nên quá dài, chỉ cần khoảng 10 dòng.
        """
        text = generate_text(prompt, generation_config={"max_output_tokens": 2048, "temperature": 0.85})
        return jsonify({"station": 3, "response": text})

    except Exception as e:
        print("❌ Lỗi trạm 3:", e)
        return jsonify({"error": str(e)}), 500


# ====================================================
# 🛡️ TRẠM 4 – AN TOÀN SỐ
# ====================================================
@app.route("/api/station4-safety", methods=["POST"])
def station4_safety():
    try:
        data = request.get_json(silent=True) or {}
        mode = data.get("mode", "generate_task")
        answer = data.get("answer", "")
        task = data.get("task", "")

        if mode == "generate_task":
            # Thêm yêu cầu KHÔNG kèm đáp án để tránh lộ
            prompt = """
            Bạn là AI giáo dục CHIRON26 giúp học sinh huấn luyện kỹ năng an toàn số.
            Hãy tạo **2 tình huống trắc nghiệm ngắn** về: bảo mật tài khoản, lừa đảo trực tuyến (phishing), hoặc bắt nạt mạng.
            
            Cấu trúc bắt buộc:
            TÌNH HUỐNG 1: [Nội dung]
            CÂU HỎI: [Câu hỏi]
            A. [Lựa chọn 1]
            B. [Lựa chọn 2]
            
            (Tương tự cho Tình huống 2)
            QUAN TRỌNG: KHÔNG được viết đáp án đúng hay giải thích ở cuối.
            """
            result = generate_text(prompt, generation_config={"max_output_tokens": 2048, "temperature": 0.8})
            return jsonify({"station": 4, "response": result})

        elif mode == "evaluate":
            # --- SỬA QUAN TRỌNG TẠI ĐÂY ---
            prompt = f"""
            Bạn là giám khảo chấm thi trắc nghiệm về AN TOÀN SỐ.
            
            1. ĐỀ BÀI:
            {task}

            2. HỌC SINH CHỌN:
            {answer}

            3. YÊU CẦU:
            - Xác định đáp án đúng dựa trên kiến thức an toàn thông tin.
            - So sánh với đáp án học sinh chọn.
            - Đếm số câu đúng (trên tổng số 2 câu).

            4. ĐỊNH DẠNG TRẢ LỜI BẮT BUỘC (Dòng đầu tiên):
            SCORE: x/2
            
            (Trong đó x là số câu đúng. Ví dụ: SCORE: 0/2, SCORE: 1/2, SCORE: 2/2).
            
            Sau dòng SCORE mới được viết phần giải thích chi tiết đúng/sai cho từng câu.
            KHÔNG chúc mừng nếu học sinh làm sai.
            """
            
            # Giảm temperature xuống 0.5 để AI chấm nghiêm túc hơn, ít "sáng tạo" lung tung
            result = generate_text(prompt, generation_config={"max_output_tokens": 2048, "temperature": 0.5})
            return jsonify({"station": 4, "feedback": result})

        else:
            return jsonify({"error": "Invalid mode"}), 400

    except Exception as e:
        print("❌ Lỗi trạm 4:", e)
        return jsonify({"error": str(e)}), 500

# ====================================================
# 🧩 TRẠM 5 – GIẢI QUYẾT VẤN ĐỀ
# ====================================================
@app.route("/api/station5-problem-solving", methods=["POST"])
def station5_problem_solving():
    try:
        data = request.get_json(silent=True) or {}
        mode = data.get("mode", "generate_task")
        answer = data.get("answer", "")
        task = data.get("task", "")

        if mode == "generate_task":
            prompt = """
            Bạn là AI giáo dục CHIRON26 giúp học sinh huấn luyện kỹ năng giải quyết vấn đề bằng công nghệ số.
            Hãy tạo **2 tình huống (3–4 câu)** mô tả sự cố kỹ thuật (mất dữ liệu, lỗi phần mềm...),
            mỗi tình huống có một câu hỏi trắc nghiệm A/B gợi ý cách xử lý.
            """
            result = generate_text(prompt, generation_config={"max_output_tokens": 2048, "temperature": 0.8})
            return jsonify({"station": 5, "response": result})

        elif mode == "evaluate":
            prompt = f"""
            Nhiệm vụ:
            {task}

            Câu trả lời của học sinh:
            {answer}

            Hãy chấm và phản hồi logic với vai trò là AI giáo dục hỗ trợ cho học sinh, khuyến khích học sinh áp dụng quy trình: 
            xác định nguyên nhân – thử giải pháp – đánh giá kết quả.
            """
            result = generate_text(prompt, generation_config={"max_output_tokens": 2048, "temperature": 0.75})
            return jsonify({"station": 5, "feedback": result})

        else:
            return jsonify({"error": "Invalid mode"}), 400

    except Exception as e:
        print("❌ Lỗi trạm 5:", e)
        return jsonify({"error": str(e)}), 500



# ====================================================
# 🤖 TRẠM 6 – ĐẠO ĐỨC & TRÍ TUỆ NHÂN TẠO (chat)
# ====================================================
@app.route("/api/station6-ai-ethics", methods=["POST"])
def station6_ai_ethics():
    try:
        data = request.get_json(silent=True) or {}
        user_message = data.get("message", "")
        if not user_message:
            user_message = "Chúng ta nên dùng AI như thế nào để có trách nhiệm?"
        prompt = f"""
        Bạn là AI giáo dục có tên CHIRON26. Bạn sẽ cùng thảo luận với học sinh về **Ứng dụng trí tuệ nhân tạo**.
        Học sinh nói: "{user_message}"
        Hãy phản hồi bằng cách gợi mở, giúp học sinh hiểu:
        - AI nên được dùng có trách nhiệm, công bằng, an toàn.
        - Tránh lạm dụng, sao chép hoặc tạo nội dung gây hại.
        - Không quá dài, không quá 10 dòng.
        """
        text = generate_text(prompt, generation_config={"max_output_tokens": 2048, "temperature": 0.7})
        return jsonify({"station": 6, "response": text})

    except Exception as e:
        print("❌ Lỗi trạm 6:", e)
        return jsonify({"error": str(e)}), 500


# ====================================================
# ✅ KIỂM TRA ROUTE
# ====================================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "routes": [
            "/api/station1-info-literacy",
            "/api/station2-digital-collab",
            "/api/station3-content-creation",
            "/api/station4-safety",
            "/api/station5-problem-solving",
            "/api/station6-ai-ethics"
        ],
        "status": "✅ Backend AI Công dân số đang chạy"
    })


# ====================================================
# 🔟 Chạy server
# ====================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)
