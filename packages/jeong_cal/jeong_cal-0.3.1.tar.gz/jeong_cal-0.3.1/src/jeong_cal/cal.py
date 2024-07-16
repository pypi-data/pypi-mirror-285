import sys

def cl_sum():

    from haram_sum.sum import sum

    if len(sys.argv) < 3:
        print("Usage: script <a> <b>")
        sys.exit(1)

    a, b = int(sys.argv[1]), int(sys.argv[2])
    print(a, "+", b)
    print(sum(a, b))


def cl_sub():
    from haram_sub.sub import sub

    if len(sys.argv) < 3:
        print("Usage: script <a> <b>")
        sys.exit(1)

    a, b = int(sys.argv[1]), int(sys.argv[2])
    print(a, "-", b)
    print(sub(a, b))


def cl_mul():

    from jeong_mul.mul import mul

    if len(sys.argv) < 3:
        print("Usage: script <a> <b>")
        sys.exit(1)

    a, b = int(sys.argv[1]), int(sys.argv[2])
    print(a, "*", b)
    print(mul(a, b))
