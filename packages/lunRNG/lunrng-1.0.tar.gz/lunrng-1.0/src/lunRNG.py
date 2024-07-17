import pylunar, datetime

# obtain moon
moon = pylunar.MoonInfo((0, 0, 0), (0, 0, 0))

# gets random number and uses that as array index
def choice(array: list):
    i = randInt(0, len(array) - 1)
    return(array[i])

# uses random seed to return a int between the given bounds
def randInt(lower: int, upper: int):
    rand = random()
    rand = rand * rand * 473
    while rand < lower or rand > upper:
        if rand < lower:
            rand = rand * rand * 473
        if rand > upper:
            rand = rand / 7
    return round(rand)

# // this is cursed
# // i am not sorry
# // returns a float between 0 and 1.0
def random():

    # // parse the entire float to isolate the numbers after the decimal point
    foundDecimal = 0
    num = "0."
    moon.update(datetime.datetime.now())
    for char in str(moon.fractional_phase() * 10000000):
        if foundDecimal:
            num += char
        if (char == "."):
            foundDecimal = 1
    
    # // truncate to 14 decimal places
    while len(num) > 16:
        num = list(num)
        num.pop(len(num) - 2)
        num = "".join(num)
    
    # // return the string as a float
    return (float(num))