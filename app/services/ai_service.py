import os
from groq import Groq
from config import Config
from app.database import save_chat_message, get_chat_history

# Groq istemcisini başlat
_groq_client = None

def _get_groq_client():
    global _groq_client
    if _groq_client is None and Config.GROQ_API_KEY:
        _groq_client = Groq(api_key=Config.GROQ_API_KEY)
    return _groq_client

def generate_ai_response(session_id: str, user_message: str) -> dict:
    """
    Sorumluluklar:
    1. Kullanıcı mesajını veritabanına kaydeder.
    2. Geçmiş mesajları çeker.
    3. Groq API (Llama-3.3-70B) veya Akıllı Fallback ile yanıt üretir.
    4. Üretilen yanıtı veritabanına kaydeder.
    5. Yanıtı ve lead/randevu teşvik durumunu döndürür.
    """
    # 1. Kullanıcı mesajını kaydet
    save_chat_message(session_id, 'user', user_message)

    # 2. Geçmiş mesajları getir
    history = get_chat_history(session_id, limit=10)

    ai_reply = None

    # 3. Groq API Dene
    client = _get_groq_client()
    if client:
        ai_reply = _call_groq_api(client, history, user_message)

    # 4. Fallback: Akıllı Dahili Veteriner AI Engine
    if not ai_reply:
        ai_reply = _generate_smart_fallback_response(user_message, history)

    # 5. AI Yanıtını kaydet
    save_chat_message(session_id, 'ai', ai_reply)

    # 6. Lead ve randevu formu teşvik kontrolü
    suggest_lead_form = _should_suggest_lead(user_message, ai_reply)
    suggest_appointment = _should_suggest_appointment(user_message, ai_reply)

    return {
        'reply': ai_reply,
        'suggest_lead_form': suggest_lead_form,
        'suggest_appointment': suggest_appointment
    }

def _call_groq_api(client: Groq, history: list, user_message: str) -> str | None:
    """Groq API üzerinden Llama-3.3-70B ile yanıt üretir."""
    try:
        messages = [
            {
                "role": "system",
                "content": Config.BUSINESS_CONTEXT
            }
        ]

        # Geçmiş mesajları ekle (son 8 mesaj)
        for msg in history[:-1]:  # Son mesaj zaten user_message olarak eklendi
            role = "user" if msg['sender'] == 'user' else "assistant"
            messages.append({"role": role, "content": msg['content']})

        # Güncel kullanıcı mesajını ekle
        messages.append({"role": "user", "content": user_message})

        completion = client.chat.completions.create(
            model=Config.GROQ_MODEL,
            messages=messages,
            temperature=0.75,
            max_tokens=512,
            stream=False
        )

        return completion.choices[0].message.content

    except Exception as e:
        print(f"Groq API hatası: {e}")
        return None

def _generate_smart_fallback_response(user_message: str, history: list) -> str:
    """
    Groq API erişilemez olduğunda çalışan akıllı bağlamsal veteriner asistanı motoru.
    """
    msg = user_message.lower()

    if any(w in msg for w in ['merhaba', 'selam', 'günaydın', 'iyi günler', 'merhabalar', 'hey']):
        return "Merhaba! 🐾 Ben SallyPet Veteriner Kliniği yapay zekâ asistanı Sally. Size ve minik dostunuza nasıl yardımcı olabilirim?"

    if any(w in msg for w in ['acil', 'kanama', 'zehirlendi', 'kusma', 'araba çarptı', 'kaza', 'nefes alamıyor', 'bayıldı']):
        return "⚠️ **ACİL DURUM:** Lütfen vakit kaybetmeden kliniğimizi arayın! **0212 555 7384** — SallyPet 7/24 Acil Servisimiz Beşiktaş'ta hizmetinizdedir."

    if any(w in msg for w in ['randevu', 'rezervasyon', 'rezerve', 'muayene', 'tarih', 'saat', 'yer al']):
        return "Randevu almak için hemen online randevu sistemimizi kullanabilirsiniz! Aşağıdaki **'Randevu Al'** butonuna tıklayarak uygun tarih ve saati seçebilirsiniz. Ya da iletişim bilgilerinizi bırakın, sizi arayalım."

    if any(w in msg for w in ['aşı', 'parazit', 'kuduz', 'karma', 'aşı takvimi']):
        return "Aşı ve parazit takvimleri evcil dostunuzun sağlığı için kritiktir. Randevu almak için 'Randevu Al' butonunu kullanabilir ya da iletişim bilgilerinizi bırakabilirsiniz."

    if any(w in msg for w in ['fiyat', 'ücret', 'ne kadar', 'kısırlaştırma', 'ameliyat']):
        return "Muayene ve işlem ücretleri için hekimlerimizin sizi araması yeterlidir. İletişim bilgilerinizi bırakın, detaylı fiyat bilgisi versin!"

    if any(w in msg for w in ['adres', 'nerede', 'konum', 'çalışma saatleri', 'açık mı', 'kaça kadar']):
        return f"Kliniğimiz **{Config.BUSINESS_ADDRESS}** adresindedir. Rutin muayene: 09:00–20:00, Acil Servis: 7/24. Tel: **{Config.BUSINESS_PHONE}**."

    if any(w in msg for w in ['teşekkür', 'sağol', 'tamam', 'harika', 'güzel']):
        return "Rica ederim! Sevimli dostunuzla birlikte sağlıklı ve mutlu günler dilerim. 🐾"

    return "SallyPet Veteriner Kliniği olarak minik dostunuzun sağlığı her şeyden önce gelir. Randevu almak veya bilgi edinmek için 'Randevu Al' butonunu kullanabilir ya da iletişim bilgilerinizi bırakabilirsiniz."

def _should_suggest_lead(user_message: str, ai_reply: str) -> bool:
    """Kullanıcının iletişim bilgisi bırakması gereken durumları tespit eder."""
    msg = user_message.lower()
    keywords = ['fiyat', 'ücret', 'bilgi almak', 'arayın', 'bilgi']
    return any(k in msg for k in keywords) or 'iletişim bilgilerinizi' in ai_reply.lower()

def _should_suggest_appointment(user_message: str, ai_reply: str) -> bool:
    """Randevu sayfasına yönlendirme gereken durumları tespit eder."""
    msg = user_message.lower()
    keywords = ['randevu', 'rezervasyon', 'muayene', 'aşı', 'kontrol', 'getirmek istiyorum', 'yer almak']
    return any(k in msg for k in keywords) or 'randevu' in ai_reply.lower()
