# Substance

![](./assets/images/substance.jpg)

Describe anything.

## Installation

### Python
```python
pip install --upgrade git+https://github.com/ParkhomenkoDV/substance.git@master
```

### Go
```go 
go get github.com/ParkhomenkoDV/substance
```

## Project structure
```
gte/
|--- docs/ 
|--- examples/  
|--- assets/images/  
|--- substance/  
|--- .gitignore
|--- README.md  
|--- requirements.txt
|--- setup.py
|--- substance_test.go
|--- substance.go
```

## Benchmarks
```
----------------------------------------------------------------- benchmark: 7 tests -----------------------------------------------------------------
Name (time in us)                           Min                Max               Mean            StdDev             Median            Rounds  Outliers
------------------------------------------------------------------------------------------------------------------------------------------------------
test_hardness_init                      17.1671 (386.32)   33.5410 (96.24)    19.1700 (374.09)   0.8229 (329.30)   19.3330 (374.74)     5180   749;878
test_substance_deepcopy                  2.0830 (46.88)    46.8330 (134.38)    2.4351 (47.52)    0.3643 (145.77)    2.4580 (47.64)     90572 1237;3870
test_substance_getattr[composition]      0.0451 (1.02)      0.4375 (1.26)      0.0516 (1.01)     0.0032 (1.30)      0.0521 (1.01)     19512028261;30192
test_substance_getattr[functions]        0.0456 (1.03)      0.3485 (1.0)       0.0523 (1.02)     0.0025 (1.0)       0.0526 (1.02)     19837313071;17249
test_substance_getattr[name]             0.0444 (1.0)       0.4766 (1.37)      0.0512 (1.0)      0.0032 (1.27)      0.0516 (1.0)      19833733871;37063
test_substance_getattr[parameters]       0.0452 (1.02)      0.3793 (1.09)      0.0521 (1.02)     0.0028 (1.11)      0.0522 (1.01)     19669719098;19514
test_substance_init                      1.1250 (25.32)    65.1249 (186.86)    1.3535 (26.41)    0.3982 (159.36)    1.3750 (26.65)     58970   309;897
------------------------------------------------------------------------------------------------------------------------------------------------------
```