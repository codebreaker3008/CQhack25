def xor_encrypt(message, key):
    # Repeat the key to match message length
    repeated_key = (key * ((len(message) // len(key)) + 1))[:len(message)]
    return ''.join(chr(ord(c) ^ int(k)) for c, k in zip(message, repeated_key))

def xor_decrypt(ciphertext, key):
    # XOR decryption is symmetric
    return xor_encrypt(ciphertext, key)
