from flask import Flask, request, Response, jsonify
from datetime import datetime, timedelta, timezone
import re
from twilio.twiml.messaging_response import MessagingResponse
from extensions import db
from models import Client, DailyLog, ReminderLog
from apscheduler.schedulers.background import BackgroundScheduler
from twilio.rest import Client as TwilioClient
import pytz
import csv

app = Flask(__name__)

# Veritabanı ayarları
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diyetisyen_chatbot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Veritabanı tablolarını oluştur
with app.app_context():
    db.create_all()
    print("✅ Veritabanı ve tablolar oluşturuldu.")

# Veritabanı tablolarını sıfırlamak için:
with app.app_context():
    db.drop_all()  # Mevcut tabloları sil
    db.create_all()  # Yeni tabloları oluştur
    print("✅ Veritabanı ve tablolar başarıyla sıfırlandı ve oluşturuldu.")

# Twilio bilgilerin
account_sid = "AC04a9f88d9719a6de2dea0451a9abaece"
auth_token = "9253bc5bf494bd4492ffce1ea4bc1b2a"
twilio_number = "whatsapp:+14155238886"
twilio_client = TwilioClient(account_sid, auth_token)

# Haftalık rapor fonksiyonu
def get_weekly_report(client_id):
    today = datetime.now(timezone.utc).date()
    week_start = today - timedelta(days=7)

    logs = DailyLog.query.filter(
        DailyLog.user_id == client_id,
        DailyLog.date >= week_start,
        DailyLog.date <= today
    ).all()

    if not logs:
        return "📭 Bu hafta için herhangi bir günlük log bulunamadı."

    total_calories = sum(log.calories_consumed for log in logs)
    total_water = sum(log.water_intake for log in logs)
    total_activity = sum(log.physical_activity for log in logs)
    moods = [log.notes for log in logs]
    average_mood = max(set(moods), key=moods.count) if moods else "Bilinmiyor"

    return (
        f"📊 Haftalık Rapor ({week_start} - {today}):\n"
        f"🔥 Toplam Kalori: {total_calories} kcal\n"
        f"💧 Toplam Su: {total_water} litre\n"
        f"🏃 Fiziksel Aktivite: {total_activity} dk\n"
        f"📝 Ortalama Ruh Hali: {average_mood}"
    )

# Hatırlatma logları için model
class ReminderLog(db.Model):
    __tablename__ = 'reminder_log'  # Tablo adını belirtiyoruz
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(100), nullable=False)
    client = db.relationship('Client', backref='reminder_logs', lazy=True)

    # extend_existing=True parametresi
    __table_args__ = {'extend_existing': True}

    def __repr__(self):
        return f'<ReminderLog {self.timestamp} - {self.status}>'

# Hatırlatma mesajı fonksiyonu
def send_reminder_messages():
    with app.app_context():
        clients = Client.query.filter_by(consent_given=True).all()
        for client in clients:
            try:
                twilio_client.messages.create(
                    from_=twilio_number,
                    to=f"whatsapp:{client.phone_number}",
                    body=f"Merhaba {client.full_name}! 📅 Bugünkü takibini yapmayı unutma. Yemek, su ve ruh halini paylaşabilirsin 🍽️💧😊"
                )
                # Hatırlama mesajı logunu veritabanına kaydet
                log = ReminderLog(client_id=client.id, status="Gönderildi")
                db.session.add(log)
                db.session.commit()
                print(f"✅ Hatırlatma gönderildi: {client.phone_number}")
            except Exception as e:
                print(f"❌ Mesaj gönderilemedi ({client.phone_number}): {e}")
                # Hatırlama mesajı logunu "Başarısız" olarak kaydet
                log = ReminderLog(client_id=client.id, status="Başarısız")
                db.session.add(log)
                db.session.commit()

# Flask webhook endpoint
@app.route("/webhook", methods=['POST'])
def webhook():
    incoming_number = request.form.get('From', '').replace("whatsapp:", "")
    message = request.form.get('Body', '').strip()

    print(f"Gelen mesaj: {message} - Numara: {incoming_number}")

    resp = MessagingResponse()
    client = Client.query.filter_by(phone_number=incoming_number).first()

    if not client or not client.consent_given:
        resp.message("❗ Lütfen önce sistem onayını verin.")
        return str(resp)

    if "haftalık rapor" in message.lower():
        report_text = get_weekly_report(client.id)
        resp.message(report_text)
        return str(resp)

    # Regex eşleşmeleri
    food_match = re.search(r"(?i)yemek:\s*(.+)", message)
    calories_match = re.search(r"(?i)kalori:\s*(\d+)", message)
    water_match = re.search(r"(?i)su:\s*([\d.]+)", message)
    mood_match = re.search(r"(?i)ruh hali:\s*(.+)", message)

    if food_match and calories_match and water_match:
        try:
            yemek = food_match.group(1).strip()
            kalori = int(calories_match.group(1))
            su = float(water_match.group(1))
            ruh_hali = mood_match.group(1).strip() if mood_match else ""

            log = DailyLog(
                user_id=client.id,
                date=datetime.utcnow().date(),
                calories_consumed=kalori,
                water_intake=su,
                physical_activity=0,
                notes=ruh_hali
            )
            db.session.add(log)
            db.session.commit()

            resp.message(f"📊 Günlük takibiniz kaydedildi. Aferin {client.full_name} 👏")
        except Exception as e:
            print("Hata:", e)
            resp.message("⚠️ Hata oluştu. Lütfen formatı kontrol edin:\nYemek: ...\nKalori: ...\nSu: ...\nRuh Hali: ...")
    else:
        resp.message("🔎 Formatı anlayamadım. Lütfen şu şekilde gönder:\nYemek: ...\nKalori: ...\nSu: ...\nRuh Hali: ...")

    return str(resp)

# CSV Dışa Aktarma Fonksiyonu
@app.route("/export_reminder_logs", methods=["GET"])
def export_reminder_logs():
    logs = ReminderLog.query.all()
    csv_file = "reminder_logs.csv"
    
    # CSV yazma
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Client ID", "Tarih ve Saat", "Durum"])
        for log in logs:
            writer.writerow([log.id, log.client_id, log.timestamp, log.status])

    return Response(
        f"CSV dosyası oluşturuldu: {csv_file}",
        mimetype="text/plain",
        status=200
    )

# Hatırlatma loglarını JSON formatında almak için
@app.route('/reminder_logs', methods=['GET'])
def get_reminder_logs():
    reminders = ReminderLog.query.all()
    
    reminder_list = []
    for reminder in reminders:
        reminder_data = {
            'id': reminder.id,
            'client_id': reminder.client_id,
            'timestamp': reminder.timestamp,
            'status': reminder.status
        }
        reminder_list.append(reminder_data)
    
    return jsonify(reminder_list)

# APScheduler - otomatik hatırlatma için
scheduler = BackgroundScheduler(timezone=pytz.timezone('Europe/Istanbul'))
scheduler.add_job(send_reminder_messages, 'cron', hour=10, minute=0)
scheduler.start()

if __name__ == "__main__":
    app.run(debug=True)
