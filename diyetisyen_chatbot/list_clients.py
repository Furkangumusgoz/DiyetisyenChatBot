# list_clients.py

from app import app, db, Client  # app burada açıkça içe aktarılıyor

def list_all_clients():
    clients = Client.query.all()
    if not clients:
        print("📭 Henüz hiç danışan eklenmemiş.")
        return

    print("📋 Danışan Listesi:\n")
    for client in clients:
        print(f"Ad Soyad     : {client.full_name}")
        print(f"Telefon      : {client.phone_number}")
        print(f"E-posta      : {client.email}")
        print(f"Onay Verdi   : {'Evet' if client.consent_given else 'Hayır'}")
        print("-" * 30)

if __name__ == "__main__":
    with app.app_context():  # Doğru olan bu
        list_all_clients()

