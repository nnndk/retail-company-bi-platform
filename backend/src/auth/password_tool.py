from passlib.context import CryptContext


class PasswordTool:
    """
    This class provides some static methods for hashing and verify passwords
    """
    _crypto_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    @staticmethod
    def get_hash_password(password: str) -> str:
        # Function to hash passwords
        return PasswordTool._crypto_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        # Function to verify passwords
        return PasswordTool._crypto_context.verify(plain_password, hashed_password)
