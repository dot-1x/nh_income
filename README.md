# NH AUTO INCOME

## LISENSI

**MIT**

## PENGGUNAAN

**PENTING**

## MEMBUAT SECRETS (PENTING)

caranya:

1. pergi ke menu repository settings
2. pada bagian `security` klik `secrets and variable`
3. lalu klik `actions`
4. tambahkan secrets dengan klik `new repository secrets` dengan **masing masing** data sebagai berikut
    - DISCORDTOKEN = di isi dengan token discord bot yang telah dibuat
    - TELETOKEN = di isi dengan token telegram bot yang telah dibuat

## CLONE REPOSITORY VIA UPLOAD

1. unduh repo ini dengan tekan tombol hijau `<> Code` lalu klik unduh zip
2. buat repository baru kamu dengan nama bebas
   **BUAT SECRETS TERLEBIH DAHULU SEBELUM LANJUT**
3. buat file baru dengan cara `add file > new file`
4. atur file path baru ke `.github/workflows/any` lalu commit
5. lalu upload file yang telah diunduh tadi dengan `add file > upload file` **kecuali** folder **.github**
6. untuk folder .github, pertama arahkan github ke `.github/workflows/` (pastikan hidden folder terlihat)
7. lalu upload semua file yang ada pada folder `.github/workflows/` ke `.github/workflows/`
8. commit

**ADA 2 CARA MENGGUNAKAN SCRIPT INI**

## PENGGUNAAN 1

1. silahkan clone repository ini
2. buat repository baru jadikan private repository (**PASTIKAN PRIVATE**)
3. edit file `data.json` sesuai berikut

    ```
    {
        "email":"isi dengan email mu",
        "password":"isi dengan password (boleh kosong)",
        "server":"isi dengan server tujuan",
        "discord_id":isi dengan discord userid notifikasi (isi dengan angka 0 jika tidak mau),
        "tele_id":isi dengan telegram userid notifikasi (isi dengan angka 0 jika tidak mau)
    }
    ```

    **NOTE: Untuk lebih lanjut, lihat `contoh.json`**

4. commit change
5. masuk ke tab actions lalu periksa running action
6. periksa warna action sebagai berikut
    1. merah - gagal
    2. kuning - jika running > 3 menit gagal
    3. hijau - berhasil

## PENGGUNAAN 2

mendatang!
