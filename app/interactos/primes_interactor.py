from fastapi.responses import JSONResponse

from app.constants import MAX_PRIME_COUNT
from app.dtos import PrimeNumbersRequestDTO, PrimeNumbersResultDTO
from app.exceptions import InvalidInputException
from app.interactos.presenter_interface import IPrimeNumbersPresenter


class PrimeNumbersInteractor:
    def __init__(self, presenter: IPrimeNumbersPresenter):
        self.presenter = presenter

    def generate_primes_wrapper(
        self, request_dto: PrimeNumbersRequestDTO
    ) -> JSONResponse:
        try:
            result = self._execute_prime_generation(request_dto=request_dto)
            return self.presenter.get_success_response(result=result)
        except InvalidInputException as e:
            return self.presenter.get_invalid_input_response(message=str(e))

    def _execute_prime_generation(
        self, request_dto: PrimeNumbersRequestDTO
    ) -> PrimeNumbersResultDTO:
        self._validate_input(request_dto=request_dto)
        primes = self._generate_n_primes(count=request_dto.count)
        return PrimeNumbersResultDTO(count=request_dto.count, primes=primes)

    def _validate_input(self, request_dto: PrimeNumbersRequestDTO) -> None:
        if request_dto.count <= 0:
            raise InvalidInputException()

        if request_dto.count > MAX_PRIME_COUNT:
            raise InvalidInputException()

    def _generate_n_primes(self, count: int) -> list[int]:
        primes = []
        num = 2

        while len(primes) < count:
            if self._is_prime(num):
                primes.append(num)
            num += 1

        return primes

    def _is_prime(self, n: int) -> bool:
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False

        for i in range(3, int(n**0.5) + 1, 2):
            if n % i == 0:
                return False
        return True
