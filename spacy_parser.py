import spacy
nlp = spacy.load("en_core_web_lg")

    
def ad_soyad_bul(metin):
    IGNORE_KELIMELER = {"özgeçmiş", "öz geçmiş", "cv", "page", "kişisel bilgiler", "curriculum vitae"}
    satirlar = metin.strip().splitlines()
    
    # İlk 20 satırı al, boş olmayanları temizle
    temiz_satirlar = [s.strip() for s in satirlar[:20] if s.strip()]

    # Yasaklı anahtar kelimeleri içeren satırları at
    temiz_satirlar = [
        s for s in temiz_satirlar 
        if not any(kelime in s.lower() for kelime in IGNORE_KELIMELER)
    ]

    # 1. Alt alta büyük harfli ad + soyad kontrolü
    for i in range(len(temiz_satirlar) - 1):
        ad = temiz_satirlar[i]
        soyad = temiz_satirlar[i + 1]
        if ad.isalpha() and soyad.isalpha():
            if ad.isupper() and soyad.isupper():
                return f"{ad.title()} {soyad.title()}"

    # 2. Aynı satırda boşlukla ayrılmış 2 kelime: ad soyad
    for satir in temiz_satirlar:
        parcalar = satir.split()
        if len(parcalar) == 2 and all(p.isalpha() for p in parcalar):
            # Yasaklı kelime içeriyorsa geçme
            if not any(k in satir.lower() for k in IGNORE_KELIMELER):
                return satir.title()

    return None



    
def spacy_analiz(metin):
    doc = nlp(metin)
    sonuc = {
        "kurumlar": list(set([ent.text for ent in doc.ents if ent.label_ == "ORG"])),
        "kişiler": list(set([ent.text for ent in doc.ents if ent.label_ == "PERSON"])),
        "tarihler": list(set([ent.text for ent in doc.ents if ent.label_ == "DATE"])),
        "diller": list(set([ent.text for ent in doc.ents if ent.label_ == "LANGUAGE"])),
        "pozisyonlar": list(set([ent.text for ent in doc.ents if ent.label_ == "TITLE"])),
        "kişi":ad_soyad_bul(metin)
    }
    
    
    
    return sonuc