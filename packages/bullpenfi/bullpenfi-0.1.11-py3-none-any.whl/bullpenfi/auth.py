from cryptography.fernet import Fernet
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Authenticator:
    def __init__(self):
        logger.debug("Initializing Authenticator")
        self.encryption_key = os.getenv("BULLPENFI_ENCRYPTION_KEY")
        logger.debug("BULLPENFI_ENCRYPTION_KEY: %s", self.encryption_key)

        if not self.encryption_key:
            logger.error("Encryption key not found in environment variables")
            raise ValueError("Encryption key not found in environment variables")

        logger.debug("Encryption key found, decrypting keys")
        self.valid_api_keys = self._decrypt_keys()

    def _decrypt_keys(self):
        encrypted_keys = b"gAAAAABmlU0dJpNsnxGZjj2jBHjV1JJIyq2wOv4gtMGzY9KW9WFjuzm9SkIKTuuITIAuRh8GWAyZJBdclqwD3o5UhqkI35pHAPYZc3xK7_j8elQeJ5oxTQpu582u_1Ak37KBpylt9enYysOkSjZh81Cwr6-d2npdZwhdsIPb9L747TSLVjxPJT_tdhrFO0RXre7kr5UBocBTf_kCLJNP7z3GNTHvdjNyP9AbjLvn3FqGxDfjMoDU2M9zXbcffs7-_bMqxpobU3EH7EahGYCjNUGNHTDHL03irLWdyAjVUSbGLcZ_F0Lxi_j5zKuWTNfPOs64aMtri-CkO1ASUKOYMAmHTuSsKzbhlNwhnfYPh8FfqRxpxbbraSE="
        cipher_suite = Fernet(self.encryption_key)
        decrypted_keys = cipher_suite.decrypt(encrypted_keys)
        return decrypted_keys.decode().split(",")

    def authenticate(self, api_key):
        if api_key not in self.valid_api_keys:
            raise PermissionError("Invalid API Key")


logger.debug("Environment variables: %s", os.environ)
authenticator = Authenticator()
