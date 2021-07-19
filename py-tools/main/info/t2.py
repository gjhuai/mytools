import datetime,time
today = datetime.datetime.today()
today.timestamp()
dt = datetime.datetime(today.year, today.month, today.day-1, 0, 0, 0)
# delta=datetime.timedelta(days=-1)
# dt=dt+delta
# print(dt)
print(int(dt.timestamp()*1000))
# print(1621067790000)
