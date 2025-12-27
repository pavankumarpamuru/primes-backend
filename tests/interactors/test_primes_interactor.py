from unittest.mock import create_autospec

import pytest
from fastapi.responses import JSONResponse

from app.dtos import PrimeNumbersRequestDTO
from app.exceptions import InvalidInputException
from app.interactos.presenter_interface import IPrimeNumbersPresenter
from app.interactos.primes_interactor import PrimeNumbersInteractor


@pytest.fixture
def mock_presenter():
    presenter = create_autospec(spec=IPrimeNumbersPresenter, instance=True)
    presenter.get_success_response.return_value = JSONResponse(
        content={"success": True}, status_code=200
    )
    presenter.get_invalid_input_response.return_value = JSONResponse(
        content={"error": "invalid"}, status_code=400
    )
    return presenter


@pytest.fixture
def primes_interactor(mock_presenter):
    return PrimeNumbersInteractor(presenter=mock_presenter)


class TestPrimeNumbersInteractor:
    def test_is_prime_with_prime_number(self, primes_interactor):
        assert primes_interactor._is_prime(2) is True
        assert primes_interactor._is_prime(3) is True
        assert primes_interactor._is_prime(5) is True
        assert primes_interactor._is_prime(7) is True
        assert primes_interactor._is_prime(11) is True
        assert primes_interactor._is_prime(13) is True
        assert primes_interactor._is_prime(97) is True

    def test_is_prime_with_non_prime_number(self, primes_interactor):
        assert primes_interactor._is_prime(0) is False
        assert primes_interactor._is_prime(1) is False
        assert primes_interactor._is_prime(4) is False
        assert primes_interactor._is_prime(6) is False
        assert primes_interactor._is_prime(8) is False
        assert primes_interactor._is_prime(9) is False
        assert primes_interactor._is_prime(100) is False

    def test_is_prime_with_negative_number(self, primes_interactor):
        assert primes_interactor._is_prime(-1) is False
        assert primes_interactor._is_prime(-5) is False
        assert primes_interactor._is_prime(-10) is False

    def test_generate_n_primes_first_five(self, primes_interactor):
        result = primes_interactor._generate_n_primes(5)
        assert result == [2, 3, 5, 7, 11]

    def test_generate_n_primes_first_ten(self, primes_interactor):
        result = primes_interactor._generate_n_primes(10)
        assert result == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]

    def test_generate_n_primes_one_prime(self, primes_interactor):
        result = primes_interactor._generate_n_primes(1)
        assert result == [2]

    def test_generate_n_primes_twenty_primes(self, primes_interactor):
        result = primes_interactor._generate_n_primes(20)
        expected = [
            2,
            3,
            5,
            7,
            11,
            13,
            17,
            19,
            23,
            29,
            31,
            37,
            41,
            43,
            47,
            53,
            59,
            61,
            67,
            71,
        ]
        assert result == expected

    def test_validate_input_with_zero_count(self, primes_interactor):
        request_dto = PrimeNumbersRequestDTO(count=0, user_id="user123")
        with pytest.raises(InvalidInputException):
            primes_interactor._validate_input(request_dto)

    def test_validate_input_with_negative_count(self, primes_interactor):
        request_dto = PrimeNumbersRequestDTO(count=-5, user_id="user123")
        with pytest.raises(InvalidInputException):
            primes_interactor._validate_input(request_dto)

    def test_validate_input_exceeds_maximum(self, primes_interactor):
        request_dto = PrimeNumbersRequestDTO(count=10001, user_id="user123")
        with pytest.raises(InvalidInputException):
            primes_interactor._validate_input(request_dto)

    def test_validate_input_at_maximum_boundary(self, primes_interactor):
        request_dto = PrimeNumbersRequestDTO(count=10000, user_id="user123")
        primes_interactor._validate_input(request_dto)

    def test_validate_input_with_valid_count(self, primes_interactor):
        request_dto = PrimeNumbersRequestDTO(count=10, user_id="user123")
        primes_interactor._validate_input(request_dto)

    def test_execute_prime_generation_success(self, primes_interactor):
        request_dto = PrimeNumbersRequestDTO(count=5, user_id="user123")
        result = primes_interactor._execute_prime_generation(request_dto)

        assert result.count == 5
        assert result.primes == [2, 3, 5, 7, 11]

    def test_execute_prime_generation_invalid_input(self, primes_interactor):
        request_dto = PrimeNumbersRequestDTO(count=0, user_id="user123")
        with pytest.raises(InvalidInputException):
            primes_interactor._execute_prime_generation(request_dto)

    def test_generate_primes_wrapper_success(self, primes_interactor, mock_presenter):
        request_dto = PrimeNumbersRequestDTO(count=3, user_id="user123")
        response = primes_interactor.generate_primes_wrapper(request_dto)

        mock_presenter.get_success_response.assert_called_once()
        call_args = mock_presenter.get_success_response.call_args[1]
        result = call_args["result"]

        assert result.count == 3
        assert result.primes == [2, 3, 5]
        assert response.status_code == 200

    def test_generate_primes_wrapper_invalid_input(
        self, primes_interactor, mock_presenter
    ):
        request_dto = PrimeNumbersRequestDTO(count=-1, user_id="user123")
        response = primes_interactor.generate_primes_wrapper(request_dto)

        mock_presenter.get_invalid_input_response.assert_called_once()
        assert response.status_code == 400

    def test_generate_primes_wrapper_exceeds_limit(
        self, primes_interactor, mock_presenter
    ):
        request_dto = PrimeNumbersRequestDTO(count=20000, user_id="user123")
        response = primes_interactor.generate_primes_wrapper(request_dto)

        mock_presenter.get_invalid_input_response.assert_called_once()
        assert response.status_code == 400
