from datetime import datetime
from extensions import db  # extensions.py içindeki db'yi import ediyoruz

# Kullanıcı modeli (Client)
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(120))
    consent_given = db.Column(db.Boolean, default=False)  # Onay verilmiş mi?
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Client ile ilişkili DailyLog'ları alıyoruz
    daily_logs = db.relationship('DailyLog', backref='user', lazy=True)
    reminder_logs = db.relationship('ReminderLog', backref='client', lazy=True)  # Hatırlatma logları ilişkisi

    def __repr__(self):
        return f"<Client {self.full_name}>"

# Günlük takip modeli (DailyLog)
class DailyLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    calories_consumed = db.Column(db.Integer, nullable=False)
    water_intake = db.Column(db.Float, nullable=False)  # Litres
    physical_activity = db.Column(db.Integer, nullable=False)  # Minutes
    notes = db.Column(db.Text)

    def __repr__(self):
        return f"<DailyLog {self.user_id} - {self.date}>"

# Hatırlatma logları (ReminderLog)
class ReminderLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(100), nullable=False)
    
    # client_id ile ilişkilendirilmiş client nesnesi
    client = db.relationship('Client', backref='reminder_logs', lazy=True)

    def __repr__(self):
        return f'<ReminderLog {self.timestamp} - {self.status}>'
