numeruesi = int(input("Enter the upper fraction : "))
emeruesi = int(input("Enter the lower fraction : "))

try:
    print(numeruesi/emeruesi)
except ZeroDivisionError:
    print("You can't divide by 0")