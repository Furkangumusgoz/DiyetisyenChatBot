from flask import Flask, request, jsonify
from datetime import datetime
import re
from extensions import db
from models import Client

# Flask app initialization
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diyetisyen_chatbot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Günlük giriş modeli
class DailyEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    food = db.Column(db.String(300))
    calories = db.Column(db.Integer)
    water = db.Column(db.Float)
    mood = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    client = db.relationship('Client', backref=db.backref('entries', lazy=True))

# Veritabanı tablolarını bir kez oluştur
with app.app_context():
    db.create_all()
    print("✅ Veritabanı ve tablolar oluşturuldu.")

@app.route("/webhook", methods=['POST'])
def webhook():
    incoming_number = request.form.get('From', '').replace("whatsapp:", "")
    message = request.form.get('Body', '').strip()

    print(f"Incoming request data: {request.form}")

    client = Client.query.filter_by(phone_number=incoming_number).first()

    if not client or not client.consent_given:
        return jsonify({"message": "❗Lütfen önce sistem onayını verin."})

    if "yemek:" in message.lower():
        try:
            yemek = re.search(r"(?i)yemek:\s*(.+)", message).group(1).split("Kalori:")[0].strip()
            kalori = int(re.search(r"(?i)kalori:\s*(\d+)", message).group(1))
            su = float(re.search(r"(?i)su:\s*([\d.]+)", message).group(1))
            ruh = re.search(r"(?i)ruh hali:\s*(.+)", message)
            ruh_hali = ruh.group(1).strip() if ruh else None

            log = DailyEntry(
                client_id=client.id,
                food=yemek,
                calories=kalori,
                water=su,
                mood=ruh_hali
            )

            db.session.add(log)
            db.session.commit()

            return jsonify({"message": f"📊 Bugünkü veriler başarıyla kaydedildi! Aferin {client.full_name} 👏"})

        except Exception as e:
            print("Hata:", e)
            return jsonify({"message": "⚠️ Verileri işlerken sorun oluştu. Lütfen şu formatı kullanın:\n\nYemek: ...\nKalori: ...\nSu: ...\nRuh Hali: ..."})

    return jsonify({"message": "👋 Merhaba! Bugün size nasıl yardımcı olabilirim?"})

if __name__ == '__main__':
    app.run(debug=True)
