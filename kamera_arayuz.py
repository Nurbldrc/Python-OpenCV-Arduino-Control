# --- KÜTÜPHANELER (ALET ÇANTAMIZ) ---
import tkinter as tk                # Pencereler ve butonlar için (Arayüz)
from tkinter import messagebox      # Hata veya bilgi kutucuğu çıkarmak için
import cv2                          # OpenCV: Kamerayı açmak ve görüntüyü işlemek için (Gözümüz)
import mediapipe as mp              # Google'ın Yapay Zekası: Eli ve parmakları tanıyan beyin
import pyfirmata                    # Arduino ile Python'u konuşturan kütüphane (Tercüman)
from PIL import Image, ImageTk      # OpenCV görüntüsünü Tkinter penceresine çeviren araç
import traceback                    # Hata oluşursa detayını görmek için (Dedektif)

# --- GLOBAL DEĞİŞKENLER (HER YERDEN ERİŞİLEBİLENLER) ---
kamera = None       # Kamerayı başta boş tanımlıyoruz
board = None        # Arduino bağlantısı başta yok
leds = []           # LED pinlerini saklayacağımız boş liste
running = False     # Sistemin çalışıp çalışmadığını kontrol eden anahtar

# --- MEDIAPIPE AYARLARI (YAPAY ZEKA KURULUMU) ---
mp_draw = mp.solutions.drawing_utils  # Elin üzerine kırmızı iskelet çizgilerini çizen araç
mp_hand = mp.solutions.hands          # El tanıma modelini çağırıyoruz

# Modeli başlatıyoruz:
# min_detection_confidence=0.5 -> %50 emin olmadan "bu bir eldir" deme.
hands_model = mp_hand.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Parmak uçlarının haritadaki numaraları (Başparmak:4, İşaret:8, Orta:12, Yüzük:16, Serçe:20)
tipIds = [4, 8, 12, 16, 20] 

# --- FONKSİYONLAR (İŞ YAPAN PARÇALAR) ---

def arduino_baglan():
    """
    Bu fonksiyon 'BAĞLAN' butonuna basınca çalışır.
    Arduino ile bağlantıyı kurar ve LED pinlerini hazırlar.
    """
    global board, leds  # Global değişkenleri içeri alıyoruz ki değiştirebilelim
    port = ent_port.get() # Kutucuğa yazılan port ismini (örn: COM4) alıyoruz
    
    # Kullanıcıya bilgi veriyoruz
    lbl_durum_port.config(text="Bağlanıyor...", fg="orange")
    pencere.update() # Arayüzü donmasın diye güncelliyoruz
    
    try:
        # --- KRİTİK NOKTA: ARDUINO BAĞLANTISI ---
        board = pyfirmata.Arduino(port) # Belirtilen porttan bağlanmayı dener
        
        # LED'lerin takılı olduğu pinleri tanımlıyoruz (13, 12, 11, 10, 9)
        leds = [
            board.get_pin('d:13:o'), # d: Dijital Pin, 13: Pin No, o: Output (Çıkış)
            board.get_pin('d:12:o'),
            board.get_pin('d:11:o'),
            board.get_pin('d:10:o'),
            board.get_pin('d:9:o')
        ]
        
        # Başarılı olursa butonları ayarlıyoruz
        lbl_durum_port.config(text=f"BAĞLANDI ({port})", fg="green")
        messagebox.showinfo("Başarılı", "Arduino bağlandı!")
        btn_baglan.config(state="disabled") # Bağlan butonunu kapat (tekrar basılmasın)
        btn_baslat.config(state="normal")   # Başlat butonunu aç (artık basılabilir)
        
    except Exception as e:
        # Hata olursa (Kablo takılı değilse vs.) program çökmez, buraya düşer
        lbl_durum_port.config(text="HATA!", fg="red")
        print(f"ARDUINO HATASI: {e}") 
        messagebox.showerror("Hata", f"Arduino Hatası:\n{e}")

def ledleri_yak(parmak_sayisi):
    """
    Gelen parmak sayısına göre LED'leri yakar.
    Örn: 3 gelirse ilk 3 LED'i yakar.
    """
    if board is None: return # Arduino yoksa işlem yapma, geri dön
    
    # Güvenlik önlemi: Maksimum 5 LED var, 6 gelirse hata olmasın diye 5'e eşitliyoruz
    if parmak_sayisi > 5: parmak_sayisi = 5
    
    try:
        # Önce bütün LED'leri söndürüyoruz (Temiz sayfa açmak için)
        for led in leds: led.write(0)
        
        # Sonra parmak sayısı kadarını yakıyoruz
        for i in range(parmak_sayisi): leds[i].write(1)
            
    except Exception as e:
        print(f"LED YAKMA HATASI: {e}") # Bir LED bozuksa program durmasın, hatayı yazsın

