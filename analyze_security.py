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


def analyze_differential_attack(original_folder: str, encrypted_folder: str) -> dict:
    """Analyze differential attack resistance"""
    results = {}

    original_files = [f for f in os.listdir(original_folder)
                     if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    encrypted_files = [f for f in os.listdir(encrypted_folder)
                      if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if not original_files or not encrypted_files:
        print("No images found in one or both folders")
        return results

    print(f"\n🔐 Analyzing differential attack resistance...")

    # Match original files with encrypted files (encrypted files have _processed suffix)
    for orig_file in original_files:
        base_name = orig_file.rsplit('.', 1)[0]  # Remove extension
        encrypted_file = f"{base_name}_processed.png"

        if encrypted_file in encrypted_files:
            original_path = os.path.join(original_folder, orig_file)
            encrypted_path = os.path.join(encrypted_folder, encrypted_file)

            try:
                metrics = SecurityAnalyzer.analyze_differential_attack(original_path, encrypted_path)
                results[orig_file] = metrics
                print(f"  ✓ {orig_file} → {encrypted_file}")
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
    """Print differential attack analysis report"""
    if not results:
        return
    
    print("\n" + "="*70)
    print("DIFFERENTIAL ATTACK RESISTANCE ANALYSIS")
    print("="*70)
    print("NPCR (Number of Pixel Change Rate)")
    print("  Theoretical value: 99.6094%")
    print("  Measures: Proportion of changed pixels\n")
    print("UACI (Unified Average Change Intensity)")
    print("  Theoretical value: 33.4635%")
    print("  Measures: Average intensity change\n")
    
    table_data = []
    for image_name, metrics in results.items():
        table_data.append([
            image_name,
            f"{metrics['NPCR']:.4f}%",
            f"{metrics['UACI']:.4f}%"
        ])
    
    headers = ["Image", "NPCR", "UACI"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # Calculate averages
    if results:
        avg_npcr = np.mean([v['NPCR'] for v in results.values()])
        avg_uaci = np.mean([v['UACI'] for v in results.values()])
        
        print(f"\n📊 Average Metrics:")
        print(f"   NPCR: {avg_npcr:.4f}% (Theoretical: 99.6094%)")
        print(f"   UACI: {avg_uaci:.4f}% (Theoretical: 33.4635%)")


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

    # Differential attack analysis
    if args.encrypted and args.original:
        diff_results = analyze_differential_attack(args.original, args.encrypted)
        print_differential_attack_report(diff_results)
    elif args.all:
        if os.path.exists('./test_images') and os.path.exists('./encrypted_images'):
            diff_results = analyze_differential_attack('./test_images', './encrypted_images')
            print_differential_attack_report(diff_results)

    print("\n" + "="*70)
    print("✅ Analysis Complete")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

