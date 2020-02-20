# This fails when we have too many recursive calls
def find_pairs_recursively(array, target_sum):
    def check_next_elem(elem, rest):
        if len(rest) < 1:
            print("Got to end of array.")
            return
        need = target_sum - elem
        if need in rest:
            print("{} and {}".format(elem, need))
        else:
            check_next_elem(rest[0], rest[1:])

    check_next_elem(array[0], array[1:])


def find_pairs_loop(array, target_sum):
    for (i, x) in enumerate(array):
        if (target_sum-x) in array[i:]:
            print("{} and {}".format(x, target_sum-x))
            break


# Driver to test
if __name__ == "__main__":
    arr = range(5, 500000000, 3)
    import timeit

    loopTime = timeit.timeit(lambda: find_pairs_loop(arr, 3698923), number=1)
    print("Loop Time: {0:.5f}".format(loopTime))
    # 5 and 3698918
    # Loop Time: 0.00003

    recursiveTime = timeit.timeit(lambda: find_pairs_recursively(arr, 3698923), number=1)
    print("Recursive time: {0:.5f}".format(recursiveTime))
    # 5 and 3698918
    # Recursive time: 0.00001

