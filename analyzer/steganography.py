import os
from PIL import Image

def detect_steganography(filepath):
    try:
        # 1. Check if the file is an image
        valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp'}
        _, ext = os.path.splitext(filepath)
        if ext.lower() not in valid_extensions:
            return {
                "detected": False, 
                "findings": ["Not an image file, skipping steganography analysis"]
            }

        detected = False
        findings = []

        # 2. Open image using Pillow
        with Image.open(filepath) as img:
            # Convert to RGB to ensure we can consistently access the red channel (index 0)
            img = img.convert('RGB')
            pixels = list(img.getdata())
            
            # CHECK 1: LSB (Least Significant Bit) Analysis
            pixels_to_check = pixels[:1000]
            if len(pixels_to_check) > 0:
                # Count how many pixels have an LSB of 1 in the red channel
                ones_count = sum(1 for pixel in pixels_to_check if (pixel[0] & 1) == 1)
                ratio_of_ones = ones_count / len(pixels_to_check)
                
                # If the ratio of 1s is between 0.4 and 0.6, flag as suspicious
                if 0.4 <= ratio_of_ones <= 0.6:
                    detected = True
                    findings.append(f"Suspicious LSB distribution detected in red channel (Ratio of 1s: {ratio_of_ones:.2f})")
                else:
                    findings.append(f"Normal LSB distribution in red channel (Ratio of 1s: {ratio_of_ones:.2f})")
            
            # CHECK 2: File size anomaly check
            actual_size = os.path.getsize(filepath)
            width, height = img.size
            expected_size = width * height * 3
            
            # If actual file is more than 20% bigger than expected, flag as suspicious
            if actual_size > expected_size * 1.2:
                detected = True
                findings.append(f"Suspicious file size anomaly: Actual size ({actual_size} bytes) is >20% larger than expected uncompressed size (~{expected_size} bytes)")
            else:
                findings.append(f"File size anomaly check passed (Actual: {actual_size} bytes, Expected: ~{expected_size} bytes)")

        # 3. Return the results dictionary
        return {
            "detected": detected,
            "findings": findings
        }

    except Exception as e:
        # 4. Wrap everything in try/except so the app never crashes
        return {
            "detected": False, 
            "findings": [f"Analysis error: {str(e)}"]
        }
