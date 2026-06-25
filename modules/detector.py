import sys
import os
sys.path.append(os.path.dirname(__file__))

from ela import generate_ela
from hasher import compare_hashes
from extracter import extract_watermark

def run_detection(original_path, suspect_path, expected_watermark="user001_2026", wm_length_bits=96, hash_threshold=10, ela_output_path="detector_ela_output.jpg"):
    """
    Combines ELA, perceptual hashing, and watermark extraction
    to give a final tamper verdict on a suspect image.
    """
    print("=" * 50)
    print("PIXELDNA - TAMPER DETECTION REPORT")
    print("=" * 50)
    
    # Layer 1: Perceptual Hash Comparison
    print("\n[1] Perceptual Hash Check")
    hash_diff = compare_hashes(original_path, suspect_path, threshold=hash_threshold)
    hash_flag = hash_diff > hash_threshold
    
    # Layer 2: ELA Analysis
    print("\n[2] Error Level Analysis")
    max_diff = generate_ela(suspect_path, ela_output_path)
    
    # Layer 3: Watermark Extraction
    print("\n[3] Watermark Verification")
    extracted = extract_watermark(suspect_path, wm_length_bits)
    watermark_flag = extracted != expected_watermark
    
    # Final Verdict
    print("\n" + "=" * 50)
    print("FINAL VERDICT")
    print("=" * 50)
    
    if hash_flag or watermark_flag:
        print("STATUS: TAMPERED / SUSPICIOUS")
        print(f"  - Hash difference: {hash_diff} (threshold: {hash_threshold})")
        print(f"  - Watermark match: {not watermark_flag}")
    else:
        print("STATUS: AUTHENTIC")
        print(f"  - Hash difference: {hash_diff} (within threshold)")
        print(f"  - Watermark verified: {expected_watermark}")
    
    print("=" * 50)
    
    return {
        "hash_diff": hash_diff,
        "ela_max_diff": max_diff,
        "watermark_extracted": extracted,
        "tampered": hash_flag or watermark_flag
    }

if __name__ == "__main__":
    run_detection("test_image.jpg", "tampered_test.jpg")