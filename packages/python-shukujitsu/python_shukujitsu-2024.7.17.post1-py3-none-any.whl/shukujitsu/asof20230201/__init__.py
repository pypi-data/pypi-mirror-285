from pkgutil import get_data

# https://www8.cao.go.jp/chosei/shukujitsu/shukujitsu.csv
BIN = get_data("shukujitsu.asof20230201", "shukujitsu.csv")
if BIN:
    TXT = BIN.decode("cp932")
else:
    raise ImportError("Can't load shukujitsu.csv under {}".format(__name__))
