# NH AUTO INCOME

Automated daily income claimer for KageHero Studio events, with optional
Discord / Telegram notifications. Rewritten as a small, modern Python package
(async HTTP with a shared connection pool, dataclass models, strict config
validation, structured logging).

## LISENSI

**MIT**

## PENGGUNAAN

**PENTING**
Jika kalian ingin notifikasi dari discord, maka buatlah discord bot dahulu, sama halnya dengan bot telegram
Jangan lupa untuk membuat repository menjadi **PRIVATE**

## 1. MEMBUAT SECRETS (PENTING)

1. pergi ke menu repository settings
2. pada bagian `security` klik `secrets and variable`
3. lalu klik `actions`
4. tambahkan secrets dengan klik `new repository secrets` dengan **masing masing** data sebagai berikut
   - DISCORDTOKEN = di isi dengan token discord bot yang telah dibuat
   - TELETOKEN = di isi dengan token telegram bot yang telah dibuat

## 2. SET UP ACCOUNT

1. buat file `data.json` sesuai berikut

   ```json
   [
     {
       "email": "isi dengan email mu",
       "password": "isi dengan password (boleh kosong)",
       "server": "isi dengan server tujuan (angka)",
       "discord_id": 1234567890,
       "tele_id": 0
     }
   ]
   ```

   - `discord_id` / `tele_id`: isi dengan userid notifikasi (angka `0` jika tidak mau)
   - **NOTE: Untuk lebih lanjut, lihat `contoh.json`**

2. commit change
3. masuk ke tab actions lalu periksa running action
4. periksa warna action sebagai berikut
   1. merah - gagal
   2. kuning - jika running > 3 menit gagal
   3. hijau - berhasil

## 3. MENJALANKAN MANUAL (LOKAL)

Butuh Python **3.11+**.

```bash
pip install .

# klaim harian untuk semua akun di data.json
python -m nh_income claim

# klaim tanpa membangun laporan lengkap (1x fetch dashboard)
python -m nh_income claim --fast

# pakai file akun lain
python -m nh_income claim --data-file akun.json

# klaim ulang reward hari ini sebanyak N kali (alat uji)
python -m nh_income skip --email kamu@gmail.com --server 1 --amount 2
```

Token notifikasi dibaca dari environment: `DISCORDTOKEN`, `TELETOKEN`
(atau file `.env`).

## STRUKTUR PROYEK

```
nh_income/
├── __main__.py      # CLI: python -m nh_income claim|skip
├── cli.py           # titik masuk console script (nh-income)
├── config.py        # validasi data.json + token dari environment
├── constants.py     # URL, class CSS, timezone event
├── models.py        # dataclass: Account, ClaimData, Report
├── parsing.py       # parsing HTML dashboard event
├── client.py        # klien httpx per akun (login, claim, skip)
├── service.py       # orkestrasi paralel antar akun
└── notify/          # discord.py & telegram.py (DM laporan)
```

`main.py` hanya shim kompatibilitas untuk perintah lama
(`python main.py --type auto` → `python -m nh_income claim`).
