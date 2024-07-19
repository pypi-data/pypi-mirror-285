# xyz-parse

A parser for the [XYZ file format](https://en.wikipedia.org/wiki/XYZ_file_format)

The formatting of the .xyz file format is as follows:

```rust
<number of atoms>
comment line
<element> <X> <Y> <Z>
...
```

Currently the parser does not support extended XYZ format, but may do so in the future
