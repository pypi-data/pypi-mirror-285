import pycountry

COUNTRY_CURRENCIES = [
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
    {'country': 'UA', 'currency': 'UAH', 'symbol': '₴'},  # Ukraine
    {'country': 'US', 'currency': 'USD', 'symbol': '$'},  # United States
    {'country': 'GB', 'currency': 'GBP', 'symbol': '£'},  # United Kingdom
    {'country': 'DE', 'currency': 'EUR', 'symbol': '€'},  # Germany
    {'country': 'CA', 'currency': 'CAD', 'symbol': '$'},  # Canada
    {'country': 'AU', 'currency': 'AUD', 'symbol': '$'},  # Australia
    {'country': 'JP', 'currency': 'JPY', 'symbol': '¥'},  # Japan
    {'country': 'CN', 'currency': 'CNY', 'symbol': '¥'},  # China
    {'country': 'RU', 'currency': 'RUB', 'symbol': '₽'},  # Country 404
    {'country': 'IN', 'currency': 'INR', 'symbol': '₹'},  # India
    {'country': 'BR', 'currency': 'BRL', 'symbol': 'R$'},  # Brazil
    {'country': 'ZA', 'currency': 'ZAR', 'symbol': 'R'},  # South Africa
    {'country': 'NG', 'currency': 'NGN', 'symbol': '₦'},  # Nigeria
    {'country': 'MX', 'currency': 'MXN', 'symbol': '$'},  # Mexico
    {'country': 'ID', 'currency': 'IDR', 'symbol': 'Rp'},  # Indonesia
    {'country': 'KR', 'currency': 'KRW', 'symbol': '₩'},  # South Korea
    {'country': 'SA', 'currency': 'SAR', 'symbol': 'ر.س'},  # Saudi Arabia
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
    {'country': 'PK', 'currency': 'PKR', 'symbol': '₨'},  # Pakistan
    {'country': 'EG', 'currency': 'EGP', 'symbol': '£'},  # Egypt
    {'country': 'CL', 'currency': 'CLP', 'symbol': '$'},  # Chile
    {'country': 'CO', 'currency': 'COP', 'symbol': '$'},  # Colombia
    {'country': 'PE', 'currency': 'PEN', 'symbol': 'S/.'},  # Peru
    {'country': 'AR', 'currency': 'ARS', 'symbol': '$'},  # Argentina
    {'country': 'VE', 'currency': 'VES', 'symbol': 'Bs.S'},  # Venezuela
    {'country': 'AE', 'currency': 'AED', 'symbol': 'د.إ'},  # United Arab Emirates
    {'country': 'QA', 'currency': 'QAR', 'symbol': 'ر.ق'},  # Qatar
    {'country': 'KW', 'currency': 'KWD', 'symbol': 'د.ك'},  # Kuwait
    {'country': 'OM', 'currency': 'OMR', 'symbol': 'ر.ع.'},  # Oman
    {'country': 'BH', 'currency': 'BHD', 'symbol': 'ب.د'},  # Bahrain
]


def get_currency(
    country_code: str
) -> dict[str, str] | None:
    """Get currency information based on a given country code.

    Args:
        country_code (str): The two-letter country code (ISO 3166-1 alpha-2).

    Returns:
        str | dict[str, str]: A dictionary containing the currency and symbol
                              for the given country code if found, otherwise
                              an error message string.

    Example:
        >>> get_currency('US')
        {'country': 'US', 'currency': 'USD', 'symbol': '$'}
        >>> get_currency('XX')
        'No country found for code: XX'
    """
    country = pycountry.countries.get(alpha_2=country_code)
    if not country:
        return f"No country found for code: {country_code}"

    currency_info = next(
        (
            item for item in COUNTRY_CURRENCIES
            if item['country'] == country_code
        ),
        None
    )
    if currency_info:
        return currency_info
    return None


def currency_symbol(currency_code: str) -> str | None:
    """Get the currency symbol based on the given currency code.

    Args:
        currency_code (str): The three-letter currency code (ISO 4217).

    Returns:
        str: The currency symbol if found, otherwise an error message string.

    Example:
        >>> currency_symbol('USD')
        '$'
        >>> currency_symbol('EUR')
        '€'
    """
    currency_info = next(
        (
            item for item in COUNTRY_CURRENCIES
            if item['currency'] == currency_code
        ),
        None
    )
    if currency_info:
        return currency_info['symbol']
    return None
