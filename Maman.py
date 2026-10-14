import streamlit as st
import urllib.parse
from datetime import datetime
import base64
import os
import io
from PIL import Image

# Importation sécurisée de psycopg2 et du pool de connexions
try:
    import psycopg2
    from psycopg2.pool import SimpleConnectionPool
    from psycopg2.extras import RealDictCursor
except ModuleNotFoundError:
    st.error("❌ Le module 'psycopg2' ou 'Pillow' est manquant. Veuillez installer 'psycopg2-binary' et 'Pillow'.")
    st.stop()

# Configuration de la page
st.set_page_config(
    page_title="Deligro by Codou Senghor", 
    page_icon="🍲", 
    layout="wide"
)

# Numéro par défaut pour WhatsApp
TEL_PAR_DEFAUT = "221774729680"

# --- RÉCUPÉRATION SÉCURISÉE DES SECRETS (SUPABASE & BOUTIQUE) ---
try:
    DB_HOST = st.secrets["postgres"]["host"]
    DB_PORT = st.secrets["postgres"]["port"]
    DB_NAME = st.secrets["postgres"]["dbname"]
    DB_USER = st.secrets["postgres"]["user"]
    DB_PASS = st.secrets["postgres"]["password"]
    
    BOUTIQUE_TEL = st.secrets.get("boutique", {}).get("telephone", TEL_PAR_DEFAUT)
except Exception:
    DB_HOST = "aws-0-eu-west-1.pooler.supabase.com"
    DB_PORT = "5432"
    DB_NAME = "postgres"
    DB_USER = "postgres.wqmxbbjzaytwwsanlckq"
    DB_PASS = "u3eS&R-e27cYmL&"
    BOUTIQUE_TEL = TEL_PAR_DEFAUT

# --- POOL DE CONNEXIONS OPTIMISÉ ---
@st.cache_resource
def get_db_pool():
    return SimpleConnectionPool(
        minconn=1,
        maxconn=10,
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def get_db_connection():
    try:
        pool = get_db_pool()
        return pool.getconn()
    except Exception as e:
        st.error(f"Erreur de connexion PostgreSQL : {e}")
        return None

def release_db_connection(conn):
    if conn:
        try:
            pool = get_db_pool()
            pool.putconn(conn)
        except Exception:
            pass

# --- ENCODAGE IMAGE SANS DECOUPAGE ET AVEC HAUTE QUALITÉ ---
def encoder_image_base64_optimisee(fichier_image, max_size=(1200, 1200)):
    if fichier_image is not None:
        try:
            image = Image.open(fichier_image)
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=100, optimize=True)
            base64_str = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/jpeg;base64,{base64_str}"
        except Exception:
            return ""
    return ""

