"""
Classical Post-Processing Utilities.

Implements classical protocols for error correction and privacy
amplification in QKD systems.

Error Correction Methods:
- CASCADE: Interactive binary search protocol
- LDPC: Low-density parity-check codes

Privacy Amplification:
- Universal hashing (Toeplitz matrices)
"""

from typing import Tuple, List, Optional, Callable
import numpy as np
from hashlib import sha256


def binary_entropy(p: float) -> float:
    """Calculate binary entropy H(p)."""
    if p <= 0 or p >= 1:
        return 0.0
    return -p * np.log2(p) - (1 - p) * np.log2(1 - p)


def error_correction(
    alice_key: np.ndarray,
    bob_key: np.ndarray,
    method: str = "cascade"
) -> Tuple[np.ndarray, int]:
    """
    Perform error correction on sifted keys.
    
    Args:
        alice_key: Alice's sifted key
        bob_key: Bob's sifted key
        method: Error correction method ("cascade" or "simple")
        
    Returns:
        Tuple of (corrected key, bits disclosed)
    """
    if method == "cascade":
        return cascade_protocol(alice_key, bob_key)
    else:
        return simple_error_correction(alice_key, bob_key)


def simple_error_correction(
    alice_key: np.ndarray,
    bob_key: np.ndarray
) -> Tuple[np.ndarray, int]:
    """
    Simple parity-based error correction.
    
    Divides key into blocks and performs parity checks.
    This is a simplified simulation - real CASCADE is more complex.
    
    Args:
        alice_key: Alice's key
        bob_key: Bob's key
        
    Returns:
        Tuple of (corrected key, bits disclosed)
    """
    n = len(bob_key)
    corrected = bob_key.copy()
    bits_disclosed = 0
    
    # Estimate initial error rate
    initial_errors = np.sum(alice_key != bob_key)
    error_rate = initial_errors / n if n > 0 else 0
    
    if error_rate == 0:
        return corrected, 0
    
    # Block size based on error rate
    block_size = max(4, int(0.73 / error_rate)) if error_rate > 0 else n
    
    # Process blocks
    for i in range(0, n, block_size):
        block_end = min(i + block_size, n)
        
        # Calculate parities
        alice_parity = np.sum(alice_key[i:block_end]) % 2
        bob_parity = np.sum(corrected[i:block_end]) % 2
        bits_disclosed += 1
        
        # If parities differ, find and correct error (simplified)
        if alice_parity != bob_parity:
            # Binary search for error (simplified to random correction)
            # In real CASCADE, this is an interactive protocol
            block_length = block_end - i
            search_bits = int(np.ceil(np.log2(block_length)))
            bits_disclosed += search_bits
            
            # Find first error in block
            for j in range(i, block_end):
                if alice_key[j] != corrected[j]:
                    corrected[j] = 1 - corrected[j]  # Flip bit
                    break
    
    return corrected, bits_disclosed


def cascade_protocol(
    alice_key: np.ndarray,
    bob_key: np.ndarray,
    num_passes: int = 4
) -> Tuple[np.ndarray, int]:
    """
    CASCADE error correction protocol.
    
    Multi-pass protocol with increasing block sizes.
    Corrects errors through parity checks and binary search.
    
    Args:
        alice_key: Alice's key
        bob_key: Bob's key
        num_passes: Number of passes
        
    Returns:
        Tuple of (corrected key, bits disclosed)
    """
    n = len(bob_key)
    corrected = bob_key.copy()
    total_bits_disclosed = 0
    
    # Initial error estimate
    initial_errors = np.sum(alice_key != bob_key)
    error_rate = initial_errors / n if n > 0 else 0
    
    if error_rate == 0:
        return corrected, 0
    
    # Initial block size
    k0 = max(4, int(0.73 / error_rate)) if error_rate > 0 else n
    
    for pass_num in range(num_passes):
        # Block size doubles each pass
        block_size = k0 * (2 ** pass_num)
        
        # Random permutation for each pass (except first)
        if pass_num > 0:
            perm = np.random.permutation(n)
            alice_perm = alice_key[perm]
            corrected_perm = corrected[perm]
        else:
            perm = np.arange(n)
            alice_perm = alice_key
            corrected_perm = corrected.copy()
        
        # Process blocks
        for i in range(0, n, block_size):
            block_end = min(i + block_size, n)
            
            alice_parity = np.sum(alice_perm[i:block_end]) % 2
            bob_parity = np.sum(corrected_perm[i:block_end]) % 2
            total_bits_disclosed += 1
            
            if alice_parity != bob_parity:
                # Binary search for error
                left, right = i, block_end
                
                while right - left > 1:
                    mid = (left + right) // 2
                    
                    alice_half_parity = np.sum(alice_perm[left:mid]) % 2
                    bob_half_parity = np.sum(corrected_perm[left:mid]) % 2
                    total_bits_disclosed += 1
                    
                    if alice_half_parity != bob_half_parity:
                        right = mid
                    else:
                        left = mid
                
                # Correct error
                corrected_perm[left] = 1 - corrected_perm[left]
        
        # Apply correction back through permutation
        if pass_num > 0:
            inv_perm = np.argsort(perm)
            corrected = corrected_perm[inv_perm]
        else:
            corrected = corrected_perm.copy()
    
    return corrected, total_bits_disclosed


