## Find the fist pair of numbers that add up to target_sum from Array/Seq/List
### Scala
```scala
  def findPairsThatAddUpTo(seq: Seq[Int], target_sum: Int): String = {
    @scala.annotation.tailrec
    def checkNextElem(elem: Int, rest: Seq[Int]): String = {
      rest.isEmpty match {
        case true => "got to end of Seq without finding a pair."
        case _ =>
          val need = target_sum - elem
          if (rest.contains(need)) s"Pair: $elem and $need"
          else checkNextElem(rest.head, rest.tail)
      }
    }
    checkNextElem(seq.head, seq.tail)
  }
  println(findPairsThatAddUpTo(Seq(1,3,5,9),8))
```
### Python3
```python3
def print_pairs_that_add_to_sum(arr, target_sum):
    def check_next_elem(elem, rest):
        if len(rest) < 1:
            return
        need = target_sum - elem
        if need in rest:
            print("{} and {}".format(elem, need))
        else:
            check_next_elem(rest[0], rest[1:])
    check_next_elem(arr[0],arr[1:])

# Driver to test
if __name__ == "__main__":
    arr = [10, 22, 28, 29, 30, 40, 31]
    print_pairs_that_add_to_sum(arr, 59)
```
