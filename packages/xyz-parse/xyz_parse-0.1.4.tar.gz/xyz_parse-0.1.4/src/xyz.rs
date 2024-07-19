use crate::molecule::{Molecule, MoleculeParseError};
use std::{error::Error, fmt, str::FromStr};

/// An error that can occur while parsing an [`Xyz`]
#[derive(Debug, Clone)]
pub enum XyzParseError<'a> {
    InvalidMolecule(usize, MoleculeParseError<'a>),
}

impl<'a> XyzParseError<'a> {
    pub fn into_owned(self) -> XyzParseError<'static> {
        match self {
            Self::InvalidMolecule(num, err) => {
                XyzParseError::InvalidMolecule(num, err.into_owned())
            }
        }
    }
}

impl<'a> fmt::Display for XyzParseError<'a> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::InvalidMolecule(num, err) => write!(f, "Invalid molecule {num}: {err}"),
        }
    }
}

impl Error for XyzParseError<'static> {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        match self {
            Self::InvalidMolecule(_, err) => Some(err),
        }
    }
}

/// A list of molecules
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct Xyz<'a> {
    pub molecules: Vec<Molecule<'a>>,
}

impl<'a> Xyz<'a> {
    pub fn parse(string: &'a str) -> Result<Self, XyzParseError> {
        let mut lines = string.lines().peekable();
        let mut molecules = Vec::new();
        while lines.peek().is_some() {
            molecules.push(
                Molecule::parse_lines(&mut lines)
                    .map_err(|err| XyzParseError::InvalidMolecule(molecules.len(), err))?,
            );
        }
        Ok(Xyz { molecules })
    }

    pub fn into_owned(self) -> Xyz<'static> {
        Xyz {
            molecules: self
                .molecules
                .into_iter()
                .map(|molecule| molecule.into_owned())
                .collect(),
        }
    }
}

impl<'a> fmt::Display for Xyz<'a> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let mut iter = self.molecules.iter().peekable();
        while let Some(molecule) = iter.next() {
            write!(f, "{molecule}")?;
            if iter.peek().is_some() {
                writeln!(f)?;
            }
        }
        Ok(())
    }
}

impl FromStr for Xyz<'static> {
    type Err = XyzParseError<'static>;
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        Xyz::parse(s)
            .map(|res| res.into_owned())
            .map_err(|err| err.into_owned())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{atom::Atom, molecule::Molecule};
    use rust_decimal::Decimal;
    use std::borrow::Cow;

    const PYRIDINE: &str = r#"11

