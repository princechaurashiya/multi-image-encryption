"""
Security Analysis Script

Analyzes the encryption algorithm's security properties:
1. Correlation coefficient analysis (Rxy)
2. NPCR and UACI for differential attack resistance
3. Generates comprehensive security report
"""

import argparse
import os
from pathlib import Path
from security_analysis import SecurityAnalyzer
import numpy as np
from PIL import Image
from tabulate import tabulate


def analyze_folder_correlation(folder_path: str) -> dict:
    """Analyze correlation for all images in a folder"""
    results = {}
    
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' not found")
        return results
    
    image_files = [f for f in os.listdir(folder_path) 
                   if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not image_files:
        print(f"No images found in '{folder_path}'")
        return results
    
    print(f"\n📊 Analyzing correlation for images in '{folder_path}'...")
    
    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        try:
            corr = SecurityAnalyzer.analyze_correlation(image_path)
            results[image_file] = corr
            print(f"  ✓ {image_file}")
        except Exception as e:
            print(f"  ✗ {image_file}: {str(e)}")
    
    return results


def create_single_image_encryptor():
    """
    Create an encryption function for a single image.
    This wrapper adapts the batch encryption to work with single images
    for NPCR/UACI analysis.
    """
    import hashlib
    import tempfile
    import shutil
    from chaotic_maps.tdlcic import tdlcic_map
    from dna_operations import core

    def encrypt_single_image(image_array: np.ndarray) -> np.ndarray:
        """Encrypt a single image and return the encrypted array"""
        # Ensure image is in correct format (M, N, n)
        if len(image_array.shape) == 2:
            # Grayscale - add channel dimension
            P = image_array[:, :, np.newaxis]
        else:
            P = image_array.copy()

        M, N, n = P.shape
        sum_pixels = M * N

        # Generate plaintext-related key
        K = hashlib.sha512(P.tobytes()).hexdigest()
        k = np.array([int(K[i:i+8], 16) for i in range(0, 128, 8)]) / 256.0
        a, b, x0, y0 = 2 + np.sum(k[0:4]), 2 + np.sum(k[4:8]), np.sum(k[8:12]) % 1, np.sum(k[12:16]) % 1

        # Generate chaotic sequences
        # Need enough values: sum_pixels for x, sum_pixels*n for xy (which uses both x and y)
        num_iterations = sum_pixels * n + 1000
        x, y = tdlcic_map(x0, y0, a, b, num_iterations)
        x, y = x[1000:], y[1000:]
        xy = np.concatenate((x, y))[:sum_pixels * n]
        C_matrix = (np.floor(np.abs(xy) * 1e14).astype(np.uint64) % 8).reshape(M, N, n)

        # DNA Cyclic Shift Encoding
        P_dna1 = core.cyclic_shift_encode(P, C_matrix)

        # Global Exchange Scrambling
        S = np.argsort(x[:sum_pixels])
        G = np.argsort(xy.reshape(sum_pixels, n), axis=1)
        P_dna2_flat = P_dna1.copy().reshape(sum_pixels, 4 * n)
        for i in range(sum_pixels):
            s_i = S[i]
            if i == s_i: continue
            for j in range(n):
                g_ij = G[i, j]
                temp_base = P_dna2_flat[i, j*4:j*4+4].copy()
                P_dna2_flat[i, j*4:j*4+4] = P_dna2_flat[s_i, g_ij*4:g_ij*4+4]
                P_dna2_flat[s_i, g_ij*4:g_ij*4+4] = temp_base
        P_dna2 = P_dna2_flat.reshape(M, N, 4 * n)

        # Multi-Directional DNA Diffusion
        E = (np.floor(np.abs(xy) * 1e14) % 256).astype(np.uint8).reshape(M, N, n)
        E_dna = np.empty((M, N, 4 * n), dtype='<U1')
        for i in range(M):
            for j in range(N):
                for k in range(n):
                    binary_E = format(E[i,j,k], '08b')
                    E_dna[i,j,4*k:4*k+4] = [core.DNA_RULES[0][binary_E[b:b+2]] for b in range(0,8,2)]

        # Lateral diffusion
        P_dna3 = P_dna2.copy()
        for i in range(M):
            for j in range(N):
                for z in range(4 * n):
                    if i == 0:
                        P_dna3[i, j, z] = core.DNA_ADD[P_dna2[i, j, z]][E_dna[i, j, z]]
                    else:
                        add_val = core.DNA_ADD[P_dna2[i, j, z]][P_dna3[i-1, j, z]]
                        P_dna3[i, j, z] = core.DNA_ADD[add_val][E_dna[i, j, z]]

        # Strand diffusion
        P_dna4 = P_dna3.copy()
        for i in range(M):
            for j in range(N):
                P_dna4[i, j, 0] = core.DNA_XOR[P_dna3[i, j, 0]][P_dna3[i, j, -1]]
                for z in range(1, 4 * n):
                    P_dna4[i, j, z] = core.DNA_XOR[P_dna3[i, j, z]][P_dna4[i, j, z-1]]

        # Final decoding to pixels
        P_end = core.final_decode_to_pixels(P_dna4, C_matrix)

        # Return with original shape
        if len(image_array.shape) == 2:
            return P_end[:, :, 0]
        return P_end

    return encrypt_single_image


def analyze_differential_attack(original_folder: str, encrypted_folder: str = None) -> dict:
    """
    Analyze differential attack resistance using correct methodology.

    According to research paper:
    1. Encrypt original image P → C1
    2. Change ONE pixel in P → P'
    3. Encrypt P' → C2
    4. Calculate NPCR and UACI between C1 and C2
    """
    results = {}

    original_files = [f for f in os.listdir(original_folder)
                     if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if not original_files:
        print("No images found in original folder")
        return results

    print(f"\n🔐 Analyzing differential attack resistance...")
    print("   (Comparing C1 vs C2 where C2 encrypts 1-pixel-modified original)")

    # Create encryption function
    encrypt_fn = create_single_image_encryptor()

    for orig_file in original_files:
        original_path = os.path.join(original_folder, orig_file)

        try:
            # Load original image
            original_image = np.array(Image.open(original_path))

            # Analyze using correct methodology
            metrics = SecurityAnalyzer.analyze_differential_attack(
                original_image=original_image,
                encrypt_function=encrypt_fn
            )
            results[orig_file] = metrics
            print(f"  ✓ {orig_file}")
        except Exception as e:
            print(f"  ✗ {orig_file}: {str(e)}")

    return results


def print_correlation_report(results: dict):
    """Print correlation analysis report"""
    if not results:
        return
    
    print("\n" + "="*70)
    print("CORRELATION COEFFICIENT ANALYSIS (Rxy)")
    print("="*70)
    print("Range: [-1, 1] | Close to 0 = Good (Low correlation)")
    print("Theoretical encrypted image values: ~0.0\n")
    
    table_data = []
    for image_name, correlations in results.items():
        table_data.append([
            image_name,
            f"{correlations['horizontal']:.6f}",
            f"{correlations['vertical']:.6f}",
            f"{correlations['diagonal']:.6f}"
        ])
    
    headers = ["Image", "Horizontal", "Vertical", "Diagonal"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # Calculate averages
    if results:
        avg_h = np.mean([v['horizontal'] for v in results.values()])
        avg_v = np.mean([v['vertical'] for v in results.values()])
        avg_d = np.mean([v['diagonal'] for v in results.values()])
        
        print(f"\n📈 Average Correlation Coefficients:")
        print(f"   Horizontal: {avg_h:.6f}")
        print(f"   Vertical:   {avg_v:.6f}")
        print(f"   Diagonal:   {avg_d:.6f}")


def print_differential_attack_report(results: dict):
    """Print differential attack analysis report (like research paper Table 11)"""
    if not results:
        return

    print("\n" + "="*90)
    print("NPCR and UACI.")
    print("="*90)

    # Collect all channel data in order
    headers = ["Image"]
    npcr_row = ["NPCR(%)"]
    uaci_row = ["UACI(%)"]

    all_npcr_values = []
    all_uaci_values = []

    for image_name, metrics in results.items():
        base_name = image_name.rsplit('.', 1)[0]
        npcr_per_ch = metrics.get('NPCR_per_channel', {})
        uaci_per_ch = metrics.get('UACI_per_channel', {})

        for ch_name in npcr_per_ch.keys():
            if ch_name == 'Gray':
                headers.append(base_name)
            else:
                headers.append(f"{base_name}-{ch_name}")

            npcr_val = npcr_per_ch[ch_name]
            uaci_val = uaci_per_ch[ch_name]

            npcr_row.append(f"{npcr_val:.4f}")
            uaci_row.append(f"{uaci_val:.4f}")

            all_npcr_values.append(npcr_val)
            all_uaci_values.append(uaci_val)

    # Add means column
    headers.append("means")
    npcr_row.append(f"{np.mean(all_npcr_values):.4f}")
    uaci_row.append(f"{np.mean(all_uaci_values):.4f}")

    # Print table with rows
    table_data = [npcr_row, uaci_row]
    print(tabulate(table_data, headers=headers, tablefmt="simple"))

    print("\n" + "="*90)


def main():
    parser = argparse.ArgumentParser(
        description="Security Analysis for Image Encryption Algorithm"
    )
    parser.add_argument('--original', '-o',
                       help="Path to original images folder")
    parser.add_argument('--encrypted', '-e',
                       help="Path to encrypted images folder")
    parser.add_argument('--all', '-a', action='store_true',
                       help="Run all analyses")

    args = parser.parse_args()

    print("\n" + "="*70)
    print("🔒 IMAGE ENCRYPTION SECURITY ANALYSIS")
    print("="*70)

    # Correlation analysis for original images
    if args.original or args.all:
        original_folder = args.original or './test_images'
        print("\n📋 ORIGINAL IMAGES ANALYSIS")
        corr_results = analyze_folder_correlation(original_folder)
        print_correlation_report(corr_results)

    # Correlation analysis for encrypted images
    if args.encrypted or args.all:
        encrypted_folder = args.encrypted or './encrypted_images'
        if os.path.exists(encrypted_folder):
            print("\n📋 ENCRYPTED IMAGES ANALYSIS")
            encrypted_corr = analyze_folder_correlation(encrypted_folder)
            print_correlation_report(encrypted_corr)

    # Differential attack analysis (only needs original images - encrypts internally)
    if args.original or args.all:
        original_folder = args.original or './test_images'
        if os.path.exists(original_folder):
            diff_results = analyze_differential_attack(original_folder)
            print_differential_attack_report(diff_results)

    print("\n" + "="*70)
    print("✅ Analysis Complete")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

