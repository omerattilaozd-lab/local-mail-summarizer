import os
import requests
from dotenv import load_dotenv

# .env dosyasından ayarları yüklüyoruz
load_dotenv()

# Lokal Ollama API adresi (Docker veya yerel kurulum için)
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"  # Bilgisayarında yüklü olan model adı

def summarize_emails(email_content):
    """
    Lokaldeki Ollama modeline mail içeriğini gönderip özet alan fonksiyon.
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
        return f"Bağlantı hatası: Ollama çalışıyor mu? Detay: {e}"

if __name__ == "__main__":
    print("Mail Özetleyici Başlatıldı...")
    sample_mails = """
    Gönderen: Proje Yöneticisi
    Konu: Haftalık Rapor
    İçerik: Cuma gününe kadar Docker entegrasyonunun bitmesi gerekiyor.
    
    Gönderen: Mentor
    Konu: Ödev Durumu
    İçerik: Otomatik tetikleme mekanizmasını unutma.
    """
    
    summary = summarize_emails(sample_mails)
    print("\n--- MAİL ÖZETİ ---")
    print(summary)