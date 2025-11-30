"""
Security Analysis Module

Implements security analysis methods for image encryption:
1. Correlation coefficient analysis (Rxy)
2. NPCR (Number of Pixel Change Rate)
3. UACI (Unified Average Change Intensity)
"""

import numpy as np
from PIL import Image
from typing import Dict, Tuple


class SecurityAnalyzer:
    """Security analysis tools for image encryption algorithms"""
    
    @staticmethod
    def _load_image_as_array(image_path: str) -> np.ndarray:
        """Load image and convert to numpy array"""
        img = Image.open(image_path)
        return np.array(img)
    
    @staticmethod
    def _calculate_correlation_coefficient(x: np.ndarray, y: np.ndarray) -> float:
        """
        Calculate correlation coefficient between two pixel sequences
        
        Formula: Rxy = E[(x - E[x])(y - E[y])] / sqrt(D[x] * D[y])
        where E[x] is expectation, D[x] is variance
        """
        # Calculate expectations (means)
        E_x = np.mean(x)
        E_y = np.mean(y)
        
        # Calculate covariance
        cov_xy = np.mean((x - E_x) * (y - E_y))
        
        # Calculate variances
        D_x = np.var(x)
        D_y = np.var(y)
        
        # Calculate correlation coefficient
        if D_x == 0 or D_y == 0:
            return 0.0
        
        R_xy = cov_xy / np.sqrt(D_x * D_y)
        return float(R_xy)
    
    @staticmethod
    def analyze_correlation(image_path: str, sample_size: int = 5000) -> Dict[str, float]:
        """
        Analyze correlation coefficients in horizontal, vertical, and diagonal directions
        
        Args:
            image_path: Path to the image file
            sample_size: Number of pixel pairs to sample for analysis
            
        Returns:
            Dictionary with 'horizontal', 'vertical', and 'diagonal' correlation values
        """
        img_array = SecurityAnalyzer._load_image_as_array(image_path)
        
        # Convert to grayscale if RGB
        if len(img_array.shape) == 3:
            # Use luminosity method for RGB to grayscale conversion
            img_array = np.dot(img_array[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
        
        M, N = img_array.shape
        
        # Randomly sample pixel positions
        np.random.seed(42)  # For reproducibility
        sample_size = min(sample_size, (M - 1) * (N - 1))
        
        # Horizontal correlation (adjacent pixels in same row)
        i_h = np.random.randint(0, M, sample_size)
        j_h = np.random.randint(0, N - 1, sample_size)
        x_h = img_array[i_h, j_h]
        y_h = img_array[i_h, j_h + 1]
        corr_horizontal = SecurityAnalyzer._calculate_correlation_coefficient(x_h, y_h)
        
        # Vertical correlation (adjacent pixels in same column)
        i_v = np.random.randint(0, M - 1, sample_size)
        j_v = np.random.randint(0, N, sample_size)
        x_v = img_array[i_v, j_v]
        y_v = img_array[i_v + 1, j_v]
        corr_vertical = SecurityAnalyzer._calculate_correlation_coefficient(x_v, y_v)
        
        # Diagonal correlation (adjacent pixels diagonally)
        i_d = np.random.randint(0, M - 1, sample_size)
        j_d = np.random.randint(0, N - 1, sample_size)
        x_d = img_array[i_d, j_d]
        y_d = img_array[i_d + 1, j_d + 1]
        corr_diagonal = SecurityAnalyzer._calculate_correlation_coefficient(x_d, y_d)
        
        return {
            'horizontal': corr_horizontal,
            'vertical': corr_vertical,
            'diagonal': corr_diagonal
        }
    
    @staticmethod
    def analyze_differential_attack(
        original_image: np.ndarray,
        encrypt_function,
        pixel_change_position: Tuple[int, int] = None
    ) -> Dict[str, float]:
        """
        Analyze differential attack resistance using NPCR and UACI metrics.

        According to research paper methodology:
        1. Encrypt original image P to get C1
        2. Change ONE pixel in P to get P'
        3. Encrypt P' to get C2
        4. Calculate NPCR and UACI between C1 and C2 (per channel for RGB)

        NPCR (Number of Pixel Change Rate): Percentage of pixels that differ between C1 and C2
        UACI (Unified Average Change Intensity): Average intensity of pixel changes

        Theoretical ideal values:
        - NPCR ≈ 99.6094%
        - UACI ≈ 33.4635%

        Args:
            original_image: Original image as numpy array
            encrypt_function: Encryption function that takes image array and returns encrypted array
            pixel_change_position: (i, j) position of pixel to change. If None, random position is used.

        Returns:
            Dictionary with 'NPCR' and 'UACI' values (as percentages), calculated per channel
        """
        # Make a copy of original image
        original = original_image.copy()

        # Get dimensions
        if len(original.shape) == 3:
            M, N, num_channels = original.shape
        else:
            M, N = original.shape
            num_channels = 1
            original = original[:, :, np.newaxis]

        # Determine pixel position to change
        if pixel_change_position is None:
            np.random.seed(42)
            i = np.random.randint(0, M)
            j = np.random.randint(0, N)
        else:
            i, j = pixel_change_position

        # Step 1: Encrypt original image to get C1
        C1 = encrypt_function(original.squeeze() if num_channels == 1 else original)
        if len(C1.shape) == 2:
            C1 = C1[:, :, np.newaxis]

        # Step 2: Create modified image P' (change ONE pixel)
        modified = original.copy()

        # Change the pixel value (increment by 1, wrap around if at 255)
        for c in range(num_channels):
            modified[i, j, c] = np.uint8((int(modified[i, j, c]) + 1) % 256)

        # Step 3: Encrypt modified image to get C2
        C2 = encrypt_function(modified.squeeze() if num_channels == 1 else modified)
        if len(C2.shape) == 2:
            C2 = C2[:, :, np.newaxis]

        # Ensure same dimensions
        if C1.shape != C2.shape:
            raise ValueError("Encrypted images C1 and C2 have different dimensions")

        total_pixels = M * N

        # Calculate NPCR and UACI per channel (as per research paper Table 11)
        channel_names = ['R', 'G', 'B'] if num_channels >= 3 else ['Gray']
        npcr_per_channel = {}
        uaci_per_channel = {}

        for c in range(min(num_channels, 3)):
            C1_channel = C1[:, :, c]
            C2_channel = C2[:, :, c]

            # NPCR = (ΣΣ D(i,j)) / (M × N) × 100%
            D = (C1_channel != C2_channel).astype(np.int32)
            npcr = (np.sum(D) / total_pixels) * 100

            # UACI = (1/(M×N)) × ΣΣ |C1(i,j) - C2(i,j)| / 255 × 100%
            intensity_diff = np.abs(C1_channel.astype(np.float64) - C2_channel.astype(np.float64))
            uaci = (np.sum(intensity_diff) / (total_pixels * 255)) * 100

            channel_name = channel_names[c] if c < len(channel_names) else f'Ch{c}'
            npcr_per_channel[channel_name] = npcr
            uaci_per_channel[channel_name] = uaci

        # Calculate mean NPCR and UACI across all channels
        mean_npcr = np.mean(list(npcr_per_channel.values()))
        mean_uaci = np.mean(list(uaci_per_channel.values()))

        return {
            'NPCR': mean_npcr,
            'UACI': mean_uaci,
            'NPCR_per_channel': npcr_per_channel,
            'UACI_per_channel': uaci_per_channel,
            'changed_pixel_position': (i, j),
            'theoretical_NPCR': 99.6094,
            'theoretical_UACI': 33.4635
        }

    @staticmethod
    def calculate_npcr_uaci(C1: np.ndarray, C2: np.ndarray) -> Dict[str, float]:
        """
        Calculate NPCR and UACI between two encrypted images directly.

        Use this when you already have two encrypted images C1 and C2
        where C2 is encrypted from an image that differs by one pixel from C1's source.

        Args:
            C1: First encrypted image as numpy array
            C2: Second encrypted image as numpy array (from 1-pixel-modified original)

        Returns:
            Dictionary with 'NPCR' and 'UACI' values (as percentages)
        """
        # Convert to grayscale if RGB
        if len(C1.shape) == 3:
            C1 = np.dot(C1[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
        if len(C2.shape) == 3:
            C2 = np.dot(C2[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)

        if C1.shape != C2.shape:
            raise ValueError("Images C1 and C2 must have the same dimensions")

        M, N = C1.shape
        total_pixels = M * N

        # Calculate NPCR
        # NPCR = (ΣΣ D(i,j)) / (M × N) × 100%
        D = (C1 != C2).astype(np.int32)
        npcr = (np.sum(D) / total_pixels) * 100

        # Calculate UACI
        # UACI = (1/(M×N)) × ΣΣ |C1(i,j) - C2(i,j)| / 255 × 100%
        intensity_diff = np.abs(C1.astype(np.float64) - C2.astype(np.float64))
        uaci = (np.sum(intensity_diff) / (total_pixels * 255)) * 100

        return {
            'NPCR': npcr,
            'UACI': uaci,
            'theoretical_NPCR': 99.6094,
            'theoretical_UACI': 33.4635
        }

