from flask import Flask
from extensions import db
from models import Client, DailyLog
from datetime import date
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diyetisyen_chatbot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    phone = input("📱 Danışan telefon numarasını girin (+90 ile başlayarak): ").strip()

    client = Client.query.filter_by(phone_number=phone).first()
    if not client:
        print("❌ Danışan bulunamadı.")
    else:
        logs = DailyLog.query.filter_by(user_id=client.id).order_by(DailyLog.date.desc()).all()

        if not logs:
            print("📭 Bu danışana ait günlük log bulunamadı.")
        else:
            print(f"\n📋 {client.full_name} adlı danışanın günlük kayıtları:")
            for log in logs:
                print(f"""
📅 Tarih       : {log.date}
🔥 Kalori      : {log.calories_consumed}
💧 Su (Litre)  : {log.water_intake}
🏃 Aktivite    : {log.physical_activity} dk
📝 Not         : {log.notes}
-----------------------------""")
