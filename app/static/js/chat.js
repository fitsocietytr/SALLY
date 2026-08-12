document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatMessages = document.getElementById('chatMessages');
    const leadModal = document.getElementById('leadModal');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const leadForm = document.getElementById('leadForm');
    const openLeadBtn = document.getElementById('openLeadBtn');
    const quickChips = document.querySelectorAll('.quick-chip');

    // Chat mesajı ekleme yardımcısı
    function appendMessage(sender, text) {
        const msgDiv = document.createElement('div');
        msgDiv.classList.add('message-bubble', sender === 'user' ? 'msg-user' : 'msg-ai');
        
        // Basit markdown kalınlaştırma desteği
        let formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        msgDiv.innerHTML = formattedText;

        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Yazıyor... göstergesi
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typingIndicator';
        typingDiv.classList.add('message-bubble', 'msg-ai');
        typingDiv.innerHTML = '<em>Sally yazıyor... 🐾</em>';
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function hideTypingIndicator() {
        const typingDiv = document.getElementById('typingIndicator');
        if (typingDiv) {
            typingDiv.remove();
        }
    }

    // Mesaj Gönderme İletişimi
    async function sendMessage(userMsgText) {
        const text = userMsgText || chatInput.value.trim();
        if (!text) return;

        appendMessage('user', text);
        if (!userMsgText) chatInput.value = '';

        showTypingIndicator();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: window.SESSION_ID,
                    message: text
                })
            });

            const data = await response.json();
            hideTypingIndicator();

            if (data.success) {
                appendMessage('ai', data.reply);

                // Randevu yönlendirmesi: Wix randevu sayfası varsa oraya yönlendir
                if (data.suggest_appointment && window.WIX_BOOKING_URL) {
                    setTimeout(() => {
                        const bookingBanner = document.createElement('div');
                        bookingBanner.classList.add('message-bubble', 'msg-ai');
                        bookingBanner.innerHTML = `
                            🗓️ Online randevu almak ister misiniz?
                            <br><br>
                            <a href="${window.WIX_BOOKING_URL}" target="_blank" rel="noopener noreferrer"
                               style="display:inline-flex;align-items:center;gap:6px;padding:8px 16px;background:linear-gradient(135deg,#2563eb,#1d4ed8);color:white;border-radius:9999px;text-decoration:none;font-weight:600;font-size:0.85rem;margin-top:4px;">
                               📅 Randevu Sayfasına Git
                            </a>`;
                        chatMessages.appendChild(bookingBanner);
                        chatMessages.scrollTop = chatMessages.scrollHeight;
                    }, 800);
                }
                // Lead teklifi varsa (ve Wix yoksa) iletişim modalı aç
                else if (data.suggest_lead_form && !window.WIX_BOOKING_URL) {
                    setTimeout(() => {
                        openModal();
                    }, 1200);
                }
            } else {
                appendMessage('ai', 'Üzgünüm, bir bağlantı hatası oluştu: ' + (data.error || 'Tekrar deneyin.'));
            }
        } catch (err) {
            hideTypingIndicator();
            appendMessage('ai', 'Bağlantı kurulamadı. Lütfen internetinizi veya sunucuyu kontrol edin.');
        }
    }

    // Modal Kontrolleri
    function openModal() {
        if (leadModal) leadModal.classList.add('active');
    }

    function closeModal() {
        if (leadModal) leadModal.classList.remove('active');
    }

    if (sendBtn) {
        sendBtn.addEventListener('click', () => sendMessage());
    }

    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    }

    if (openLeadBtn) {
        openLeadBtn.addEventListener('click', openModal);
    }

    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closeModal);
    }

    // Hızlı Soru Butonları
    quickChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const promptText = chip.getAttribute('data-prompt');
            if (promptText) {
                sendMessage(promptText);
            }
        });
    });

    // Lead Formu Gönderimi
    if (leadForm) {
        leadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const fullName = document.getElementById('fullName').value.trim();
            const phone = document.getElementById('phone').value.trim();
            const petName = document.getElementById('petName').value.trim();
            const petType = document.getElementById('petType').value;
            const notes = document.getElementById('notes').value.trim();

            if (!fullName || !phone) {
                alert('Lütfen Ad Soyad ve Telefon numarası alanlarını doldurun.');
                return;
            }

            try {
                const response = await fetch('/api/lead', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        full_name: fullName,
                        phone: phone,
                        pet_name: petName,
                        pet_type: petType,
                        notes: notes
                    })
                });

                const data = await response.json();
                if (data.success) {
                    closeModal();
                    leadForm.reset();
                    appendMessage('ai', '🎉 **Tebrikler!** İletişim bilgileriniz ve kaydınız başarıyla alındı. Veteriner hekimlerimiz en kısa sürede size ulaşacaktır. Minik dostunuza sevgiler!');
                } else {
                    alert(data.error || 'Bir hata oluştu.');
                }
            } catch (err) {
                alert('Gönderim sırasında hata oluştu.');
            }
        });
    }
});
