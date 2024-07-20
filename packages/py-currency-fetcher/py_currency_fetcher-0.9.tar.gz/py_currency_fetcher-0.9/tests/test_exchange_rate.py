import requests


def check_currency_support(base_currency, target_currency):
    url = f'https://api.frankfurter.app/latest?amount=1&from={base_currency}&to={target_currency}'
    response = requests.get(url)
    data = response.json()
    return 'message' not in data


def check_all_currencies(currencies):
    base_currency = 'USD'
    unsupported_currencies = []

    for country, currency in currencies.items():
        if currency != base_currency:
            if not check_currency_support(base_currency, currency):
                unsupported_currencies.append(currency)

    return unsupported_currencies


COUNTRY_CURRENCIES = {
    'UA': 'UAH', 'US': 'USD', 'GB': 'GBP', 'DE': 'EUR', 'CA': 'CAD',
    'AU': 'AUD', 'JP': 'JPY', 'CN': 'CNY', 'RU': 'RUB', 'IN': 'INR',
    'BR': 'BRL', 'ZA': 'ZAR', 'NG': 'NGN', 'MX': 'MXN', 'ID': 'IDR',
    'KR': 'KRW', 'SA': 'SAR', 'SE': 'SEK', 'NO': 'NOK', 'DK': 'DKK',
    'CH': 'CHF', 'NZ': 'NZD', 'SG': 'SGD', 'HK': 'HKD', 'MY': 'MYR',
    'TH': 'THB', 'PH': 'PHP', 'TR': 'TRY', 'IL': 'ILS', 'PL': 'PLN',
    'PK': 'PKR', 'EG': 'EGP', 'CL': 'CLP', 'CO': 'COP', 'PE': 'PEN',
    'AR': 'ARS', 'VE': 'VES', 'AE': 'AED', 'QA': 'QAR', 'KW': 'KWD',
    'OM': 'OMR', 'BH': 'BHD', 'FR': 'EUR', 'ES': 'EUR', 'PT': 'EUR',
    'IT': 'EUR', 'GR': 'EUR', 'CY': 'EUR', 'NL': 'EUR', 'BE': 'EUR',
    'LU': 'EUR', 'IE': 'EUR', 'FI': 'EUR', 'AT': 'EUR', 'MT': 'EUR',
    'LT': 'EUR', 'LV': 'EUR', 'EE': 'EUR', 'SK': 'EUR', 'SI': 'EUR'
}

unsupported = check_all_currencies(COUNTRY_CURRENCIES)
print("Непідтримувані валюти:")
for currency in unsupported:
    print(currency)