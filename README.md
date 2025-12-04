# Multi-Image Encryption System

A sophisticated image encryption system based on chaotic maps and DNA computing operations, implementing advanced cryptographic techniques for secure multi-image processing.

## 🔒 Overview

This project implements a multi-image encryption algorithm that combines:
- **Chaotic Maps**: TDLCIC (Two-Dimensional Logistic-Cosine Iterative Chaotic) map for generating pseudo-random sequences
- **DNA Computing**: DNA encoding/decoding operations for biological-inspired cryptography
- **Multi-directional Diffusion**: Advanced scrambling and diffusion techniques
- **Plaintext-related Key Generation**: Dynamic key generation based on input images

## 🛠️ Technologies Used

### Core Technologies
- **Python 3.9+** - Primary programming language
- **NumPy** - Numerical computations and array operations
- **Pillow (PIL)** - Image processing and manipulation
- **Hashlib** - Cryptographic hashing (SHA-512)

### Cryptographic Components
- **TDLCIC Chaotic Map** - Two-dimensional chaotic system for sequence generation
- **DNA Operations** - 8 different DNA encoding rules with ADD, SUB, XOR operations
- **Cyclic Shift Encoding** - Binary data transformation with cyclic shifts
- **Global Exchange Scrambling** - Position-based pixel scrambling
- **Multi-directional Diffusion** - Lateral and strand-based diffusion operations

## 📁 Project Structure

```
multi-image-encryption/
├── main.py                 # Command-line interface
├── encrypt.py             # Main encryption logic
├── decrypt.py             # Main decryption logic
├── chaotic_maps/          # Chaotic map implementations
│   ├── __init__.py
│   └── tdlcic.py         # TDLCIC chaotic map
├── dna_operations/        # DNA computing operations
│   ├── __init__.py
│   └── core.py           # DNA encoding/decoding rules
├── utils/                 # Utility functions
│   ├── __init__.py
│   └── image_handler.py  # Image processing utilities
├── test_images/          # Sample input images
├── encrypted_images/     # Output encrypted images
└── decrypted_images/     # Output decrypted images
```

## 🚀 Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Install Dependencies
```bash
pip install numpy pillow
```

### Clone Repository
```bash
git clone <repository-url>
cd multi-image-encryption
```

## 💻 Usage

### Command Line Interface

#### Encrypt Images
```bash
python main.py encrypt --input ./test_images --output ./encrypted_images
```

#### Decrypt Images
```bash
python main.py decrypt --input ./encrypted_images --output ./decrypted_images --key <128-character-hex-key>
```

### Parameters
- `action`: Choose 'encrypt' or 'decrypt'
- `--input, -i`: Path to input folder containing images
- `--output, -o`: Path to output folder
- `--key, -k`: 128-character (512-bit) hex key (required for decryption)

### Example Usage
```bash
# Encrypt images
python3 main.py encrypt -i ./test_images -o ./encrypted_images

# Decrypt images (using the key from encryption)
python3 main.py decrypt -i ./encrypted_images -o ./decrypted_images -k <your-512-bit-hex-key>
#security analysis
 python3 analyze_security.py --all
```

## 🔐 Encryption Process

The encryption follows these steps:

1. **Image Preprocessing**: Load and normalize multiple images to uniform dimensions
2. **Key Generation**: Generate plaintext-related 512-bit key using SHA-512
3. **Chaotic Sequence Generation**: Use TDLCIC map to generate pseudo-random sequences
4. **DNA Cyclic Shift Encoding**: Convert pixels to DNA sequences with cyclic shifts
5. **Global Exchange Scrambling**: Perform position-based pixel scrambling
6. **Multi-directional DNA Diffusion**: Apply lateral and strand diffusion
7. **Final Encoding**: Convert back to encrypted pixel values

## 🔓 Decryption Process

Decryption reverses the encryption process:

1. **Key Reconstruction**: Regenerate chaotic sequences from the provided key
2. **Inverse Diffusion**: Reverse multi-directional DNA diffusion
3. **Inverse Scrambling**: Undo global exchange scrambling
4. **Inverse DNA Encoding**: Decode DNA sequences back to original pixels
5. **Image Reconstruction**: Restore original image dimensions and format

## 🔑 Security Features

- **512-bit Key Space**: Large key space for cryptographic security
- **Plaintext Sensitivity**: Key generation depends on input images
- **Chaotic Dynamics**: Non-linear chaotic system for unpredictability
- **DNA Computing**: Biological-inspired operations for additional complexity
- **Multi-layer Encryption**: Multiple transformation layers for enhanced security

## 📊 Supported Image Formats

- **Input**: PNG, JPG, JPEG
- **Output**: PNG (preserves quality and supports transparency)
- **Color Modes**: RGB (color) and Grayscale images
- **Multiple Images**: Processes multiple images simultaneously

## ⚠️ Important Notes

1. **Key Security**: The 128-character hex key is essential for decryption. Store it securely!
2. **Key Loss**: Lost keys cannot be recovered - encrypted images will be permanently inaccessible
3. **Image Order**: Maintain the same image order for proper decryption
4. **Memory Usage**: Large images may require significant memory for processing

## 🧪 Testing

The project includes sample images in the `test_images/` directory for testing:

```bash
# Test encryption
python3 main.py encrypt -i ./test_images -o ./encrypted_images

# Test decryption (use the key from encryption output)
python3 main.py decrypt -i ./encrypted_images -o ./decrypted_images -k <key>
```

## 📈 Performance Considerations

- **Processing Time**: Depends on image size and number of images
- **Memory Usage**: Proportional to total pixel count across all images
- **Optimization**: Uses NumPy for efficient array operations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source. Please check the license file for details.

## 🔬 Research Background

This implementation is based on advanced cryptographic research combining:
- Chaos theory and dynamical systems
- DNA computing and biological algorithms
- Modern image encryption techniques
- Multi-dimensional diffusion operations

## 📞 Support

For issues, questions, or contributions, please open an issue in the repository.
