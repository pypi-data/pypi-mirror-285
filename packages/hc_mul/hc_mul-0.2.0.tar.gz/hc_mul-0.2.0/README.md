# hc_calculation

## Description

Python package `hc_mul`, which is a dependency for the package `simpleCalc_cmd`. 

## Installation

```
$ pip install hc_mul
```

Alternatively, it is automatically installed when you install `simpleCalc_cmd`, which can be done by
```
$ pip install simpleCalc_cmd
```
For more information, refer [simpleCalc_cmd github](https://github.com/hamsunwoo/simpleCalc_cmd)

## What does it do?
This package holds a simple function `mul` which take 2 integer in-line variables and calculates the corresponding multiplication operation. Handles errors if in-line variables are in the wrong format or number.

For additional usages, look at `simpleCalc_cmd` github or read below.

### Package Import example

```
from hc_mul.hc_mul import mul
mul()
```
