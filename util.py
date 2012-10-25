from datetime import datetime

def parse_date(d):
    """
    Parse a date of style "Tue Oct 23 15:55:52 +0000 2012"
    @author Markus Tacker <m@coderbyheart.de>
    """
    d = d.split(" ")
    year = int(d[5])
    months = {1: "Jan", 2:"Feb", 3:"Mar", 4:"Apr", 5:"May", 6:"Jun", 7:"Jul", 8:"Aug", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dec"}
    month = 1
    for m in months.iterkeys():
        if d[1] == months[m]:
            month = m
    day = int(d[2])
    time = d[3].split(":")
    hour = int(time[0])
    minute = int(time[1])
    second = int(time[2])
    return datetime(year, month, day, hour, minute, second)