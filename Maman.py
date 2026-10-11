import streamlit as st
import urllib.parse
from datetime import datetime
import base64
import os

# Importation sécurisée de psycopg2
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ModuleNotFoundError:
    st.error("❌ Le module 'psycopg2' n'est pas installé. Veuillez installer 'psycopg2-binary'.")
    st.stop()

# Configuration de la page
st.set_page_config(
    page_title="Maman Dogo Fashion Store", 
    page_icon="👑", 
    layout="wide"
)

# --- RÉCUPÉRATION DES SECRETS POSTGRESQL / SUPABASE ---
try:
    DB_HOST = st.secrets["postgres"]["host"]
    DB_PORT = st.secrets["postgres"]["port"]
    DB_NAME = st.secrets["postgres"]["dbname"]
    DB_USER = st.secrets["postgres"]["user"]
    DB_PASS = st.secrets["postgres"]["password"]
except Exception:
    DB_HOST = "aws-0-eu-west-1.pooler.supabase.com"
    DB_PORT = "5432"
    DB_NAME = "postgres"
    DB_USER = "postgres.wqmxbbjzaytwwsanlckq"
    DB_PASS = "u3eS&R-e27cYmL&"

# Fonction d'obtention de la connexion à la base de données
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

# --- CONVERTISSEUR D'IMAGE EN BASE64 POUR STOCKAGE PERMANENT ---
def encoder_image_base64(fichier_image):
    if fichier_image is not None:
        bytes_data = fichier_image.getvalue()
        base64_str = base64.b64encode(bytes_data).decode()
        mime_type = fichier_image.type
        return f"data:{mime_type};base64,{base64_str}"
    return ""

