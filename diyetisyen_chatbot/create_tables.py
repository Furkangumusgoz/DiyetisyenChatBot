from app import app, db  # app ve db'yi app.py dosyasından import ediyoruz
from models import Client, DailyLog  # Veritabanı modellerini import ediyoruz
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Veritabanı ve tabloları oluşturmak için context başlatıyoruz
with app.app_context():
    db.create_all()  # Tabloları oluşturuyoruz
    print("Veritabanı ve tablolar oluşturuldu.")
