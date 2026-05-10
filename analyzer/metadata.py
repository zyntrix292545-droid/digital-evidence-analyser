import os
import datetime
from PIL import Image

def extract_metadata(filepath):
    metadata = {
        "author": "N/A",
        "created": "N/A",
        "file_type": "N/A",
        "gps_latitude": "N/A",
        "gps_longitude": "N/A",
        "file_size": "N/A",
        "modified": "N/A",
        "file_extension": "N/A",
        "image_width": "N/A",
        "image_height": "N/A",
        "image_format": "N/A",
        "image_mode": "N/A"
    }
    
    if not os.path.exists(filepath):
        return metadata

    # OS metadata
    try:
        metadata["file_size"] = os.path.getsize(filepath)
        
        # Created and modified dates
        ctime = os.path.getctime(filepath)
        mtime = os.path.getmtime(filepath)
        
        metadata["created"] = datetime.datetime.fromtimestamp(ctime).strftime('%Y-%m-%d %H:%M:%S')
        metadata["modified"] = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        
        # File extension
        _, ext = os.path.splitext(filepath)
        metadata["file_extension"] = ext.lower() if ext else "N/A"
        
        # Fallback file_type to extension if no other info
        if ext:
            metadata["file_type"] = ext.replace(".", "").upper()
            
    except Exception as e:
        print(f"Error reading file stats: {e}")

    # Image metadata using Pillow
    try:
        with Image.open(filepath) as img:
            metadata["image_width"] = img.width
            metadata["image_height"] = img.height
            metadata["image_format"] = img.format
            metadata["image_mode"] = img.mode
            metadata["file_type"] = img.format # Use Pillow's format as file_type if available
    except Exception:
        # Not an image or cannot be opened by Pillow
        pass
        
    return metadata
