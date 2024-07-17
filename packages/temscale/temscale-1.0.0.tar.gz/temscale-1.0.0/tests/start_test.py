from temscale import temscale

while True:
    value = float(input("Enter a number: "))
    type_tem = input("Enter a str: ")
    test = temscale.Temscale(value, type_tem)
    print(test.get_value())
    test.to_celsius()
    print(test.get_value())

    value = float(input("Enter a number: "))
    type_tem = input("Enter a str: ")
    test = temscale.Temscale(value, type_tem)
    print(test.get_value())
    test.to_fahrenheit()
    print(test.get_value())
