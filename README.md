YouTube Auto Video Generator — Self-hosted POC

Bu repo, yerel sunucunda çalıştırabileceğin basit bir otomatik video üretici (POC) içerir.

Özet
- input: content/ dizinine koyacağın .txt dosyaları (örnek: myvideo.txt). Aynı isimde .jpg koyarsan kapak olarak kullanılır.
- pipeline: metin -> gTTS (MP3) -> ffmpeg ile tek-resim video -> SRT altyazı -> out/ dizinine MP4.
- yükleme: upload_youtube.py içinde YouTube API upload helper var (opsiyonel).

Dosyalar eklendi
- docker-compose.yml
- Dockerfile
- requirements.txt
- scheduler.py
- generate_video.py
- upload_youtube.py
- .env.example

Kurulum
1) Gereksinimler: Docker ve docker-compose.
2) Klonla veya zip çıkar.
3) content/ dizinine .txt dosyaları koy (ve istersen .jpg kapaklar).
4) credentials/client_secrets.json dosyasını ekle (YouTube OAuth client secret) — upload için gerekli.
5) .env oluştur (.env.example'e bak).
6) docker-compose up --build -d

İlk upload (token oluşturma)
- Container içinde interaktif olarak token oluştur:
  docker exec -it yt_generator bash
  python -c "import upload_youtube; upload_youtube.get_authenticated_service()"
- Konsolda çıkan URL'yi açıp izin ver, oluşan kodu yapıştır.

Notlar ve geliştirme
- gTTS internet gerektirir; daha kaliteli self-hosted TTS için Coqui gibi çözümler önerilir.
- Stok klip/AI görsel üretim, birden çok slayt, geçiş efektleri ve daha gelişmiş altyazı hizalaması ileride eklenebilir.
- Lisans ve telif kurallarına dikkat et.

Nasıl ilerleyelim?
- İstersen PR açayım ve repo üzerinde branch üzerine commit yaptım; şimdi PR açmamı ister misin veya başka değişiklik yapmak ister misin?
