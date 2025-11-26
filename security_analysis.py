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
    def analyze_differential_attack(original_path: str, encrypted_path: str) -> Dict[str, float]:
        """
        Analyze differential attack resistance using NPCR and UACI metrics
        
        NPCR (Number of Pixel Change Rate): Percentage of pixels that change
        UACI (Unified Average Change Intensity): Average intensity of pixel changes
        
        Args:
            original_path: Path to original image
            encrypted_path: Path to encrypted image
            
        Returns:
            Dictionary with 'NPCR' and 'UACI' values (as percentages)
        """
        original = SecurityAnalyzer._load_image_as_array(original_path)
        encrypted = SecurityAnalyzer._load_image_as_array(encrypted_path)
        
        # Convert to grayscale if RGB
        if len(original.shape) == 3:
            original = np.dot(original[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
        if len(encrypted.shape) == 3:
            encrypted = np.dot(encrypted[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
        
        # Ensure same dimensions
        if original.shape != encrypted.shape:
            # Resize encrypted to match original
            from PIL import Image as PILImage
            encrypted_img = PILImage.fromarray(encrypted)
            encrypted_img = encrypted_img.resize((original.shape[1], original.shape[0]))
            encrypted = np.array(encrypted_img)
        
        M, N = original.shape
        total_pixels = M * N
        
        # Calculate NPCR (Number of Pixel Change Rate)
        # NPCR = (Number of different pixels / Total pixels) * 100
        different_pixels = np.sum(original != encrypted)
        npcr = (different_pixels / total_pixels) * 100
        
        # Calculate UACI (Unified Average Change Intensity)
        # UACI = (1 / (M * N)) * Σ|original(i,j) - encrypted(i,j)| / 255 * 100
        intensity_diff = np.abs(original.astype(np.float64) - encrypted.astype(np.float64))
        uaci = (np.sum(intensity_diff) / (total_pixels * 255)) * 100
        
        return {
            'NPCR': npcr,
            'UACI': uaci
        }

