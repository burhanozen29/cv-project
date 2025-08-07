# 📄 CV Uygunluk ve Yetenek Skorlama Sistemi

Bu proje, kullanıcıların PDF formatında CV'lerini yükleyerek bir iş pozisyonu ile ne kadar uyumlu olduklarını analiz etmelerini sağlar.  
NLP teknikleriyle yetenek çıkarımı yapılır, pozisyonla eşleştirme sonucu bir **uygunluk skoru** hesaplanır.  
Gelişmiş versiyonlarda otomatik öneriler, kapak mektubu üretimi ve iş başvuru takibi modülleri de dahil edilecektir.

---

## 🚀 Başlangıç

### Gereksinimler

- Python 3.9+
- MongoDB (lokal veya cloud)
- Streamlit
- pip ile:
  ```bash
  pip install -r requirements.txt
  ```

### Uygulama Başlatma

```bash
streamlit run app.py
```

> İlk kullanımda `cv_dosyalar`, `pozisyonlar`, `skorlar` gibi Mongo koleksiyonları otomatik oluşacaktır.

---

## 🧠 Kullanım Özeti

1. Kullanıcı arayüzünden CV (PDF) yüklenir  
2. Pozisyon seçimi yapılır veya elle tanım girilir  
3. NLP ile CV metni analiz edilir  
4. Pozisyonun anahtar yetenekleriyle eşleşme yapılır  
5. Uyum skoru ve yorum ekranda görüntülenir  

---

## 🧭 Yol Haritası

| Aşama | Başlık                                 | Durum     |
|-------|----------------------------------------|-----------|
| ✅    | CV yükleme ve metin çıkarımı (OCR/PDF) | Tamamlandı |
| ✅    | Pozisyon tanımı girişi / seçimi        | Tamamlandı |
| ✅    | NLP ile yetenek çıkarımı               | Tamamlandı |
| ✅    | Cosine Similarity ile eşleşme skoru    | Tamamlandı |
| 🔜    | Kapak mektubu üretimi (LLM)            | Planlandı |
| 🔜    | CV iyileştirme önerileri               | Planlandı |
| 🔜    | LinkedIn pozisyon entegrasyonu         | Planlandı |
| 🔜    | Kurumsal kullanıcı paneli              | Planlandı |

---

## 🏗️ Teknolojiler

- `Streamlit` – Web arayüzü
- `PyMuPDF` / `pdfplumber` – PDF içerik okuma
- `spaCy` / `sklearn` – NLP & skorlama
- `pandas` – Veri işleme
- `MongoDB` – Veri depolama

---

## 💡 Neden Bu Proje?

- Kariyer hedeflerine uygunluk analizi
- Otomatik geri bildirim oluşturma
- Başvuru yapmadan önce **hazırlık analizi**
- Kişisel gelişim yönlendirmesi

---

## 🧩 Geliştirici

Burhan Özen  
📫 [GitHub](https://github.com/burhanozen29)  
📧 burhan.ozen@example.com

---

## ⚠️ Lisans

Bu proje henüz açık kaynak lisanslanmamıştır. Tüm hakları saklıdır.