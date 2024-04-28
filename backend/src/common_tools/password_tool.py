from common_tools import crypto_context


class PasswordTool:
    @staticmethod
    def get_hash_password(password: str) -> str:
        # Function to hash passwords
        return crypto_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        # Function to verify passwords
        return crypto_context.verify(plain_password, hashed_password)
