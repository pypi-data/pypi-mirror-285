def cl_sum():
    import sys
    from haram_sum.sum import sum

    if len(sys.argv) < 3:
        print("Usage: script <a> <b>")
        sys.exit(1)

    a, b = int(sys.argv[1]), int(sys.argv[2])
    print(a, "+", b)
    print(sum(a, b))


def cl_sub():
    import sys
    from haram_sub.sub import sub

    if len(sys.argv) < 3:
        print("Usage: script <a> <b>")
        sys.exit(1)

    a, b = int(sys.argv[1]), int(sys.argv[2])
    print(a, "-", b)
    print(sub(a, b))


def cl_mul():
    import sys
    from jeong_mul.mul import mul

    if len(sys.argv) < 3:
        print("Usage: script <a> <b>")
        sys.exit(1)

    a, b = int(sys.argv[1]), int(sys.argv[2])
    print(a, "*", b)
    print(mul(a, b))
