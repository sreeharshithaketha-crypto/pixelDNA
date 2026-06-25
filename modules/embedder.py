from imwatermark import WatermarkEncoder
import cv2

def embed_watermark(image_path, watermark_text, output_path):
    bgr = cv2.imread(image_path)
    
    if bgr is None:
        print(f"Error: Could not load image from {image_path}")
        return
    
    wm_bytes = watermark_text.encode('utf-8')
    
    encoder = WatermarkEncoder()
    encoder.set_watermark('bytes', wm_bytes)
    
    watermarked = encoder.encode(bgr, 'dwtDct')
    
    cv2.imwrite(output_path, watermarked)
    print(f"Watermark embedded successfully -> {output_path}")
    print(f"Watermark length used: {len(wm_bytes) * 8} bits")

if __name__ == "__main__":
    embed_watermark("test_image.jpg", "user001_2026", "watermarked_output.png")