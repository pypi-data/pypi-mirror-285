# generify
generifies python classes to generic dict containing only python internals, numpy arrays and panda lists.

## Usage Example
below is a basic example

```python
from generify import generify

class Scalar:
    def __init__(self) -> None:
        self.val_int = 3
        self.val_float = 10.0
        self.val_str = "jhon"
        self.val_bool = True

generic_obj = generify(Scalar())
print(generic_obj)
```
