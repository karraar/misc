
object FindPairs extends App {
  def findPairsRecursively(seq: Seq[Int], target_sum: Int): String = {
    @scala.annotation.tailrec
    def checkNextElem(elem: Int, rest: Seq[Int]): String = {
      rest.isEmpty match {
        case true => "No Pairs found"
        case _ =>
          val need = target_sum - elem
          if (rest.contains(need)) s"Pair: $elem and $need"
          else checkNextElem(rest.head, rest.tail)
      }
    }
    checkNextElem(seq.head, seq.tail)
  }

  def findPairsInLoop(seq: Seq[Int], target_sum: Int): String = {
    for (elem <- seq) {
      if (seq.tail.contains(target_sum-elem))
        return s"Pair: $elem and ${target_sum-elem}"
    }
    "No Pairs found"
  }

  def measureCall(f: (Seq[Int],Int) => String, s: Seq[Int], i: Int): Unit = {
    val startTime = System.nanoTime
    println(s"\t${f(s,i)}")
    val micros = (System.nanoTime - startTime) / 1000
    println(f"\tExecution Took: ${micros}%,d MicroSeconds")
  }

  val seq = 1 to 50000000 by 5
  val target_sum = 347332
  println("Recursive:")
  measureCall(findPairsRecursively, seq, target_sum)
//  Recursive:
//    Pair: 1 and 347331
//  Execution Took: 868 MicroSeconds
  println("Loop:")
  measureCall(findPairsInLoop, seq, target_sum)
//  Loop:
//    Pair: 1 and 347331
//  Execution Took: 2,336 MicroSeconds
}
