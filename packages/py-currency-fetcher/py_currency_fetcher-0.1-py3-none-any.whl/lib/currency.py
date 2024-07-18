import pycountry

COUNTRY_CURRENCIES = {
    'UA': 'UAH',  # Ukraine
    'US': 'USD',  # United States
    'GB': 'GBP',  # United Kingdom
    'DE': 'EUR',  # Germany
    'CA': 'CAD',  # Canada
    'AU': 'AUD',  # Australia
    'JP': 'JPY',  # Japan
    'CN': 'CNY',  # China
    'RU': 'RUB',  # Country 404
    'IN': 'INR',  # India
    'BR': 'BRL',  # Brazil
    'ZA': 'ZAR',  # South Africa
    'NG': 'NGN',  # Nigeria
    'MX': 'MXN',  # Mexico
    'ID': 'IDR',  # Indonesia
    'KR': 'KRW',  # South Korea
    'SA': 'SAR',  # Saudi Arabia
    'SE': 'SEK',  # Sweden
    'NO': 'NOK',  # Norway
    'DK': 'DKK',  # Denmark
    'CH': 'CHF',  # Switzerland
    'NZ': 'NZD',  # New Zealand
    'SG': 'SGD',  # Singapore
    'HK': 'HKD',  # Hong Kong
    'MY': 'MYR',  # Malaysia
    'TH': 'THB',  # Thailand
    'PH': 'PHP',  # Philippines
    'TR': 'TRY',  # Turkey
    'IL': 'ILS',  # Israel
    'PL': 'PLN',  # Poland
    'PK': 'PKR',  # Pakistan
    'EG': 'EGP',  # Egypt
    'CL': 'CLP',  # Chile
    'CO': 'COP',  # Colombia
    'PE': 'PEN',  # Peru
    'AR': 'ARS',  # Argentina
    'VE': 'VES',  # Venezuela
    'AE': 'AED',  # United Arab Emirates
    'QA': 'QAR',  # Qatar
    'KW': 'KWD',  # Kuwait
    'OM': 'OMR',  # Oman
    'BH': 'BHD',  # Bahrain
    'FR': 'EUR',  # France
    'ES': 'EUR',  # Spain
    'PT': 'EUR',  # Portugal
    'IT': 'EUR',  # Italy
    'GR': 'EUR',  # Greece
    'CY': 'EUR',  # Cyprus
    'NL': 'EUR',  # Netherlands
    'BE': 'EUR',  # Belgium
    'LU': 'EUR',  # Luxembourg
    'IE': 'EUR',  # Ireland
    'FI': 'EUR',  # Finland
    'AT': 'EUR',  # Austria
    'MT': 'EUR',  # Malta
    'LT': 'EUR',  # Lithuania
    'LV': 'EUR',  # Latvia
    'EE': 'EUR',  # Estonia
    'SK': 'EUR',  # Slovakia
    'SI': 'EUR',  # Slovenia
}


def get_currency(country_code):
    country = pycountry.countries.get(alpha_2=country_code)
    if not country:
        return f"No country found for code: {country_code}"
    return COUNTRY_CURRENCIES.get(country_code, "Currency not found")

