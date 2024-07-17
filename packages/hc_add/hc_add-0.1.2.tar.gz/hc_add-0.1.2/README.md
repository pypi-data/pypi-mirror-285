# hc_calculation

## Description

This repository holds the code for the three python packages `hc_add`, `hc_mul`, and `hc_div`, which are dependencies for the package `simpleCalc_cmd`. 

## Installation

```
$ pip install hc_add
$ pip install hc_mul
$ pip install hc_div
```

Alternatively, these packages are automatically installed if you install `simpleCalc_cmd`, which can be done by
```
$ pip install simpleCalc_cmd
```
For more information, refer [simpleCalc_cmd github](https://github.com/hamsunwoo/simpleCalc_cmd)

## What does it do?
All of these modules have simple functions which take 2 integer in-line variables and calculates the corresponding operation: addition for `hc_add`, multiplication for `hc_mul`, and integer division for `hc_div`.

In particular, for `hc_div` the division result is formatted into the form of `QUOTIENT remainder REMAINDER`.

For additional usages, look at `simpleCalc_cmd` github or read below.

### Package Import example

```
from hc_add.hc_add import add
add()
```
```
from hc_mul.hc_mul import mul
mul()
```
```
from hc_div.hc_div import div
div()
```

