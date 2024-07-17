def callback(a, b):
    print('Sum = {0}'.format(a+b))

def main(a,b,f=None):
    print('Add any two digits.')
    if f is not None:
        f(a,b)

main(1, 2, callback)