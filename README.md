# Projet Olist — Pipeline AWS, Tableau et Application Streamlit

## Résumé
Ce dépôt contient l'application Streamlit permettant d'ajouter des commandes (module de démonstration). Cette application fait partie d'un projet plus large : ingestion des fichiers Olist (CSV) vers AWS S3, transformation et chargement dans une base RDS MySQL depuis une instance EC2, puis visualisation temps réel via un dashboard Tableau connecté à RDS.

## Liens
- Lien vers le dashboard Tableau : <https://public.tableau.com/app/profile/pape.mamadou.badji/viz/Dashboard_AWS_Olist_AS3/VueglobaleURL_DASHBOARD_A_METTRE_ICI>
- Lien vers la présentation canva : <https://www.canva.com/design/DAG7CcMOwnk/m4EhDpyFmzNFIbKcW-nfBQ/edit?utm_content=DAG7CcMOwnk&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton>

## Contexte et flux global
1. Téléchargement des fichiers CSV Olist (données e‑commerce Brésil).
2. Stockage des CSV dans un bucket S3.
3. Sur une instance EC2, exécution du script coler dans `AWS_S3_RDS/aws_s3_rds.txt` :
   - Récupère les fichiers depuis S3
   - Charge/transforme les CSV en tables SQL dans la base `MA_BASE` sur Amazon RDS
4. Tableau se connecte à la base RDS pour visualiser les données et produire le dashboard (temps réel / rafraîchissement).
5. L'application Streamlit (`app.py`) sert de démonstrateur : ajout manuel de commandes directement dans RDS pour montrer l'impact sur le dashboard Tableau.

## Fichiers clés
- app.py — Application Streamlit pour ajouter des commandes et prévisualiser.
- AWS_S3_RDS/aws_s3_rds.py — Script exécuté sur EC2 pour charger les CSV S3 → RDS.
- config.py — Configuration RDS (ne doit pas contenir d'identifiants publics).
- assets/style.css — Styles visuels pour l'application Streamlit.
- requirements.txt — Dépendances Python.

## Comment reproduire localement / rapide
1. Préparer l'environnement Python :
   ```bash
   pip install -r requirements.txt
   ```
2. Configurer `config.py` (ou variables d'environnement) avec les accès RDS.
3. Pour charger les données depuis S3 (sur EC2) :
   - Placer `aws_s3_rds.py` sur l'instance EC2 avec IAM role/bucket access
   - Exécuter : `python AWS_S3_RDS/aws_s3_rds.py`
4. Vérifier les tables dans la base `MA_BASE` (MySQL RDS).
5. Démarrer l'application Streamlit (local ou serveur) :
   ```bash
   streamlit run app.py
   ```
6. Ouvrir le dashboard Tableau (lien fourni) pour voir la synchronisation.

## Exécution du script S3→RDS
- Le script utilise boto3 pour lire les objets S3, pandas pour charger les CSV et SQLAlchemy pour écrire dans MySQL.
- Veiller à fournir les bonnes dépendances et autorisations IAM sur EC2.
- Ne pas committer les credentials dans le dépôt.

## Bonnes pratiques et sécurité
- Utiliser des variables d'environnement ou AWS Secrets Manager pour les credentials.
- Restreindre les rôles IAM à l'accès nécessaire au bucket S3 et à RDS.
- Ne pas exposer `config.py` avec des identifiants réels dans le repo.

## Notes pour la soutenance
- Expliquez le pipeline point par point (S3 → EC2 → RDS → Tableau → Streamlit).

## Auteur
Projet réalisé dans le cadre du cours Big Data & Cloud Computing de l'Ecole Nationale de la Statistique et de l'Analyse Economique ENSAE.
