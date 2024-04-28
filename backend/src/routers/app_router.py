from fastapi import APIRouter, Response, status


AppRouter = APIRouter(
    prefix=''
)


@AppRouter.get('/', status_code=status.HTTP_200_OK)
def generate_model(response: Response):
    return 'test'
