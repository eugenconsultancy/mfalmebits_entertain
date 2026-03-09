"""
Image optimization utilities for web performance
"""

from PIL import Image
import os
from io import BytesIO
from django.core.files.base import ContentFile
import logging

logger = logging.getLogger(__name__)

def optimize_uploaded_image(image_field, sizes=None, quality=85):
    """
    Create responsive image sizes with WebP format
    
    Args:
        image_field: Django ImageField instance
        sizes: Dict of size names and dimensions
        quality: JPEG/WebP quality (1-100)
    
    Returns:
        Dict with paths to optimized images
    """
    if not sizes:
        sizes = {
            'thumbnail': (300, 200),
            'medium': (800, 600),
            'large': (1200, 900),
        }
    
    if not image_field or not image_field.path:
        logger.warning("No image field provided or file doesn't exist")
        return {}
    
    try:
        base_path = image_field.path
        base_name, ext = os.path.splitext(base_path)
        base_url = image_field.url
        base_url_path, _ = os.path.splitext(base_url)
        
        optimized_paths = {}
        
        # Open original image
        with Image.open(base_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            
            # Create resized versions
            for size_name, dimensions in sizes:
                # Create copy for resizing
                resized_img = img.copy()
                resized_img.thumbnail(dimensions, Image.Resampling.LANCZOS)
                
                # Save WebP version
                webp_path = f"{base_name}_{size_name}.webp"
                webp_url = f"{base_url_path}_{size_name}.webp"
                resized_img.save(webp_path, 'WEBP', quality=quality)
                optimized_paths[f'webp_{size_name}'] = webp_url
                
                # Save JPEG version
                jpeg_path = f"{base_name}_{size_name}.jpg"
                jpeg_url = f"{base_url_path}_{size_name}.jpg"
                resized_img.save(jpeg_path, 'JPEG', quality=quality, optimize=True)
                optimized_paths[f'jpeg_{size_name}'] = jpeg_url
        
        return optimized_paths
        
    except Exception as e:
        logger.error(f"Error optimizing image: {e}")
        return {}


def generate_webp_version(image_field, quality=85):
    """
    Generate WebP version of an image
    """
    if not image_field or not image_field.path:
        return None
    
    try:
        base_path = image_field.path
        base_name, _ = os.path.splitext(base_path)
        webp_path = f"{base_name}.webp"
        
        with Image.open(base_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            
            img.save(webp_path, 'WEBP', quality=quality)
        
        return webp_path
        
    except Exception as e:
        logger.error(f"Error generating WebP: {e}")
        return None


def get_image_dimensions(image_field):
    """
    Get image dimensions safely
    """
    if not image_field or not image_field.path:
        return None
    
    try:
        with Image.open(image_field.path) as img:
            return img.size
    except Exception as e:
        logger.error(f"Error getting image dimensions: {e}")
        return None


def create_image_thumbnail(image_field, size=(150, 150), quality=85):
    """
    Create a thumbnail for an image
    """
    if not image_field or not image_field.path:
        return None
    
    try:
        base_path = image_field.path
        base_name, ext = os.path.splitext(base_path)
        thumb_path = f"{base_name}_thumb.jpg"
        
        with Image.open(base_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(thumb_path, 'JPEG', quality=quality, optimize=True)
        
        return thumb_path
        
    except Exception as e:
        logger.error(f"Error creating thumbnail: {e}")
        return None
