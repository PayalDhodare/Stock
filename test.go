package main

import (
	"fmt"
	"github.com/shubhamgosain/stockrate"
)

func main() {
	fmt.Println(stockrate.GetMovingAverage("aubank"))
}