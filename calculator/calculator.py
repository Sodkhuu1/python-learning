print("Toonii mashin")
a = int(input("ehnii toogoo oruulna uu: "))
opr = input("uildelee oruulna uu (+, -, *, /)")
b = int(input("2 dahi toogoo oruulna uu: "))
match opr:
    case "+":
        print("Niilber ni: ", a + b)
    case "-":
        print("ylgavar ni: ", a - b)
    case "*":
        print("urjver ni: ", a * b)
    case "/":
        if b == 0:
            print("Тоог 0-д хувааж болохгүй!")
        else:
            print("noogdvor ni: ", a / b)
    case _:
        print("Буруу үйлдэл орууллаа!")