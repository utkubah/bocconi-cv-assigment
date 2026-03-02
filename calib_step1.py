import glob
import os

# 1) Burayı kendi uzantına göre ayarla: jpg / png / jpeg
IMAGE_GLOB = "data/calibration/*.jpeg"
images = sorted(glob.glob(IMAGE_GLOB))

print("Folder:", os.path.dirname(IMAGE_GLOB))
print("Found images:", len(images))

# İlk 5 dosyayı gösterelim (kontrol için)
for p in images[:5]:
    print(" -", p)

if len(images) == 0:
    print("\nHATA: Görsel bulunamadı.")
    print("Kontrol et:")
    print(" - Fotoğraflar calib_images/ içinde mi?")
    print(" - Uzantı .jpg mi? Değilse IMAGE_GLOB'u değiştir.")