import time
import qrcode
from pyngrok import ngrok

# Buka tunnel ke localhost:5000
http_tunnel = ngrok.connect(5000, "http")
public_url = http_tunnel.public_url

# Print URL
print("Ngrok URL:", public_url)

# Buat QR Code dari URL
qr = qrcode.make(public_url)
qr.show()  # Tampilkan QR Code langsung

# Biarkan program tetap berjalan agar ngrok tetap aktif
try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    print("Shutdown ngrok...")
    ngrok.disconnect(public_url)
