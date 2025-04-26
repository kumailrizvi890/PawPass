"""
Encryption module for PawPass
"""
from pawpass.encryption.crypto import (
    EncryptionService,
    EncryptionProvider,
    SecureStore,
    secure_store
)

# Create a singleton instance of the encryption service
encryption_service = EncryptionService()

# Export functions that use the singleton
def encrypt_data(plaintext, context=None, user_id=None):
    """Encrypt sensitive data"""
    return encryption_service.encrypt_data(plaintext, context, user_id)

def decrypt_data(ciphertext, context=None, user_id=None):
    """Decrypt encrypted data"""
    return encryption_service.decrypt_data(ciphertext, context, user_id)

__all__ = [
    'EncryptionService',
    'EncryptionProvider',
    'SecureStore',
    'encryption_service',
    'secure_store',
    'encrypt_data',
    'decrypt_data'
]