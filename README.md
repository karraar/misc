# misc-python
## Puzzles
### Pairs that Add up to sum in array
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
