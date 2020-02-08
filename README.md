# Misc Excercises
## Pairs that Add up to sum in array
### Scala
```scala
  def printPairsThatAddUpTo(seq: Seq[Int], target_sum: Int): Unit = {
    def checkRest(elem: Int, rest: Seq[Int]): Unit = {
      if (rest.length < 1) return
      val need = target_sum - elem
      if (rest.contains(need)) println(s"$elem and $need")
      else checkRest(rest.head, rest.tail)
    }

    checkRest(seq.head, seq.tail)
  }
  printPairsThatAddUpTo(Seq(1,3,5,9),6)
```
### Python3
```python3
def print_pairs_that_add_to_sum(arr, target_sum):
    def check_rest(elem, rest):
        if len(rest) < 1:
            return
        need = target_sum - elem
        if need in rest:
            print("{} and {}".format(elem, need))
        else:
            check_rest(rest[0], rest[1:])
    check_rest(arr[0],arr[1:])

# Driver to test
if __name__ == "__main__":
    arr = [10, 22, 28, 29, 30, 40, 31]
    print_pairs_that_add_to_sum(arr, 59)
```
