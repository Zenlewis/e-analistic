import os
import requests
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from requests_oauthlib import OAuth2Session
import sqlite3
from flask import g
import redis
import time
import socket
import psycopg2
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import bcrypt
from dotenv import load_dotenv
import paypalrestsdk
from flask import send_from_directory
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Charger les variables d'environnement
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
cipher_suite = Fernet(os.getenv('FERNET_KEY'))
SHOPIFY_API_KEY = os.getenv('SHOPIFY_API_KEY')
SHOPIFY_API_SECRET = os.getenv('SHOPIFY_API_SECRET')
REDIRECT_URI = "http://localhost:8000/callback"

def migrate_table(source_conn, target_conn, table_name):
    src = source_conn.cursor()
    src.execute(f"SELECT * FROM {table_name}")
    cols = [desc[0] for desc in src.description]
    
    with target_conn.cursor() as tgt:
        tgt.executemany(
            f"INSERT INTO {table_name} ({','.join(cols)}) VALUES ({','.join(['%s']*len(cols))})",
            src.fetchall()
        )
    target_conn.commit()

def get_user_from_db(user_id):
    """Récupère un utilisateur depuis la base de données"""
    with sqlite3.connect('users.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return cursor.fetchone()

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                             'favicon.ico', mimetype='image/vnd.microsoft.icon')

#print("Migration démarrée...")
#with sqlite3.connect('users.db') as sqlite_conn, \
 #    psycopg2.connect(os.getenv('DATABASE_URL')) as pg_conn:
     
#    for table in ['users', 'orders']:
#        migrate_table(sqlite_conn, pg_conn, table)
#print("Migration terminée avec succès !")

# Configurer PayPal
paypalrestsdk.configure({
    "mode": "sandbox",  # Change à "live" en production
    "client_id": os.getenv('PAYPAL_CLIENT_ID'),
    "client_secret": os.getenv('PAYPAL_SECRET')
})

# Configuration de Flask-Session avec Redis
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=int(os.getenv('REDIS_PORT')),
    db=int(os.getenv('REDIS_DB'))
)
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
Session(app)

# Nouvelle configuration - Ajoutez ici
app.config['SESSION_COOKIE_SECURE'] = True  # Force HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Protection CSRF
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)  # Session 1h

# Initialisation Talisman (avant Session)
Talisman(
    app,
    content_security_policy=None,  # Désactive CSP si vous avez des assets externes
    force_https=True,
    strict_transport_security=True
)

# Configuration Limiter (après Redis)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri=f"redis://{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}",
    default_limits=["500 per day", "100 per hour"]
)

@app.before_request
def before_request():
    if 'user_id' in session:
        # Récupère l'utilisateur et met en cache si nécessaire
        user = get_user_from_db(session['user_id'])
        if user:
            g.user = user
            cache_key = f"user_{session['user_id']}_data"
            g.cached_data = r.get(cache_key) or {}

