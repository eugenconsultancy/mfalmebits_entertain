from PIL import Image
import os
from io import BytesIO
from django.core.files.base import ContentFile

def optimize_uploaded_image(image_field, quality=85, max_width=1920, max_height=1080, convert_to_webp=True):
    """
    Optimize uploaded image by resizing and compressing.
    
    Args:
        image_field: Django ImageField instance
        quality: JPEG/WebP quality (1-100)
        max_width: Maximum width in pixels
        max_height: Maximum height in pixels
        convert_to_webp: Whether to convert to WebP format
    
    Returns:
        bool: True if optimization succeeded
    """
    try:
        # Open the image
        img = Image.open(image_field)
        
        # Convert RGBA to RGB if necessary
        if img.mode == 'RGBA':
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3])
            img = rgb_img
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if too large
        if img.width > max_width or img.height > max_height:
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Save to buffer
        buffer = BytesIO()
        
        if convert_to_webp:
            # Convert to WebP
            img.save(buffer, format='WEBP', quality=quality, method=6)
            extension = '.webp'
        else:
            # Save as JPEG
            img.save(buffer, format='JPEG', quality=quality, optimize=True)
            extension = '.jpg'
        
        # Create new file name
        original_name = os.path.splitext(image_field.name)[0]
        new_name = f"{original_name}{extension}"
        
        # Replace the file
        buffer.seek(0)
        image_field.save(new_name, ContentFile(buffer.read()), save=False)
        
        return True
        
    except Exception as e:
        print(f"Image optimization failed: {e}")
        return False