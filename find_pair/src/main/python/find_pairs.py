#!/usr/bin/env python3


# This fails when we have too many recursive calls
def find_pairs_recursively(array, target_sum):

    def check_next_elem(elem, rest):
        if len(rest) < 1:
            print("\tGot to end of array.")
            return
        need = target_sum - elem
        if need in rest:
            print("\tPair: {} and {}".format(elem, need))
        else:
            check_next_elem(rest[0], rest[1:])

    check_next_elem(array[0], array[1:])


def find_pairs_loop(array, target_sum):
    for (i, x) in enumerate(array):
        if (target_sum-x) in array[i:]:
            print("\tPair: {} and {}".format(x, target_sum-x))
            return
    print("\tGot to end of array.")


# Driver to test
if __name__ == "__main__":
    arr = range(2, 5000, 8)
    target_sum = 5004 + (8*21)
    import timeit

    print("Loop:")
    loopTime = timeit.timeit(lambda: find_pairs_loop(arr, target_sum), number=1) * 1000 * 1000
    print("\tExecution Time: {0:.0f} MilliSeconds".format(loopTime))
    # Loop:
        # Pair: 1508994 and 49999994
        # Execution Time: 81 MicroSeconds


    print()
    print("Recursive:")
    recursiveTime = timeit.timeit(lambda: find_pairs_recursively(arr, target_sum), number=1) * 1000 * 1000
    print("\tExecution Time: {0:.0f} MilliSeconds".format(recursiveTime))
    # Recursive:
    # Pair: 5 and 3698918
    # Execution Time: 0.00001