# --- INITIALISATION AUTOMATIQUE DE LA STRUCTURE DB ---
def init_db_automatique():
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
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
                    description TEXT,
                    image_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
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

            cur.execute("""
                CREATE TABLE IF NOT EXISTS infos_boutique (
                    id INT PRIMARY KEY DEFAULT 1,
                    nom_boutique VARCHAR(255),
                    description TEXT,
                    telephone VARCHAR(50),
                    adresse VARCHAR(255)
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS commandes (
                    id SERIAL PRIMARY KEY,
                    nom_client VARCHAR(255) NOT NULL,
                    telephone VARCHAR(50) NOT NULL,
                    adresse VARCHAR(255) NOT NULL,
                    details_articles TEXT NOT NULL,
                    montant_total INT NOT NULL,
                    statut VARCHAR(50) DEFAULT 'En attente',
                    date_commande VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cur.execute("""
                INSERT INTO infos_boutique (id, nom_boutique, description, telephone, adresse)
                VALUES (1, 'Maman Dogo Fashion Store', 'L''excellence et l''élégance de la mode pour toute la famille à votre portée.', '221770000000', 'Dakar, Sénégal')
                ON CONFLICT (id) DO NOTHING;
            """)
            conn.commit()
        conn.close()

init_db_automatique()

# --- STYLES CSS PERSONNALISÉS ULTRA-RESPONSIVE (OPTIMISÉ TOUS SUPPORTS) ---
st.markdown("""
<style>
    header[data-testid="stHeader"] {
        display: none !important;
    }
    footer {
        visibility: hidden;
    }

    .stApp {
        background: linear-gradient(135deg, #fff5f7 0%, #fce4ec 50%, #f8bbd0 100%);
        font-family: 'Poppins', system-ui, -apple-system, sans-serif;
        overflow-x: hidden;
    }

    .logo-xxl-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 15px;
        padding: 5px;
        width: 100%;
    }
    .logo-xxl-frame {
        background: linear-gradient(135deg, #d4af37 0%, #e91e63 50%, #880e4f 100%);
        padding: 4px;
        border-radius: 24px;
        box-shadow: 0 8px 25px rgba(233, 30, 99, 0.25);
        max-width: 100%;
    }
    .logo-xxl-inner {
        background-color: #ffffff;
        border-radius: 20px;
        overflow: hidden;
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 4px;
    }
    .logo-xxl-inner img {
        border-radius: 16px;
        max-height: 140px;
        width: auto;
        max-width: 100%;
        object-fit: contain;
    }

    .brand-title {
        font-size: clamp(1.5rem, 4vw, 2.8rem) !important;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #d81b60, #e91e63, #c2185b, #d4af37);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        word-break: break-word;
    }
    .brand-subtitle {
        text-align: center;
        color: #880e4f;
        font-size: clamp(0.8rem, 1.8vw, 1rem);
        margin-bottom: 12px;
        font-style: italic;
        padding: 0 10px;
    }

    div[data-testid="stRadio"] > div {
        flex-direction: row !important;
        justify-content: center !important;
        flex-wrap: wrap !important;
        gap: 6px !important;
        background-color: #2c001e;
        padding: 8px 10px;
        border-radius: 16px;
        box-shadow: 0 4px 15px rgba(44, 0, 30, 0.2);
        margin-bottom: 20px;
        width: 100%;
    }

    div[data-testid="stRadio"] label {
        background-color: rgba(255, 255, 255, 0.08) !important;
        color: #f8bbd0 !important;
        padding: 6px 12px !important;
        border-radius: 10px !important;
        border: 1px solid rgba(248, 187, 208, 0.2) !important;
        font-size: clamp(0.8rem, 1.5vw, 0.95rem) !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
        flex: 1 1 auto;
        text-align: center;
    }

    div[data-testid="stRadio"] label:hover {
        background-color: #e91e63 !important;
        color: #ffffff !important;
    }

    .product-card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 12px;
        box-shadow: 0 6px 15px rgba(233, 30, 99, 0.08);
        transition: transform 0.2s ease;
        border: 1px solid #f8bbd0;
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        margin-bottom: 15px;
    }
    
    .product-card img {
        border-radius: 12px;
        max-height: 200px;
        object-fit: cover;
        width: 100%;
    }

    .product-desc {
        font-size: 0.85rem;
        color: #666;
        margin: 6px 0;
        background-color: #fff5f7;
        padding: 6px;
        border-radius: 8px;
    }

    .review-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 12px;
        border-left: 4px solid #e91e63;
        margin-bottom: 10px;
        box-shadow: 0 3px 10px rgba(233, 30, 99, 0.05);
    }

    .order-card {
        background-color: #ffffff;
        border-radius: 14px;
        padding: 14px;
        border: 1px solid #f8bbd0;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(233, 30, 99, 0.06);
    }

    .promo-badge {
        background: linear-gradient(45deg, #e91e63, #ff4081);
        color: white;
        padding: 3px 10px;
        border-radius: 16px;
        font-size: 0.75rem;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 4px;
    }
    
    .price-old {
        text-decoration: line-through;
        color: #ad1457;
        font-size: 0.85rem;
        margin-right: 4px;
    }
    
    .price-new {
        color: #880e4f;
        font-weight: 800;
        font-size: 1.1rem;
    }

    .stButton>button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        background-color: #e91e63 !important;
        color: #ffffff !important;
        border: none !important;
        padding: 10px 14px !important;
        width: 100% !important;
        min-height: 42px !important;
    }

    .whatsapp-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        background-color: #25D366;
        color: white !important;
        text-align: center;
        padding: 12px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 0.95rem;
        text-decoration: none;
        margin-top: 12px;
        box-shadow: 0 4px 12px rgba(37, 211, 102, 0.3);
    }

    .footer-container {
        background: linear-gradient(135deg, #2c001e 0%, #4a0033 100%);
        color: #f8bbd0;
        padding: 25px 15px 15px 15px;
        border-radius: 20px 20px 0 0;
        margin-top: 40px;
        box-shadow: 0 -6px 20px rgba(0, 0, 0, 0.15);
    }
    .footer-features {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 15px;
        text-align: center;
        margin-bottom: 20px;
        padding-bottom: 20px;
        border-bottom: 1px solid rgba(248, 187, 208, 0.2);
    }
    .feature-box h4 {
        color: #d4af37;
        margin-bottom: 4px;
        font-size: 0.95rem;
    }
    .feature-box p {
        font-size: 0.78rem;
        color: #fce4ec;
        margin: 0;
    }
    .footer-bottom {
        text-align: center;
        font-size: 0.8rem;
        color: #f8bbd0;
    }
    .footer-bottom a {
        color: #d4af37;
        text-decoration: none;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- REQUÊTES LECTURE SUPABASE ---
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

def charger_commandes():
    conn = get_db_connection()
    cmds = []
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM commandes ORDER BY id DESC;")
            cmds = cur.fetchall()
        conn.close()
    return cmds

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
        "menu_bebe": "👶 Bébé",
        "menu_enfants": "🧒 Enfants",
        "menu_femmes": "👗 Femmes",
        "menu_hommes": "👔 Hommes",
        "menu_promotions": "🔥 Promos",
        "menu_avis": "⭐ Avis",
        "menu_vendeur": "✨ Vendeur",
        "menu_admin": "⚙️ Admin",
        "menu_panier": f"🛒 Panier ({len(st.session_state.panier)})",
        "sub_vetements": "👗 Vêtements",
        "sub_chaussures": "👟 Chaussures",
        "sub_tissus": "🧵 Tissus",
        "sub_accessoires": "👜 Accessoires",
        "promo_titre": "🔥 Espace Promos",
        "promo_desc": "Profitez de nos prix réduits sur une sélection de pièces magnifiques.",
        "vide_cat": "Aucun article disponible actuellement dans ce rayon",
        "vide_promo": "Aucun produit en promo pour le moment.",
        "sans_photo": "📷 Pas de visuel",
        "btn_ajouter": "Ajouter au Panier",
        "succes_ajout": "ajouté au panier !",
        "vendeur_titre": "✨ Espace Vendeur & Gestion Boutique",
        "vendeur_desc": "Gérez vos articles et suivez l'état des commandes de vos clients en direct.",
        "nom_article": "Nom du produit (ex: Ensemble Bébé, Robe Fille...)",
        "desc_article": "Description & Détails (Tailles disponibles, couleurs, matières...)",
        "prix_article": "Prix standard (en FCFA)",
        "est_promo": "Placer cet article en Promo ?",
        "taux_promo": "Pourcentage de remise (%)",
        "cat_choix": "Choisir le public cible",
        "sub_choix": "Choisir le type d'article",
        "btn_publier": "Mettre en ligne",
        "err_nom": "Veuillez entrer un nom d'article valide.",
        "succes_publi": "Succès ! Votre création est enregistrée.",
        "panier_titre": "🛒 Mon Panier d'Achat VIP",
        "panier_vide": "Votre panier est vide.",
        "btn_retirer": "Retirer",
        "total_depenses": "Total des Achats :",
        "btn_valider": "Commander sur WhatsApp",
        "succes_commande": "🎉 Commande enregistrée ! Cliquez ci-dessous pour l'envoyer sur WhatsApp.",
        "recherche": "🔎 Rechercher..."
    },
    "WOLOF": {
        "titre_app": f"👑 {infos_boutique['nom_boutique']}",
        "sous_titre_app": "Tar, rafet ak taru yeere ak simis yi njabot gi yepp.",
        "menu_bebe": "👶 Liir yi",
        "menu_enfants": "🧒 Xale yi",
        "menu_femmes": "👗 Jigéen yi",
        "menu_hommes": "👔 Góor yi",
        "menu_promotions": "🔥 Promos",
        "menu_avis": "⭐ Xalaat",
        "menu_vendeur": "✨ Jaaykat",
        "menu_admin": "⚙️ Boroom",
        "menu_panier": f"🛒 Saku ({len(st.session_state.panier)})",
        "sub_vetements": "👗 Yeere yi",
        "sub_chaussures": "👟 Dall yi",
        "sub_tissus": "🧵 Tissu yi",
        "sub_accessoires": "👜 Bagas yi",
        "promo_titre": "🔥 Wàññi Njeeg (Promos)",
        "promo_desc": "Jëfandikool sunu njeeg yi wàññiku ngir jënd lu rafet !",
        "vide_cat": "Amagul benn bagas léegi ci fi",
        "vide_promo": "Amagul benn bagas bu wàññiku njeeg bi léegi.",
        "sans_photo": "📷 Amul nataal",
        "btn_ajouter": "Yobbal ci saku",
        "succes_ajout": "dugg na ci saku gi !",
        "vendeur_titre": "✨ Palu Jaaykat bi - Maman Dogo Fashion Store",
        "vendeur_desc": "Bindal fisii ngir feenalaat sa bagas ci lëlu jaay gi.",
        "nom_article": "Turu bagas bi (souba: Yeere liir, Robe xale...)",
        "desc_article": "Misalin bagas bi (Taail yi am, melokaan...)",
        "prix_article": "Njeeg bu njëkk bi (ci FCFA)",
        "est_promo": "Ndax daṅa bëgg wàññi njeeg bi (Promo) ?",
        "taux_promo": "Turu wàññi gi (ci %)",
        "cat_choix": "Tannal ñimuy jaay (Bébé, Femmes...)",
        "sub_choix": "Tannal mbolloom bagas bi (Yeere, Dall...)",
        "btn_publier": "Feenale bagas bi",
        "err_nom": "Diisaleel turu bagas bu dëggu.",
        "succes_publi": "Mbegte ! Sa bagas dugg na ci Supabase.",
        "panier_titre": "🛒 Sa Saku Jënd VIP - Maman Dogo",
        "panier_vide": "Sa saku jënd feesul.",
        "btn_retirer": "Dindi",
        "total_depenses": "Mbolloog xalis bi :",
        "btn_valider": "Yöbbal ci WhatsApp",
        "succes_commande": "🎉 Jënd gi pare na !",
        "recherche": "🔎 Seetbal..."
    }
}

