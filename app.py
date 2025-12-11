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
        return order_id

    except Error as e:
        conn.rollback()
        st.error(f"Erreur insertion : {e}")
        return None

# ---------------------- STREAMLIT ----------------------
st.set_page_config(page_title="Olist - Ajout de Commandes", layout="wide")

# Charger CSS externe pour un style moderne/pro
try:
    with open("assets/style.css", "r", encoding="utf-8") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
except Exception:
    # fallback — style basique si le fichier est manquant
    st.markdown("""
    <style>
    .app-card { padding:18px; border-radius:12px; background:#ffffff; box-shadow:0 6px 18px rgba(15,15,15,0.08); }
    .page-title { font-family: Inter, sans-serif; font-size:28px; color:#0b3d91; text-align:center; margin-bottom:8px; }
    </style>
    """, unsafe_allow_html=True)

# Header visuel professionnel
st.markdown("""
<div class="topbar">
  <div class="topbar-inner">
    <div class="topbar-center">
      <div class="topbar-title">🛒 Ajout de commandes Olist</div>
      <div class="small-muted">Application interne de gestion des commandes </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

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

    # --- Formulaire dans layout 2 colonnes (gauche: form, droite: aperçu) ---
    st.subheader("Ajouter une nouvelle commande")

    # Carte globale
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    col_left, col_right = st.columns([2, 1])

    with col_left:
        # Formulaire principal
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
            st.markdown(f'<div class="product-row"> <strong>Produit {i+1}</strong> </div>', unsafe_allow_html=True)
            colA, colB, colC, colD = st.columns([2,1,1,1])

            with colA:
                product_choice_name = st.selectbox("Produit", products["display_name"], key=f"prod_{i}")
                product_choice_id = products_lookup[product_choice_name]

            # Prix et frais par défaut
            price_default = price_lookup.get(product_choice_id, 0.0)
            freight_default = freight_lookup.get(product_choice_id, 0.0)
            product_sellers = sellers_lookup.get(product_choice_id, ["unknown_seller"])

            with colB:
                price = st.number_input(
                    "Prix",
                    min_value=0.0,
                    value=float(price_default),
                    step=0.1,
                    key=f"price_{i}_{product_choice_id}"
                )
            with colC:
                freight_value = st.number_input(
                    "Frais",
                    min_value=0.0,
                    value=float(freight_default),
                    step=0.1,
                    key=f"freight_{i}_{product_choice_id}"
                )
            with colD:
                seller_choice = st.selectbox(
                    "Seller",
                    product_sellers,
                    key=f"seller_{i}_{product_choice_id}"
                )

            items.append({
                "product_id": product_choice_id,
                "product_name": product_choice_name,
                "price": price,
                "freight_value": freight_value,
                "seller_id": seller_choice
            })

        # Boutons d'action sous le formulaire
        btn_col1, btn_col2 = st.columns([1,1])
        with btn_col1:
            if st.button("Ajouter la commande", key="add_order_button"):
                order_id = insert_order(conn, customer_id, order_date, items)
                if order_id:
                    st.success("Commande ajoutée avec succès !")
        with btn_col2:
            if st.button("Réinitialiser le formulaire", key="reset_form"):
                st.rerun()

    with col_right:
        # Aperçu / résumé de commande
        st.markdown('<div class="summary-card">', unsafe_allow_html=True)
        st.markdown("<h4>Récapitulatif</h4>", unsafe_allow_html=True)
        if items:
            # table de preview simplifiée
            preview_df = pd.DataFrame([{
                "Produit": it["product_name"],
                "Prix": f'{it["price"]:.2f} $',
                "Frais": f'{it["freight_value"]:.2f} $',
                "Seller": it["seller_id"]
            } for it in items])
            st.table(preview_df)

            total = sum([x["price"] + x["freight_value"] for x in items])
            st.markdown(f'<div class="summary-total">Total commande<br><span class="total-amount">{total:.2f} $</span></div>', unsafe_allow_html=True)
        else:
            st.markdown("<div class='small-muted'>Aucun produit sélectionné</div>", unsafe_allow_html=True)

        # Téléchargement du preview (CSV)
        try:
            csv = pd.DataFrame(items).to_csv(index=False).encode('utf-8')
            st.download_button("Télécharger preview (CSV)", data=csv, file_name="order_preview.csv", mime="text/csv")
        except Exception:
            pass
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # --- Historique 10 dernières commandes ---
    st.subheader("10 dernières commandes")
    last_orders = pd.read_sql("""
        SELECT c.customer_unique_id AS client,
               GROUP_CONCAT(p.product_category_name SEPARATOR ', ') AS produits,
               GROUP_CONCAT(p.product_category_name SEPARATOR ', ') AS produits,
               SUM(oi.price + oi.freight_value) AS total,
               o.order_purchase_timestamp AS date
        FROM olist_orders_dataset o
        JOIN olist_customers_dataset c ON o.customer_id = c.customer_idt c ON o.customer_id = c.customer_id
        JOIN olist_order_items_dataset oi ON oi.order_id = o.order_id
        JOIN olist_products_dataset p ON oi.product_id = p.product_id
        GROUP BY c.customer_unique_id, o.order_purchase_timestamp
        ORDER BY o.order_purchase_timestamp DESC
        LIMIT 10
    """, conn)
    st.dataframe(last_orders.style.format({"total": "${:,.2f}"}))