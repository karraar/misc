package FindPair

object FindPair extends App {
  def findPairsRecursively(seq: Seq[Int], target_sum: Int): String = {
    @scala.annotation.tailrec
    def checkNextElem(elem: Int, rest: Seq[Int]): String = {
      if (rest.isEmpty)
        "No Pairs found"
      else {
          val need = target_sum - elem
          if (rest.contains(need)) s"Pair: $elem and $need"
          else checkNextElem(rest.head, rest.tail)
      }
    }
    checkNextElem(seq.head, seq.tail)
  }

  def findPairsInLoop(seq: Seq[Int], target_sum: Int): String = {
    var rest = seq.tail
    for (elem <- seq) {
      if (rest.contains(target_sum-elem))
        return s"Pair: $elem and ${target_sum-elem}"
      else
        if (rest.nonEmpty)
          rest = rest.tail
    }
    "No Pairs found"
  }

  def measureCall(f: (Seq[Int],Int) => String, s: Seq[Int], i: Int): Unit = {
    val startTime = System.nanoTime
    println(s"\t${f(s,i)}")
    println(f"\tExecution Took: ${(System.nanoTime - startTime) / 1000 }%,d MicroSeconds")
  }

  val seq = 2 to 50000000 by 8

  val target_sum = 51508988

  println("Recursive:")
  measureCall(findPairsRecursively, seq, target_sum)
//  Recursive:
//    Pair: 1508994 and 49999994
//  Execution Took: 24,085 MicroSeconds
  println("Loop:")
  measureCall(findPairsInLoop, seq, target_sum)
//  Loop:
//    Pair: 1508994 and 49999994
//  Execution Took: 16,985 MicroSeconds
}
