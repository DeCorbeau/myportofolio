Nama : Faiz Yusuf Elriki

NPM : 2506607921

Kelas : PBP A

## Tentang Proyek

Repositori portofolio website pribadi yang dibangun bertahap untuk memenuhi tugas individu mata kuliah Pemrograman Berbasis Platform (PBP) sepanjang semester ini.

Halaman portofolio ini berisi dua section utama:
- **About Me**: perkenalan diri dengan foto, bio, dan tautan sosial.
- **Organizational Experience**: timeline pengalaman kepanitiaan/organisasi dalam format kartu interaktif.

## Cara Menjalankan Proyek Secara Lokal

1. Clone repository ini, lalu masuk ke foldernya.
2. Buat dan aktifkan virtual environment:
   ```
   python -m venv env
   env\Scripts\activate      # Windows
   source env/bin/activate   # macOS/Linux
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Jalankan migrasi bawaan Django:
   ```
   python manage.py migrate
   ```
5. Jalankan server:
   ```
   python manage.py runserver
   ```
6. Buka `http://localhost:8000` di browser.

## Assets & Credits

- Background ilustrasi angkasa dan aksen astronot diambil dari **"Space Themed Portfolio"**, sebuah Figma Community file, dilisensikan di bawah [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
  Sumber: https://www.figma.com/community/file/1192903581929005722/space-themed-portfolio
- Font **Space Grotesk** dari Google Fonts.

## Progres Tugas Mingguan

### Tugas 1

1. **Pada Tutorial dan Tugas 1, Anda diberi kebebasan untuk menentukan tampilan dari website portofolio Anda. Saat Anda merancang struktur HTML yang digunakan, apakah Anda menggunakan elemen semantik HTML5 seperti <section>, <article>, atau <aside>? Jika iya, bagaimana elemen tersebut membantu Anda dalam membuat static web? Jika tidak, mengapa tanpa elemen tersebut sudah memenuhi kebutuhan desain Anda?**

   Ya, saya menggunakan elemen semantik HTML5 secara konsisten, yaitu header untuk navigasi, section untuk dua blok konten utama (About dan Experience), article untuk setiap kartu pengalaman pada timeline, serta footer untuk penutup halaman. Pemilihan article didasarkan pada pemahaman bahwa setiap entri pengalaman merupakan konten yang berdiri sendiri dan tetap bermakna meskipun dipisahkan dari konteks sekitarnya, sesuai dengan definisi elemen tersebut pada spesifikasi HTML5. Sementara itu, section digunakan untuk mengelompokkan tema besar pada halaman, yang juga memudahkan saya dalam menulis aturan CSS secara lebih terstruktur tanpa nama kelas yang generik.

2. **Ketika Anda mengatur CSS Anda agar tetap responsive, tantangan tata letak apa yang Anda temukan? Bagaimana Anda mengevaluasi elemen mana yang harus diubah posisinya atau diprioritaskan ukurannya saat berpindah dari tampilan desktop ke mobile?**

   Tantangan utama terletak pada elemen dekoratif yang posisinya diatur secara manual menggunakan position absolute. Garis vertikal beserta titik penanda pada timeline memerlukan penyesuaian posisi agar tidak terpotong pada layar sempit. Tata letak bagian hero yang semula sejajar horizontal juga diubah menjadi vertikal pada tampilan mobile, disertai penyesuaian ukuran foto profil agar tetap proporsional. Elemen ilustrasi astronot yang bersifat dekoratif saya sembunyikan sepenuhnya pada tampilan mobile karena ruang yang terbatas. Prinsip yang saya gunakan adalah memprioritaskan elemen yang membawa informasi, sedangkan elemen dekoratif menjadi bagian pertama yang disesuaikan atau disembunyikan apabila ruang tidak mencukupi. Evaluasi dilakukan dengan menguji tampilan secara langsung melalui device toolbar pada website karena posisi absolute rentan sekali terlihat sesuai di satu lebar layar, tetapi rusak di lebar lain.

3. **Website yang Anda buat saat ini adalah static web murni. Batasan apa yang Anda rasakan saat mencoba menyajikan informasi pada portofolio Anda secara optimal? Berdasarkan batasan tersebut, fungsionalitas dinamis apa yang paling ingin Anda persiapkan dan tambahkan pada iterasi proyek selanjutnya?**

   Batasan yang paling terasa adalah setiap pembaruan konten, misalnya menambahkan pengalaman baru pada timeline, harus dilakukan dengan mengubah berkas HTML secara langsung tanpa adanya mekanisme pengisian data yang lebih praktis. Pada iterasi berikutnya, saya berencana menambahkan model Django untuk data pengalaman beserta panel admin sehingga pembaruan konten dapat dilakukan tanpa perlu mengubah kode. Saya juga berencana mengganti tautan email statis dengan formulir kontak fungsional yang terhubung langsung dengan tampilan Django.

**AI Disclosure — Tugas 1**

Dalam pengerjaan Tugas Individu 1 ini, saya memanfaatkan AI, yaitu Claude dan sebagian Google Gemini pada tahap awal eksplorasi ide. Setiap kali menghadapi kendala teknis, kebingungan mengenai penyebab suatu masalah, atau mencari arah tampilan yang sesuai dengan konsep yang saya bayangkan, AI membantu saya memahami konsep dasar di balik permasalahan tersebut.

Secara garis besar, hal hal yang saya lakukan dengan AI pada codebase ini meliputi:
- Berdiskusi mengenai arah desain visual yang sesuai dengan konsep yang saya bayangkan, termasuk menolak beberapa opsi yang ditawarkan AI karena dirasa kurang cocok atau kurang memungkinkan dikerjakan dalam waktu yang tersisa.
- Meminta bantuan menyusun struktur dan isi README.md, termasuk merapikan tata bahasa pada jawaban refleksi.
- Meminta bantuan penambahan comment pada style.css, termasuk merapikan tata bahasa comment tersebut.

Saya tidak pernah menyalin dan menempelkan kode yang diberikan AI ke dalam proyek begitu saja. Setiap saran atau potongan kode yang diberikan selalu saya pelajari terlebih dahulu alur logikanya, saya uji coba secara bertahap pada localhost dan saya sesuaikan secara manual agar sesuai dengan kebutuhan proyek.

Saya juga menemukan bahwa AI tidak selalu tepat dalam mendiagnosis suatu masalah pada percobaan pertama sehingga saya perlu melakukan verifikasi mandiri sebelum menerima kesimpulan yang diberikan. Beberapa contoh konkret mengenai hal ini dapat dilihat pada rincian interaksi di bawah.

Berikut 3 contoh interaksi saya bersama AI selama proses pengerjaan:

1. **Debugging Halaman yang Tampil Tanpa Gaya Sama Sekali**
   * Prompt: "Kenapa CSS aku nggak muncul sama sekali padahal filenya udah aku buat?"
   * Tujuan: Mencari penyebab halaman tampil polos tanpa gaya apa pun padahal file style.css sudah dibuat dan dihubungkan.
   * Respon AI: Meminta saya membuka tab Network di DevTools untuk memastikan apakah file style.css benar dimuat browser atau gagal, sebelum menyimpulkan penyebabnya.
   * Tindakan Saya: Saya buka sendiri tab Network dan laporkan hasilnya (semua file berstatus 200, cuma favicon yang 404). Dari situ AI menyimpulkan penyebabnya bukan file gagal dimuat, melainkan nama class di CSS dan HTML yang tidak cocok satu sama lain.

2. **Menentukan Batas Antara Tema Angkasa yang Elegan dan Kekanakan**
   * Prompt: "Kalau aku tambahin planet atau bulan gitu, apa kesannya jadi kekanak-kanakan?"
   * Tujuan: Menentukan gaya visual dark space yang tetap terlihat profesional untuk portofolio, bukan seperti desain anak-anak.
   * Respon AI: Menjelaskan bahwa yang membedakan childish atau elegan itu gaya render-nya (kartun berwarna cerah vs bentuk blur lembut abstrak), bukan objeknya, lalu menyarankan pendekatan starfield dan glow murni CSS.
   * Tindakan Saya: Saya pertimbangkan saran itu, tetapi tetap saya sendiri yang memutuskan kombinasi akhirnya, termasuk menolak beberapa opsi referensi visual lain yang ditawarkan karena dirasa kurang cocok atau terlalu banyak kerjaan tambahan untuk tenggat waktu saya.

3. **Verifikasi Lisensi Aset dari Figma Community**
   * Prompt: "Ini Licensed under CC BY 4.0, artinya apa?"
   * Tujuan: Memastikan aset background dan ilustrasi astronot dari Figma Community boleh saya pakai untuk tugas kuliah tanpa melanggar hak cipta.
   * Respon AI: Menjelaskan CC BY 4.0 mengizinkan pemakaian dan modifikasi bebas, asal mencantumkan atribusi ke pembuat aslinya.
   * Tindakan Saya: AI sendiri tidak bisa membuka halaman Figma-nya karena diblokir otomatisasi, jadi saya yang membuka dan mengecek langsung ke halamannya untuk memastikan filenya benar bisa diduplikasi gratis, sebelum saya cantumkan kreditnya di README ini.