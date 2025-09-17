import numpy as np
from utils import image_handler
from dna_operations import core

from chaotic_maps.tdlcic import tdlcic_map



def decrypt_images(input_folder, output_folder, K):
    print("Step 1: Loading encrypted images and regenerating keys...")
    images, paths = image_handler.load_images(input_folder)
    P_end, original_shapes, channel_map = image_handler.preprocess_images(images)
    M, N, n = P_end.shape
    sum_pixels = M * N

    k = np.array([int(K[i:i+8], 16) for i in range(0, 128, 8)]) / 256.0
    a, b, x0, y0 = 2 + np.sum(k[0:4]), 2 + np.sum(k[4:8]), np.sum(k[8:12]) % 1, np.sum(k[12:16]) % 1

    print("Step 2: Regenerating chaotic sequences...")
    num_iterations = (sum_pixels * n // 2) + 1000
    x, y = tdlcic_map(x0, y0, a, b, num_iterations)

    x, y = x[1000:], y[1000:]
    xy = np.concatenate((x, y))[:sum_pixels * n]
    C_matrix = (np.floor(np.abs(xy) * 1e14).astype(np.uint64) % 8).reshape(M, N, n)
    S = np.argsort(x[:sum_pixels])
    G = np.argsort(xy.reshape(sum_pixels, n), axis=1)
    E = (np.floor(np.abs(xy) * 1e14) % 256).astype(np.uint8).reshape(M, N, n)

    print("Step 3: Preparing for inverse diffusion...")
    P_dna4 = core.initial_encode_for_decryption(P_end, C_matrix)

    print("Step 4: Performing Inverse Multi-Directional DNA Diffusion...")
    E_dna = np.empty((M, N, 4 * n), dtype='<U1')
    for i in range(M):
        for j in range(N):
            for k in range(n):
                binary_E = format(E[i,j,k], '08b')
                E_dna[i,j,4*k:4*k+4] = [core.DNA_RULES[0][binary_E[b:b+2]] for b in range(0,8,2)]

    # Inverse Strand diffusion
    P_dna3 = P_dna4.copy()
    for i in range(M):
        for j in range(N):
            for z in range(4 * n - 1, 0, -1):
                P_dna3[i, j, z] = core.DNA_XOR[P_dna4[i, j, z]][P_dna4[i, j, z - 1]]
            P_dna3[i, j, 0] = core.DNA_XOR[P_dna4[i, j, 0]][P_dna3[i, j, -1]]

    # Inverse Lateral diffusion
    P_dna2 = P_dna3.copy()
    for i in range(M - 1, -1, -1):
        for j in range(N - 1, -1, -1):
            for z in range(4 * n - 1, -1, -1):
                if i == 0:
                    P_dna2[i, j, z] = core.DNA_SUB[P_dna3[i, j, z]][E_dna[i, j, z]]
                else:
                    sub_val_1 = core.DNA_SUB[P_dna3[i, j, z]][E_dna[i, j, z]]
                    P_dna2[i, j, z] = core.DNA_SUB[sub_val_1][P_dna2[i-1, j, z]]

    print("Step 5: Performing Inverse Global Exchange Scrambling...")
    P_dna1_flat = P_dna2.reshape(sum_pixels, 4 * n)
    for i in range(sum_pixels - 1, -1, -1):
        s_i = S[i]
        if i == s_i: continue
        for j in range(n):
            g_ij = G[i, j]
            temp_base = P_dna1_flat[i, j*4:j*4+4].copy()
            P_dna1_flat[i, j*4:j*4+4] = P_dna1_flat[s_i, g_ij*4:g_ij*4+4]
            P_dna1_flat[s_i, g_ij*4:g_ij*4+4] = temp_base
    P_dna1 = P_dna1_flat.reshape(M, N, 4 * n)

    print("Step 6: Performing Inverse DNA Cyclic Shift Encoding...")
    P_decrypted = core.cyclic_shift_decode(P_dna1, C_matrix)

    print(f"Step 7: Saving decrypted images to '{output_folder}'...")
    image_handler.save_images(P_decrypted, output_folder, paths, original_shapes, channel_map)
    print("Decryption complete.")
