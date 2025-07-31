import random
import string

def xor_encrypt(message, key):
    repeated_key = (key * ((len(message) // len(key)) + 1))[:len(message)]
    return ''.join(chr(ord(m) ^ ord(k)) for m, k in zip(message, repeated_key))

def xor_decrypt(cipher, key):
    return xor_encrypt(cipher, key)

def gibberish(s):
    gib = ''.join(random.choice(string.ascii_letters + string.digits + "!@#$%^&*") for _ in s)
    return gib
