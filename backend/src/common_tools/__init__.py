from passlib.context import CryptContext


crypto_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
