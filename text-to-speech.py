import streamlit as st
import asyncio
import edge_tts
import io

st.set_page_config(page_title="Công cụ TTS Cá Nhân", page_icon="🕵️")
st.title("🕵️ Hồ Sơ Âm Thanh: Công cụ TTS Bí Ẩn")
st.write("Tối ưu hóa riêng cho thể loại kể chuyện, podcast vụ án và kinh dị.")

# Danh sách giọng đọc được tuyển chọn cho concept Kể chuyện / Bí ẩn
VOICES = {
    "🇻🇳 Tiếng Việt - Nam (Nam Minh) - Điềm tĩnh, thời sự": "vi-VN-NamMinhNeural",
    "🇻🇳 Tiếng Việt - Nữ (Hoài My) - Tự nhiên, truyền cảm": "vi-VN-HoaiMyNeural",
    "🇺🇸 Tiếng Anh - Nam (Christopher) - Trầm khàn, kể chuyện tâm lý": "en-US-ChristopherNeural",
    "🇺🇸 Tiếng Anh - Nam (Roger) - Gai góc, hồ sơ vụ án": "en-US-RogerNeural",
    "🇺🇸 Tiếng Anh - Nam (Steffan) - Sắc lạnh, rành mạch": "en-US-SteffanNeural",
    "🇺🇸 Tiếng Anh - Nữ (Aria) - Trầm ấm, bí ẩn": "en-US-AriaNeural"
}

st.subheader("1. Setup nhân vật kể chuyện")
selected_voice_label = st.selectbox("Chọn chất giọng AI:", list(VOICES.keys()))
voice_id = VOICES[selected_voice_label]

col1, col2 = st.columns(2)
with col1:
    # Để làm giọng bí ẩn, tốc độ nên giảm xuống khoảng 0.8x - 0.9x
    rate = st.slider("Tốc độ kể (Speed):", min_value=0.5, max_value=2.0, value=0.9, step=0.1, 
                     help="Giảm tốc độ xuống 0.8x - 0.9x để tạo cảm giác chậm rãi, hồi hộp.")
    rate_str = f"{'+' if rate >= 1.0 else ''}{int((rate - 1.0) * 100)}%"

with col2:
    # Hạ cao độ (Pitch) xuống số âm để giọng trầm và lạnh hơn
    pitch = st.slider("Độ trầm bổng (Pitch):", min_value=-50, max_value=50, value=-15, step=1,
                      help="Kéo về số âm (-15 đến -25) để giọng trầm, nam tính và rùng rợn hơn.")
    pitch_str = f"{'+' if pitch >= 0 else ''}{int(pitch)}Hz"

st.subheader("2. Kịch bản vụ án")
uploaded_file = st.file_uploader("Tải lên file kịch bản (.txt)", type=["txt"])

default_text = "Vào một đêm sương mù dày đặc năm 1998, tại một thị trấn hẻo lánh không có trên bản đồ... cảnh sát phát hiện ra một manh mối mà họ ước rằng mình chưa từng tìm thấy."
if uploaded_file is not None:
    stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
    default_text = stringio.read()

text_content = st.text_area(
    "Nội dung cần thu âm:", 
    value=default_text, 
    height=250
)

st.subheader("3. Thu âm & Trích xuất")
if st.button("Bắt đầu kết xuất MP3", type="primary"):
    if not text_content.strip():
        st.error("Kịch bản đang trống!")
    else:
        # Cập nhật hàm gọi API có thêm tham số pitch
        async def convert_text_to_mp3(text, voice, speed, pitch_val):
            communicate = edge_tts.Communicate(text, voice, rate=speed, pitch=pitch_val)
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            return audio_data

        with st.spinner("Đang trong phòng thu AI..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                mp3_bytes = loop.run_until_complete(convert_text_to_mp3(text_content, voice_id, rate_str, pitch_str))
                
                st.success("🎙️ Xử lý hoàn tất!")
                st.audio(mp3_bytes, format="audio/mp3")
                
                st.download_button(
                    label="💾 Tải file MP3 (Án mạng bí ẩn) về máy",
                    data=mp3_bytes,
                    file_name="ho_so_vu_an.mp3",
                    mime="audio/mp3"
                )
            except Exception as e:
                st.error(f"Lỗi hệ thống: {e}")