def privacy_amplification(
    key: np.ndarray,
    final_length: int,
    method: str = "toeplitz"
) -> np.ndarray:
    """
    Perform privacy amplification on corrected key.
    
    Reduces key length while removing Eve's information.
    
    Args:
        key: Corrected key
        final_length: Target key length
        method: Hashing method ("toeplitz" or "sha256")
        
    Returns:
        Final secure key
    """
    if final_length >= len(key):
        return key[:final_length]
    
    if method == "toeplitz":
        return toeplitz_hash(key, final_length)
    else:
        return sha256_hash(key, final_length)


def toeplitz_hash(key: np.ndarray, output_length: int) -> np.ndarray:
    """
    Universal hash using Toeplitz matrix.
    
    A Toeplitz matrix is defined by its first row and first column,
    and is known to be a good universal hash family.
    
    Args:
        key: Input key
        output_length: Desired output length
        
    Returns:
        Hashed key
    """
    n = len(key)
    m = output_length
    
    if m >= n:
        return key[:m]
    
    # Generate random Toeplitz matrix
    # Need n + m - 1 random bits
    seed_length = n + m - 1
    seed = np.random.randint(0, 2, seed_length)
    
    # Build Toeplitz matrix
    result = np.zeros(m, dtype=int)
    
    for i in range(m):
        row = seed[m - 1 - i:m - 1 - i + n]
        result[i] = np.sum(row * key) % 2
    
    return result


def sha256_hash(key: np.ndarray, output_length: int) -> np.ndarray:
    """
    Privacy amplification using SHA-256.
    
    Note: SHA-256 may have some theoretical weaknesses for 
    quantum-secure privacy amplification, but is practical.
    
    Args:
        key: Input key
        output_length: Desired output length
        
    Returns:
        Hashed key
    """
    # Convert key to bytes
    key_bytes = bytes(key.tolist())
    
    # Generate enough hash output
    result_bits = []
    counter = 0
    
    while len(result_bits) < output_length:
        # Hash with counter
        hash_input = key_bytes + counter.to_bytes(4, 'big')
        hash_output = sha256(hash_input).digest()
        
        # Convert to bits
        for byte in hash_output:
            for i in range(8):
                result_bits.append((byte >> (7 - i)) & 1)
        
        counter += 1
    
    return np.array(result_bits[:output_length])


def universal_hash(
    key: np.ndarray,
    output_length: int,
    hash_key: Optional[np.ndarray] = None
) -> np.ndarray:
    """
    General universal hash function.
    
    Args:
        key: Input to hash
        output_length: Desired output length
        hash_key: Optional pre-shared hash key
        
    Returns:
        Hashed output
    """
    n = len(key)
    
    if hash_key is None:
        # Generate random hash key
        hash_key = np.random.randint(0, 2, (output_length, n))
    
    # Matrix multiplication mod 2
    result = np.mod(hash_key @ key, 2)
    
    return result.astype(int)


def information_reconciliation_efficiency(
    bits_disclosed: int,
    key_length: int,
    qber: float
) -> float:
    """
    Calculate efficiency of information reconciliation.
    
    f = bits_disclosed / (key_length * H(QBER))
    
    Ideal f = 1, practical systems achieve f ≈ 1.16
    
    Args:
        bits_disclosed: Number of bits revealed during EC
        key_length: Original key length
        qber: Quantum bit error rate
        
    Returns:
        Efficiency factor f
    """
    if qber <= 0:
        return 1.0
    
    theoretical_min = key_length * binary_entropy(qber)
    
    if theoretical_min == 0:
        return 1.0
    
    return bits_disclosed / theoretical_min


def estimate_final_key_length(
    sifted_length: int,
    qber: float,
    ec_efficiency: float = 1.16,
    security_parameter: float = 1e-10
) -> int:
    """
    Estimate final secure key length.
    
    Args:
        sifted_length: Length of sifted key
        qber: Quantum bit error rate
        ec_efficiency: Error correction efficiency
        security_parameter: Security parameter ε
        
    Returns:
        Expected final key length
    """
    if qber >= 0.11:
        return 0
    
    n = sifted_length
    h = binary_entropy(qber)
    
    # Privacy amplification removes:
    # - Eve's information (≈ h(QBER) bits per sifted bit)
    # - Error correction leakage (f * h(QBER))
    # - Finite-key correction
    
    pa_fraction = h
    ec_fraction = ec_efficiency * h
    
    secret_fraction = max(0, 1 - pa_fraction - ec_fraction)
    
    # Finite key correction
    finite_correction = np.sqrt(n) * np.log2(1 / security_parameter)
    
    final_length = int(n * secret_fraction - finite_correction)
    
    return max(0, final_length)
