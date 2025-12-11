# Olist - Gestion des Commandes

## Description du Projet

Application Streamlit moderne et professionnelle pour la gestion des commandes Olist. L'application permet d'ajouter de nouvelles commandes sur notre base RDS de AWS, visualiser un récapitulatif en temps réel, et consulter l'historique des commandes récentes.

---

## Objectifs

- Fournir une interface intuitive et professionnelle pour ajouter des commandes
- Valider les données en temps réel (client, produits, prix, frais)
- Stocker les commandes dans une base de données RDS MySQL
- Afficher un aperçu instantané avec total de la commande
- Permettre l'export des données en CSV

---

## Architecture

### Structure du Projet

```
BIG DATA/
├── app.py                    # Application principale Streamlit
├── config.py                 # Configuration RDS (identifiants)
├── assets/
│   └── style.css             # Styles CSS modernes
├── README.md                 # Documentation complète
└── requirements.txt          # Dépendances Python
```

---

## Technologies Utilisées

- Frontend : Streamlit (Python)
- Backend : Python (pandas, mysql-connector)
- Base de Données : MySQL RDS (AWS)
- Styling : CSS3 (polices Inter, gradients, ombres)

---

## Dépendances

```
streamlit >= 1.28
pandas >= 1.5
mysql-connector-python >= 8.0
```

### Installation

```bash
pip install -r requirements.txt
```

---

## Démarrage de l'Application

```bash
streamlit run app.py
```

L'application sera accessible sur `http://localhost:8501`

---

## Fonctionnalités Détaillées

### 1. Header Professionnel

- Titre centré et en gros caractères : "Ajout de commandes Olist"
- Sous-titre : "Application interne de gestion des commandes"
- Design gradient bleu et vert avec ombre douce

### 2. Formulaire d'Ajout de Commande (Colonne Gauche)

#### Informations Client
- **Sélection du client** : Liste déroulante pré-chargée depuis la base de données
- **Date de commande** : Sélecteur de date avec défaut à aujourd'hui

#### Gestion des Produits
- **Nombre de produits** : Input numérique avec minimum 1
- **Pour chaque produit** :
  - Sélection du produit (liste déroulante avec catégories)
  - Prix (auto-rempli avec la moyenne historique, modifiable)
  - Frais de port (auto-rempli avec la moyenne historique, modifiable)
  - Sélection du vendeur associé

#### Boutons d'Action
- **Ajouter la commande** : Valide et insère la commande dans la base de données
- **Réinitialiser le formulaire** : Vide tous les champs et recharge l'interface

### 3. Récapitulatif (Colonne Droite)

#### Carte de Récapitulatif
- **Table de prévisualisation** : Affiche tous les produits sélectionnés avec détails
- **Calcul du total** : Somme dynamique affichée en gros caractères
- **Arrière-plan gradient** : Fond bleu clair pour meilleure lisibilité
- **Bouton Télécharger** : Exporte la commande en format CSV

### 4. Historique des Commandes

#### Table des 10 Dernières Commandes
- **Client** : Identifiant unique du client
- **Produits** : Liste complète des produits (séparés par virgule)
- **Total** : Montant total incluant frais de port
- **Date** : Date et heure de la commande

Format : Tableau responsive avec styling cohérent

---

## Structure de la Base de Données

### Tables Principales

#### olist_customers_dataset
```
- customer_id (Clé primaire)
- customer_unique_id
```

#### olist_products_dataset
```
- product_id (Clé primaire)
- product_category_name
```

#### olist_order_items_dataset
```
- order_id
- product_id
- seller_id
- price
- freight_value
```

#### olist_orders_dataset
```
- order_id (Clé primaire)
- customer_id (Clé étrangère)
- order_status
- order_purchase_timestamp
```

---

## Design et Expérience Utilisateur

### Palette de Couleurs

- Bleu principal : #0b63d6 (accent, boutons)
- Vert secondaire : #0b8a6f (téléchargement)
- Fond : #f4f6fb (gris très clair)
- Texte principal : #162029 (noir charbon)
- Texte secondaire : #6b7280 (gris moyen)

### Composants Visuels

- **Cards** : Angles arrondis 14px, ombre douce, dégradé léger
- **Boutons** : Gradient bleu avec shadow, effet transform au survol
- **Séparation colonnes** : Barre bleue de 3px à gauche du récapitulatif
- **Typographie** : Police Inter (Google Fonts), poids 400-700

### Responsive Design

