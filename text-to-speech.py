import streamlit as st
import asyncio
import edge_tts
import io
import os

# Cấu hình giao diện chung
st.set_page_config(page_title="Trạm Thu Âm TTS", page_icon="🎙️", layout="centered")

st.title("🎙️ Trạm Thu Âm Văn Bản (TTS Studio)")
st.write("Công cụ chuyển đổi văn bản sang giọng nói đa năng. Hoàn toàn miễn phí.")

# Phân loại giọng đọc để dễ lựa chọn
st.subheader("1. Lựa chọn Giọng đọc")

# Sử dụng cột để giao diện gọn gàng hơn
col1, col2 = st.columns(2)

with col1:
    language = st.radio("Ngôn ngữ chính:", ["Tiếng Việt 🇻🇳", "Tiếng Anh (US) 🇺🇸"])

with col2:
    if language == "Tiếng Việt 🇻🇳":
        voices = {
            "Nữ - Hoài My (Tự nhiên, truyền cảm)": "vi-VN-HoaiMyNeural",
            "Nam - Nam Minh (Điềm tĩnh, thời sự)": "vi-VN-NamMinhNeural"
        }
    else:
        voices = {
            "Nam - Christopher (Trầm ấm, kể chuyện)": "en-US-ChristopherNeural",
            "Nữ - Aria (Rõ ràng, chuyên nghiệp)": "en-US-AriaNeural",
            "Nam - Steffan (Sắc sảo, tin tức)": "en-US-SteffanNeural",
            "Nữ - Jenny (Trẻ trung, năng động)": "en-US-JennyNeural"
        }
    selected_voice = st.selectbox("Chất giọng AI:", list(voices.keys()))
    voice_id = voices[selected_voice]

st.subheader("2. Tùy chỉnh Nâng cao")
col3, col4 = st.columns(2)
with col3:
    rate = st.slider("Tốc độ (Speed):", 0.5, 2.0, 1.0, 0.1, help="1.0 là tốc độ chuẩn.")
    rate_str = f"{'+' if rate >= 1.0 else ''}{int((rate - 1.0) * 100)}%"
with col4:
    pitch = st.slider("Cao độ (Pitch):", -50, 50, 0, 1, help="Âm (-) để giọng trầm hơn, Dương (+) để giọng cao hơn.")
    pitch_str = f"{'+' if pitch >= 0 else ''}{int(pitch)}Hz"

st.subheader("3. Nhập Dữ liệu")
uploaded_file = st.file_uploader("Tải file văn bản (.txt) lên đây:", type=["txt"])

# Xác định tên file đầu ra
if uploaded_file is not None:
    export_filename = uploaded_file.name.replace(".txt", ".mp3")
    stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
    default_text = stringio.read()
else:
    export_filename = "ban_thu_am_tts.mp3"
    default_text = "Chào mừng bạn đến với Trạm thu âm. Hãy dán đoạn văn bản cần chuyển đổi vào đây..."

text_content = st.text_area("Hoặc nhập trực tiếp văn bản:", value=default_text, height=200)

st.subheader("4. Xử lý & Trích xuất")
if st.button("🎧 Bắt đầu tạo file MP3", type="primary", use_container_width=True):
    if not text_content.strip():
        st.warning("Vui lòng cung cấp nội dung cần đọc!")
    else:
        async def convert_text_to_mp3(text, voice, speed, pitch_val):
            communicate = edge_tts.Communicate(text, voice, rate=speed, pitch=pitch_val)
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            return audio_data

        with st.spinner("Đang tổng hợp giọng nói..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                mp3_bytes = loop.run_until_complete(convert_text_to_mp3(text_content, voice_id, rate_str, pitch_str))
                
                st.success("✅ Hoàn tất! Bạn có thể nghe thử hoặc tải về bên dưới.")
                st.audio(mp3_bytes, format="audio/mp3")
                
                st.download_button(
                    label=f"⬇️ Tải xuống: {export_filename}",
                    data=mp3_bytes,
                    file_name=export_filename,
                    mime="audio/mp3",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Có lỗi xảy ra: {e}")