import streamlit as st
import urllib.parse
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

# Configuration de la page
st.set_page_config(
    page_title="Maman Dogo Fashion Store", 
    page_icon="👑", 
    layout="wide"
)

# --- PARAMÈTRES DE CONNEXION POSTGRESQL SUPABASE ---
DB_HOST = "aws-0-eu-west-1.pooler.supabase.com"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_USER = "postgres.wqmxbbjzaytwwsanlckq"
DB_PASS = "u3eS&R-e27cYmL&"

# Fonction pour obtenir une connexion à la BDD
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        st.error(f"Erreur de connexion PostgreSQL : {e}")
        return None

# --- CRÉATION AUTOMATIQUE DES TABLES DANS SUPABASE ---
def init_db_automatique():
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            # 1. Table Produits
            cur.execute("""
                CREATE TABLE IF NOT EXISTS produits (
                    id SERIAL PRIMARY KEY,
                    nom VARCHAR(255) NOT NULL,
                    categorie VARCHAR(100) NOT NULL,
                    sous_categorie VARCHAR(100) NOT NULL,
                    prix_origine INT NOT NULL,
                    prix_final INT NOT NULL,
                    en_promo BOOLEAN DEFAULT FALSE,
                    reduction INT DEFAULT 0,
                    image_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # 2. Table Avis Clients
            cur.execute("""
                CREATE TABLE IF NOT EXISTS avis_clients (
                    id SERIAL PRIMARY KEY,
                    nom VARCHAR(255) NOT NULL,
                    note INT NOT NULL,
                    produit VARCHAR(255) NOT NULL,
                    commentaire TEXT NOT NULL,
                    date VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 3. Table Infos Boutique
            cur.execute("""
                CREATE TABLE IF NOT EXISTS infos_boutique (
                    id INT PRIMARY KEY DEFAULT 1,
                    nom_boutique VARCHAR(255),
                    description TEXT,
                    telephone VARCHAR(50),
                    adresse VARCHAR(255)
                );
            """)

            # Insertion des données par défaut si vide
            cur.execute("""
                INSERT INTO infos_boutique (id, nom_boutique, description, telephone, adresse)
                VALUES (1, 'Maman Dogo Fashion Store', 'L''excellence et l''élégance de la mode pour toute la famille à votre portée.', '221770000000', 'Dakar, Sénégal')
                ON CONFLICT (id) DO NOTHING;
            """)
            conn.commit()
        conn.close()

# Exécution de l'initialisation automatique au lancement
init_db_automatique()

# --- STYLES CSS PERSONNALISÉS ULTRA-RESPONSIVE ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #fff5f7 0%, #fce4ec 50%, #f8bbd0 100%);
        font-family: 'Poppins', system-ui, -apple-system, sans-serif;
    }
    .brand-title {
        font-size: clamp(1.8rem, 5vw, 3rem) !important;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #d81b60, #e91e63, #c2185b, #d4af37);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 5px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .brand-subtitle {
        text-align: center;
        color: #880e4f;
        font-size: clamp(0.9rem, 2.5vw, 1.1rem);
        margin-bottom: 20px;
        font-style: italic;
    }
    .product-card {
        background-color: #ffffff;
        border-radius: 20px;
        padding: 16px;
        box-shadow: 0 8px 20px rgba(233, 30, 99, 0.08);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        border: 1px solid #f8bbd0;
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 25px rgba(216, 27, 96, 0.18);
        border-color: #e91e63;
    }
    .review-card {
        background-color: #ffffff;
        border-radius: 14px;
        padding: 14px;
        border-left: 5px solid #e91e63;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(233, 30, 99, 0.05);
    }
    .promo-badge {
        background: linear-gradient(45deg, #e91e63, #ff4081);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 6px;
    }
    .price-old {
        text-decoration: line-through;
        color: #ad1457;
        font-size: 0.9rem;
        margin-right: 6px;
    }
    .price-new {
        color: #880e4f;
        font-weight: 800;
        font-size: 1.2rem;
    }
    [data-testid="stSidebar"] {
        background-color: #2c001e !important;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h1 {
        color: #f8bbd0 !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] * {
        color: #2c001e !important;
    }
    .stButton>button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        background-color: #e91e63 !important;
        color: #ffffff !important;
        border: none !important;
        padding: 8px 16px !important;
        width: 100% !important;
    }
    .whatsapp-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        background-color: #25D366;
        color: white !important;
        text-align: center;
        padding: 14px;
        border-radius: 14px;
        font-weight: bold;
        font-size: 1rem;
        text-decoration: none;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- FONCTIONS DE REQUÊTES SQL SUPABASE ---
def charger_infos_boutique():
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM infos_boutique WHERE id = 1;")
            res = cur.fetchone()
        conn.close()
        if res:
            return res
    return {
        "nom_boutique": "Maman Dogo Fashion Store",
        "description": "L'excellence et l'élégance de la mode pour toute la famille à votre portée.",
        "telephone": "221770000000",
        "adresse": "Dakar, Sénégal"
    }

def charger_produits():
    conn = get_db_connection()
    prods = []
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM produits ORDER BY id DESC;")
            prods = cur.fetchall()
        conn.close()
    return prods

def charger_avis():
    conn = get_db_connection()
    avis = []
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM avis_clients ORDER BY id DESC;")
            avis = cur.fetchall()
        conn.close()
    return avis

# --- INITIALISATION SESSION ---
if "panier" not in st.session_state:
    st.session_state.panier = []

if "admin_connecte" not in st.session_state:
    st.session_state.admin_connecte = False

infos_boutique = charger_infos_boutique()
CATEGORIES = ["Bébé", "Enfants", "Femmes", "Hommes"]
SOUS_CATEGORIES = ["Vêtements", "Chaussures", "Tissus", "Accessoires"]

# --- TRADUCTIONS ---
TRADUCTIONS = {
    "FR": {
        "titre_app": f"👑 {infos_boutique['nom_boutique']}",
        "sous_titre_app": infos_boutique['description'],
        "menu_label": "Navigation :",
        "menu_bebe": "👶 Rayon Bébé",
        "menu_enfants": "🧒 Rayon Enfants",
        "menu_femmes": "👗 Rayon Femmes",
        "menu_hommes": "👔 Rayon Hommes",
        "menu_promotions": "🔥 Promos",
        "menu_avis": "⭐ Avis & Retours Clients",
        "menu_vendeur": "✨ Espace Vendeur",
        "menu_admin": "⚙️ Espace Administrateur",
        "menu_panier": "🛒 Mon Panier VIP",
        "panier_sidebar_titre": "🛒 Votre Panier",
        "articles_select": "Articles sélectionnés :",
        "total_label": "Total estimé :",
        "btn_vider": "Vider le panier",
        "sub_vetements": "👗 Vêtements",
        "sub_chaussures": "👟 Chaussures",
        "sub_tissus": "🧵 Tissus",
        "sub_accessoires": "👜 Accessoires",
        "promo_titre": "🔥 Espace Promos",
        "promo_desc": "Profitez de nos prix réduits sur une sélection de pièces magnifiques.",
        "vide_cat": "Aucun article disponible actuellement dans ce rayon",
        "vide_promo": "Aucun produit en promo pour le moment.",
        "sans_photo": "📷 Pas de visuel disponible",
        "btn_ajouter": "Ajouter au Panier",
        "succes_ajout": "a été ajouté à votre panier !",
        "vendeur_titre": "✨ Espace Vendeur & Publication Directe",
        "vendeur_desc": "Publiez ou gérez vos articles enregistrés de façon permanente dans Supabase.",
        "nom_article": "Nom du produit (ex: Ensemble Bébé, Robe Fille...)",
        "prix_article": "Prix standard (en FCFA)",
        "est_promo": "Placer cet article en Promo ?",
        "taux_promo": "Pourcentage de remise (%)",
        "cat_choix": "Choisir le public cible",
        "sub_choix": "Choisir le type d'article",
        "photo_article": "Saisir l'URL de la photo ou laisser vide",
        "btn_publier": "Mettre en ligne l'article",
        "err_nom": "Veuillez entrer un nom d'article valide.",
        "succes_publi": "Succès ! Votre création est enregistrée dans Supabase.",
        "panier_titre": "🛒 Mon Panier d'Achat VIP",
        "panier_vide": "Votre panier est vide.",
        "btn_retirer": "Retirer",
        "total_depenses": "Montant Total des Achats :",
        "btn_valider": "Générer ma commande WhatsApp",
        "succes_commande": "🎉 Commande prête ! Cliquez ci-dessous pour envoyer votre commande sur WhatsApp.",
        "recherche": "🔎 Rechercher un article..."
    },
    "WOLOF": {
        "titre_app": f"👑 {infos_boutique['nom_boutique']}",
        "sous_titre_app": "Tar, rafet ak taru yeere ak simis yi njabot gi yepp.",
        "menu_label": "Tannal fi nga jëm :",
        "menu_bebe": "👶 Wàllu Liir yi (Bébé)",
        "menu_enfants": "🧒 Wàllu Xale yi (Enfants)",
        "menu_femmes": "👗 Wàllu Jigéen yi (Femmes)",
        "menu_hommes": "👔 Wàllu Góor yi (Hommes)",
        "menu_promotions": "🔥 Promos",
        "menu_avis": "⭐ Xalaat & Kadduy Jëndkat yi",
        "menu_vendeur": "✨ Palu Jaaykat bi",
        "menu_admin": "⚙️ Palu Boroom Boutik bi",
        "menu_panier": "🛒 Sama Saku Jënd VIP",
        "panier_sidebar_titre": "🛒 Sa Saku Jënd",
        "articles_select": "Limu bagas yi :",
        "total_label": "Mbolloog xalis bi :",
        "btn_vider": "Fay saku gi",
        "sub_vetements": "👗 Yeere yi",
        "sub_chaussures": "👟 Dall yi",
        "sub_tissus": "🧵 Tissu yi",
        "sub_accessoires": "👜 Bagas yi",
        "promo_titre": "🔥 Wàññi Njeeg (Promos)",
        "promo_desc": "Jëfandikool sunu njeeg yi wàññiku ngir jënd lu rafet !",
        "vide_cat": "Amagul benn bagas léegi ci fi",
        "vide_promo": "Amagul benn bagas bu wàññiku njeeg bi léegi.",
        "sans_photo": "📷 Amul nataal",
        "btn_ajouter": "Yobbal ci saku gi",
        "succes_ajout": "dugg na ci saku gi !",
        "vendeur_titre": "✨ Palu Jaaykat bi - Maman Dogo Fashion Store",
        "vendeur_desc": "Bindal fisii ngir feenalaat sa bagas ci lëlu jaay gi.",
        "nom_article": "Turu bagas bi (souba: Yeere liir, Robe xale...)",
        "prix_article": "Njeeg bu njëkk bi (ci FCFA)",
        "est_promo": "Ndax daṅa bëgg wàññi njeeg bi (Promo) ?",
        "taux_promo": "Turu wàññi gi (ci %)",
        "cat_choix": "Tannal ñimuy jaay (Bébé, Femmes...)",
        "sub_choix": "Tannal mbolloom bagas bi (Yeere, Dall...)",
        "photo_article": "Duggal nataalu bagas bi",
        "btn_publier": "Feenale bagas bi",
        "err_nom": "Diisaleel turu bagas bu dëggu.",
        "succes_publi": "Mbegte ! Sa bagas dugg na ci Supabase.",
        "panier_titre": "🛒 Sa Saku Jënd VIP - Maman Dogo",
        "panier_vide": "Sa saku jënd feesul.",
        "btn_retirer": "Dindi",
        "total_depenses": "Mbolloog xalis bi nga wara fay :",
        "btn_valider": "Yöbbal sama jënd ci WhatsApp",
        "succes_commande": "🎉 Jënd gi pare na !",
        "recherche": "🔎 Seetbal bagas..."
    }
}

# --- BARRE LATÉRALE ---
st.sidebar.markdown(f"# 👑 Maman Dogo")
st.sidebar.caption("Fashion Store — Mode & Élégance")

langue = st.sidebar.selectbox("🌐 Langue / Lakk :", ["Français", "Wolof"])
lang_code = "FR" if langue == "Français" else "WOLOF"
t = TRADUCTIONS[lang_code]

st.sidebar.markdown("---")

menu_options = [
    t["menu_bebe"],
    t["menu_enfants"],
    t["menu_femmes"],
    t["menu_hommes"],
    t["menu_promotions"],
    t["menu_avis"],
    t["menu_vendeur"],
    t["menu_admin"],
    t["menu_panier"]
]
choix_menu = st.sidebar.radio(t["menu_label"], menu_options)

st.sidebar.markdown("---")
st.sidebar.subheader(t["panier_sidebar_titre"])
nb_articles = len(st.session_state.panier)
st.sidebar.write(f"{t['articles_select']} **{nb_articles}**")

if nb_articles > 0:
    total_panier = sum(item['prix_final'] for item in st.session_state.panier)
    st.sidebar.write(f"{t['total_label']} **{total_panier:,} FCFA**")
    if st.sidebar.button(t["btn_vider"], use_container_width=True):
        st.session_state.panier = []
        st.rerun()

# --- ENTÊTE PRINCIPAL ---
st.markdown(f'<h1 class="brand-title">{t["titre_app"]}</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="brand-subtitle">{t["sous_titre_app"]}</p>', unsafe_allow_html=True)

# FONCTION D'AFFICHAGE DU RAYON
def afficher_rayon(cat_courante):
    recherche = st.text_input(t["recherche"], placeholder="Tapez le nom d'un article...")
    sous_labels = [t["sub_vetements"], t["sub_chaussures"], t["sub_tissus"], t["sub_accessoires"]]
    sous_tabs = st.tabs(sous_labels)

    tous_produits = charger_produits()
    tous_avis = charger_avis()

    for j, tab_sub in enumerate(sous_tabs):
        with tab_sub:
            sous_cat_courante = SOUS_CATEGORIES[j]
            produits_categorie = [
                p for p in tous_produits 
                if p["categorie"] == cat_courante and p["sous_categorie"] == sous_cat_courante
            ]
            
            if recherche:
                produits_categorie = [p for p in produits_categorie if recherche.lower() in p["nom"].lower()]

            if not produits_categorie:
                st.info(f"{t['vide_cat']} '{sous_labels[j]}'.")
            else:
                cols = st.columns([1, 1, 1])
                for index, produit in enumerate(produits_categorie):
                    with cols[index % 3]:
                        st.markdown('<div class="product-card">', unsafe_allow_html=True)
                        
                        if produit.get("image_url"):
                            st.image(produit["image_url"], use_container_width=True)
                        else:
                            st.markdown(f"<p style='color:#aaa;'>{t['sans_photo']}</p>", unsafe_allow_html=True)
                        
                        avis_article = [a for a in tous_avis if a["produit"] == produit["nom"]]
                        if avis_article:
                            note_moyenne = sum(a["note"] for a in avis_article) / len(avis_article)
                            st.caption(f"⭐ {note_moyenne:.1f}/5 ({len(avis_article)} avis)")
                        else:
                            st.caption("⭐ Pas encore d'avis")

                        if produit.get("en_promo"):
                            st.markdown(f'<span class="promo-badge">PROMO -{produit["reduction"]}%</span>', unsafe_allow_html=True)
                            st.markdown(f"### {produit['nom']}")
                            st.markdown(f'<span class="price-old">{produit["prix_origine"]:,} FCFA</span><span class="price-new">{produit["prix_final"]:,} FCFA</span>', unsafe_allow_html=True)
                        else:
                            st.markdown(f"### {produit['nom']}")
                            st.markdown(f'<span class="price-new">{produit["prix_final"]:,} FCFA</span>', unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        btn_key = f"add_{cat_courante}_{sous_cat_courante}_{produit['id']}"
                        if st.button(t["btn_ajouter"], key=btn_key, use_container_width=True):
                            st.session_state.panier.append(produit)
                            st.success(f"'{produit['nom']}' {t['succes_ajout']}")
                        
                        st.markdown('</div>', unsafe_allow_html=True)

# FONCTION DE GESTION DU CATALOGUE
def afficher_gestion_catalogue():
    prods = charger_produits()
    if not prods:
        st.info("Aucun article disponible dans Supabase.")
    else:
        for idx, prod in enumerate(prods):
            c1, c2, c3, c4 = st.columns([1, 2, 2, 1])
            with c1:
                if prod.get("image_url"):
                    st.image(prod["image_url"], width=50)
                else:
                    st.write("📷")
            with c2:
                st.write(f"**{prod['nom']}** ({prod['categorie']} > {prod['sous_categorie']})")
            with c3:
                st.write(f"{prod['prix_final']:,} FCFA")
            with c4:
                if st.button("🗑️ Supprimer", key=f"del_spb_{prod['id']}"):
                    conn = get_db_connection()
                    if conn:
                        with conn.cursor() as cur:
                            cur.execute("DELETE FROM produits WHERE id = %s;", (prod['id'],))
                            conn.commit()
                        conn.close()
                    st.success(f"Article '{prod['nom']}' supprimé !")
                    st.rerun()

# --- NAVIGATION PAR MENU ---
if choix_menu == t["menu_bebe"]:
    st.subheader("👶 Rayon Bébé")
    afficher_rayon("Bébé")

elif choix_menu == t["menu_enfants"]:
    st.subheader("🧒 Rayon Enfants")
    afficher_rayon("Enfants")

elif choix_menu == t["menu_femmes"]:
    st.subheader("👗 Rayon Femmes")
    afficher_rayon("Femmes")

elif choix_menu == t["menu_hommes"]:
    st.subheader("👔 Rayon Hommes")
    afficher_rayon("Hommes")

elif choix_menu == t["menu_promotions"]:
    st.subheader(t["promo_titre"])
    st.write(t["promo_desc"])

    tous_produits = charger_produits()
    articles_en_promo = [p for p in tous_produits if p.get("en_promo")]

    if not articles_en_promo:
        st.info(t["vide_promo"])
    else:
        cols = st.columns([1, 1, 1])
        for index, produit in enumerate(articles_en_promo):
            with cols[index % 3]:
                st.markdown('<div class="product-card">', unsafe_allow_html=True)
                if produit.get("image_url"):
                    st.image(produit["image_url"], use_container_width=True)
                st.markdown(f'<span class="promo-badge">PROMO -{produit["reduction"]}%</span>', unsafe_allow_html=True)
                st.markdown(f"### {produit['nom']}")
                st.markdown(f'<span class="price-old">{produit["prix_origine"]:,} FCFA</span><span class="price-new">{produit["prix_final"]:,} FCFA</span>', unsafe_allow_html=True)
                
                if st.button(t["btn_ajouter"], key=f"promo_add_{produit['id']}", use_container_width=True):
                    st.session_state.panier.append(produit)
                    st.success(f"'{produit['nom']}' {t['succes_ajout']}")
                st.markdown('</div>', unsafe_allow_html=True)

elif choix_menu == t["menu_avis"]:
    st.subheader("⭐ Avis & Retours Expérience Clients")
    col_form, col_liste = st.columns([1, 1])

    with col_form:
        st.markdown("### 📝 Laisser un Avis")
        with st.form("form_avis", clear_on_submit=True):
            nom_client = st.text_input("Votre Prénom & Nom")
            note_client = st.slider("Votre Note", min_value=1, max_value=5, value=5)
            
            prods = charger_produits()
            tous_produits_noms = ["Général"] + [p["nom"] for p in prods]
            produit_concerne = st.selectbox("Article concerné", tous_produits_noms)
            commentaire = st.text_area("Votre commentaire")
            
            submit_avis = st.form_submit_button("Publier mon avis", use_container_width=True)

            if submit_avis:
                if not nom_client.strip() or not commentaire.strip():
                    st.error("Veuillez remplir tous les champs.")
                else:
                    date_now = datetime.now().strftime("%d/%m/%Y")
                    conn = get_db_connection()
                    if conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                INSERT INTO avis_clients (nom, note, produit, commentaire, date)
                                VALUES (%s, %s, %s, %s, %s);
                            """, (nom_client.strip(), note_client, produit_concerne, commentaire.strip(), date_now))
                            conn.commit()
                        conn.close()
                    st.success("Merci ! Votre avis a été enregistré.")
                    st.rerun()

    with col_liste:
        st.markdown("### 💬 Avis Récents de la Communauté")
        avis_liste = charger_avis()
        if not avis_liste:
            st.info("Aucun avis déposé pour le moment.")
        else:
            for avis in avis_liste:
                st.markdown(f"""
                <div class="review-card">
                    <div style="display:flex; justify-content:space-between;">
                        <strong>👤 {avis['nom']}</strong>
                        <span style="color:#d4af37;">{"⭐" * avis['note']}</span>
                    </div>
                    <small style="color:#777;">Produit : {avis['produit']} | Publié le {avis['date']}</small>
                    <p style="margin-top:8px; color:#333;">"{avis['commentaire']}"</p>
                </div>
                """, unsafe_allow_html=True)

elif choix_menu == t["menu_vendeur"]:
    st.subheader(t["vendeur_titre"])

    if not st.session_state.admin_connecte:
        st.info("🔒 Connexion sécurisée requise")
        with st.form("form_login_vendeur"):
            identifiant = st.text_input("Nom d'utilisateur Vendeur / Admin")
            mot_de_passe = st.text_input("Mot de passe", type="password")
            btn_connexion = st.form_submit_button("Se connecter", use_container_width=True)

            if btn_connexion:
                if identifiant == "Maman Dogo" and mot_de_passe == "Dogo2026":
                    st.session_state.admin_connecte = True
                    st.success("Connexion réussie !")
                    st.rerun()
                else:
                    st.error("Identifiant ou mot de passe incorrect.")
    else:
        tab_publi, tab_mes_prods = st.tabs(["➕ Publier un Nouvel Article", "📦 Mes Articles en Ligne"])

        with tab_publi:
            with st.form("form_vendeur", clear_on_submit=True):
                nom_produit = st.text_input(t["nom_article"])
                prix_origine = st.number_input(t["prix_article"], min_value=100, step=500, value=10000)
                
                appliquer_promo = st.checkbox(t["est_promo"])
                taux_reduction = st.slider(t["taux_promo"], min_value=5, max_value=70, value=15, step=5) if appliquer_promo else 0
                
                dict_categories = {"👶 Bébé": "Bébé", "🧒 Enfants": "Enfants", "👗 Femmes": "Femmes", "👔 Hommes": "Hommes"}
                dict_sous_categories = {t["sub_vetements"]: "Vêtements", t["sub_chaussures"]: "Chaussures", t["sub_tissus"]: "Tissus", t["sub_accessoires"]: "Accessoires"}

                cat_choisie_label = st.selectbox(t["cat_choix"], list(dict_categories.keys()))
                sub_choisie_label = st.selectbox(t["sub_choix"], list(dict_sous_categories.keys()))
                
                categorie_cible = dict_categories[cat_choisie_label]
                sous_categorie_cible = dict_sous_categories[sub_choisie_label]
                
                image_url_input = st.text_input("URL / Lien web de l'image du produit (Optionnel)")
                valider_ajout = st.form_submit_button(t["btn_publier"], use_container_width=True)

                if valider_ajout:
                    if not nom_produit.strip():
                        st.error(t["err_nom"])
                    else:
                        prix_final = int(prix_origine * (1 - taux_reduction / 100)) if appliquer_promo else prix_origine
                        conn = get_db_connection()
                        if conn:
                            with conn.cursor() as cur:
                                cur.execute("""
                                    INSERT INTO produits (nom, categorie, sous_categorie, prix_origine, prix_final, en_promo, reduction, image_url)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                                """, (nom_produit.strip(), categorie_cible, sous_categorie_cible, prix_origine, prix_final, appliquer_promo, taux_reduction, image_url_input.strip()))
                                conn.commit()
                            conn.close()

                        st.success(t["succes_publi"])
                        st.rerun()

        with tab_mes_prods:
            afficher_gestion_catalogue()

elif choix_menu == t["menu_admin"]:
    st.subheader("🔐 Espace Administrateur - Maman Dogo")

    if not st.session_state.admin_connecte:
        st.info("Veuillez vous identifier.")
        with st.form("form_login_admin"):
            identifiant = st.text_input("Nom d'utilisateur Administrateur")
            mot_de_passe = st.text_input("Mot de passe", type="password")
            btn_connexion = st.form_submit_button("Se connecter", use_container_width=True)

            if btn_connexion:
                if identifiant == "Maman Dogo" and mot_de_passe == "Dogo2026":
                    st.session_state.admin_connecte = True
                    st.rerun()
                else:
                    st.error("Identifiant ou mot de passe incorrect.")
    else:
        tab_infos, tab_produits, tab_avis_mod, tab_stats = st.tabs(["📝 Données Boutique", "📦 Gestion Catalogue", "💬 Modération Avis", "📊 Statistiques"])

        with tab_infos:
            infos = charger_infos_boutique()
            with st.form("form_infos_boutique"):
                nouveau_nom = st.text_input("Nom de la boutique", value=infos["nom_boutique"])
                nouvelle_desc = st.text_area("Description", value=infos["description"])
                nouveau_tel = st.text_input("Téléphone WhatsApp", value=infos["telephone"])
                nouvelle_adresse = st.text_input("Adresse", value=infos["adresse"])

                save_infos = st.form_submit_button("Enregistrer", use_container_width=True)
                if save_infos:
                    conn = get_db_connection()
                    if conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                INSERT INTO infos_boutique (id, nom_boutique, description, telephone, adresse)
                                VALUES (1, %s, %s, %s, %s)
                                ON CONFLICT (id) DO UPDATE SET
                                    nom_boutique = EXCLUDED.nom_boutique,
                                    description = EXCLUDED.description,
                                    telephone = EXCLUDED.telephone,
                                    adresse = EXCLUDED.adresse;
                            """, (nouveau_nom, nouvelle_desc, nouveau_tel.replace("+", "").replace(" ", ""), nouvelle_adresse))
                            conn.commit()
                        conn.close()
                    st.success("Modifications enregistrées !")
                    st.rerun()

        with tab_produits:
            afficher_gestion_catalogue()

        with tab_avis_mod:
            avis_liste = charger_avis()
            if not avis_liste:
                st.info("Aucun avis déposé.")
            else:
                for avis in avis_liste:
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.write(f"**{avis['nom']}** ({avis['note']}/5⭐) : {avis['commentaire']}")
                    with c2:
                        if st.button("🗑️ Supprimer", key=f"del_av_{avis['id']}"):
                            conn = get_db_connection()
                            if conn:
                                with conn.cursor() as cur:
                                    cur.execute("DELETE FROM avis_clients WHERE id = %s;", (avis['id'],))
                                    conn.commit()
                                conn.close()
                            st.rerun()

        with tab_stats:
            prods = charger_produits()
            valeur_stock = sum(p["prix_final"] for p in prods)
            col_s1, col_s2, col_s3 = st.columns([1, 1, 1])
            col_s1.metric("Total Articles Supabase", len(prods))
            col_s2.metric("Valeur du Stock", f"{valeur_stock:,} FCFA")
            col_s3.metric("Nombre d'avis", len(charger_avis()))

elif choix_menu == t["menu_panier"]:
    st.subheader(t["panier_titre"])

    if not st.session_state.panier:
        st.info(t["panier_vide"])
    else:
        for idx, item in enumerate(st.session_state.panier):
            col_img, col_desc, col_prix, col_action = st.columns([1, 2, 2, 1])
            with col_img:
                if item.get("image_url"):
                    st.image(item["image_url"], width=70)
                else:
                    st.write("📦")
            with col_desc:
                st.markdown(f"**{item['nom']}**")
            with col_prix:
                st.markdown(f'**{item["prix_final"]:,} FCFA**')
            with col_action:
                if st.button("❌ " + t["btn_retirer"], key=f"suppr_panier_{idx}"):
                    st.session_state.panier.pop(idx)
                    st.rerun()
            st.markdown("---")

        total_general = sum(item['prix_final'] for item in st.session_state.panier)
        st.markdown(f"### {t['total_depenses']} <span style='color:#e91e63; font-size:1.8rem; font-weight:bold;'>{total_general:,} FCFA</span>", unsafe_allow_html=True)

        with st.form("form_commande_whatsapp"):
            nom_client = st.text_input("Prénom & Nom *")
            tel_client = st.text_input("Téléphone *")
            adresse_client = st.text_input("Adresse de livraison *")
            valider_cmd = st.form_submit_button(t["btn_valider"], use_container_width=True)

        if valider_cmd:
            if not nom_client.strip() or not tel_client.strip() or not adresse_client.strip():
                st.error("Veuillez remplir toutes vos informations de livraison.")
            else:
                lignes_commande = [f"{i+1}. *{item['nom']}* - {item['prix_final']:,} FCFA" for i, item in enumerate(st.session_state.panier)]
                msg_whatsapp = (
                    f"👑 *COMMANDE - {infos_boutique['nom_boutique']}*\n\n"
                    f"👤 *Client* : {nom_client.strip()}\n"
                    f"📞 *Tél* : {tel_client.strip()}\n"
                    f"📍 *Livraison* : {adresse_client.strip()}\n\n"
                    f"🛍️ *PANIER* :\n" + "\n".join(lignes_commande) + f"\n\n"
                    f"💰 *TOTAL* : *{total_general:,} FCFA*"
                )
                lien_whatsapp = f"https://wa.me/{infos_boutique['telephone']}?text={urllib.parse.quote(msg_whatsapp)}"
                st.balloons()
                st.success(t["succes_commande"])
                st.markdown(f'<a href="{lien_whatsapp}" target="_blank" class="whatsapp-btn">📲 Envoyer ma commande sur WhatsApp</a>', unsafe_allow_html=True)