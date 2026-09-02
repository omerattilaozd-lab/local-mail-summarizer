import os
import imaplib
import email
from email.header import decode_header
import time
import requests
from dotenv import load_dotenv

# .env dosyasından ayarları yüklüyoruz
load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL_NAME = "gemma3:latest"

IMAP_SERVER = "imap.gmail.com"
EMAIL_USER = os.getenv("GMAIL_USER")
EMAIL_PASS = os.getenv("GMAIL_APP_PASSWORD")

def fetch_today_emails():
    """
    Gmail hesabına bağlanarak son mailleri çeken fonksiyon.
    """
    if not EMAIL_USER or not EMAIL_PASS or EMAIL_USER == "senin_mailin@gmail.com":
        print("⚠️ Gmail kullanıcı adı veya şifresi .env dosyasında ayarlanmamış! Örnek metin ile simüle ediliyor.")
        return "Simüle Edilen Mail: Mentorun projeyi kontrol edeceğini bildirdi."

    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        status, messages = mail.search(None, 'UNSEEN')
        email_content = ""

        if status == "OK":
            for num in messages[0].split():
                res, msg_data = mail.fetch(num, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8")
                        email_content += f"Konu: {subject}\n"
        
        mail.logout()
        return email_content if email_content else "Bugün okunmamış yeni mail bulunmuyor."
    except Exception as e:
        return f"Mail çekilirken hata oluştu: {e}"

def summarize_emails(email_content):
    """
    Lokal Ollama modeline mailleri gönderip özet çıkartan fonksiyon.
    """
    prompt = f"Aşağıdaki mailleri profesyonel ve kısa bir metin olarak özetle:\n\n{email_content}"
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        if response.status_code == 200:
            return response.json().get("response", "Özet alınamadı.")
        else:
            return f"Hata: Ollama yanıt döndüremedi (Kod: {response.status_code})"
    except Exception as e:
        return f"Bağlantı hatası: {e}"

def job():
    print("\n[OTOMATİK ÇALIŞMA] Mailler kontrol ediliyor ve özetleniyor...")
    mails = fetch_today_emails()
    summary = summarize_emails(mails)
    print("\n--- GÜNLÜK MAİL ÖZETİ ---")
    print(summary)
    print("--------------------------")

if __name__ == "__main__":
    print("Mail Özetleyici Sistemi Başlatıldı...")
    
    # Harici tetikleme (Anında bir kez çalıştırma)
    job()

    # Otomatik Çalışma Döngüsü (Mentorun istediği periyodik çalışma)
    # Test için kısa tutabiliriz veya günde 1 kez çalışacak şekilde ayarlayabiliriz.
    print("\nSistem otomatik modda çalışıyor (Her 24 saatte bir tetiklenecek)... Çıkış için Ctrl+C yapabilirsin.")
    while True:
        # 24 saatte bir çalışması için (86400 saniye). Test etmek istersen süreyi küçültebilirsin.
        time.sleep(86400) 
        job()
