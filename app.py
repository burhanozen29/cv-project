import streamlit as st
import fitz  # PyMuPDF
from pymongo import MongoClient
from datetime import datetime
from cv_parser import parse_cv,ayikla_egitim,ayikla_diller
from spacy_parser import spacy_analiz
import os,sys
import re


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def kullanici_dogrula(mail_input, sifre):
    client = MongoClient("mongodb://localhost:27017/")
    # Veritabanı ve koleksiyon seç
    db = client["cv_analiz"]
    kullanicilar = db["cv_kullanicilar"]
    user = kullanicilar.find_one({"kullanici_mail": mail_input, "sifre": sifre})
    
    if user:
        return {"kullanici_mail":mail_input,"sifre":sifre}
    return None

def giris_yap():
    st.title("🔐 Kullanıcı Girişi")

    # Giriş formu
    with st.form("giris_formu"):
        mail_input = st.text_input("E-posta", key="mail_input")
        sifre = st.text_input("Şifre", type="password", key="sifre")
        giris_button = st.form_submit_button("Giriş Yap")

    if giris_button:
        sonuc = kullanici_dogrula(mail_input, sifre)
        
        if sonuc:
            st.session_state.giris_yapildi = True
            st.session_state.kullanici_mail = sonuc["kullanici_mail"]
            st.success("✅ Giriş başarılı!")
            st.rerun()
        else:
            st.error("❌ Kullanıcı adı veya şifre hatalı.")

# Eğer henüz giriş yapılmadıysa, formu göster

if "giris_yapildi" not in st.session_state:
    st.session_state.giris_yapildi = False
    st.set_option("client.showSidebarNavigation", False)


if not st.session_state.giris_yapildi:
    giris_yap()
    st.stop()
else:
    st.success(f"Hoş geldiniz!")


# === Mongo bağlantısı ===
client = MongoClient("mongodb://localhost:27017/")
db = client["cv_analiz"]
cv_dosyalar = db["cv_dosyalar"]

st.set_page_config(page_title="CV Skorlama (PyMuPDF)", layout="wide")
st.title("📄 CV Uygunluk ve Yetenek Skorlama (TR + EN)")

uploaded_file = st.file_uploader("📎 CV dosyanızı yükleyin (PDF)", type=["pdf"])

