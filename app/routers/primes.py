from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.constants import MAX_PRIME_COUNT
from app.dependencies import get_current_user
from app.dtos import PrimeNumbersRequestDTO
from app.interactos.primes_interactor import PrimeNumbersInteractor
from app.models import User
from app.presenters.presenter_implementation import PrimeNumbersPresenter

router = APIRouter(prefix="/api/v1/primes", tags=["primes"])


class PrimeNumbersRequest(BaseModel):
    count: int = Field(..., gt=0, le=MAX_PRIME_COUNT)


@router.post("/generate")
async def generate_primes(
    request_data: PrimeNumbersRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    presenter = PrimeNumbersPresenter()
    interactor = PrimeNumbersInteractor(presenter=presenter)

    request_dto = PrimeNumbersRequestDTO(
        count=request_data.count, user_id=current_user.id
    )

    return interactor.generate_primes_wrapper(request_dto=request_dto)
