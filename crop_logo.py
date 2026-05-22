from PIL import Image
import os

img_path = r'C:\Users\Ziyodjon\.gemini\antigravity\brain\8737d435-0160-4235-a185-e991c77b4c43\media__1779427186611.jpg'
if not os.path.exists(img_path):
    print(f'Rasm topilmadi: {img_path}')
else:
    img = Image.open(img_path)
    width, height = img.size
    print(f'Original size: {width}x{height}')
    
    # Gemini yulduzini olib tashlash va logoni o'rtaga olish.
    # O'ngdan va pastdan 15% qirqamiz.
    crop_box = (0, 0, int(width * 0.92), int(height * 0.90))
    cropped = img.crop(crop_box)
    
    out_dir = r'c:\Users\Ziyodjon\Zdn projects\Zdn projects\StartUp uchun\TenderHelper\frontend\public\assets'
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'logo-dark.jpg')
    cropped.save(out_path)
    print(f'Cropped and saved to: {out_path}')
