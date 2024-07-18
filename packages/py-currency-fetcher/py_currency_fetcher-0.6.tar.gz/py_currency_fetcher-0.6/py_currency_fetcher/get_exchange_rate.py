import requests

FRANKFURTER_API_URL = 'https://api.frankfurter.app/latest'


def get_exchange_rate(
    amount: int,
    base_currency: str,
    target_currency: str
) -> dict[str | str, float] | str:
    """Get the exchange rate from base currency to target currency.

    Args:
        amount (int): The amount to convert.
        base_currency (str): The base currency code (ISO 4217).
        target_currency (str): The target currency code (ISO 4217).

    Returns:
        dict: A dictionary containing the exchange rate information.
        str: An error message if the request fails or the response is invalid.

    Example:
        >>> get_exchange_rate('USD', 'ILS')
        {'base': 'USD', 'target': 'ILS', 'amount': 10, 'rate': 3.25}
    """
    url = '{0}?amount={1}&from={2}&to={3}'.format(
        FRANKFURTER_API_URL,
        amount,
        base_currency,
        target_currency
    )
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()

        # Extracting relevant data
        rate = data['rates'].get(target_currency)
        if rate is not None:
            return {
                'base': base_currency,
                'target': target_currency,
                'amount': amount,
                'rate': rate
            }
        else:
            return f"Exchange rate not found for {target_currency}."

    except requests.RequestException as e:
        return f"An error occurred while fetching exchange rate: {e}"
    except ValueError:
        return "An error occurred while parsing the response."
