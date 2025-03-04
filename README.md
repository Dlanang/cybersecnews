# Dokumentasi Proyek Discord Scraper

Proyek ini melakukan scraping berita dari Reddit dan The Hacker News, kemudian mengirimkan hasilnya sebagai pesan embed ke Discord. Fitur terbaru:
- **Judul Artikel Klikable:** Judul langsung bisa diklik untuk membuka URL artikel.
- **Snippet Artikel:** Menampilkan cuplikan singkat (maks. 150 karakter) dari isi artikel untuk menarik perhatian.
- **Optimasi Anti-Bot:** Menggunakan session, retries, dan delay acak untuk menghindari blokir.

---

## 1. Struktur Proyek

![Project Structure]

- **.env:** File konfigurasi environment.
- **main.py:** Entry point aplikasi.
- **scraper.py:** Modul untuk scraping (Reddit & The Hacker News).
- **discord_webhook.py:** Modul untuk mengirim pesan embed ke Discord.
- **.github/workflows/ci.yml:** Konfigurasi CI/CD GitHub Actions.
- **requirements.txt:** Daftar dependensi Python.

---

## 2. Cara Kerja

1. **Scraping Data:**
   - **RedditScraper:** Mengambil thread dari subreddit *cybersecurity* dengan indexing.
   - **HackerNewsScraper:** Mengambil artikel dari dua kategori: *Vulnerability* dan *Cyber Attack*.
     - Mencoba mengekstrak *snippet* (cuplikan isi) dari elemen dengan kelas `home-desc`.
     - Jika snippet melebihi 150 karakter, akan dipotong dan ditambahkan "..." di akhir.
     - Jika scraping gagal, terdapat fallback dengan pesan untuk membuka `view-source:` URL untuk debugging.

2. **Pengiriman ke Discord:**
   - Data dikemas ke dalam format embed Discord:
     - **Judul Artikel:** Klikable karena disertai properti `url`.
     - **Snippet:** Ditampilkan sebagai deskripsi untuk menarik perhatian.
     - **Gambar:** Jika tidak tersedia, menggunakan gambar default dari `.env`.
     - **Footer:** Menampilkan signature unik.
   - Jika jumlah embed melebihi batas (10), hanya 10 embed pertama yang akan dikirim.

3. **CI/CD:**
   - Setiap push/PR ke branch *main* menjalankan pipeline untuk memeriksa integritas kode.

---

## 3. Contoh Tampilan Embed di Discord

Contoh tampilan embed:

**Embed untuk Artikel Hacker News:**
- **Judul:** [Judul Artikel Cyber Attack](https://link-artikel.com)
- **Deskripsi:** "Cuplikan isi artikel yang menarik dan singkat..."
- **Gambar:** Ditampilkan (atau gambar default jika tidak ada)
- **Footer:** "Made with (love) from N4THE4N+P7312=0x000"

![Discord Embed Example](https://via.placeholder.com/600x400?text=Discord+Embed+Example)

---

## 4. Menjalankan Proyek

1. **Instal Dependensi:**
   ```bash
   pip install -r requirements.txt
