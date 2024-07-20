import requests

FRANKFURTER_API_URL = 'https://api.frankfurter.app/latest'

SUPPORTED_CURRENCIES = [
    {'country': 'IL', 'currency': 'ILS', 'symbol': '₪'},  # Israel
    {'country': 'FR', 'currency': 'EUR', 'symbol': '€'},  # France
    {'country': 'ES', 'currency': 'EUR', 'symbol': '€'},  # Spain
    {'country': 'PT', 'currency': 'EUR', 'symbol': '€'},  # Portugal
    {'country': 'IT', 'currency': 'EUR', 'symbol': '€'},  # Italy
    {'country': 'GR', 'currency': 'EUR', 'symbol': '€'},  # Greece
    {'country': 'CY', 'currency': 'EUR', 'symbol': '€'},  # Cyprus
    {'country': 'NL', 'currency': 'EUR', 'symbol': '€'},  # Netherlands
    {'country': 'BE', 'currency': 'EUR', 'symbol': '€'},  # Belgium
    {'country': 'LU', 'currency': 'EUR', 'symbol': '€'},  # Luxembourg
    {'country': 'IE', 'currency': 'EUR', 'symbol': '€'},  # Ireland
    {'country': 'FI', 'currency': 'EUR', 'symbol': '€'},  # Finland
    {'country': 'AT', 'currency': 'EUR', 'symbol': '€'},  # Austria
    {'country': 'MT', 'currency': 'EUR', 'symbol': '€'},  # Malta
    {'country': 'LT', 'currency': 'EUR', 'symbol': '€'},  # Lithuania
    {'country': 'LV', 'currency': 'EUR', 'symbol': '€'},  # Latvia
    {'country': 'EE', 'currency': 'EUR', 'symbol': '€'},  # Estonia
    {'country': 'SK', 'currency': 'EUR', 'symbol': '€'},  # Slovakia
    {'country': 'SI', 'currency': 'EUR', 'symbol': '€'},  # Slovenia
    {'country': 'US', 'currency': 'USD', 'symbol': '$'},  # United States
    {'country': 'GB', 'currency': 'GBP', 'symbol': '£'},  # United Kingdom
    {'country': 'DE', 'currency': 'EUR', 'symbol': '€'},  # Germany
    {'country': 'CA', 'currency': 'CAD', 'symbol': '$'},  # Canada
    {'country': 'AU', 'currency': 'AUD', 'symbol': '$'},  # Australia
    {'country': 'JP', 'currency': 'JPY', 'symbol': '¥'},  # Japan
    {'country': 'CN', 'currency': 'CNY', 'symbol': '¥'},  # China
    {'country': 'IN', 'currency': 'INR', 'symbol': '₹'},  # India
    {'country': 'BR', 'currency': 'BRL', 'symbol': 'R$'},  # Brazil
    {'country': 'ZA', 'currency': 'ZAR', 'symbol': 'R'},  # South Africa
    {'country': 'MX', 'currency': 'MXN', 'symbol': '$'},  # Mexico
    {'country': 'ID', 'currency': 'IDR', 'symbol': 'Rp'},  # Indonesia
    {'country': 'KR', 'currency': 'KRW', 'symbol': '₩'},  # South Korea
    {'country': 'SE', 'currency': 'SEK', 'symbol': 'kr'},  # Sweden
    {'country': 'NO', 'currency': 'NOK', 'symbol': 'kr'},  # Norway
    {'country': 'DK', 'currency': 'DKK', 'symbol': 'kr'},  # Denmark
    {'country': 'CH', 'currency': 'CHF', 'symbol': 'CHF'},  # Switzerland
    {'country': 'NZ', 'currency': 'NZD', 'symbol': '$'},  # New Zealand
    {'country': 'SG', 'currency': 'SGD', 'symbol': '$'},  # Singapore
    {'country': 'HK', 'currency': 'HKD', 'symbol': '$'},  # Hong Kong
    {'country': 'MY', 'currency': 'MYR', 'symbol': 'RM'},  # Malaysia
    {'country': 'TH', 'currency': 'THB', 'symbol': '฿'},  # Thailand
    {'country': 'PH', 'currency': 'PHP', 'symbol': '₱'},  # Philippines
    {'country': 'TR', 'currency': 'TRY', 'symbol': '₺'},  # Turkey
    {'country': 'PL', 'currency': 'PLN', 'symbol': 'zł'},  # Poland
]


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