# --- AFFICHAGE DU LOGO A.JPEG DANS LE CADRE XXL ---
if os.path.exists("a.jpeg"):
    with open("a.jpeg", "rb") as f:
        logo_bytes = f.read()
    logo_base64 = base64.b64encode(logo_bytes).decode()
    st.markdown(f"""
        <div class="logo-xxl-container">
            <div class="logo-xxl-frame">
                <div class="logo-xxl-inner">
                    <img src="data:image/jpeg;base64,{logo_base64}" alt="Logo Maman Dogo">
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div style="text-align: center; margin-bottom: 12px;">
            <span style="background: linear-gradient(135deg, #d4af37, #e91e63); color: white; padding: 8px 20px; border-radius: 16px; font-weight: bold; font-size: 1.05rem; box-shadow: 0 4px 12px rgba(233,30,99,0.3);">👑 MAMAN DOGO FASHION STORE 👑</span>
        </div>
    """, unsafe_allow_html=True)

# --- ENTÊTE PRINCIPAL & CHOIX DE LA LANGUE ---
col_head_title, col_head_lang = st.columns([3, 1])

with col_head_lang:
    langue = st.selectbox("🌐 Langue :", ["Français", "Wolof"], label_visibility="collapsed")
    lang_code = "FR" if langue == "Français" else "WOLOF"
    t = TRADUCTIONS[lang_code]

