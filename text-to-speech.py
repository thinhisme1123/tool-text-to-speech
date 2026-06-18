import streamlit as st
import asyncio
import edge_tts
import io

# Cấu hình tiêu đề trang web
st.set_page_config(page_title="Công cụ TTS Cá Nhân", page_icon="🔊")
st.title("🔊 Công cụ Chuyển Văn Bản Thành Giọng Nói (TTS)")
st.write("Dành riêng cho mục đích sử dụng cá nhân - Hoàn toàn miễn phí")

# CẬP NHẬT: Thêm các giọng đọc tiếng Anh (US) trầm ấm
VOICES = {
    "🇻🇳 Tiếng Việt - Nữ miền Nam (Hoài My)": "vi-VN-HoaiMyNeural",
    "🇻🇳 Tiếng Việt - Nam miền Bắc (Nam Minh)": "vi-VN-NamMinhNeural",
    "🇺🇸 Tiếng Anh - Nam US (Christopher - Trầm ấm, vang)": "en-US-ChristopherNeural",
    "🇺🇸 Tiếng Anh - Nam US (Steffan - Trầm ấm, chuyên nghiệp)": "en-US-SteffanNeural",
    "🇺🇸 Tiếng Anh - Nữ US (Aria - Trầm ấm, truyền cảm)": "en-US-AriaNeural"
}

# Giao diện cấu hình tham số
st.subheader("1. Cấu hình giọng đọc")
selected_voice_label = st.selectbox("Chọn giọng đọc AI:", list(VOICES.keys()))
voice_id = VOICES[selected_voice_label]

# Cấu hình điều chỉnh tốc độ đọc (Rate)
rate = st.slider("Tốc độ đọc:", min_value=0.5, max_value=2.0, value=1.0, step=0.1)
rate_str = f"{'+' if rate >= 1.0 else ''}{int((rate - 1.0) * 100)}%"

st.subheader("2. Dữ liệu đầu vào")
# Bộ tải file văn bản (.txt)
uploaded_file = st.file_uploader("Tải lên file văn bản của bạn (.txt)", type=["txt"])

# Ô nhập văn bản trực tiếp
default_text = ""
if uploaded_file is not None:
    stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
    default_text = stringio.read()

text_content = st.text_area(
    "Nội dung văn bản cần chuyển đổi:", 
    value=default_text, 
    height=250, 
    placeholder="Nhập văn bản hoặc tải file .txt ở trên..."
)

st.subheader("3. Xử lý và Xuất bản")
# Nút bấm kích hoạt xử lý
if st.button("Bắt đầu chuyển đổi sang MP3", type="primary"):
    if not text_content.strip():
        st.error("Vui lòng nhập văn bản hoặc tải lên file dữ liệu trước!")
    else:
        async def convert_text_to_mp3(text, voice, speed):
            communicate = edge_tts.Communicate(text, voice, rate=speed)
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            return audio_data

        with st.spinner("Đang render âm thanh AI... Vui lòng đợi trong giây lát."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                mp3_bytes = loop.run_until_complete(convert_text_to_mp3(text_content, voice_id, rate_str))
                
                st.success("🎉 Chuyển đổi thành công!")
                st.audio(mp3_bytes, format="audio/mp3")
                
                st.download_button(
                    label="💾 Tải file MP3 về máy",
                    data=mp3_bytes,
                    file_name="giong_doc_tts.mp3",
                    mime="audio/mp3"
                )
            except Exception as e:
                st.error(f"Đã xảy ra lỗi trong quá trình xử lý: {e}")