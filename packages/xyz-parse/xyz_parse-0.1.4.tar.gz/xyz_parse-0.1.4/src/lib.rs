//! A parser for the [XYZ file format](https://en.wikipedia.org/wiki/XYZ_file_format)
//!
//! The formatting of the .xyz file format is as follows:
//!
//! ```
//! <number of atoms>
//! comment line
//! <element> <X> <Y> <Z>
//! ...
//! ```
//!
//! Currently the parser does not support extended XYZ format, but may do so in the future

mod atom;
mod molecule;
mod xyz;

#[cfg(feature = "pyo3")]
mod python;

pub use rust_decimal;

pub use atom::*;
pub use molecule::*;
pub use xyz::*;

/// Parse an [`Xyz`] string
pub fn parse_xyz(s: &str) -> Result<Xyz, XyzParseError> {
    Xyz::parse(s)
}