def kamerayi_baslat():
    """
    'SİSTEMİ BAŞLAT' butonuna basınca çalışır.
    Pencereyi büyütür ve kamerayı açar.
    """
    global kamera, running
    
    # --- ARAYÜZ NUMARASI ---
    pencere.geometry("900x750")     # Pencereyi aşağı doğru uzatıyoruz (Animasyon gibi)
    frame_kamera_kutusu.config(height=480) # Siyah kutuyu görünür yapıyoruz
    
    if kamera is None:
        print("Kamera başlatılıyor...") 
        kamera = cv2.VideoCapture(0) # 0: Bilgisayarın varsayılan kamerası
        
        # Kamera gerçekten açıldı mı kontrolü
        if not kamera.isOpened():
            messagebox.showerror("Kamera Hatası", "Kamera açılamadı!")
            return

        running = True # Döngüyü başlatmak için anahtarı açıyoruz
        lbl_kamera_durum.config(text="Sistem Çalışıyor", fg="green")
        video_akisi() # Sonsuz döngü fonksiyonunu ilk kez çağırıyoruz

def video_akisi():
    """
    BU KODUN KALBİDİR.
    Sürekli kendini tekrar eder, fotoğrafı çeker, parmağı sayar, ekrana basar.
    """
    global running
    
    try:
        if kamera is not None and running:
            # 1. Kameradan bir kare fotoğraf oku
            ret, frame = kamera.read()
            
            if not ret: # Eğer fotoğraf okuyamadıysa (kamera koptuysa)
                print("HATA: Görüntü gelmiyor!")
                return

            # 2. RENK DÜZELTME (Çok Önemli!)
            # OpenCV renkleri BGR (Mavi-Yeşil-Kırmızı) okur.
            # Bizim gözümüz ve ekranlar RGB (Kırmızı-Yeşil-Mavi) görür.
            # O yüzden renkleri ters çeviriyoruz.
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 3. EL TESPİTİ YAP (MediaPipe'e gönderiyoruz)
            results = hands_model.process(frame_rgb)
            
            total_fingers = 0 # Sayacı sıfırla
            
            # Eğer ekranda el varsa...
            if results.multi_hand_landmarks:
                for hand_landmark in results.multi_hand_landmarks:
                    # Elin üzerine kırmızı çizgileri (iskeleti) çiz
                    mp_draw.draw_landmarks(frame_rgb, hand_landmark, mp_hand.HAND_CONNECTIONS)
                    
                    # --- KOORDİNAT HESAPLAMA ---
                    lmList = []
                    myHands = results.multi_hand_landmarks[0]
                    h, w, c = frame_rgb.shape # Ekranın boyunu enini al
                    
                    # 21 noktanın tek tek koordinatını buluyoruz
                    for id, lm in enumerate(myHands.landmark):
                        # MediaPipe '0.5' gibi oran verir, biz bunu piksele (örn: 300. piksel) çeviririz
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        lmList.append([id, cx, cy])
                    
                    # --- PARMAK SAYMA MANTIĞI ---
                    if len(lmList) != 0:
                        fingers = []
                        
                        # Başparmak (X eksenine bakılır - Sağda mı solda mı?)
                        # Uç noktası (4), alt noktasından (3) daha sağdaysa açıktır
                        if lmList[tipIds[0]][1] > lmList[tipIds[0]-1][1]: fingers.append(1)
                        else: fingers.append(0)
                        
                        # Diğer 4 Parmak (Y eksenine bakılır - Yukarıda mı aşağıda mı?)
                        # Uç noktası, alt boğumundan daha küçükse (yukarıdaysa) açıktır.
                        # (Not: Ekran koordinatlarında yukarı gittikçe sayı küçülür)
                        for id in range(1, 5):
                            if lmList[tipIds[id]][2] < lmList[tipIds[id]-2][2]: fingers.append(1)
                            else: fingers.append(0)
                        
                        total_fingers = fingers.count(1) # Açık olanları (1'leri) topla
            
            # 4. FİZİKSEL SONUÇ (Arduino'ya komut gönder)
            ledleri_yak(total_fingers)
            
            # 5. ARAYÜZÜ GÜNCELLE (Yazıları değiştir)
            if total_fingers > 0:
                lbl_sonuc.config(text=f"{total_fingers} Parmak -> LED Yanıyor", fg="#2196F3")
            else:
                lbl_sonuc.config(text="0 Parmak / LED Kapalı", fg="red")

            # 6. RESMİ EKRANA BASMA (OpenCV -> Tkinter Dönüşümü)
            resim = Image.fromarray(frame_rgb) # Resmi oluştur
            gorsel = ImageTk.PhotoImage(image=resim) # Tkinter formatına çevir
            kamera_etiketi.configure(image=gorsel) # Etiketin içine koy
            kamera_etiketi.imgtk = gorsel # Hafızada tut
            
            # 7. DÖNGÜYÜ SAĞLA (En Önemli Kısım)
            # while True kullanmıyoruz! Arayüz donmasın diye.
            # "10 milisaniye sonra beni (video_akisi fonksiyonunu) tekrar çağır" diyoruz.
            kamera_etiketi.after(10, video_akisi)
            
    except Exception as e:
        # Beklenmedik bir hata olursa program kapanmasın, hatayı yazsın
        print("HATA OLUŞTU:")
        traceback.print_exc() 

def kapat():
    """ 'ÇIKIŞ' butonuna basınca her şeyi temizleyip kapatır """
    global kamera, running, board
    running = False
    if kamera: kamera.release() # Kamerayı serbest bırak (Işığı sönsün)
    if board:
        try:
            for led in leds: led.write(0) # Çıkarken LED'leri söndür
        except: pass
    pencere.destroy() # Pencereyi yok et

# --- ARAYÜZ TASARIMI (GÖRÜNÜM KISMI) ---
pencere = tk.Tk()
pencere.title("HATA AYIKLAMA MODU - LED KONTROL")
pencere.geometry("700x200") # Başlangıçta küçük pencere
pencere.configure(bg="#f5f5f5") # Arka plan rengi

# Üst Panel (Port ve Bağlan butonu)
frm_ust = tk.Frame(pencere, bg="#e0e0e0", pady=10, relief="groove", bd=2)
frm_ust.pack(side="top", fill="x")

# Port Giriş Kutusu
tk.Label(frm_ust, text="Arduino Port:", bg="#e0e0e0").pack(side="left", padx=5)
ent_port = tk.Entry(frm_ust, width=8)
ent_port.insert(0, "COM4") # Varsayılan olarak COM4 yazsın
ent_port.pack(side="left", padx=5)

# Bağlan Butonu
btn_baglan = tk.Button(frm_ust, text="BAĞLAN", command=arduino_baglan, bg="#FF9800", fg="white")
btn_baglan.pack(side="left", padx=10)

# Durum Yazısı
lbl_durum_port = tk.Label(frm_ust, text="Bekleniyor...", bg="#e0e0e0")
lbl_durum_port.pack(side="left", padx=10)

# Kamera Alanı (Başlangıçta gizli gibi, yüksekliği 1 piksel)
tk.Label(pencere, text="KAMERA GÖRÜNTÜSÜ", bg="#f5f5f5").pack(pady=5)
frame_kamera_kutusu = tk.Frame(pencere, width=640, height=1, bg="black")
frame_kamera_kutusu.pack_propagate(False) # İçindekine göre boyutu değişmesin, sabit kalsın
frame_kamera_kutusu.pack(padx=10, pady=5)

kamera_etiketi = tk.Label(frame_kamera_kutusu, bg="black")
kamera_etiketi.pack(fill="both", expand=True)

# Alt Panel (Kontrol Butonları)
frm_alt = tk.Frame(pencere, bg="#ddd", pady=15)
frm_alt.pack(side="bottom", fill="x")

# Başlat Butonu
btn_baslat = tk.Button(frm_alt, text="SİSTEMİ BAŞLAT", command=kamerayi_baslat, state="disabled", bg="#4CAF50", fg="white")
btn_baslat.pack(side="left", padx=20)

# Sonuç Yazıları
lbl_kamera_durum = tk.Label(frm_alt, text="", bg="#ddd")
lbl_kamera_durum.pack(side="left")
lbl_sonuc = tk.Label(frm_alt, text="Sonuç Bekleniyor...", font=("Arial", 12), bg="#ddd")
lbl_sonuc.pack(side="left", padx=40)

# Çıkış Butonu
btn_cikis = tk.Button(frm_alt, text="ÇIKIŞ", command=kapat, bg="#f44336", fg="white")
btn_cikis.pack(side="right", padx=20)

# Pencereyi açık tutan döngü
pencere.mainloop()