from app import app, db, Client

with app.app_context():
    # Yeni bir danışan oluştur
    new_client = Client(
        full_name="Furkan Test",
        phone_number="+905388426172",  # WhatsApp numarası burayla eşleşmeli
        email="furkan@example.com",
        consent_given=True
    )

    # Veritabanına ekle
    db.session.add(new_client)
    db.session.commit()

    print("✅ Danışan başarıyla eklendi.")