- Adaptation automatique sur écrans petits (< 900px)
- Ajustement du padding et des espacements
- Flexibilité des colonnes

---

## Configuration et Sécurité

### Fichier config.py

Contient les paramètres de connexion RDS :

```python
RDS_CONFIG = {
    "host": "votre_host_rds",
    "user": "votre_user",
    "password": "votre_password",
    "database": "votre_database"
}
```

**Important** : Ne jamais committer ce fichier avec les identifiants réels sur Git. En production, utiliser des variables d'environnement ou un gestionnaire de secrets.

### Variables d'Environnement (Recommandé)

```bash
export RDS_HOST=your_host
export RDS_USER=your_user
export RDS_PASSWORD=your_password
export RDS_DATABASE=your_database
```

---

## Flux de Traitement des Données

```
1. Chargement initial des données
   ├─ Récupération des clients depuis olist_customers_dataset
   ├─ Récupération des produits depuis olist_products_dataset
   └─ Calcul des moyennes de prix et frais

2. Interaction utilisateur
   ├─ Sélection du client
   ├─ Choix de la date
   └─ Ajout des produits avec prix/frais

3. Validation et insertion
   ├─ Génération d'un UUID pour order_id
   ├─ Insertion dans olist_orders_dataset
   ├─ Insertion de chaque item dans olist_order_items_dataset
   └─ Commit de la transaction

4. Affichage et retour utilisateur
   ├─ Message de succès avec Order ID
   ├─ Mise à jour de la table historique
   └─ Option de téléchargement en CSV
```

---

## Gestion des Erreurs

### Erreurs de Connexion

- Affichage d'un message d'erreur si la connexion RDS échoue
- L'application s'arrête tant que la connexion n'est pas établie

### Erreurs d'Insertion

- Rollback automatique en cas d'erreur SQL
- Message d'erreur détaillé affiché à l'utilisateur
- Données non validées ne sont pas persistées

### Fichiers Manquants

- Si assets/style.css est absent, fallback avec styles CSS basiques intégrés
- L'application reste fonctionnelle

### Réinitialisation

- Utilisation de st.rerun() pour relancer le script
- Nettoyage complet de st.session_state
- Remise à zéro de tous les widgets

---

## Performance et Optimisation

### Optimisations Implémentées

- Lookup tables chargées une seule fois en mémoire au démarrage
- Dictionnaires pour accès rapide aux prix et frais moyens
- Clés uniques sur les widgets pour éviter les conflits Streamlit
- Chargement lazy de l'historique à la demande

### Complexité Temporelle

- Création d'une commande : O(n) où n = nombre de produits
- Chargement de l'historique : O(1) requête SQL
- Recherche de prix/frais : O(1) lookup dict

---

## Limitations Connues

1. Le bouton de téléchargement ne prend pas la couleur verte (limitation du moteur CSS de Streamlit avec les boutons personnalisés)

2. L'historique affiche seulement les 10 dernières commandes (limitation volontaire pour performance)

3. Pas de système de pagination sur l'historique

4. Modification des commandes existantes non implémentée (lecture seule)

5. Export CSV limité à la commande en cours, pas d'export massif

---

## Évolutions Futures Possibles

- Pagination sur l'historique avec filtres
- Modification et annulation des commandes existantes
- Dashboard d'analytics et statistiques
- Authentification utilisateur
- Notifications email
- Support multi-langues
- API REST pour intégration externe
- Tests automatisés (pytest)
- Déploiement sur Streamlit Cloud

---

## Déploiement

### Streamlit Cloud

```bash
git push origin main
# Puis connecter le repo sur https://share.streamlit.io
```

### Serveur Local

```bash
streamlit run app.py --logger.level=info
```


---

## Support et Dépannage

### Le formulaire ne se réinitialise pas

Vérifier que st.rerun() est bien appelé. Sinon, utiliser st.session_state.clear() manuellement.

### Les prix/frais ne se mettent pas à jour

S'assurer que les clés des widgets sont basées sur l'index de produit uniquement (prod_{i}, price_{i}, etc.).

### Erreur de connexion RDS

Vérifier les identifiants dans config.py et la disponibilité du host RDS.

### Styles CSS non appliqués

Vérifier que assets/style.css existe dans le bon répertoire et recharger la page.

---

## Auteur

Projet réalisé dans le cadre du cours Big Data & Cloud Computing.

---

## Licence

Propriétaire - Utilisation interne uniquement.

---

## Contact et Questions

Pour toute question sur le fonctionnement de l'application, consulter le code source ou contacter le responsable du projet.
