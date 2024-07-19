use rust_decimal::Decimal;
use std::{borrow::Cow, error::Error, fmt, str::FromStr};

/// An error that can occur when parsing an [`Atom`]
#[derive(Debug, Clone)]
pub enum AtomParseError<'a> {
    InvalidCoordinate(Cow<'a, str>, rust_decimal::Error),
    NoSymbol,
    InvalidNumberOfCoordinates(usize),
}

impl<'a> AtomParseError<'a> {
    pub fn into_owned(self) -> AtomParseError<'static> {
        match self {
            Self::InvalidCoordinate(input, err) => {
                AtomParseError::InvalidCoordinate(Cow::Owned(input.into_owned()), err)
            }
            Self::NoSymbol => AtomParseError::NoSymbol,
            Self::InvalidNumberOfCoordinates(num) => {
                AtomParseError::InvalidNumberOfCoordinates(num)
            }
        }
    }
}

impl<'a> fmt::Display for AtomParseError<'a> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::InvalidCoordinate(input, err) => write!(f, "Invalid coordinate '{input}': {err}"),
            Self::NoSymbol => write!(f, "No symbol found"),
            Self::InvalidNumberOfCoordinates(num) => {
                write!(f, "Invalid number of coordinates. Found {num}, expected 3")
            }
        }
    }
}

impl Error for AtomParseError<'static> {}

/// An atom in a molecule
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct Atom<'a> {
    pub symbol: Cow<'a, str>,
    pub x: Decimal,
    pub y: Decimal,
    pub z: Decimal,
}

impl<'a> Atom<'a> {
    pub fn parse(string: &'a str) -> Result<Self, AtomParseError> {
        let mut parts = string.split_whitespace();
        let symbol = parts
            .next()
            .map(Cow::Borrowed)
            .ok_or(AtomParseError::NoSymbol)?;
        let mut coordinates: [Decimal; 3] = Default::default();
        coordinates
            .iter_mut()
            .enumerate()
            .try_for_each(|(i, coord)| {
                let part = parts
                    .next()
                    .ok_or(AtomParseError::InvalidNumberOfCoordinates(i))?;
                *coord = Decimal::from_str_exact(part)
                    .map_err(|e| AtomParseError::InvalidCoordinate(Cow::Borrowed(part), e))?;
                Ok(())
            })?;
        let remaining = parts.count();
        if remaining > 0 {
            return Err(AtomParseError::InvalidNumberOfCoordinates(3 + remaining));
        }
        Ok(Self {
            symbol,
            x: coordinates[0],
            y: coordinates[1],
            z: coordinates[2],
        })
    }

    pub fn into_owned(self) -> Atom<'static> {
        Atom {
            symbol: Cow::Owned(self.symbol.into_owned()),
            ..self
        }
    }

    pub fn coordinates(&self) -> [Decimal; 3] {
        [self.x, self.y, self.z]
    }
}

impl<'a> fmt::Display for Atom<'a> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{} {} {} {}", self.symbol, self.x, self.y, self.z)
    }
}

impl FromStr for Atom<'static> {
    type Err = AtomParseError<'static>;
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        Atom::parse(s)
            .map(|res| res.into_owned())
            .map_err(|err| err.into_owned())
    }
}
