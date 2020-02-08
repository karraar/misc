## Misc Excercises
### Pairs that Add up to sum in array
```scala
  def printPairsThatAddUpTo(seq: Seq[Int], target_sum: Int): Unit = {
    def checkRest(elem: Int, rest: Seq[Int]): Unit = {
      if (rest.length < 2) return
      val need = target_sum - elem
      if (rest.contains(need)) println(s"$elem and $need")
      else checkRest(rest.head, rest.tail)
    }

    checkRest(seq.head, seq.tail)
  }
  printPairsThatAddUpTo(Seq(1,3,5,9),6)
```
```python
def printPairsThatAddUpTo(arr, target_sum):
    if len(arr) < 2:
        return
    for index, curr_element in enumerate(arr):
        need = target_sum - curr_element
        if need in arr[index+1:]:   #Only look after current position
           print("{} and {}".format(curr_element, need))
           break # exit if we found the first pair

# Driver to test
if __name__ == "__main__":
    arr = [10, 22, 28, 29, 30, 31, 40]
    printPairsThatAddUpTo(arr, 59)
```