st.markdown(f'<h1 class="brand-title">{t["titre_app"]}</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="brand-subtitle">{t["sous_titre_app"]}</p>', unsafe_allow_html=True)

# --- BARRE DE NAVIGATION HORIZONTALE EN HAUT DE PAGE ---
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

choix_menu = st.radio("Navigation", menu_options, horizontal=True, label_visibility="collapsed")

st.markdown("---")

# FONCTION D'AFFICHAGE DES RAYONS
def afficher_rayon(cat_courante):
    recherche = st.text_input(t["recherche"], placeholder="Rechercher...")
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
                cols = st.columns(3)
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
                            if produit.get("description"):
                                st.markdown(f'<div class="product-desc">📝 {produit["description"]}</div>', unsafe_allow_html=True)
                            st.markdown(f'<span class="price-old">{produit["prix_origine"]:,} FCFA</span><span class="price-new">{produit["prix_final"]:,} FCFA</span>', unsafe_allow_html=True)
                        else:
                            st.markdown(f"### {produit['nom']}")
                            if produit.get("description"):
                                st.markdown(f'<div class="product-desc">📝 {produit["description"]}</div>', unsafe_allow_html=True)
                            st.markdown(f'<span class="price-new">{produit["prix_final"]:,} FCFA</span>', unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        btn_key = f"add_{cat_courante}_{sous_cat_courante}_{produit['id']}"
                        if st.button(t["btn_ajouter"], key=btn_key, use_container_width=True):
                            st.session_state.panier.append(produit)
                            st.success(f"'{produit['nom']}' {t['succes_ajout']}")
                            st.rerun()
                        
                        st.markdown('</div>', unsafe_allow_html=True)

# FONCTION DE GESTION ET MODIFICATION DU CATALOGUE
def afficher_gestion_catalogue():
    prods = charger_produits()
    if not prods:
        st.info("Aucun article disponible dans Supabase.")
    else:
        for idx, prod in enumerate(prods):
            with st.container():
                c1, c2, c3, c4, c5 = st.columns([1, 2, 2, 1, 1])
                with c1:
                    if prod.get("image_url"):
                        st.image(prod["image_url"], width=50)
                    else:
                        st.write("📷")
                with c2:
                    st.write(f"**{prod['nom']}** ({prod['categorie']} > {prod['sous_categorie']})")
                    if prod.get("description"):
                        st.caption(f"📝 {prod['description']}")
                with c3:
                    st.write(f"{prod['prix_final']:,} FCFA")
                with c4:
                    btn_edit_key = f"edit_btn_{prod['id']}"
                    editer_clique = st.button("✏️ Modifier", key=btn_edit_key)
                with c5:
                    if st.button("🗑️ Suppr", key=f"del_spb_{prod['id']}"):
                        conn = get_db_connection()
                        if conn:
                            with conn.cursor() as cur:
                                cur.execute("DELETE FROM produits WHERE id = %s;", (prod['id'],))
                                conn.commit()
                            conn.close()
                        st.success("Article supprimé !")
                        st.rerun()

                # Formulaire de modification dynamique si le bouton Modifier est activé pour ce produit
                if f"edition_active_{prod['id']}" not in st.session_state:
                    st.session_state[f"edition_active_{prod['id']}"] = False

                if editer_clique:
                    st.session_state[f"edition_active_{prod['id']}"] = not st.session_state[f"edition_active_{prod['id']}"]
                    st.rerun()

                if st.session_state.get(f"edition_active_{prod['id']}", False):
                    with st.form(f"form_edit_prod_{prod['id']}"):
                        st.markdown(f"#### ✏️ Modification de : {prod['nom']}")
                        nouveau_nom = st.text_input("Nom du produit", value=prod["nom"])
                        nouvelle_desc = st.text_area("Description & Détails", value=prod.get("description", ""))
                        nouveau_prix = st.number_input("Prix standard (FCFA)", min_value=100, step=500, value=prod["prix_origine"])
                        
                        est_promo_edit = st.checkbox("Mettre en Promo ?", value=prod.get("en_promo", False))
                        taux_promo_edit = st.slider("Remise (%)", min_value=5, max_value=70, value=prod.get("reduction", 15), step=5 if est_promo_edit else 15)
                        
                        cats_dispos = ["Bébé", "Enfants", "Femmes", "Hommes"]
                        subs_dispos = ["Vêtements", "Chaussures", "Tissus", "Accessoires"]
                        
                        cat_edit = st.selectbox("Catégorie", cats_dispos, index=cats_dispos.index(prod["categorie"]) if prod["categorie"] in cats_dispos else 0)
                        sub_edit = st.selectbox("Sous-catégorie", subs_dispos, index=subs_dispos.index(prod["sous_categorie"]) if prod["sous_categorie"] in subs_dispos else 0)
                        
                        new_img_file = st.file_uploader("Nouvelle image (Optionnel)", type=["jpg", "png", "jpeg"], key=f"img_up_{prod['id']}")
                        new_img_url = st.text_input("Ou URL image web", value=prod.get("image_url", "") if not str(prod.get("image_url", "")).startswith("data:") else "")

                        valider_modif = st.form_submit_button("💾 Enregistrer les modifications", use_container_width=True)

                        if valider_modif:
                            prix_fin = int(nouveau_prix * (1 - taux_promo_edit / 100)) if est_promo_edit else nouveau_prix
                            img_finale = encoder_image_base64(new_img_file) if new_img_file is not None else (new_img_url.strip() if new_img_url.strip() else prod.get("image_url"))

                            conn = get_db_connection()
                            if conn:
                                with conn.cursor() as cur:
                                    cur.execute("""
                                        UPDATE produits 
                                        SET nom = %s, categorie = %s, sous_categorie = %s, prix_origine = %s, prix_final = %s, en_promo = %s, reduction = %s, description = %s, image_url = %s
                                        WHERE id = %s;
                                    """, (nouveau_nom.strip(), cat_edit, sub_edit, nouveau_prix, prix_fin, est_promo_edit, taux_promo_edit, nouvelle_desc.strip(), img_finale, prod['id']))
                                    conn.commit()
                                conn.close()
                            
                            st.session_state[f"edition_active_{prod['id']}"] = False
                            st.success("Modifications enregistrées avec succès !")
                            st.rerun()

            st.markdown("---")

# FONCTION D'AFFICHAGE & GESTION DES COMMANDES (POUR LE VENDEUR)
def afficher_gestion_commandes():
    cmds = charger_commandes()
    if not cmds:
        st.info("Aucune commande n'a été passée pour le moment.")
    else:
        statuts_dispos = ["Toutes", "En attente", "En cours de livraison", "Livrée", "Annulée"]
        filtre_statut = st.selectbox("🎯 Filtrer par état :", statuts_dispos)
        
        if filtre_statut != "Toutes":
            cmds = [c for c in cmds if c["statut"] == filtre_statut]

        st.caption(f"Total : {len(cmds)} commande(s)")

        for cmd in cmds:
            badge_color = "#ff9800" if cmd["statut"] == "En attente" else ("#2196F3" if cmd["statut"] == "En cours de livraison" else ("#4CAF50" if cmd["statut"] == "Livrée" else "#f44336"))
            
            with st.container():
                st.markdown(f"""
                <div class="order-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:5px;">
                        <h4 style="margin:0; color:#880e4f;">📦 Commande #{cmd['id']} — {cmd['nom_client']}</h4>
                        <span style="background-color:{badge_color}; color:white; padding:3px 10px; border-radius:10px; font-weight:bold; font-size:0.8rem;">{cmd['statut']}</span>
                    </div>
                    <p style="margin:5px 0; color:#555; font-size:0.85rem;">📅 {cmd['date_commande']} | 📞 {cmd['telephone']} | 📍 {cmd['adresse']}</p>
                    <div style="background-color:#fff5f7; padding:8px; border-radius:8px; margin:6px 0;">
                        <b>🛍️ Articles :</b><br>
                        <small>{cmd['details_articles'].replace(chr(10), '<br>')}</small>
                    </div>
                    <h4 style="color:#e91e63; margin-top:4px;">💰 Total : {cmd['montant_total']:,} FCFA</h4>
                </div>
                """, unsafe_allow_html=True)

                col_stat, col_wa, col_del = st.columns([2, 2, 1])
                
                with col_stat:
                    nouveau_statut = st.selectbox(
                        "État :", 
                        ["En attente", "En cours de livraison", "Livrée", "Annulée"], 
                        index=["En attente", "En cours de livraison", "Livrée", "Annulée"].index(cmd["statut"]) if cmd["statut"] in ["En attente", "En cours de livraison", "Livrée", "Annulée"] else 0,
                        key=f"status_select_{cmd['id']}"
                    )
                    if nouveau_statut != cmd["statut"]:
                        conn = get_db_connection()
                        if conn:
                            with conn.cursor() as cur:
                                cur.execute("UPDATE commandes SET statut = %s WHERE id = %s;", (nouveau_statut, cmd['id']))
                                conn.commit()
                            conn.close()
                        st.success("Mis à jour !")
                        st.rerun()

                with col_wa:
                    tel_clean = cmd['telephone'].replace("+", "").replace(" ", "").replace("-", "")
                    msg_relance = urllib.parse.quote(f"Bonjour {cmd['nom_client']}, concernant votre commande #{cmd['id']} chez Maman Dogo Fashion Store (Statut: {nouveau_statut})...")
                    lien_wa_client = f"https://wa.me/{tel_clean}?text={msg_relance}"
                    st.markdown(f'<a href="{lien_wa_client}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366; color:white; border:none; border-radius:10px; padding:10px; width:100%; font-weight:bold; cursor:pointer;">📲 WhatsApp</button></a>', unsafe_allow_html=True)

                with col_del:
                    if st.button("🗑️", key=f"del_cmd_{cmd['id']}"):
                        conn = get_db_connection()
                        if conn:
                            with conn.cursor() as cur:
                                cur.execute("DELETE FROM commandes WHERE id = %s;", (cmd['id'],))
                                conn.commit()
                            conn.close()
                        st.success("Supprimée !")
                        st.rerun()

            st.markdown("---")

# --- PAGES PRINCIPALES ---
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
        cols = st.columns(3)
        for index, produit in enumerate(articles_en_promo):
            with cols[index % 3]:
                st.markdown('<div class="product-card">', unsafe_allow_html=True)
                if produit.get("image_url"):
                    st.image(produit["image_url"], use_container_width=True)
                st.markdown(f'<span class="promo-badge">PROMO -{produit["reduction"]}%</span>', unsafe_allow_html=True)
                st.markdown(f"### {produit['nom']}")
                if produit.get("description"):
                    st.markdown(f'<div class="product-desc">📝 {produit["description"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<span class="price-old">{produit["prix_origine"]:,} FCFA</span><span class="price-new">{produit["prix_final"]:,} FCFA</span>', unsafe_allow_html=True)
                
                if st.button(t["btn_ajouter"], key=f"promo_add_{produit['id']}", use_container_width=True):
                    st.session_state.panier.append(produit)
                    st.success(f"'{produit['nom']}' {t['succes_ajout']}")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

elif choix_menu == t["menu_avis"]:
    st.subheader("⭐ Avis & Retours Expérience Clients")
    col_form, col_liste = st.columns(2)

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
        st.markdown("### 💬 Avis Récents")
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
                    <small style="color:#777;">Produit : {avis['produit']} | {avis['date']}</small>
                    <p style="margin-top:6px; color:#333;">"{avis['commentaire']}"</p>
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
        tab_cmds, tab_publi, tab_mes_prods = st.tabs(["📋 Commandes", "➕ Publier", "📦 En Ligne"])

        with tab_cmds:
            afficher_gestion_commandes()

        with tab_publi:
            with st.form("form_vendeur", clear_on_submit=True):
                nom_produit = st.text_input(t["nom_article"])
                description_produit = st.text_area(t["desc_article"], placeholder="Ex: Tailles disponibles (S, M, L), 100% Coton, Couleurs: Rose, Blanc...")
                prix_origine = st.number_input(t["prix_article"], min_value=100, step=500, value=10000)
                
                appliquer_promo = st.checkbox(t["est_promo"])
                taux_reduction = st.slider(t["taux_promo"], min_value=5, max_value=70, value=15, step=5) if appliquer_promo else 0
                
                dict_categories = {"👶 Bébé": "Bébé", "🧒 Enfants": "Enfants", "👗 Femmes": "Femmes", "👔 Hommes": "Hommes"}
                dict_sous_categories = {t["sub_vetements"]: "Vêtements", t["sub_chaussures"]: "Chaussures", t["sub_tissus"]: "Tissus", t["sub_accessoires"]: "Accessoires"}

                cat_choisie_label = st.selectbox(t["cat_choix"], list(dict_categories.keys()))
                sub_choisie_label = st.selectbox(t["sub_choix"], list(dict_sous_categories.keys()))
                
                categorie_cible = dict_categories[cat_choisie_label]
                sous_categorie_cible = dict_sous_categories[sub_choisie_label]
                
                photo_fichier = st.file_uploader("📷 Photo du produit (PNG, JPG)", type=["jpg", "png", "jpeg"])
                image_url_input = st.text_input("🔗 Ou lien image web (Optionnel)")
                
                valider_ajout = st.form_submit_button(t["btn_publier"], use_container_width=True)

                if valider_ajout:
                    if not nom_produit.strip():
                        st.error(t["err_nom"])
                    else:
                        prix_final = int(prix_origine * (1 - taux_reduction / 100)) if appliquer_promo else prix_origine
                        
                        if photo_fichier is not None:
                            final_image_url = encoder_image_base64(photo_fichier)
                        else:
                            final_image_url = image_url_input.strip()

                        conn = get_db_connection()
                        if conn:
                            with conn.cursor() as cur:
                                cur.execute("""
                                    INSERT INTO produits (nom, categorie, sous_categorie, prix_origine, prix_final, en_promo, reduction, description, image_url)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                                """, (nom_produit.strip(), categorie_cible, sous_categorie_cible, prix_origine, prix_final, appliquer_promo, taux_reduction, description_produit.strip(), final_image_url))
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
        tab_infos, tab_produits, tab_avis_mod, tab_stats = st.tabs(["📝 Boutique", "📦 Catalogue", "💬 Avis", "📊 Stats"])

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
                        if st.button("🗑️", key=f"del_av_{avis['id']}"):
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
            col_s1, col_s2, col_s3 = st.columns(3)
            col_s1.metric("Articles", len(prods))
            col_s2.metric("Valeur Stock", f"{valeur_stock:,} FCFA")
            col_s3.metric("Avis", len(charger_avis()))

elif choix_menu == t["menu_panier"]:
    st.subheader(t["panier_titre"])

    if not st.session_state.panier:
        st.info(t["panier_vide"])
    else:
        for idx, item in enumerate(st.session_state.panier):
            col_img, col_desc, col_prix, col_action = st.columns([1, 2, 2, 1])
            with col_img:
                if item.get("image_url"):
                    st.image(item["image_url"], width=60)
                else:
                    st.write("📦")
            with col_desc:
                st.markdown(f"**{item['nom']}**")
                if item.get("description"):
                    st.caption(f"📝 {item['description']}")
            with col_prix:
                st.markdown(f'**{item["prix_final"]:,} FCFA**')
            with col_action:
                if st.button("❌", key=f"suppr_panier_{idx}"):
                    st.session_state.panier.pop(idx)
                    st.rerun()
            st.markdown("---")

        total_general = sum(item['prix_final'] for item in st.session_state.panier)
        st.markdown(f"### {t['total_depenses']} <span style='color:#e91e63; font-size:1.6rem; font-weight:bold;'>{total_general:,} FCFA</span>", unsafe_allow_html=True)

        with st.form("form_commande_whatsapp"):
            nom_client = st.text_input("Prénom & Nom *")
            tel_client = st.text_input("Téléphone *")
            adresse_client = st.text_input("Adresse de livraison *")
            valider_cmd = st.form_submit_button(t["btn_valider"], use_container_width=True)

        if valider_cmd:
            if not nom_client.strip() or not tel_client.strip() or not adresse_client.strip():
                st.error("Veuillez remplir toutes vos informations de livraison.")
            else:
                lignes_commande = [f"{i+1}. {item['nom']} (Détails: {item.get('description', 'N/A')}) - {item['prix_final']:,} FCFA" for i, item in enumerate(st.session_state.panier)]
                details_str = "\n".join(lignes_commande)
                date_cmd = datetime.now().strftime("%d/%m/%Y %H:%M")

                conn = get_db_connection()
                if conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            INSERT INTO commandes (nom_client, telephone, adresse, details_articles, montant_total, statut, date_commande)
                            VALUES (%s, %s, %s, %s, %s, 'En attente', %s);
                        """, (nom_client.strip(), tel_client.strip(), adresse_client.strip(), details_str, total_general, date_cmd))
                        conn.commit()
                    conn.close()

                msg_whatsapp = (
                    f"👑 *COMMANDE - {infos_boutique['nom_boutique']}*\n\n"
                    f"👤 *Client* : {nom_client.strip()}\n"
                    f"📞 *Tél* : {tel_client.strip()}\n"
                    f"📍 *Livraison* : {adresse_client.strip()}\n\n"
                    f"🛍️ *PANIER* :\n" + details_str + f"\n\n"
                    f"💰 *TOTAL* : *{total_general:,} FCFA*"
                )
                lien_whatsapp = f"https://wa.me/{infos_boutique['telephone']}?text={urllib.parse.quote(msg_whatsapp)}"
                st.balloons()
                st.success(t["succes_commande"])
                st.markdown(f'<a href="{lien_whatsapp}" target="_blank" class="whatsapp-btn">📲 Envoyer ma commande sur WhatsApp</a>', unsafe_allow_html=True)

# --- PIED DE PAGE (FOOTER) DE VALORISATION ---
st.markdown(f"""
<div class="footer-container">
    <div class="footer-features">
        <div class="feature-box">
            <h4>✨ Qualité Supérieure</h4>
            <p>Sélection rigoureuse des plus beaux articles.</p>
        </div>
        <div class="feature-box">
            <h4>🚚 Livraison Rapide</h4>
            <p>À Dakar et dans toutes les régions du Sénégal.</p>
        </div>
        <div class="feature-box">
            <h4>💬 Service Client</h4>
            <p>Assistance rapide et directe via WhatsApp.</p>
        </div>
        <div class="feature-box">
            <h4>🔒 Paiement Sécurisé</h4>
            <p>Paiement à la livraison en toute confiance.</p>
        </div>
    </div>
    <div class="footer-bottom">
        <p>👑 <strong>{infos_boutique['nom_boutique']}</strong> — Élégance & Style</p>
        <p>📍 {infos_boutique['adresse']} | 📞 WhatsApp : <a href="https://wa.me/{infos_boutique['telephone']}" target="_blank">+{infos_boutique['telephone']}</a></p>
        <p style="margin-top:8px; font-size:0.75rem; color:rgba(248,187,208,0.6);">© {datetime.now().year} Tous droits réservés.</p>
    </div>
</div>
""", unsafe_allow_html=True)