# Initialisation de la base de données
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Crée la table users si elle n'existe pas
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 email TEXT UNIQUE NOT NULL,
                 password TEXT NOT NULL,
                 shop_url TEXT UNIQUE,
                 shopify_token TEXT,
                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                 subscription_status TEXT DEFAULT 'trial',
                 is_admin INTEGER DEFAULT 0
                 )''')
    
    # Vérifie si la colonne is_admin existe, sinon l'ajoute
    c.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in c.fetchall()]
    if 'is_admin' not in columns:
        c.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
    
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
                 id INTEGER PRIMARY KEY,
                 shop_url TEXT,
                 order_data TEXT,
                 fetched_at TIMESTAMP)''')
    conn.commit()
    conn.close()

    conn = sqlite3.connect('tokens.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tokens (
                 user_id INTEGER PRIMARY KEY,
                 access_token BLOB,
                 last_renewed TIMESTAMP)''')
    conn.commit()
    conn.close()
    print("Bases de données initialisées")

def set_initial_admin():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET is_admin = 1 WHERE id = 1")
    conn.commit()
    conn.close()

# Appeler une seule fois après avoir recréé la base
init_db()
set_initial_admin()

# Fonctions utilitaires
def is_user_admin(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT is_admin FROM users WHERE id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] == 1 if result else False

def get_user_count():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    count = c.fetchone()[0]
    conn.close()
    return count

def store_access_token(user_id, token):
    conn = sqlite3.connect('tokens.db')
    c = conn.cursor()
    encrypted_token = cipher_suite.encrypt(token.encode())
    c.execute("INSERT OR REPLACE INTO tokens (user_id, access_token, last_renewed) VALUES (?, ?, ?)",
              (user_id, encrypted_token, datetime.now()))
    conn.commit()
    conn.close()

def safe_get(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code == 429:
        time.sleep(1)
        return requests.get(url, headers=headers)
    response.raise_for_status()
    return response

r = redis.Redis(host=os.getenv('REDIS_HOST'), port=int(os.getenv('REDIS_PORT')), db=int(os.getenv('REDIS_DB')))
def get_orders(shop_url, headers):
    cache_key = f"orders:{shop_url}"
    cached = r.get(cache_key)
    if cached:
        return pd.read_json(cached.decode('utf-8')).to_dict(orient="records")
    
    try:
        response = safe_get(f"{shop_url}/admin/api/2023-10/orders.json?status=any&limit=100", headers)
        orders = response.json().get("orders", [])
        for order in orders:
            for item in order.get("line_items", []):
                item["price"] = float(item["price"]) if item.get("price") else 0.0
        r.setex(cache_key, 3600, pd.DataFrame(orders).to_json())
        return orders
    except Exception as e:
        print(f"Erreur lors de la récupération des commandes : {e}")
        return []

def create_sequences(data, seq_length):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length, 0])
    return np.array(X), np.array(y)

# Langues supportées
#LANGUAGES = ['fr', 'en']

# Routes principales
@app.route('/')
def home():
    if 'user_id' in session and 'shopify_token' in session:
        return redirect(url_for('dashboard'))
        if request.method == 'POST':
            language = request.form.get('language')
        if language in LANGUAGES:
            session['language'] = language
            return redirect(url_for('home')) 
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT id, email, password, shop_url, shopify_token FROM users WHERE email = ?", (email,))
        user = c.fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[2]):
            session['user_id'] = user[0]
            session['shop_url'] = user[3]
            session['shopify_token'] = user[4]
            return redirect(url_for('dashboard'))
        return "Identifiants incorrects", 401
    return render_template('login.html')

@app.route('/install', methods=['GET', 'POST'])
def install():
    shop = request.args.get('shop')
    if not shop and request.method == 'GET':
        return render_template('install.html')
    elif request.method == 'POST':
        shop = request.form.get('shop')
        if not shop:
            return render_template('install.html', error="Veuillez entrer le domaine de votre boutique.")
    shop_url = f"https://{shop.strip()}"
    session['shop_url'] = shop_url
    return redirect(url_for('auth'))

@app.route('/auth')
def auth():
    shop_url = session.get('shop_url')
    if not shop_url:
        shop = request.args.get('shop')
        if not shop:
            return redirect(url_for('install'))
        shop_url = f"https://{shop.strip()}"
        session['shop_url'] = shop_url
    oauth = OAuth2Session(SHOPIFY_API_KEY, redirect_uri=REDIRECT_URI, scope="read_orders")
    authorization_url, state = oauth.authorization_url(f"{shop_url}/admin/oauth/authorize")
    session['oauth_state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    shop_url = session.get('shop_url')
    if not shop_url:
        print("Erreur dans /callback : shop_url manquant")
        return redirect(url_for('home'))
    oauth = OAuth2Session(SHOPIFY_API_KEY, state=session.get('oauth_state'), redirect_uri=REDIRECT_URI)
    try:
        token = oauth.fetch_token(
            f"{shop_url}/admin/oauth/access_token",
            client_secret=SHOPIFY_API_SECRET,
            code=request.args.get('code')
        )
    except Exception as e:
        print(f"Erreur OAuth dans /callback : {e}")
        return redirect(url_for('home'))
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE shop_url = ?", (shop_url,))
    user = c.fetchone()
    if not user:
        email = f"user@{shop_url.replace('https://', '').replace('.myshopify.com', '')}.com"
        default_password = bcrypt.hashpw("default_password".encode('utf-8'), bcrypt.gensalt())
        c.execute("INSERT INTO users (email, password, shop_url, shopify_token, subscription_status) VALUES (?, ?, ?, ?, ?)",
                  (email, default_password, shop_url, token['access_token'], 'trial'))
        user_id = c.lastrowid
    else:
        user_id = user[0]
        c.execute("UPDATE users SET shopify_token = ? WHERE id = ?", (token['access_token'], user_id))
    conn.commit()
    conn.close()

    store_access_token(user_id, token['access_token'])
    session['user_id'] = user_id
    session['shop_url'] = shop_url
    session['shopify_token'] = token['access_token']
    
    print(f"Session après /callback : {session}")
    return redirect(url_for('dashboard'))

@app.route('/webhook/uninstall', methods=['POST'])
def uninstall():
    shop_url = request.headers.get('X-Shopify-Shop-Domain')
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE shop_url = ?", (f"https://{shop_url}",))
    conn.commit()
    conn.close()
    return "", 200

# Routes PayPal
@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('home'))

    if request.method == 'POST':
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "redirect_urls": {
                "return_url": "http://localhost:8000/subscribe_success",
                "cancel_url": "http://localhost:8000/subscribe"
            },
            "transactions": [{
                "amount": {"total": "30.00", "currency": "USD"},
                "description": "Abonnement Insights Prevision"
            }]
        })

        if payment.create():
            for link in payment.links:
                if link.rel == "approval_url":
                    return redirect(link.href)
        else:
            return f"Erreur de paiement : {payment.error}", 500

    return render_template('subscribe.html')

@app.route('/subscribe_success')
def subscribe_success():
    payment_id = request.args.get('paymentId')
    payer_id = request.args.get('PayerID')
    user_id = session.get('user_id')

    if not user_id or not payment_id or not payer_id:
        return redirect(url_for('home'))

    payment = paypalrestsdk.Payment.find(payment_id)
    if payment.execute({"payer_id": payer_id}):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("UPDATE users SET subscription_status = 'paid' WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    else:
        return f"Erreur lors de la finalisation : {payment.error}", 500

@app.route('/payment_required')
def payment_required():
    return render_template('payment_required.html', shop_url=session.get('shop_url'))

# Routes admin sécurisées
@app.route('/admin/user_count')
def user_count():
    user_id = session.get('user_id')
    if not user_id or not is_user_admin(user_id):
        return "Accès refusé : réservé à l'administrateur", 403
    total_users = get_user_count()
    return f"Nombre total d'utilisateurs : {total_users}"

@app.route('/admin/users')
def list_users():
    user_id = session.get('user_id')
    if not user_id or not is_user_admin(user_id):
        return "Accès refusé : réservé à l'administrateur", 403
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT id, email, shop_url, created_at, subscription_status FROM users")
    users = c.fetchall()
    conn.close()

    user_list = []
    for user in users:
        user_id, email, shop_url, created_at, subscription_status = user
        trial_end = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S') + timedelta(days=14)
        user_list.append({
            'id': user_id,
            'email': email,
            'shop_url': shop_url,
            'trial_end': trial_end,
            'status': subscription_status
        })
    
    return render_template('user_list.html', users=user_list)

@app.route('/dashboard')
def dashboard():
    print("Route /dashboard atteinte")
    shop_url = session.get('shop_url')
    shopify_token = session.get('shopify_token')

    if not shopify_token or not shop_url:
        print("Session incomplète, redirection vers config")
        return redirect(url_for('config'))

    headers = {"Authorization": f"Bearer {shopify_token}"}
    print(f"Utilisation du token : {shopify_token}")

    conn = sqlite3.connect('shopify_data.db')
    c = conn.cursor()
    c.execute("SELECT order_data FROM orders WHERE shop_url = ? ORDER BY fetched_at DESC LIMIT 1", (shop_url,))
    cached = c.fetchone()
    if cached:
        orders = pd.read_json(cached[0]).to_dict(orient="records")
        print("Données récupérées depuis cache")
    else:
        try:
            response = safe_get(f"{shop_url}/admin/api/2023-10/orders.json?status=any&limit=100", headers)
            orders = response.json().get("orders", [])
            print(f"Réponse API : {response.status_code} - {response.text[:100]}")
            c.execute("INSERT INTO orders (shop_url, order_data, fetched_at) VALUES (?, ?, CURRENT_TIMESTAMP)", 
                      (shop_url, pd.DataFrame(orders).to_json()))
            conn.commit()
            print(f"Données récupérées via API - Nombre de commandes : {len(orders)}")
        except Exception as e:
            orders = []
            print(f"Erreur récupération données : {str(e)}")

    conn.close()

    currency = orders[0]["currency"] if orders else "USD"

    if not orders or len(orders) < 10:
        print("Pas assez de données, utilisation de données fictives")
        monthly_forecast = 2279.11
        min_mensuelle = monthly_forecast * 0.9
        max_mensuelle = monthly_forecast * 1.1
        daily_forecast = [monthly_forecast / 30] * 7
        best_selling_product = "Produit fictif"
        trend = "Stable (données fictives)"
        future_dates = pd.date_range(start="2025-01-01", periods=8, freq='D')[1:].strftime('%Y-%m-%d').tolist()
        data_limited = True
        top_product_forecast = 2279.11
    else:
        df_orders = pd.DataFrame(orders)
        df_orders['created_at'] = pd.to_datetime(df_orders['created_at'])
        df_orders['total_price'] = df_orders['total_price'].astype(float)

        df_orders['date'] = pd.to_datetime(df_orders['created_at'].dt.date)
        daily_totals = df_orders.groupby('date')['total_price'].sum().reset_index()
        print(f"Totaux quotidiens : {daily_totals.to_dict()}")

        dates = pd.date_range(start=daily_totals['date'].min(), end=daily_totals['date'].max())
        complete_data = pd.DataFrame({'date': dates})
        complete_data = complete_data.merge(daily_totals, on='date', how='left').fillna(0)
        print(f"Lignes de données complètes : {len(complete_data)}")

        if len(complete_data) < 2:
            print("Pas assez de jours pour entraîner un modèle, utilisation de données simples")
            monthly_forecast = float(daily_totals['total_price'].sum() * 30)
            min_mensuelle = monthly_forecast * 0.9
            max_mensuelle = monthly_forecast * 1.1
            daily_forecast = [daily_totals['total_price'].mean()] * 7
            future_dates = pd.date_range(start=daily_totals['date'].max(), periods=8, freq='D')[1:].strftime('%Y-%m-%d').tolist()
            data_limited = True
        else:
            X = complete_data.index.values.reshape(-1, 1)
            y = complete_data['total_price'].values
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            future_dates = pd.date_range(start=dates[-1], periods=8, freq='D')[1:].strftime('%Y-%m-%d').tolist()
            X_future = np.array(range(len(dates), len(dates) + 7)).reshape(-1, 1)

            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            forecast = model.predict(X_future)
            
            monthly_forecast = float(forecast.sum())
            min_mensuelle = float(monthly_forecast * 0.9)
            max_mensuelle = float(monthly_forecast * 1.1)
            daily_forecast = forecast.tolist()
            data_limited = False

        # Produit le plus vendu et prévision
        line_items = df_orders.explode('line_items')
        print("Articles pour débogage :")
        print(line_items['line_items'].apply(lambda x: (x['name'], float(x['price']) * float(x['quantity'])) if isinstance(x, dict) else None))
        best_selling_product = line_items['line_items'].apply(lambda x: x['name'] if isinstance(x, dict) else None).mode()[0] if not line_items.empty else "Inconnu"
        product_sales = line_items[line_items['line_items'].apply(lambda x: x['name'] if isinstance(x, dict) else None) == best_selling_product]
        total_product_sales = product_sales['line_items'].apply(lambda x: float(x['price']) * float(x['quantity']) if isinstance(x, dict) and 'price' in x and 'quantity' in x else 0.0).sum()
        product_share = total_product_sales / daily_totals['total_price'].sum() if daily_totals['total_price'].sum() > 0 else 0.0
        # Ajustement : si une seule journée, supposer que le produit domine
        top_product_forecast = monthly_forecast * product_share  # Remplace la condition

        # Tendance
        trend_value = (daily_totals['total_price'].iloc[-1] - daily_totals['total_price'].iloc[0]) / daily_totals['total_price'].iloc[0] * 100 if len(daily_totals) > 1 and daily_totals['total_price'].iloc[0] != 0 else 0
        trend = "Croissance" if trend_value > 0 else "Baisse" if trend_value < 0 else "Stable"

        print(f"Données envoyées au tableau de bord : mensuelle={monthly_forecast}, quotidiennes={daily_forecast}, top_product_forecast={top_product_forecast}")

    # Débogage
    print(f"Types avant rendu : monthly_forecast={type(monthly_forecast)}, min_mensuelle={type(min_mensuelle)}, max_mensuelle={type(max_mensuelle)}, top_product_forecast={type(top_product_forecast)}")
    print(f"Valeurs avant rendu : monthly_forecast={monthly_forecast}, min_mensuelle={min_mensuelle}, max_mensuelle={max_mensuelle}, top_product_forecast={top_product_forecast}")

    forecast_data = {
    'monthly': float(monthly_forecast),
    'min_mensuelle': float(min_mensuelle),
    'max_mensuelle': float(max_mensuelle),
    'daily_forecast': [float(x) for x in daily_forecast],
    'top_product_forecast': float(top_product_forecast)
}

    return render_template('dashboard.html',
                          monthly_forecast=round(monthly_forecast, 2),
                          min_mensuelle=round(min_mensuelle, 2),
                          max_mensuelle=round(max_mensuelle, 2),
                          daily_forecast=daily_forecast,
                          future_dates=future_dates,
                          best_selling_product=best_selling_product,
                          trend=trend,
                          data_limited=data_limited,
                          top_product_forecast=round(top_product_forecast, 2),
                          currency=currency) 

if __name__ == "__main__":
    port = 8000
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
        init_db()
        set_initial_admin()
    
    try:
        print(f"Serveur démarré sur http://localhost:{port}")
        app.run(debug=True, port=port)
    except socket.error:
        port = 8001
        print(f"Serveur démarré sur http://localhost:{port}")
        app.run(debug=True, port=port)