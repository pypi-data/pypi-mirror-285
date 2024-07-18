# rmcc
The rmcc is Regional Mesh Code Calculator.

# Installation
```
pip install rmcc
```

# Usage
```python
from rmcc import MeshCode

meshCode = MeshCode.parse("5339-00-00-1")
neighbors = meshCode.calNeighbors(2)
```
The variable `neighbors` is an array. It represents the yellow and blue fields in the image below. An Argument "2" of `calNeighbors` method means distance from center mesh.

![](./images/neighbors.drawio.svg)
