

def isleapYear(n):
    leap = False
    if n%4 == 0:
        leap = True
    if n%4 == 0 and n%100 == 0:
        leap =False
    if n%4 == 0 and n%100 == 0 and n%400 == 0:
        leap = True
    return leap

print(isleapYear(1990))