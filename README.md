# NH AUTO INCOME

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

## 2. CLONE REPOSITORY VIA UPLOAD

1. unduh repo ini dengan tekan tombol hijau `<> Code` lalu klik unduh zip
2. kembali ke repository yang sudah dibuat tadi
3. buat file baru dengan cara `add file > new file`
4. atur file path baru ke `.github/workflows/any` lalu commit
5. masuk ke FOLDER unduhan file tadi lalu ekstrak lalu show hidden folder
6. kembali ke repo github, lalu arahkan ke `ROOT` path (klik nama repo)
7. lalu upload semua file-nya dengan `add file > upload file` **kecuali** folder **.github**
8. untuk folder .github, pertama arahkan GITHUB ke `.github/workflows/` (pastikan hidden folder terlihat)
9. lalu upload semua file yang ada pada folder `.github/workflows/` ke `.github/workflows/`
10. commit

## 3. SET UP ACCOUNT

1. buat file `data.json` sesuai berikut

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

2. commit change
3. masuk ke tab actions lalu periksa running action
4. periksa warna action sebagai berikut
   1. merah - gagal
   2. kuning - jika running > 3 menit gagal
   3. hijau - berhasil
