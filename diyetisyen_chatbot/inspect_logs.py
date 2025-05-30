from extensions import db
from models import DailyLog, Client
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diyetisyen_chatbot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    logs = DailyLog.query.all()
    print(f"Toplam log sayısı: {len(logs)}")
    for log in logs:
        print(f"ID: {log.id} | Kullanıcı ID: {log.user_id} | Tarih: {log.date} | Kalori: {log.calories_consumed} | Su: {log.water_intake}")
