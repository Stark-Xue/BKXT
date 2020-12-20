l = []
s = "heLLO woRLD"
for i in s:
    if ord(i)<=97 and ord(i)<=122 :
        l.append(chr(ord(i)-32))
    elif ord(i)<=65 and ord(i)<=90 :
        l.append(chr(ord(i)+32))
l = str(l)
print(l)