"""
Utility functions for encryption module
"""
import os
import base64
import hashlib
import secrets
import logging

# Setup logging
logger = logging.getLogger(__name__)

def generate_key():
    """
    Generate a cryptographically secure key
    
    Returns:
        bytes: Generated key
    """
    return base64.urlsafe_b64encode(secrets.token_bytes(32))

def generate_salt():
    """
    Generate a random salt
    
    Returns:
        bytes: Generated salt
    """
    return secrets.token_bytes(16)

def key_derivation(password, salt, iterations=100000):
    """
    Derive a key from a password using PBKDF2
    
    Args:
        password: Password to derive key from
        salt: Salt for key derivation
        iterations: Number of iterations
        
    Returns:
        bytes: Derived key
    """
    if isinstance(password, str):
        password = password.encode()
        
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password,
        salt,
        iterations
    )
    
    return base64.urlsafe_b64encode(key)

def secure_compare(a, b):
    """
    Compare two strings in constant time to prevent timing attacks
    
    Args:
        a: First string
        b: Second string
        
    Returns:
        bool: True if equal, False otherwise
    """
    if len(a) != len(b):
        return False
    
    result = 0
    for x, y in zip(a, b):
        result |= ord(x) ^ ord(y) if isinstance(x, str) else x ^ y
        
    return result == 0

def sanitize_key_name(key_name):
    """
    Sanitize a key name for storage
    
    Args:
        key_name: Name of the key
        
    Returns:
        str: Sanitized key name
    """
    # Remove special characters and limit length
    sanitized = ''.join(c for c in key_name if c.isalnum() or c in ['_', '-'])
    return sanitized[:50]  # Limit to 50 characters

def encrypt_file(file_path, output_path, key):
    """
    Encrypt a file
    
    Args:
        file_path: Path to the file to encrypt
        output_path: Path to save the encrypted file
        key: Encryption key
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        from cryptography.fernet import Fernet
        
        # Read the file
        with open(file_path, 'rb') as f:
            data = f.read()
        
        # Encrypt the data
        cipher = Fernet(key)
        encrypted_data = cipher.encrypt(data)
        
        # Write the encrypted data
        with open(output_path, 'wb') as f:
            f.write(encrypted_data)
            
        return True
    except Exception as e:
        logger.error(f"Error encrypting file: {e}")
        return False

def decrypt_file(file_path, output_path, key):
    """
    Decrypt a file
    
    Args:
        file_path: Path to the encrypted file
        output_path: Path to save the decrypted file
        key: Decryption key
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        from cryptography.fernet import Fernet
        
        # Read the encrypted file
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()
        
        # Decrypt the data
        cipher = Fernet(key)
        decrypted_data = cipher.decrypt(encrypted_data)
        
        # Write the decrypted data
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)
            
        return True
    except Exception as e:
        logger.error(f"Error decrypting file: {e}")
        return False