import comics
#date="2024-11-21"
date = input("Date?\n")
comic="bignate"

ch = comics.search(comic, date=date)
ch.download(comic + ".png")
#print(ch.date)