if uploaded_file:
    metin = ""
    blocks = []
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        for sayfa in doc:
            blocks += sayfa.get_text("blocks")
            # metin = "\n".join(blok[4])
        doc.close()
    except Exception as e:
        st.error(f"❌ PDF okunamadı: {e}")
        st.stop()
    
    paragraflar = [blok[4].strip() for blok in blocks if blok[4].strip()]
    metin = "\n".join(paragraflar)
    
    st.subheader("📄 PyMuPDF OCR Sonucu (İlk 2000 karakter)")
    st.text_area("OCR Metni", metin[:2000], height=300)

    # === Analizler ===
    st.subheader("🧠 Anahtar Kelime Bazlı Analiz (cv_parser.py)")
    parser_result = parse_cv(metin,paragraflar)
    st.write(parser_result)

    st.subheader("🧠 spaCy Tabanlı NER Analizi (spacy_parser.py)")
    spacy_result = spacy_analiz(metin)
    st.write(spacy_result)
    
    # st.write(f" Nice to meet you {spacy_result['kişi']}. You are currently a {parser_result['deneyimler'][0]['pozisyon']} ")
    st.write(f" Nice to meet you {spacy_result['kişi']}. You are currently a non employee ")
    
    if st.button("📥 Veritabanına Kaydet"):
        cv_dosyalar.insert_one({
            "kullanici": st.session_state.kullanici_mail,
            "cv_adi": uploaded_file.name,
            "yuklenme_tarihi": datetime.now(),
            "icerik_ocr": metin,
            "analiz": {
                "cv_parser": parser_result,
                "spacy": spacy_result
            },
            "kaynak": "pymupdf"
        })
        st.success("✅ Kaydedildi.")
    
    # ÜNİVERSİTE BURADAN ALINMALI
    # Muhtemel CV başlıkları (bunu daha sonra genişletebiliriz)
    BASLIK_GRUPLARI = {
        "EXPERIENCE": ["EXPERIENCE", "EXPERIENCES", "ACTIVITY", "ACTIVITIES", "WORK EXPERIENCE", "PROFESSIONAL EXPERIENCE"],
        "EDUCATION": ["EDUCATION", "ACADEMIC", "SCHOOL"],
        "PROJECTS": ["PROJECTS", "PROJECT"],
        "CERTIFICATES": ["CERTIFICATES", "CERTIFICATE","EVENTS","MEMBERSHIPS","PROJECTS"],
        "SKILLS": ["SKILLS", "TECHNICAL SKILLS"],
        "LANGUAGES": ["LANGUAGES","LANGUAGE"],
        "PROFILE": ["PROFILE", "SUMMARY", "BRIEF","OBJECTIVE"],
        "CONTACT": ["CONTACT", "PERSONAL INFORMATION"],
        "REFERENCES": ["REFERENCES"]
    }
    BASLIK_EQUIV_MAP = {}
    for ana, eslesmeler in BASLIK_GRUPLARI.items():
        for e in eslesmeler:
            BASLIK_EQUIV_MAP[e] = ana
    
    
    def normalize_baslik(text):
        text = text.upper()
        text = re.sub(r"[\&\+\-/]", " ", text)
        text = re.sub(r"\bAND\b", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()
    
    from collections import defaultdict
    
    def bolumleri_ayir(cv_metin):
        bolumler = defaultdict(str)
        satirlar = cv_metin.splitlines()
        baslik_satirlari = []
    
        for i, satir in enumerate(satirlar):
            parcalar = re.split(r"[\&\+\-/]| and ", satir, flags=re.IGNORECASE)
            for parca in parcalar:
                norm = normalize_baslik(parca)
                if norm in BASLIK_EQUIV_MAP:
                    ana_baslik = BASLIK_EQUIV_MAP[norm]
                    baslik_satirlari.append((ana_baslik, i))
    
        for idx, (ana_baslik, baslangic) in enumerate(baslik_satirlari):
            bitis = baslik_satirlari[idx + 1][1] if idx + 1 < len(baslik_satirlari) else len(satirlar)
            icerik = "\n".join(satirlar[baslangic + 1:bitis]).strip()
            bolumler[ana_baslik] += icerik + "\n"
    
        return dict(bolumler)
    
    a = bolumleri_ayir(metin)
    
    egitim_gecmisi = ayikla_egitim(a.get("EDUCATION",""))
    diller = ayikla_diller(a.get("LANGUAGES",""))
    deneyim = [d['pozisyon'] for d in parser_result['deneyimler']]
    deneyimYillar = [d['yillar'] for d in parser_result['deneyimler']]
    deneyimIcerik = [d['icerik'] for d in parser_result['deneyimler']]
    
    import spacy
    nlp = spacy.load("en_core_web_lg")
    YANLIS_ORG_KELIMELERI = {"analyst", "intern", "specialist", "engineer", "manager", "scientist", "developer"}

    def kurum_bul(metin):
        doc = nlp(metin)
    
        # 1. SpaCy'den doğru ORG alabiliyorsak onu kullan
        org_ents = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
        if org_ents:
            secilen_org = org_ents[0].strip()
            if not any(kelime.lower() in secilen_org.lower() for kelime in YANLIS_ORG_KELIMELERI):
                return secilen_org
    
        # 2. "at/in/with/for" sonrası büyük harfli ifadeyi tümüyle al
        match = re.search(
            r"\b(?:at|in|with|for)\s+((?:[A-Z][\w\-]*(?:\s+(?:of|and|&|the|[A-Z][\w\-]*))*)+)",
            metin
        )
        if match:
            return match.group(1).strip()
    
        # 3. Satırda tarih geçiyorsa, o satırdan virgüle kadar olan kısmı kurum say
        for satir in metin.splitlines():
            if re.search(r"\d{2}\.\d{2}[-–]\d{2}\.\d{2}\.\d{4}", satir):
                kalan = re.sub(r"^\d{2}\.\d{2}[-–]\d{2}\.\d{2}\.\d{4}\s*", "", satir)
                kurum = kalan.split(",")[0].strip()
                return kurum
    
        return "Bulunamadı"




        
    kurumlar = [kurum_bul(metin) for metin in deneyimIcerik]

    for i, kurum in enumerate(kurumlar):
        st.write(f"{i+1}. Deneyimde kurum: {kurum}")
    
    st.write(deneyim, "\n")
    st.write(deneyimYillar , "\n")
    
    st.write(deneyimIcerik, "\n")
    
    # import spacy
    # nlp = spacy.load("en_core_web_lg")
    
    # deneyimKurum = []
    
    # for metin in deneyimIcerik:  # metin = str
    #     doc = nlp(metin)
    #     kurumlar = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
    #     deneyimKurum.extend(kurumlar)
    
    # deneyimKurum = list(set(deneyimKurum))
    # st.write(deneyimKurum)
    



    st.markdown("---")
    # st.write(f"""
    #          Merhaba {spacy_result['kişi']} \n
             
    #          En son pozisyon: {parser_result['deneyimler'][0]['pozisyon']} \n
             
    #          Diller: {parser_result['diller']} \n
             
    #          Yetenekler: {', '.join(parser_result['yetenekler'])} \n
             
    #          Eğitim Geçmişi: {', '.join(ayikla_egitim(a["EDUCATION"]))}
             
             
             
             
    #          """)

else:
    st.info("CV yükleyin.")
