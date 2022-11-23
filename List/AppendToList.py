def latin(speak):
    translate = []
    arr=speak.split()
    for word in arr:
        translate.append(word[1:] + word[0] + 'ay')
        say = " ".join(translate)
    return say
print(latin("hello how are you"))