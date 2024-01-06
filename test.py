
def myMethod(a, b, **kwargs):
    print(a)
    print(b)
    print(kwargs)


if __name__ == "__main__":
    mydict = {'c': 3, 'd': 4}

    myarr = [1,2,{'c': 3, 'd': 4}]
    myMethod(1, 2, **myarr[2])
    # print("Hello World!

