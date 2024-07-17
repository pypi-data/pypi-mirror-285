# hc_calculation

## Description

Python package `hc_add`, which is a dependency for the package `simpleCalc_cmd`. 

## Installation

```
$ pip install hc_add
```

Alternatively, it is automatically installed when you install `simpleCalc_cmd`, which can be done by
```
$ pip install simpleCalc_cmd
```
For more information, refer [simpleCalc_cmd github](https://github.com/hamsunwoo/simpleCalc_cmd)

## What does it do?
This package holds a simple function `add` which take 2 integer in-line variables and calculates the corresponding addition operation. Handles error when in-line arguments are not given, in the wrong number, or wrong format.

For additional usages, look at `simpleCalc_cmd` github or read below.

### Package Import example

```
from hc_add.hc_add import add
add()
```
