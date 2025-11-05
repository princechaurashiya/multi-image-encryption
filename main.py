import argparse
from encrypt import encrypt_images
from decrypt import decrypt_images

def main():
    parser = argparse.ArgumentParser(description="Multi-image encryption based on the paper by Zhou et al.")
    parser.add_argument('action', choices=['encrypt', 'decrypt'], help="Action to perform: 'encrypt' or 'decrypt'")
    parser.add_argument('--input', '-i', required=True, help="Path to the input folder containing images.")
    parser.add_argument('--output', '-o', required=True, help="Path to the output folder.")
    parser.add_argument('--key', '-k', help="128-character (512-bit) hex key required for decryption.")

    args = parser.parse_args()

    if args.action == 'encrypt':
        print("--- Starting Encryption ---")
        key = encrypt_images(args.input, args.output)
        if key:
            print(f"\nEncryption successful! Your secret key is:\n{key}")
            print("\nIMPORTANT: Save this key securely.")

    elif args.action == 'decrypt':
        print("--- Starting Decryption ---")
        if not args.key or len(args.key) != 128:
            print("Error: Decryption requires a valid 128-character (512-bit) hex key. Please provide it with --key.")
            return
        decrypt_images(args.input, args.output, args.key)

if __name__ == "__main__":
    main()




