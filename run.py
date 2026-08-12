from app import create_app

app = create_app()

if __name__ == '__main__':
    print("🐾 SallyPet SmartLead AI Sunucusu Başlatılıyor...")
    print("👉 Ana Sayfa & AI Chat: http://127.0.0.1:5000")
    print("👉 Yönetim Paneli (Dashboard): http://127.0.0.1:5000/dashboard")
    app.run(debug=True, host='0.0.0.0', port=5001)
