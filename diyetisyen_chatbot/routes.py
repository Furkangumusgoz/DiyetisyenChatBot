from flask import Flask, request, jsonify
from datetime import datetime
from models import db, User, DailyLog  # db, User, ve DailyLog modellerini import ediyoruz

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diyetisyen_chatbot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)  # Veritabanı bağlantısını başlatıyoruz

@app.route('/daily-log', methods=['POST'])
def add_daily_log():
    data = request.get_json()

    # Verilerin alınması
    user_id = data.get('user_id')
    date = data.get('date')
    calories = data.get('calories_consumed')
    water_intake = data.get('water_intake')
    physical_activity = data.get('physical_activity')
    notes = data.get('notes')

    # Date format kontrolü
    try:
        date = datetime.strptime(date, '%Y-%m-%d').date()  # YYYY-MM-DD formatında
    except ValueError:
        return jsonify({"message": "Tarih formatı geçersiz. Lütfen YYYY-MM-DD formatını kullanın."}), 400

    # User veritabanında mevcut mu?
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "Kullanıcı bulunamadı."}), 404

    # Yeni günlük kaydını oluşturma
    log = DailyLog(user_id=user_id, date=date, calories_consumed=calories, 
                   water_intake=water_intake, physical_activity=physical_activity, notes=notes)
    
    db.session.add(log)
    db.session.commit()

    return jsonify({"message": "Günlük başarıyla kaydedildi."}), 201


@app.route('/daily-log/<user_id>/<date>', methods=['GET'])
def get_daily_log(user_id, date):
    try:
        date = datetime.strptime(date, '%Y-%m-%d').date()  # YYYY-MM-DD formatında
    except ValueError:
        return jsonify({"message": "Tarih formatı geçersiz. Lütfen YYYY-MM-DD formatını kullanın."}), 400

    # Günlük kaydını sorgulama
    log = DailyLog.query.filter_by(user_id=user_id, date=date).first()

    if log:
        return jsonify({
            'date': log.date,
            'calories_consumed': log.calories_consumed,
            'water_intake': log.water_intake,
            'physical_activity': log.physical_activity,
            'notes': log.notes
        })
    
    return jsonify({"message": "Veri bulunamadı."}), 404


# Uygulama başlatma
if __name__ == '__main__':
    app.run(debug=True)
