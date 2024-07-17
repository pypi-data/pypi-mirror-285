# PyO2: A lightweight method to call Rust code from Python

*Not affiliated at all with [PyO3](https://github.com/PyO3/pyo3). Is that what you were looking for?*

## Usage

File: *Cargo.toml*

```toml
[package]
name = "mylib"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]

[dependencies]
pyo2 = "0.1.0"
```

File: *src/lib.rs*

```rust
use pyo2::{PyStr, PyVec};

#[no_mangle]
pub extern "C" fn test(name: &PyStr, numbers: &mut PyVec<i64>) {
    println!("Hello, {}!", unsafe { name.as_str_unchecked() });
    println!("Sum of numbers: {}", numbers.iter().cloned().sum::<i64>());
    numbers[0] = 6;
}
```

File: *test.py*

```python
from pyo2 import RustDLL

dll = RustDLL('./libmylib.so')

s = 'World'
lst = [1, 2, 3, 4, 5]
dll.test(s, lst)
print(lst)
```

Output:

```text
Hello, World!
Sum of numbers: 15
[6, 2, 3, 4, 5]
```
