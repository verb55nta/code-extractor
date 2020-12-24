from getCodes import getCodes


def main():
    filepath = '../tests/test_object/5ch_stock.html'
    url = 'https://egg.5ch.net/test/read.cgi/stock/1608794163/'
    #codes = getCodes(filepath=filepath, sortOps=True)
    codes = getCodes(url=url, sortOps=True)
    print(codes[:10])


if __name__ == "__main__":
    main()
