#  here all URLs for web-based data defined

# general macrotrends URL, ticker should be defined
url_general = 'https://www.macrotrends.net/stocks/charts/{ticker}/xxx/'

sub_urls = {
    # INCOME STATEMENT
    'Revenue': 'revenue',
    'Gross Profit': 'gross-profit',  # revenue with costs of sales excluded
    'Research and Development Expenses': 'research-development-expenses',
    'SG&A Expenses': 'selling-general-administrative-expenses',
    'EBITDA': 'ebitda',
    'Operating Income': 'operating-income',  # income before taxes and interest paid
    'Net Income': 'net-income',
    'EPS': 'eps-earnings-per-share-diluted',
    'Shares Outstanding': 'shares-outstanding',
    # PRICE
    'Price': 'stock-price-history',
    'Market Cap': 'market-cap',
    # BALANCE
    'Total Liabilities': 'total-liabilities',
    'Total Assets': 'total-assets'

}
