import datetime

timeformart = "%b %d %Y %H:%M:%S"

def timestr(text):
    return datetime.datetime.now().strftime(timeformart) + ":" + text

def line(text):
    print(timestr(text))

def readnum(text):
    num = input(timestr(text))
    try:
        num = int(num)
    except Exception as e:
        print(e)
        return readnum(text)
    else:
        return num