C       -0.180226841      0.360945118     -1.120304970
C       -0.180226841      1.559292118     -0.407860970
C       -0.180226841      1.503191118      0.986935030
N       -0.180226841      0.360945118      1.29018350
C       -0.180226841     -0.781300882      0.986935030
C       -0.180226841     -0.837401882     -0.407860970
H       -0.180226841      0.360945118     -2.206546970
H       -0.180226841      2.517950118     -0.917077970
H       -0.180226841      2.421289118      1.572099030
H       -0.180226841     -1.699398882      1.572099030
H       -0.180226841     -1.796059882     -0.917077970"#;

    fn pyridine() -> Molecule<'static> {
        Molecule {
            comment: Cow::Borrowed(""),
            atoms: vec![
                Atom {
                    symbol: Cow::Borrowed("C"),
                    x: Decimal::from_str_exact("-0.180226841").unwrap(),
                    y: Decimal::from_str_exact("0.360945118").unwrap(),
                    z: Decimal::from_str_exact("-1.120304970").unwrap(),
                },
                Atom {
                    symbol: Cow::Borrowed("C"),
                    x: Decimal::from_str_exact("-0.180226841").unwrap(),
                    y: Decimal::from_str_exact("1.559292118").unwrap(),
                    z: Decimal::from_str_exact("-0.407860970").unwrap(),
                },
                Atom {
                    symbol: Cow::Borrowed("C"),
                    x: Decimal::from_str_exact("-0.180226841").unwrap(),
                    y: Decimal::from_str_exact("1.503191118").unwrap(),
                    z: Decimal::from_str_exact("0.986935030").unwrap(),
                },
                Atom {
                    symbol: Cow::Borrowed("N"),
                    x: Decimal::from_str_exact("-0.180226841").unwrap(),
                    y: Decimal::from_str_exact("0.360945118").unwrap(),
                    z: Decimal::from_str_exact("1.29018350").unwrap(),
                },
                Atom {
                    symbol: Cow::Borrowed("C"),
                    x: Decimal::from_str_exact("-0.180226841").unwrap(),
                    y: Decimal::from_str_exact("-0.781300882").unwrap(),
                    z: Decimal::from_str_exact("0.986935030").unwrap(),
                },
                Atom {
                    symbol: Cow::Borrowed("C"),
                    x: Decimal::from_str_exact("-0.180226841").unwrap(),
                    y: Decimal::from_str_exact("-0.837401882").unwrap(),
                    z: Decimal::from_str_exact("-0.407860970").unwrap(),
                },
                Atom {
                    symbol: Cow::Borrowed("H"),
                    x: Decimal::from_str_exact("-0.180226841").unwrap(),
                    y: Decimal::from_str_exact("0.360945118").unwrap(),
                    z: Decimal::from_str_exact("-2.206546970").unwrap(),
                },
                Atom {
                    symbol: Cow::Borrowed("H"),
                    x: Decimal::from_str_exact("-0.180226841").unwrap(),
                    y: Decimal::from_str_exact("2.517950118").unwrap(),
                    z: Decimal::from_str_exact("-0.917077970").unwrap(),
                },
                Atom {
                    symbol: Cow::Borrowed("H"),
                    x: Decimal::from_str_exact("-0.180226841").unwrap(),
                    y: Decimal::from_str_exact("2.421289118").unwrap(),
                    z: Decimal::from_str_exact("1.572099030").unwrap(),
                },
                Atom {
                    symbol: Cow::Borrowed("H"),
                    x: Decimal::from_str_exact("-0.180226841").unwrap(),
                    y: Decimal::from_str_exact("-1.699398882").unwrap(),
                    z: Decimal::from_str_exact("1.572099030").unwrap(),
                },
                Atom {
                    symbol: Cow::Borrowed("H"),
                    x: Decimal::from_str_exact("-0.180226841").unwrap(),
                    y: Decimal::from_str_exact("-1.796059882").unwrap(),
                    z: Decimal::from_str_exact("-0.917077970").unwrap(),
                },
            ],
        }
    }

    const H2: &str = r#"2
H2
H 0.3710 0.0 0.0
H -0.3710 0.0 0.0"#;

    fn h2() -> Molecule<'static> {
        Molecule {
            comment: Cow::Borrowed("H2"),
            atoms: vec![
                Atom {
                    symbol: Cow::Borrowed("H"),
                    x: Decimal::from_str_exact("0.3710").unwrap(),
                    y: Decimal::from_str_exact("0.0").unwrap(),
                    z: Decimal::from_str_exact("0.0").unwrap(),
                },
                Atom {
                    symbol: Cow::Borrowed("H"),
                    x: Decimal::from_str_exact("-0.3710").unwrap(),
                    y: Decimal::from_str_exact("0.0").unwrap(),
                    z: Decimal::from_str_exact("0.0").unwrap(),
                },
            ],
        }
    }

    #[test]
    fn parse_h2() {
        assert_eq!(Molecule::parse(H2).unwrap(), h2())
    }

    #[test]
    fn parse_pyridine() {
        assert_eq!(Molecule::parse(PYRIDINE).unwrap(), pyridine())
    }

    #[test]
    fn parse_together() {
        let together = format!("{H2}\n{PYRIDINE}");
        assert_eq!(
            Xyz::parse(&together).unwrap(),
            Xyz {
                molecules: vec![h2(), pyridine()]
            }
        );
    }

    #[test]
    fn print_h2() {
        assert_eq!(h2().to_string(), H2);
    }
}
