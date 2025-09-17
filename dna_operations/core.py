import numpy as np

# DNA encoding rules
DNA_RULES = {
    0: {'00': 'A', '01': 'C', '10': 'G', '11': 'T'},
    1: {'00': 'A', '01': 'G', '10': 'C', '11': 'T'},
    2: {'00': 'C', '01': 'A', '10': 'T', '11': 'G'},
    3: {'00': 'C', '01': 'T', '10': 'A', '11': 'G'},
    4: {'00': 'G', '01': 'A', '10': 'T', '11': 'C'},
    5: {'00': 'G', '01': 'T', '10': 'A', '11': 'C'},
    6: {'00': 'T', '01': 'C', '10': 'G', '11': 'A'},
    7: {'00': 'T', '01': 'G', '10': 'C', '11': 'A'},
}
DNA_INVERSE_RULES = {rule_idx: {v: k for k, v in rule.items()} for rule_idx, rule in DNA_RULES.items()}

DNA_ADD = {
    'A': {'A': 'A', 'G': 'G', 'C': 'C', 'T': 'T'},
    'G': {'A': 'G', 'G': 'C', 'C': 'T', 'T': 'A'},
    'C': {'A': 'C', 'G': 'T', 'C': 'A', 'T': 'G'},
    'T': {'A': 'T', 'G': 'A', 'C': 'G', 'T': 'C'}
}
DNA_SUB = {
    'A': {'A': 'A', 'G': 'T', 'C': 'C', 'T': 'G'},
    'G': {'A': 'G', 'G': 'A', 'C': 'T', 'T': 'C'},
    'C': {'A': 'C', 'G': 'G', 'C': 'A', 'T': 'T'},
    'T': {'A': 'T', 'G': 'C', 'C': 'G', 'T': 'A'}
}
DNA_XOR = {
    'A': {'A': 'A', 'G': 'G', 'C': 'C', 'T': 'T'},
    'G': {'A': 'G', 'G': 'A', 'C': 'T', 'T': 'C'},
    'C': {'A': 'C', 'G': 'T', 'C': 'A', 'T': 'G'},
    'T': {'A': 'T', 'G': 'C', 'C': 'G', 'T': 'A'}
}

def cyclic_shift_encode(pixel_matrix, C_matrix):
    M, N, n = pixel_matrix.shape
    dna_matrix = np.empty((M, N, 4 * n), dtype='<U1')
    for i in range(M):
        for j in range(N):
            for k in range(n):
                pixel_val = pixel_matrix[i, j, k]
                binary_val = format(pixel_val, '08b')
                shift = int(C_matrix[i, j, k]) % 8
                rule_idx = int(C_matrix[i, j, k]) % 8
                shifted_binary = binary_val[shift:] + binary_val[:shift]
                encoded_dna = "".join([DNA_RULES[rule_idx][shifted_binary[b:b+2]] for b in range(0, 8, 2)])
                dna_matrix[i, j, 4*k : 4*(k+1)] = list(encoded_dna)
    return dna_matrix

def cyclic_shift_decode(dna_matrix, C_matrix):
    M, N, total = dna_matrix.shape
    n = total // 4
    pixel_matrix = np.empty((M, N, n), dtype=np.uint8)
    for i in range(M):
        for j in range(N):
            for k in range(n):
                rule_idx = int(C_matrix[i, j, k]) % 8
                encoded_dna = "".join(dna_matrix[i, j, 4*k : 4*(k+1)])
                binary_str = "".join([DNA_INVERSE_RULES[rule_idx][base] for base in encoded_dna])
                shift = int(C_matrix[i, j, k]) % 8
                binary_val = binary_str[-shift:] + binary_str[:-shift] if shift else binary_str
                pixel_matrix[i, j, k] = int(binary_val, 2)
    return pixel_matrix

def final_decode_to_pixels(dna_matrix, C_matrix):
    return cyclic_shift_decode(dna_matrix, C_matrix)

def initial_encode_for_decryption(pixel_matrix, C_matrix):
    return cyclic_shift_encode(pixel_matrix, C_matrix)
