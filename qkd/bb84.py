import random

def generate_bits(n):
    return [random.randint(0, 1) for _ in range(n)]

def generate_bases(n):
    return [random.choice(['+', 'x']) for _ in range(n)]

def encode_bits(bits, bases):
    return [(bit, base) for bit, base in zip(bits, bases)]

def measure_bits(encoded_qubits, bases):
    measured = []
    for (bit, base_sender), base_receiver in zip(encoded_qubits, bases):
        if base_sender == base_receiver:
            measured.append(bit)
        else:
            measured.append(random.randint(0, 1))
    return measured

def sift_key(sender_bases, receiver_bases, bits):
    return [bit for s_base, r_base, bit in zip(sender_bases, receiver_bases, bits) if s_base == r_base]

def bb84_protocol(n_bits=32):
    alice_bits = generate_bits(n_bits)
    alice_bases = generate_bases(n_bits)
    bob_bases = generate_bases(n_bits)

    encoded_qubits = encode_bits(alice_bits, alice_bases)
    bob_results = measure_bits(encoded_qubits, bob_bases)

    raw_key = sift_key(alice_bases, bob_bases, bob_results)

    # Return raw key as a binary string
    return ''.join(map(str, raw_key))

def bb84_protocol(length):
    bases = ['Z', 'X']
    sender_bits = [random.randint(0, 1) for _ in range(length)]
    sender_bases = [random.choice(bases) for _ in range(length)]
    receiver_bases = [random.choice(bases) for _ in range(length)]
    key = ''.join(str(sender_bits[i]) for i in range(length) if sender_bases[i] == receiver_bases[i])
    return key
