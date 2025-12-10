import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import uuid
from config import RDS_CONFIG

# ---------------------- CONNEXION ----------------------
def connect_rds():
    try:
        conn = mysql.connector.connect(
            host=RDS_CONFIG["host"],
            user=RDS_CONFIG["user"],
            password=RDS_CONFIG["password"],
            database=RDS_CONFIG["database"]
        )
        return conn
    except Error as e:
        st.error(f"Erreur de connexion RDS : {e}")
        return None

# ---------------------- INSERT ORDER --------------------
def insert_order(conn, customer_id, order_date, items):
    try:
        cursor = conn.cursor()
        order_id = str(uuid.uuid4())
        order_date_str = order_date.strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute("""
            INSERT INTO olist_orders_dataset
            (order_id, customer_id, order_status, order_purchase_timestamp)
            VALUES (%s, %s, %s, %s)
        """, (order_id, customer_id, "delivered", order_date_str))

        for item in items:
            cursor.execute("""
                INSERT INTO olist_order_items_dataset
                (order_id, product_id, price, freight_value, seller_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (order_id, item["product_id"], item["price"], item["freight_value"], item["seller_id"]))

        conn.commit()
        st.write(f"Order ID généré côté Python : {order_id}")
        return order_id

    except Error as e:
        conn.rollback()
        st.error(f"Erreur insertion : {e}")
        return None

# ---------------------- STREAMLIT ----------------------
st.set_page_config(page_title="Olist - Ajout de Commandes", layout="wide")

# Styles custom (tu peux créer assets/style.css si tu veux plus de personnalisation)
st.markdown("""
<style>
h1 {color: #0d6efd; text-align:center;}
h2 {color: #198754;}
.stButton>button {background-color: #0d6efd; color:white; font-weight:bold;}
.stMetric {background-color: #f8f9fa; padding:10px; border-radius:8px;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🛒 Ajout de commandes Olist</h1>", unsafe_allow_html=True)

# Connexion RDS
conn = connect_rds()


if conn:
    # Charger les données
    clients = pd.read_sql("SELECT customer_id, customer_unique_id FROM olist_customers_dataset", conn)
    products = pd.read_sql("SELECT product_id, product_category_name FROM olist_products_dataset", conn)
    products.rename(columns={"product_category_name": "display_name"}, inplace=True)
    order_items_info = pd.read_sql("SELECT product_id, seller_id, price, freight_value FROM olist_order_items_dataset", conn)

    # Lookup tables pour rapidité
    products_lookup = dict(zip(products["display_name"], products["product_id"]))
    product_info = order_items_info.groupby("product_id").agg({"price": "mean", "freight_value": "mean"})
    price_lookup = product_info["price"].to_dict()
    freight_lookup = product_info["freight_value"].to_dict()
    sellers_lookup = order_items_info.groupby("product_id")["seller_id"].unique().to_dict()

    # --- Formulaire ---
    st.subheader("➕ Ajouter une nouvelle commande")

    col1, col2 = st.columns(2)
    with col1:
        customer_choice = st.selectbox("Client", clients["customer_unique_id"])
        customer_id = clients.loc[clients["customer_unique_id"] == customer_choice, "customer_id"].values[0]
    with col2:
        order_date = st.date_input("Date de commande", datetime.today())

    st.markdown("### Produits")
    items = []
    n_items = st.number_input("Nombre de produits", min_value=1, value=1)

    for i in range(int(n_items)):
        st.write(f"#### Produit {i+1}")
        colA, colB, colC, colD = st.columns(4)

        with colA:
            product_choice_name = st.selectbox("Produit", products["display_name"], key=f"prod_{i}")
            product_choice_id = products_lookup[product_choice_name]

        # Prix et frais par défaut
        price_default = price_lookup.get(product_choice_id, 0.0)
        freight_default = freight_lookup.get(product_choice_id, 0.0)
        product_sellers = sellers_lookup.get(product_choice_id, ["unknown_seller"])

        # Number_input avec key unique dépendant du produit
        with colB:
            price = st.number_input(
                "Prix",
                min_value=0.0,
                value=float(price_default),
                step=0.1,
                key=f"price_{i}_{product_choice_id}"  # key unique par produit
            )
        with colC:
            freight_value = st.number_input(
                "Frais",
                min_value=0.0,
                value=float(freight_default),
                step=0.1,
                key=f"freight_{i}_{product_choice_id}"  # key unique par produit
            )
        with colD:
            seller_choice = st.selectbox(
                "Seller",
                product_sellers,
                key=f"seller_{i}_{product_choice_id}"  # key unique par produit
            )

        items.append({
            "product_id": product_choice_id,
            "price": price,
            "freight_value": freight_value,
            "seller_id": seller_choice
        })

    total = sum([x["price"] + x["freight_value"] for x in items])
    st.metric("Total commande", f"{total:.2f} $")

    if st.button("Ajouter la commande"):
        st.write("Items à insérer:", items)
        order_id = insert_order(conn, customer_id, order_date, items)
        if order_id:
            st.success(f"Commande ajoutée avec succès !")


    # --- Historique 10 dernières commandes ---
    st.subheader("10 dernières commandes")
    last_orders = pd.read_sql("""
        SELECT c.customer_unique_id AS client,
               GROUP_CONCAT(p.product_category_name SEPARATOR ', ') AS produits,
               SUM(oi.price + oi.freight_value) AS total,
               o.order_purchase_timestamp AS date
        FROM olist_orders_dataset o
        JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
        JOIN olist_order_items_dataset oi ON oi.order_id = o.order_id
        JOIN olist_products_dataset p ON oi.product_id = p.product_id
        GROUP BY c.customer_unique_id, o.order_purchase_timestamp
        ORDER BY o.order_purchase_timestamp DESC
        LIMIT 10
    """, conn)
    st.dataframe(last_orders.style.format({"total": "${:,.2f}"}))
