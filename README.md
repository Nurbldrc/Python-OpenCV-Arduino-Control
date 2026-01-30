# Python-OpenCV-Arduino-Control
# 🖐️ El Hareketleri ile LED Kontrol Sistemi (Bitirme Projesi)

Bu proje, bilgisayar kamerası aracılığıyla el hareketlerini algılayarak bağlı olan LED'leri kontrol etmeyi sağlar. Görüntü işleme teknikleri kullanılarak temassız bir kontrol mekanizması oluşturulmuştur.

## 🌟 Özellikler
* **Gerçek Zamanlı Tespit:** Kamera üzerinden el ve parmak hareketlerinin anlık analizi.
* **Görüntü İşleme:** MediaPipe ve OpenCV kütüphaneleri ile yüksek doğrulukta el izleme.
* **Donanım Entegrasyonu:** Algılanan hareketlerin seri haberleşme üzerinden Arduino'ya iletilmesi (Kodlar yakında eklenecek).

## 🛠️ Kullanılan Teknolojiler
* **Programlama Dili:** Python
* **Kütüphaneler:** OpenCV, MediaPipe, PySerial (Haberleşme için)
* **Donanım:** Arduino (LED devresi ile)

## 🎥 Proje Görselleri
*(Buraya elini kameraya tuttuğun ve LED'in yandığı bir fotoğraf veya GIF eklersen harika olur!)*

## 🚀 Çalıştırma Talimatları
1. Gerekli kütüphaneleri yükleyin: `pip install opencv-python mediapipe pyserial`
2. `main.py` dosyasını çalıştırın.
3. Kameraya elinizi göstererek sistemi test edin.
