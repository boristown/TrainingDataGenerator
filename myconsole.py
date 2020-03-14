import datetime

timeformart = "%b %d %Y %H:%M:%S"

def timestr(text):
    return datetime.datetime.now().strftime(timeformart) + ":" + text

def out(text):
    print(timestr(text))

def in_num(text):
    num = input(timestr(text))
    try:
        num = int(num)
    except Exception as e:
        out(str(e))
        return in_num(text)
    else:
        return num