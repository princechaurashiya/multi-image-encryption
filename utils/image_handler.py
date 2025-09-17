import numpy as np
from PIL import Image
import os

def load_images(folder_path):
    images, paths = [], []
    sorted_paths = sorted([os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(('png', 'jpg', 'jpeg'))])
    if not sorted_paths: raise ValueError("No images found in the directory.")
    for path in sorted_paths:
        images.append(np.array(Image.open(path), dtype=np.uint8))
        paths.append(path)
    return images, paths

def preprocess_images(images):
    max_h = max(img.shape[0] for img in images)
    max_w = max(img.shape[1] for img in images)
    channels, original_shapes, channel_map = [], {}, []
    for i, img in enumerate(images):
        h, w = img.shape[:2]
        original_shapes[i] = (h, w)
        pad_h, pad_w = max_h - h, max_w - w
        padded_img = np.pad(img, ((0, pad_h), (0, pad_w), (0, 0)) if img.ndim == 3 else ((0, pad_h), (0, pad_w)), 'constant')
        if padded_img.ndim == 3:
            channels.extend([padded_img[:, :, j] for j in range(3)])
            channel_map.append(3)
        else:
            channels.append(padded_img)
            channel_map.append(1)
    return np.stack(channels, axis=-1), original_shapes, channel_map

def stitch_images_for_key(processed_images_matrix):
    return np.concatenate([processed_images_matrix[:,:,i] for i in range(processed_images_matrix.shape[2])], axis=1)

def save_images(image_matrix, base_path, original_paths, original_shapes, channel_map, preserve_padding=False):
    os.makedirs(base_path, exist_ok=True)
    current_channel_idx = 0
    for i, num_channels in enumerate(channel_map):
        if preserve_padding:
            # Save full padded images (for encrypted images)
            original_h, original_w = image_matrix.shape[0], image_matrix.shape[1]
        else:
            # Crop to original size (for final decrypted images)
            original_h, original_w = original_shapes[i]

        if num_channels == 3:
            img_array = np.stack(
                [image_matrix[:original_h, :original_w, current_channel_idx + j] for j in range(3)],
                axis=-1
            )
        else:
            img_array = image_matrix[:original_h, :original_w, current_channel_idx]
        current_channel_idx += num_channels
        filename = os.path.basename(original_paths[i])
        new_filename = f"{os.path.splitext(filename)[0]}_processed.png"
        Image.fromarray(img_array.astype(np.uint8)).save(os.path.join(base_path, new_filename))
