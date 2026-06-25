from imwatermark import WatermarkDecoder
import cv2

def extract_watermark(image_path, wm_length_bits=72):
    bgr = cv2.imread(image_path)
    print(f"Image loaded: {bgr is not None}, shape: {bgr.shape if bgr is not None else 'N/A'}")
    
    decoder = WatermarkDecoder('bytes', wm_length_bits)
    watermark = decoder.decode(bgr, 'dwtDct')
    print(f"Raw decoded bytes: {watermark}")
    
    decoded_text = watermark.decode('utf-8', errors='replace').strip('\x00')
    safe_print_text = decoded_text.encode('ascii', errors='backslashreplace').decode('ascii')
    print(f"Extracted watermark: {safe_print_text}")
    return decoded_text

if __name__ == "__main__":
    extract_watermark("watermarked_output.png", wm_length_bits=72)