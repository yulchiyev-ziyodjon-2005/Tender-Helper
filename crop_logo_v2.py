from PIL import Image
import os

img_path = r'C:\Users\Ziyodjon\.gemini\antigravity\brain\8737d435-0160-4235-a185-e991c77b4c43\media__1779427186611.jpg'
img = Image.open(img_path)
width, height = img.size

# Let's crop the center part tightly
left = int(width * 0.25)
top = int(height * 0.15)
right = int(width * 0.75)
bottom = int(height * 0.85)

cropped = img.crop((left, top, right, bottom))
out_dir = r'c:\Users\Ziyodjon\Zdn projects\Zdn projects\StartUp uchun\TenderHelper\frontend\public\logo'
os.makedirs(out_dir, exist_ok=True)

# Save as PNG
out_path = os.path.join(out_dir, 'logo-cropped.png')
cropped.save(out_path, format='PNG')
print(f'Cropped dimensions: {cropped.size}')
print(f'Saved to {out_path}')
