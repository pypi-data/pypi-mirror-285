# UnitConvert

![win](https://github.com/LorenzoPeri17/UnitConverter/actions/workflows/Windows.yaml/badge.svg)
![ubu](https://github.com/LorenzoPeri17/UnitConverter/actions/workflows/Ubuntu.yaml/badge.svg)
![mac](https://github.com/LorenzoPeri17/UnitConverter/actions/workflows/macOS.yaml/badge.svg)

A CLI tool to convert units!

Have you ever been stuck in a horrible place where $\hbar \neq 1$?
Tired of remembering that $50$ mK $\sim 70$ mT $\sim 1$ GHz?
I know how it feels, I have been there too! And I can offer the solution to all the problems with this fantasmagorical tool!

To get it, simply

``` bash
$ pip install electronunitconverter
```

and then you will be able to type 

``` bash
$ UnitConverter T=10mK
Temperature
10.0 mK
0.2 GHz
0.9 ueV
```

For those adventuorous, there is also a python interface

``` python
from UnitConverter import MagneticField

B = MagneticField(1e-3, "T")

B_in_GHz = B.convert("GHz")
```
