from fastapi.security import OAuth2PasswordBearer


# Authentication & authorization settings
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')
ACCESS_TOKEN_EXPIRE_MINUTES = 30
