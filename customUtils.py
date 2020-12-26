from string import ascii_letters, digits, punctuation

letters1Byte = ascii_letters + digits + punctuation + " "

def getLettersNum(text: str):
    letterN = 0
    for letter in text:
        if letter in letters1Byte:
            letterN += 1
        else:
            letterN += 2
    return letterN