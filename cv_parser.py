import re

YETENEK_KELIMELERI = [
    "Python", "SQL", "Java", "C++", "Power BI", "Excel", "Pandas",
    "Numpy", "Grafana", "HTML", "CSS", "KNIME", "Photoshop"
]

DILLER = ["İngilizce", "English",
          "Türkçe", "Turkish",
          "Fransızca", "French",
          "Almanca","German",
          "İspanyolca","Spanish",
          "İtalyanca","Italian",
          "Rusça","Russian",
          "Çince","Chinese"]
          # "IELTS", "TOEFL"]
GEÇERLİ_SEVİYELER = [
    "A1", "A2", "B1", "B2", "C1", "C2",
    "A+","B+","C+",
    "BEGINNER", "INTERMEDIATE", "UPPER-INTERMEDIATE",
    "ADVANCED", "PROFICIENT", "FLUENT", "ELEMENTARY",
    "NATIVE"
]

orijinal_pozisyonlar = [
        "Intern","Internship","Data Analyst", "Data Scientist", "Engineer",
        "Specialist", "Manager", "Intern", "Data Analyst Specialist"
    ]

def temizle_metin(metin):
    return re.sub(r"[\t\n\r]+", " ", metin).strip()

def ayikla_yetenekler(metin):
    return list({kelime for kelime in YETENEK_KELIMELERI if kelime.lower() in metin.lower()})

def ayikla_diller(metin):
    sonuc = []
    satirlar = metin.split("\n")  # satır satır bakmak hataları azaltır

    for satir in satirlar:
        for dil in DILLER:
            # Pattern: Dil ardından kısa seviye bilgisi gelebilir
            pattern = rf"\b({dil})\b\s*[:\-–]?\s*(\b[A-Za-z0-9\+\-]+)?"
            matches = re.findall(pattern, satir, flags=re.IGNORECASE)

            for match in matches:
                dil_adi = match[0].capitalize()
                seviye_raw = match[1].strip("() ").upper() if match[1] else ""

                if any(seviye_raw == valid for valid in GEÇERLİ_SEVİYELER):
                    sonuc.append((dil_adi, seviye_raw))

    return list({(d, s) for d, s in sonuc})


def ayikla_egitim(metin):
    pattern = r"((?:[A-ZÇĞİÖŞÜ][a-zçğıöşü]+ ?)+(?:Üniversitesi|University|School|Lisesi|Enstitüsü|Okulu))"
    bulunanlar = re.findall(pattern, metin)

    # Türkçe karakter dönüşüm haritası
    cevir = str.maketrans({
        'ı': 'i',
        'ü': 'u',
        'ö': 'o',
        'ç': 'c',
        'ğ': 'g',
        'ş': 's'
    })

    # Normalize, büyüt ve unique hale getir
    sonuc = set()
    for okul in bulunanlar:
        temiz = okul.lower().translate(cevir).upper()
        sonuc.add(temiz)

    return list(sonuc)



def ayikla_deneyim(paragraflar: list[str]):

    # "Intern" varyantlarını da dahil et
    pozisyonlar = []
    for p in orijinal_pozisyonlar:
        pozisyonlar.append(p)
        if "Intern" not in p:
            pozisyonlar.append(p + " Intern")

    deneyimler = []
    ilk_yil_konumu = None  # alt / ust / ayni

    for i, paragraf in enumerate(paragraflar):
        # Pozisyon eşleştirme: kelime sınırlarına dikkat et
        eslesen_pozisyonlar = [
            p for p in pozisyonlar
            if re.search(rf"\b{re.escape(p.lower())}\b", paragraf.lower())
        ]
        if not eslesen_pozisyonlar:
            continue

        # En uzun pozisyonu seç
        secilen_pozisyon = max(eslesen_pozisyonlar, key=len)

        # Yıl arama alanı: ilk eşleşmede tüm çevreye bak, sonra sadece belirlenen yere
        satirlar = []

        if ilk_yil_konumu is None:
            if i > 0:
                satirlar.append(("ust", paragraflar[i - 1]))
            satirlar.append(("ayni", paragraf))
            if i < len(paragraflar) - 1:
                satirlar.append(("alt", paragraflar[i + 1]))
        else:
            if ilk_yil_konumu == "alt" and i < len(paragraflar) - 1:
                satirlar.append(("alt", paragraflar[i + 1]))
            elif ilk_yil_konumu == "ust" and i > 0:
                satirlar.append(("ust", paragraflar[i - 1]))
            elif ilk_yil_konumu == "ayni":
                satirlar.append(("ayni", paragraf))

        yillar = []
        for konum, s in satirlar:
            bulunan = re.findall(r"\b(19\d{2}|20\d{2})\b", s)
            if bulunan:
                yillar.extend(bulunan)
                if ilk_yil_konumu is None:
                    ilk_yil_konumu = konum

        deneyimler.append({
            "pozisyon": secilen_pozisyon,
            "yillar": sorted(set(yillar)) if yillar else ["Bulunamadı"],
            "icerik": paragraf.strip()
        })

    return deneyimler




def parse_cv(metin,paragraflar):
    metin = temizle_metin(metin)
    return {
        "yetenekler": ayikla_yetenekler(metin),
        "diller": ayikla_diller(metin),
        "egitim_gecmisi": ayikla_egitim(metin),
        "deneyimler": ayikla_deneyim(paragraflar)
    }