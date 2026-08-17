import qrcode
import os

url = input("Enter the URL :").strip()
file_path = "C:\\Users\\jurca\\Hicheel\\Self\\python-learning\\QRcodes\\QRCode01.png"

qr = qrcode.QRCode()
qr.add_data(url)

img = qr.make_image(fill_color="brown", back_color="green")
img.save(file_path)