# --- INITIALISATION AUTOMATIQUE DE LA STRUCTURE DB ---
def init_db_automatique():
    conn = get_db_connection()
    if conn:
        try:
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
                        publie BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                cur.execute("ALTER TABLE avis_clients ADD COLUMN IF NOT EXISTS publie BOOLEAN DEFAULT FALSE;")
                cur.execute("ALTER TABLE produits ADD COLUMN IF NOT EXISTS description TEXT;")

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
                    VALUES (1, 'Deligro by Codou Senghor', 'Délicieux plats fait maison, jus locaux et spécialités gourmandes préparés avec amour.', %s, 'Dakar, Sénégal')
                    ON CONFLICT (id) DO UPDATE SET 
                        nom_boutique = EXCLUDED.nom_boutique,
                        telephone = EXCLUDED.telephone;
                """, (BOUTIQUE_TEL,))
                conn.commit()
        finally:
            release_db_connection(conn)

init_db_automatique()

# --- REQUÊTES AVEC MISE EN CACHE ---
@st.cache_data(ttl=60)
def charger_infos_boutique():
    conn = get_db_connection()
    res = None
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM infos_boutique WHERE id = 1;")
                res = cur.fetchone()
        finally:
            release_db_connection(conn)
    if res:
        return res
    return {
        "nom_boutique": "Deligro by Codou Senghor",
        "description": "Délicieux plats fait maison, jus locaux et spécialités gourmandes préparés avec amour.",
        "telephone": BOUTIQUE_TEL,
        "adresse": "Dakar, Sénégal"
    }

@st.cache_data(ttl=30)
def charger_produits():
    conn = get_db_connection()
    prods = []
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM produits ORDER BY id DESC;")
                prods = cur.fetchall()
        finally:
            release_db_connection(conn)
    return prods

@st.cache_data(ttl=30)
def charger_avis_publies():
    conn = get_db_connection()
    avis = []
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM avis_clients WHERE publie = TRUE ORDER BY id DESC;")
                avis = cur.fetchall()
        finally:
            release_db_connection(conn)
    return avis

def charger_tous_les_avis():
    conn = get_db_connection()
    avis = []
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM avis_clients ORDER BY id DESC;")
                avis = cur.fetchall()
        finally:
            release_db_connection(conn)
    return avis

def charger_commandes():
    conn = get_db_connection()
    cmds = []
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM commandes ORDER BY id DESC;")
                cmds = cur.fetchall()
        finally:
            release_db_connection(conn)
    return cmds

# --- STYLES CSS ---
st.markdown("""
<style>
    header[data-testid="stHeader"] { display: none !important; }
    footer { visibility: hidden; }

    .stApp {
        background: linear-gradient(135deg, #fff8f0 0%, #ffeedb 50%, #ffd8b1 100%);
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
        background: linear-gradient(135deg, #d4af37 0%, #e65100 50%, #bf360c 100%);
        padding: 4px;
        border-radius: 24px;
        box-shadow: 0 8px 25px rgba(230, 81, 0, 0.25);
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
        color: #e65100;
        text-align: center;
        margin-bottom: 2px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        word-break: break-word;
    }
    
    .brand-author {
        font-size: clamp(1.8rem, 4.5vw, 3.2rem) !important;
        font-weight: 900;
        background: -webkit-linear-gradient(45deg, #d4af37, #e65100, #c2185b, #d4af37);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 2px 10px rgba(212, 175, 55, 0.3);
        letter-spacing: 1px;
        text-decoration: underline;
        text-decoration-color: #d4af37;
    }

    .brand-subtitle {
        text-align: center;
        color: #bf360c;
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
        background-color: #3e2723;
        padding: 8px 10px;
        border-radius: 16px;
        box-shadow: 0 4px 15px rgba(62, 39, 35, 0.2);
        margin-bottom: 20px;
        width: 100%;
    }

    div[data-testid="stRadio"] label {
        background-color: rgba(255, 255, 255, 0.08) !important;
        color: #ffe0b2 !important;
        padding: 6px 12px !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 224, 178, 0.2) !important;
        font-size: clamp(0.8rem, 1.5vw, 0.95rem) !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
        flex: 1 1 auto;
        text-align: center;
    }

    div[data-testid="stRadio"] label:hover {
        background-color: #e65100 !important;
        color: #ffffff !important;
    }

    .product-card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 12px;
        box-shadow: 0 6px 15px rgba(230, 81, 0, 0.08);
        border: 1px solid #ffe0b2;
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        margin-bottom: 15px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .product-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(230, 81, 0, 0.15);
    }

    .product-img-wrapper {
        width: 100%;
        height: 250px;
        border-radius: 12px;
        overflow: hidden;
        margin-bottom: 10px;
        background-color: #fff8f0;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 6px;
        border: 1px dashed #ffe0b2;
    }

    .product-img-wrapper img {
        max-width: 100%;
        max-height: 100%;
        width: auto;
        height: auto;
        object-fit: contain;
        transition: transform 0.3s ease;
    }

    .product-img-wrapper img:hover {
        transform: scale(1.03);
    }

    .product-desc {
        font-size: 0.85rem;
        color: #555;
        margin: 6px 0;
        background-color: #fff8f0;
        padding: 6px;
        border-radius: 8px;
    }

    .review-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 12px;
        border-left: 4px solid #e65100;
        margin-bottom: 10px;
        box-shadow: 0 3px 10px rgba(230, 81, 0, 0.05);
    }

    .order-card {
        background-color: #ffffff;
        border-radius: 14px;
        padding: 14px;
        border: 1px solid #ffe0b2;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(230, 81, 0, 0.06);
    }

    .promo-badge {
        background: linear-gradient(45deg, #e65100, #ff9800);
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
        color: #b71c1c;
        font-size: 0.85rem;
        margin-right: 4px;
    }
    
    .price-new {
        color: #bf360c;
        font-weight: 800;
        font-size: 1.1rem;
    }

    .stButton>button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        background-color: #e65100 !important;
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
</style>
""", unsafe_allow_html=True)

# --- INITIALISATION SESSION ---
if "panier" not in st.session_state:
    st.session_state.panier = []

if "admin_connecte" not in st.session_state:
    st.session_state.admin_connecte = False

infos_boutique = charger_infos_boutique()

# --- STRUCTURE DE RESTAURATION (CATEGORIES ET SOUS-CATEGORIES) ---
STRUCTURE_FOOD = {
    "Plats Chauds": ["Thiéboudienne / Rice", "Yassa / Mafé", "Grillades & Dibi", "Pastels & Fast-Food"],
    "Boissons & Jus": ["Jus Locaux (Bissap/Bouye)", "Sodas & Eaux", "Smoothies & Milkshakes", "Café & Thé"],
    "Desserts & Douceurs": ["Thiakry & Lait caillé", "Gâteaux & Tartes", "Glaces & Coupes", "Beignets sucrés"],
    "Packs & Menus": ["Menu Familial", "Formule Express Midi", "Pack Événement VIP", "Buffet sur mesure"]
}

CATEGORIES_FOOD = list(STRUCTURE_FOOD.keys())

# --- TRADUCTIONS ---
TRADUCTIONS = {
    "FR": {
        "sous_titre_app": infos_boutique['description'],
        "menu_plats": "🍛 Plats Chauds",
        "menu_boissons": "🥤 Boissons & Jus",
        "menu_desserts": "🍰 Desserts",
        "menu_packs": "🍱 Menus & Packs",
        "menu_promotions": "🔥 Offres Spéciales",
        "menu_avis": "⭐ Avis Gourmands",
        "menu_vendeur": "✨ Espace Cuisine",
        "menu_admin": "⚙️ Admin",
        "menu_panier": f"🛒 Ma Commande ({len(st.session_state.panier)})",
        "promo_titre": "🔥 Offres & Menus Spéciaux",
        "vide_cat": "Aucun plat disponible actuellement dans cette rubrique",
        "vide_promo": "Aucune promo gourmande pour le moment.",
        "sans_photo": "📷 Photo du plat à venir",
        "btn_ajouter": "Ajouter au Panier",
        "succes_ajout": "ajouté à votre commande !",
        "nom_article": "Nom du plat / boisson (ex: Thieboudienne Penda Mbaye, Jus de Bouye...)",
        "desc_article": "Ingrédients & Détails (Spécifications, accompagnements, portions...)",
        "prix_article": "Prix unitaire (en FCFA)",
        "est_promo": "Placer en Offre Spéciale / Promo ?",
        "taux_promo": "Pourcentage de remise (%)",
        "cat_choix": "Catégorie Principale",
        "sub_choix": "Sous-catégorie / Spécialité",
        "btn_publier": "Mettre au Menu",
        "succes_publi": "Succès ! Votre plat est au menu.",
        "panier_titre": "🛒 Ma Commande Gourmande VIP",
        "panier_vide": "Votre panier de commande est vide.",
        "btn_valider": "Commander sur WhatsApp",
        "succes_commande": "🎉 Commande enregistrée ! Préparation imminente.",
        "recherche": "🔎 Rechercher un plat, une boisson..."
    },
    "WOLOF": {
        "sous_titre_app": "Lék bu neex, reer ak añ bu saddu, sangara ak jus neex yi.",
        "menu_plats": "🍛 Ceeb ak Yassa",
        "menu_boissons": "🥤 Jus ak Nann yi",
        "menu_desserts": "🍰 Thiakry ak Neexal",
        "menu_packs": "🍱 Mbolloog Lék",
        "menu_promotions": "🔥 Wàññi Njeeg",
        "menu_avis": "⭐ Xalaatu Lékkat yi",
        "menu_vendeur": "✨ Wañ bi (Cuisine)",
        "menu_admin": "⚙️ Boroom Wañ bi",
        "menu_panier": f"🛒 Sa Mbollo ({len(st.session_state.panier)})",
        "promo_titre": "🔥 Wàññi Njeeg ci Lék yi",
        "vide_cat": "Amagul benn lék léegi fi",
        "vide_promo": "Amul benn wàññi njeeg léegi ci lék yi.",
        "sans_photo": "📷 Nataal bi ngi ñëw",
        "btn_ajouter": "Yobbal ci sa commande",
        "succes_ajout": "dugg na ci sa commande !",
        "nom_article": "Turu lék bi / jus bi...",
        "desc_article": "Lumu am (misal: ceeb, yapp, jën, piment...)",
        "prix_article": "Njeeg bi (ci FCFA)",
        "est_promo": "Promo?",
        "taux_promo": "Turu wàññi gi (%)",
        "cat_choix": "Tannal wàllu lék bi",
        "sub_choix": "Tannal mbolloom lék bi",
        "btn_publier": "Duggal ci menu bi",
        "succes_publi": "Mbegte ! Sa lék dugg na ci menu bi.",
        "panier_titre": "🛒 Sa Commande Lék VIP",
        "panier_vide": "Amugul benn lék ci sa panier.",
        "btn_valider": "Yöbbal ci WhatsApp",
        "succes_commande": "🎉 Jënd gi pare na ! Ñungi waajalt sa lék.",
        "recherche": "🔎 Seetbal lék wala jus..."
    }
}

# --- LOGO ---
if os.path.exists("a.jpeg"):
    with open("a.jpeg", "rb") as f:
        logo_bytes = f.read()
    logo_base64 = base64.b64encode(logo_bytes).decode()
    st.markdown(f"""
        <div class="logo-xxl-container">
            <div class="logo-xxl-frame">
                <div class="logo-xxl-inner">
                    <img src="data:image/jpeg;base64,{logo_base64}" alt="Logo Deligro">
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- ENTÊTE & LANGUE ---
col_head_title, col_head_lang = st.columns([3, 1])
with col_head_lang:
    langue = st.selectbox("🌐 Langue :", ["Français", "Wolof"], label_visibility="collapsed")
    lang_code = "FR" if langue == "Français" else "WOLOF"
    t = TRADUCTIONS[lang_code]

st.markdown('<h1 class="brand-title">🍲 DELIGRO <br>by <span class="brand-author">Codou Senghor</span></h1>', unsafe_allow_html=True)
st.markdown(f'<p class="brand-subtitle">{t["sous_titre_app"]}</p>', unsafe_allow_html=True)

menu_options = [
    t["menu_plats"], t["menu_boissons"], t["menu_desserts"], t["menu_packs"],
    t["menu_promotions"], t["menu_avis"], t["menu_vendeur"], t["menu_admin"], t["menu_panier"]
]
choix_menu = st.radio("Navigation", menu_options, horizontal=True, label_visibility="collapsed")
st.markdown("---")

# FONCTION RAYON NOURRITURE
def afficher_rayon_food(cat_courante):
    recherche = st.text_input(t["recherche"], placeholder="Ex: Thieboudienne, Yassa, Jus de Bouye...")
    sous_categories_dispos = STRUCTURE_FOOD.get(cat_courante, [])
    sous_tabs = st.tabs(sous_categories_dispos)

    tous_produits = charger_produits()
    tous_avis = charger_avis_publies()

    for j, tab_sub in enumerate(sous_tabs):
        with tab_sub:
            sous_cat_courante = sous_categories_dispos[j]
            produits_categorie = [p for p in tous_produits if p["categorie"] == cat_courante and p["sous_categorie"] == sous_cat_courante]
            
            if recherche:
                produits_categorie = [p for p in produits_categorie if recherche.lower() in p["nom"].lower() or recherche.lower() in p.get("description", "").lower()]

            if not produits_categorie:
                st.info(f"{t['vide_cat']} '{sous_cat_courante}'.")
            else:
                cols = st.columns(3)
                for index, produit in enumerate(produits_categorie):
                    with cols[index % 3]:
                        st.markdown('<div class="product-card">', unsafe_allow_html=True)
                        
                        if produit.get("image_url"):
                            st.markdown(f'''
                                <div class="product-img-wrapper">
                                    <img src="{produit["image_url"]}" alt="{produit["nom"]}">
                                </div>
                            ''', unsafe_allow_html=True)
                        else:
                            st.markdown(f'''
                                <div class="product-img-wrapper">
                                    <p style="color:#aaa; font-size:0.9rem;">{t["sans_photo"]}</p>
                                </div>
                            ''', unsafe_allow_html=True)
                        
                        avis_article = [a for a in tous_avis if a["produit"] == produit["nom"]]
                        if avis_article:
                            note_moyenne = sum(a["note"] for a in avis_article) / len(avis_article)
                            st.caption(f"⭐ {note_moyenne:.1f}/5 ({len(avis_article)} avis gourmands)")
                        else:
                            st.caption("⭐ Pas encore d'avis sur ce plat")

                        if produit.get("en_promo"):
                            st.markdown(f'<span class="promo-badge">OFFRE SPÉCIALE -{produit["reduction"]}%</span>', unsafe_allow_html=True)
                            st.markdown(f"### {produit['nom']}")
                            if produit.get("description"):
                                st.markdown(f'<div class="product-desc">🍲 {produit["description"]}</div>', unsafe_allow_html=True)
                            st.markdown(f'<span class="price-old">{produit["prix_origine"]:,} FCFA</span><span class="price-new">{produit["prix_final"]:,} FCFA</span>', unsafe_allow_html=True)
                        else:
                            st.markdown(f"### {produit['nom']}")
                            if produit.get("description"):
                                st.markdown(f'<div class="product-desc">🍲 {produit["description"]}</div>', unsafe_allow_html=True)
                            st.markdown(f'<span class="price-new">{produit["prix_final"]:,} FCFA</span>', unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        btn_key = f"add_{cat_courante}_{sous_cat_courante}_{produit['id']}"
                        if st.button(t["btn_ajouter"], key=btn_key, use_container_width=True):
                            st.session_state.panier.append(produit)
                            st.success(f"'{produit['nom']}' {t['succes_ajout']}")
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

# FONCTION GESTION MENU
def afficher_gestion_catalogue():
    prods = charger_produits()
    if not prods:
        st.info("Aucun plat enregistré au menu.")
    else:
        for prod in prods:
            with st.container():
                c1, c2, c3, c4, c5 = st.columns([1, 2, 2, 1, 1])
                with c1:
                    if prod.get("image_url"):
                        st.image(prod["image_url"], width=60)
                    else:
                        st.write("🍲")
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
                            try:
                                with conn.cursor() as cur:
                                    cur.execute("DELETE FROM produits WHERE id = %s;", (prod['id'],))
                                    conn.commit()
                            finally:
                                release_db_connection(conn)
                        charger_produits.clear()
                        st.success("Plat retiré du menu !")
                        st.rerun()

                if f"edition_active_{prod['id']}" not in st.session_state:
                    st.session_state[f"edition_active_{prod['id']}"] = False

                if editer_clique:
                    st.session_state[f"edition_active_{prod['id']}"] = not st.session_state[f"edition_active_{prod['id']}"]
                    st.rerun()

                if st.session_state.get(f"edition_active_{prod['id']}", False):
                    with st.form(f"form_edit_prod_{prod['id']}"):
                        st.markdown(f"#### ✏️ Modification du plat : {prod['nom']}")
                        nouveau_nom = st.text_input("Nom du plat", value=prod["nom"])
                        nouvelle_desc = st.text_area("Ingrédients & Détails", value=prod.get("description", ""))
                        nouveau_prix = st.number_input("Prix unitaire (FCFA)", min_value=100, step=250, value=prod["prix_origine"])
                        est_promo_edit = st.checkbox("Mettre en Offre Spéciale ?", value=prod.get("en_promo", False))
                        taux_promo_edit = st.slider("Remise (%)", min_value=5, max_value=70, value=prod.get("reduction", 15), step=5)
                        
                        cats_dispos = CATEGORIES_FOOD
                        cat_edit = st.selectbox("Catégorie", cats_dispos, index=cats_dispos.index(prod["categorie"]) if prod["categorie"] in cats_dispos else 0)
                        subs_dispos = STRUCTURE_FOOD.get(cat_edit, [])
                        sub_edit = st.selectbox("Sous-catégorie", subs_dispos, index=subs_dispos.index(prod["sous_categorie"]) if prod["sous_categorie"] in subs_dispos else 0)
                        
                        new_img_file = st.file_uploader("Nouvelle photo du plat (Optionnel)", type=["jpg", "png", "jpeg"], key=f"img_up_{prod['id']}")
                        new_img_url = st.text_input("Ou URL image web", value="")

                        valider_modif = st.form_submit_button("💾 Enregistrer les modifications", use_container_width=True)

                        if valider_modif:
                            prix_fin = int(nouveau_prix * (1 - taux_promo_edit / 100)) if est_promo_edit else nouveau_prix
                            img_finale = encoder_image_base64_optimisee(new_img_file) if new_img_file is not None else (new_img_url.strip() if new_img_url.strip() else prod.get("image_url"))

                            conn = get_db_connection()
                            if conn:
                                try:
                                    with conn.cursor() as cur:
                                        cur.execute("""
                                            UPDATE produits 
                                            SET nom = %s, categorie = %s, sous_categorie = %s, prix_origine = %s, prix_final = %s, en_promo = %s, reduction = %s, description = %s, image_url = %s
                                            WHERE id = %s;
                                        """, (nouveau_nom.strip(), cat_edit, sub_edit, nouveau_prix, prix_fin, est_promo_edit, taux_promo_edit, nouvelle_desc.strip(), img_finale, prod['id']))
                                        conn.commit()
                                finally:
                                    release_db_connection(conn)
                            
                            st.session_state[f"edition_active_{prod['id']}"] = False
                            charger_produits.clear()
                            st.success("Modifications enregistrées !")
                            st.rerun()
            st.markdown("---")

# FONCTION COMMANDES
def afficher_gestion_commandes():
    cmds = charger_commandes()
    if not cmds:
        st.info("Aucune commande n'a été passée pour le moment.")
    else:
        statuts_dispos = ["Toutes", "En attente", "En préparation", "En cours de livraison", "Livrée", "Annulée"]
        filtre_statut = st.selectbox("🎯 Filtrer par état de préparation :", statuts_dispos)
        if filtre_statut != "Toutes":
            cmds = [c for c in cmds if c["statut"] == filtre_statut]

        for cmd in cmds:
            badge_color = "#ff9800" if cmd["statut"] == "En attente" else ("#e65100" if cmd["statut"] == "En préparation" else ("#2196F3" if cmd["statut"] == "En cours de livraison" else ("#4CAF50" if cmd["statut"] == "Livrée" else "#f44336")))
            with st.container():
                st.markdown(f"""
                <div class="order-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4 style="margin:0; color:#bf360c;">🍱 Commande #{cmd['id']} — {cmd['nom_client']}</h4>
                        <span style="background-color:{badge_color}; color:white; padding:3px 10px; border-radius:10px; font-weight:bold; font-size:0.8rem;">{cmd['statut']}</span>
                    </div>
                    <p style="margin:5px 0; color:#555; font-size:0.85rem;">📅 {cmd['date_commande']} | 📞 {cmd['telephone']} | 📍 Adresse / Livraison: {cmd['adresse']}</p>
                    <div style="background-color:#fff8f0; padding:8px; border-radius:8px; margin:6px 0;">
                        <b>🍲 Plats / Menus commandés :</b><br><small>{cmd['details_articles'].replace(chr(10), '<br>')}</small>
                    </div>
                    <h4 style="color:#e65100; margin-top:4px;">💰 Total Commande : {cmd['montant_total']:,} FCFA</h4>
                </div>
                """, unsafe_allow_html=True)

                col_stat, col_wa, col_del = st.columns([2, 2, 1])
                with col_stat:
                    nouveau_statut = st.selectbox(
                        "Changer l'état :", ["En attente", "En préparation", "En cours de livraison", "Livrée", "Annulée"], 
                        index=["En attente", "En préparation", "En cours de livraison", "Livrée", "Annulée"].index(cmd["statut"]) if cmd["statut"] in ["En attente", "En préparation", "En cours de livraison", "Livrée", "Annulée"] else 0,
                        key=f"status_select_{cmd['id']}"
                    )
                    if nouveau_statut != cmd["statut"]:
                        conn = get_db_connection()
                        if conn:
                            try:
                                with conn.cursor() as cur:
                                    cur.execute("UPDATE commandes SET statut = %s WHERE id = %s;", (nouveau_statut, cmd['id']))
                                    conn.commit()
                            finally:
                                release_db_connection(conn)
                        st.success("Statut de livraison mis à jour !")
                        st.rerun()
                with col_wa:
                    tel_clean = cmd['telephone'].replace("+", "").replace(" ", "").replace("-", "")
                    msg_relance = urllib.parse.quote(f"Bonjour {cmd['nom_client']}, concernant votre commande gourmande #{cmd['id']}...")
                    lien_wa_client = f"https://wa.me/{tel_clean}?text={msg_relance}"
                    st.markdown(f'<a href="{lien_wa_client}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366; color:white; border-radius:10px; padding:10px; width:100%; font-weight:bold; cursor:pointer;">📲 Contacter Client sur WhatsApp</button></a>', unsafe_allow_html=True)
                with col_del:
                    if st.button("🗑️", key=f"del_cmd_{cmd['id']}"):
                        conn = get_db_connection()
                        if conn:
                            try:
                                with conn.cursor() as cur:
                                    cur.execute("DELETE FROM commandes WHERE id = %s;", (cmd['id'],))
                                    conn.commit()
                            finally:
                                release_db_connection(conn)
                        st.success("Commande effacée !")
                        st.rerun()
            st.markdown("---")

# FONCTION GESTION AVIS
def afficher_gestion_avis():
    tous_les_avis = charger_tous_les_avis()
    if not tous_les_avis:
        st.info("Aucun avis client enregistré.")
    else:
        st.markdown("### 💬 Modération des Avis Clients (Validation avant publication)")
        for avis in tous_les_avis:
            statut_pub = avis.get("publie", False)
            badge_pub = "🟢 Publié" if statut_pub else "🔴 En attente / Masqué"
            with st.container():
                c1, c2, c3 = st.columns([3, 1, 1])
                with c1:
                    st.markdown(f"""
                    <div class="review-card">
                        <strong>👤 {avis['nom']} ({badge_pub})</strong> - <span style="color:#d4af37;">{"⭐" * avis['note']}</span>
                        <br><small>Plat dégusté : {avis['produit']} | Date : {avis['date']}</small>
                        <p style="margin-top:6px; color:#333;">"{avis['commentaire']}"</p>
                    </div>
                    """, unsafe_allow_html=True)
                with c2:
                    nouveau_etat = st.checkbox("Valider & Afficher", value=statut_pub, key=f"pub_avis_{avis['id']}")
                    if nouveau_etat != statut_pub:
                        conn = get_db_connection()
                        if conn:
                            try:
                                with conn.cursor() as cur:
                                    cur.execute("UPDATE avis_clients SET publie = %s WHERE id = %s;", (nouveau_etat, avis['id']))
                                    conn.commit()
                            finally:
                                release_db_connection(conn)
                        charger_avis_publies.clear()
                        st.success("Avis mis à jour !")
                        st.rerun()
                with c3:
                    if st.button("🗑️", key=f"del_avis_{avis['id']}"):
                        conn = get_db_connection()
                        if conn:
                            try:
                                with conn.cursor() as cur:
                                    cur.execute("DELETE FROM avis_clients WHERE id = %s;", (avis['id'],))
                                    conn.commit()
                            finally:
                                release_db_connection(conn)
                        charger_avis_publies.clear()
                        st.rerun()
            st.markdown("---")

# --- NAVIGATION PRINCIPALE ---
if choix_menu == t["menu_plats"]:
    afficher_rayon_food("Plats Chauds")
elif choix_menu == t["menu_boissons"]:
    afficher_rayon_food("Boissons & Jus")
elif choix_menu == t["menu_desserts"]:
    afficher_rayon_food("Desserts & Douceurs")
elif choix_menu == t["menu_packs"]:
    afficher_rayon_food("Packs & Menus")
elif choix_menu == t["menu_promotions"]:
    st.subheader(t["promo_titre"])
    tous_produits = charger_produits()
    tous_avis = charger_avis_publies()
    articles_en_promo = [p for p in tous_produits if p.get("en_promo")]
    if not articles_en_promo:
        st.info(t["vide_promo"])
    else:
        cols = st.columns(3)
        for index, produit in enumerate(articles_en_promo):
            with cols[index % 3]:
                st.markdown('<div class="product-card">', unsafe_allow_html=True)
                if produit.get("image_url"):
                    st.markdown(f'''
                        <div class="product-img-wrapper">
                            <img src="{produit["image_url"]}" alt="{produit["nom"]}">
                        </div>
                    ''', unsafe_allow_html=True)
                st.markdown(f'<span class="promo-badge">OFFRE SPÉCIALE -{produit["reduction"]}%</span>', unsafe_allow_html=True)
                st.markdown(f"### {produit['nom']}")
                if produit.get("description"):
                    st.markdown(f'<div class="product-desc">🍲 {produit["description"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<span class="price-old">{produit["prix_origine"]:,} FCFA</span><span class="price-new">{produit["prix_final"]:,} FCFA</span>', unsafe_allow_html=True)
                if st.button(t["btn_ajouter"], key=f"promo_add_{produit['id']}", use_container_width=True):
                    st.session_state.panier.append(produit)
                    st.success(t["succes_ajout"])
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

elif choix_menu == t["menu_avis"]:
    st.subheader("⭐ Avis & Dégustations de nos Clients")
    col_form, col_liste = st.columns(2)
    with col_form:
        with st.form("form_avis", clear_on_submit=True):
            nom_client = st.text_input("Votre Prénom & Nom")
            note_client = st.slider("Note de dégustation", 1, 5, 5)
            prods = charger_produits()
            produit_concerne = st.selectbox("Plat ou boisson apprécié(e)", ["L'ensemble du menu"] + [p["nom"] for p in prods])
            commentaire = st.text_area("Votre commentaire gourmand")
            if st.form_submit_button("Soumettre mon avis", use_container_width=True):
                if nom_client.strip() and commentaire.strip():
                    date_now = datetime.now().strftime("%d/%m/%Y")
                    conn = get_db_connection()
                    if conn:
                        try:
                            with conn.cursor() as cur:
                                cur.execute("INSERT INTO avis_clients (nom, note, produit, commentaire, date, publie) VALUES (%s, %s, %s, %s, %s, FALSE);", (nom_client.strip(), note_client, produit_concerne, commentaire.strip(), date_now))
                                conn.commit()
                        finally:
                            release_db_connection(conn)
                    charger_avis_publies.clear()
                    st.success("Merci ! Votre avis a été transmis au chef et sera publié après validation.")
                    st.rerun()
    with col_liste:
        st.markdown("### 💬 Avis Validés")
        avis_valides = charger_avis_publies()
        if not avis_valides:
            st.info("Aucun avis validé pour le moment.")
        else:
            for avis in avis_valides:
                st.markdown(f"""
                <div class="review-card">
                    <strong>👤 {avis['nom']}</strong> - <span style="color:#d4af37;">{"⭐" * avis['note']}</span>
                    <p style="margin-top:4px; color:#333;">"{avis['commentaire']}"</p>
                </div>
                """, unsafe_allow_html=True)

elif choix_menu == t["menu_vendeur"]:
    if not st.session_state.admin_connecte:
        with st.form("form_login_vendeur"):
            st.markdown("### 🔐 Connexion Espace Cuisine / Vendeur")
            identifiant = st.text_input("Nom d'utilisateur Cuisine")
            mot_de_passe = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Se connecter", use_container_width=True):
                if identifiant == "MD2026" and mot_de_passe == "Dogo2026":
                    st.session_state.admin_connecte = True
                    st.success("Connexion réussie !")
                    st.rerun()
                else:
                    st.error("Identifiant ou mot de passe incorrect.")
    else:
        tab_cmds, tab_publi, tab_mes_prods, tab_avis_g = st.tabs(["📋 Commandes Plats", "➕ Ajouter au Menu", "📦 Menu Actuel", "⭐ Modération Avis"])
        with tab_cmds: afficher_gestion_commandes()
        with tab_publi:
            with st.form("form_vendeur", clear_on_submit=True):
                nom_produit = st.text_input(t["nom_article"])
                description_produit = st.text_area(t["desc_article"])
                prix_origine = st.number_input(t["prix_article"], min_value=100, step=250, value=3000)
                appliquer_promo = st.checkbox(t["est_promo"])
                taux_reduction = st.slider(t["taux_promo"], 5, 70, 15, 5) if appliquer_promo else 0
                
                cat_choisie = st.selectbox(t["cat_choix"], CATEGORIES_FOOD)
                subs_pour_cat = STRUCTURE_FOOD.get(cat_choisie, [])
                sub_choisie = st.selectbox(t["sub_choix"], subs_pour_cat)
                
                photo_fichier = st.file_uploader("Photo du plat", type=["jpg", "png", "jpeg"])
                
                if st.form_submit_button(t["btn_publier"], use_container_width=True):
                    if nom_produit.strip():
                        prix_final = int(prix_origine * (1 - taux_reduction / 100)) if appliquer_promo else prix_origine
                        img_url = encoder_image_base64_optimisee(photo_fichier) if photo_fichier else ""
                        conn = get_db_connection()
                        if conn:
                            try:
                                with conn.cursor() as cur:
                                    cur.execute("INSERT INTO produits (nom, categorie, sous_categorie, prix_origine, prix_final, en_promo, reduction, description, image_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);", 
                                                (nom_produit.strip(), cat_choisie, sub_choisie, prix_origine, prix_final, appliquer_promo, taux_reduction, description_produit.strip(), img_url))
                                    conn.commit()
                            finally:
                                release_db_connection(conn)
                        charger_produits.clear()
                        st.success(t["succes_publi"])
                        st.rerun()
        with tab_mes_prods: afficher_gestion_catalogue()
        with tab_avis_g: afficher_gestion_avis()

elif choix_menu == t["menu_admin"]:
    if not st.session_state.admin_connecte:
        with st.form("form_login_admin"):
            st.markdown("### 🔐 Connexion Espace Administrateur")
            identifiant = st.text_input("Nom d'utilisateur Administrateur")
            mot_de_passe = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Connexion", use_container_width=True):
                if identifiant == "MD2026" and mot_de_passe == "Dogo2026":
                    st.session_state.admin_connecte = True
                    st.rerun()
                else:
                    st.error("Identifiant ou mot de passe incorrect.")
    else:
        tab_infos, tab_produits, tab_avis_mod, tab_stats = st.tabs(["📝 Informations", "📦 Gestion Menu", "💬 Avis", "📊 Statistiques"])
        with tab_produits: afficher_gestion_catalogue()
        with tab_avis_mod: afficher_gestion_avis()
        with tab_stats:
            prods = charger_produits()
            st.metric("Nombre de plats au menu", len(prods))

elif choix_menu == t["menu_panier"]:
    st.subheader(t["panier_titre"])
    if not st.session_state.panier:
        st.info(t["panier_vide"])
    else:
        for idx, item in enumerate(st.session_state.panier):
            c1, c2, c3, c4 = st.columns([1, 2, 2, 1])
            with c1:
                if item.get("image_url"): st.image(item["image_url"], width=60)
            with c2: st.markdown(f"**{item['nom']}**")
            with c3: st.markdown(f"**{item['prix_final']:,} FCFA**")
            with c4:
                if st.button("❌", key=f"suppr_panier_{idx}"):
                    st.session_state.panier.pop(idx)
                    st.rerun()
            st.markdown("---")

        total_general = sum(item['prix_final'] for item in st.session_state.panier)
        st.markdown(f"### Total de votre commande : {total_general:,} FCFA")

        with st.form("form_commande_whatsapp"):
            nom_client = st.text_input("Prénom & Nom *")
            tel_client = st.text_input("Numéro de Téléphone *")
            adresse_client = st.text_input("Adresse exacte de livraison / Quartier *")
            if st.form_submit_button(t["btn_valider"], use_container_width=True):
                if nom_client.strip() and tel_client.strip() and adresse_client.strip():
                    lignes_commande = [f"- {item['nom']} ({item['prix_final']:,} FCFA)" for item in st.session_state.panier]
                    details_str = "\n".join(lignes_commande)
                    date_cmd = datetime.now().strftime("%d/%m/%Y %H:%M")
                    
                    conn = get_db_connection()
                    if conn:
                        try:
                            with conn.cursor() as cur:
                                cur.execute("INSERT INTO commandes (nom_client, telephone, adresse, details_articles, montant_total, statut, date_commande) VALUES (%s, %s, %s, %s, %s, 'En attente', %s);", 
                                            (nom_client.strip(), tel_client.strip(), adresse_client.strip(), details_str, total_general, date_cmd))
                                conn.commit()
                        finally:
                            release_db_connection(conn)

                    msg = f"🍲 Commande Deligro by Codou Senghor\nClient: {nom_client}\nTél: {tel_client}\nLivraison: {adresse_client}\n\n{details_str}\n\nTotal: {total_general:,} FCFA"
                    
                    num_whatsapp_destination = TEL_PAR_DEFAUT
                    lien_wa = f"https://wa.me/{num_whatsapp_destination}?text={urllib.parse.quote(msg)}"
                    
                    st.balloons()
                    st.success(t["succes_commande"])
                    st.markdown(f'<a href="{lien_wa}" target="_blank" class="whatsapp-btn">📲 Envoyer la commande sur WhatsApp</a>', unsafe_allow_html=True)
