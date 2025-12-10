import mysql.connector
import pandas as pd
from config import RDS_CONFIG

# ---------------------- Connexion à RDS ----------------------
try:
    conn = mysql.connector.connect(
        host=RDS_CONFIG["host"],
        user=RDS_CONFIG["user"],
        password=RDS_CONFIG["password"],
        database=RDS_CONFIG["database"]
    )
    print("✅ Connexion réussie à RDS !")
except mysql.connector.Error as e:
    print(f"❌ Erreur de connexion : {e}")
    exit()

# ---------------------- Vérifier les dernières commandes ----------------------
print("\n📦 10 dernières commandes :")
query_orders = """
SELECT * 
FROM olist_orders_dataset
ORDER BY order_purchase_timestamp DESC
LIMIT 10
"""
orders = pd.read_sql(query_orders, conn)
print(orders)

# ---------------------- Vérifier les derniers items ----------------------
print("\n🛒 10 derniers items de commande :")
query_items = """
SELECT * 
FROM olist_order_items_dataset
ORDER BY order_id DESC
LIMIT 10
"""
items = pd.read_sql(query_items, conn)
print(items)

# ---------------------- Fermeture de la connexion ----------------------
conn.close()
print("\n🔒 Connexion fermée.")
