import numpy as np
import hashlib
from utils import image_handler
from dna_operations import core

from chaotic_maps.tdlcic import tdlcic_map




def encrypt_images(input_folder, output_folder):
    print("Step 1: Loading and preprocessing images...")
    images, paths = image_handler.load_images(input_folder)
    P, original_shapes, channel_map = image_handler.preprocess_images(images)
    M, N, n = P.shape
    sum_pixels = M * N

    print("Step 2: Generating plaintext-related key...")
    stitched_img = image_handler.stitch_images_for_key(P)
    K = hashlib.sha512(stitched_img.tobytes()).hexdigest()
    k = np.array([int(K[i:i+8], 16) for i in range(0, 128, 8)]) / 256.0
    a, b, x0, y0 = 2 + np.sum(k[0:4]), 2 + np.sum(k[4:8]), np.sum(k[8:12]) % 1, np.sum(k[12:16]) % 1

    print("Step 3: Generating chaotic sequences...")
    num_iterations = (sum_pixels * n // 2) + 1000
   
    x, y = tdlcic_map(x0, y0, a, b, num_iterations)

    x, y = x[1000:], y[1000:]
    xy = np.concatenate((x, y))[:sum_pixels * n]
    C_matrix = (np.floor(np.abs(xy) * 1e14).astype(np.uint64) % 8).reshape(M, N, n)

    print("Step 4: Performing DNA Cyclic Shift Encoding...")
    P_dna1 = core.cyclic_shift_encode(P, C_matrix)

    print("Step 5: Performing Global Exchange Scrambling...")
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

    print("Step 6: Performing Multi-Directional DNA Diffusion...")
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

    print("Step 7: Final decoding to pixels...")
    P_end = core.final_decode_to_pixels(P_dna4, C_matrix)

    print(f"Step 8: Saving encrypted images to '{output_folder}'...")
    image_handler.save_images(P_end, output_folder, paths, original_shapes, channel_map, preserve_padding=True)
    print("Encryption complete.")
    return K
