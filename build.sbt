ThisBuild / name := "misc"
ThisBuild / organization := "misc"
ThisBuild / version := "0.0.1-SNAPSHOT"

ThisBuild / scalaVersion := "2.13.1"

lazy val root = (project in file("."))
  .aggregate(find_pair)

lazy val find_pair = (project in file("find_pair"))