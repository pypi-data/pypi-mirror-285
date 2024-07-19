use crate::atom::{Atom, AtomParseError};
use rust_decimal::Decimal;
use std::{borrow::Cow, error::Error, fmt, str::FromStr};

/// An error that can occur when parsing a [`Molecule`]
#[derive(Debug, Clone)]
pub enum MoleculeParseError<'a> {
    NoAtomNumber,
    InvalidAtomNumber(Cow<'a, str>, std::num::ParseIntError),
    NoComment,
    InvalidAtom(Cow<'a, str>, AtomParseError<'a>),
    InvalidNumberOfAtoms(usize, usize),
}

impl<'a> MoleculeParseError<'a> {
    pub fn into_owned(self) -> MoleculeParseError<'static> {
        match self {
            Self::NoAtomNumber => MoleculeParseError::NoAtomNumber,
            Self::InvalidAtomNumber(input, err) => {
                MoleculeParseError::InvalidAtomNumber(Cow::Owned(input.into_owned()), err)
            }
            Self::NoComment => MoleculeParseError::NoComment,
            Self::InvalidAtom(input, err) => {
                MoleculeParseError::InvalidAtom(Cow::Owned(input.into_owned()), err.into_owned())
            }
            Self::InvalidNumberOfAtoms(found, expected) => {
                MoleculeParseError::InvalidNumberOfAtoms(found, expected)
            }
        }
    }
}

impl<'a> fmt::Display for MoleculeParseError<'a> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::NoAtomNumber => write!(f, "No atom number found"),
            Self::InvalidAtomNumber(input, err) => {
                write!(f, "Invalid atom number '{input}': {err}")
            }
            Self::NoComment => write!(f, "No comment found"),
            Self::InvalidAtom(input, err) => write!(f, "Invalid atom '{input}': {err}"),
            Self::InvalidNumberOfAtoms(found, expected) => {
                write!(
                    f,
                    "Invalid number of coordinates. Found {found}, expected {expected}"
                )
            }
        }
    }
}

impl Error for MoleculeParseError<'static> {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        match self {
            Self::InvalidAtomNumber(_, err) => Some(err),
            Self::InvalidAtom(_, err) => Some(err),
            _ => None,
        }
    }
}

/// A molecule
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct Molecule<'a> {
    pub comment: Cow<'a, str>,
    pub atoms: Vec<Atom<'a>>,
}

impl<'a> Molecule<'a> {
    pub fn parse(string: &'a str) -> Result<Self, MoleculeParseError> {
        let mut lines = string.lines();
        let molecule = Self::parse_lines(&mut lines)?;
        let remaining = lines.count();
        if remaining > 0 {
            return Err(MoleculeParseError::InvalidNumberOfAtoms(
                molecule.atoms.len() + remaining,
                molecule.atoms.len(),
            ));
        }
        Ok(molecule)
    }

    pub(crate) fn parse_lines(
        lines: &mut impl Iterator<Item = &'a str>,
    ) -> Result<Self, MoleculeParseError<'a>> {
        let atom_number: usize = if let Some(atom_number) = lines.next() {
            atom_number
                .parse()
                .map_err(|e| MoleculeParseError::InvalidAtomNumber(Cow::Borrowed(atom_number), e))?
        } else {
            return Err(MoleculeParseError::NoAtomNumber);
        };
        let comment = lines
            .next()
            .map(Cow::Borrowed)
            .ok_or(MoleculeParseError::NoComment)?;
        let mut atoms = Vec::with_capacity(atom_number);
        for line in lines.take(atom_number) {
            atoms.push(
                Atom::parse(line)
                    .map_err(|err| MoleculeParseError::InvalidAtom(Cow::Borrowed(line), err))?,
            );
        }
        if atoms.len() < atom_number {
            return Err(MoleculeParseError::InvalidNumberOfAtoms(
                atoms.len(),
                atom_number,
            ));
        }
        Ok(Molecule { comment, atoms })
    }

    pub fn into_owned(self) -> Molecule<'static> {
        Molecule {
            comment: Cow::Owned(self.comment.into_owned()),
            atoms: self
                .atoms
                .into_iter()
                .map(|atom| atom.into_owned())
                .collect(),
        }
    }

    pub fn symbols(&self) -> impl ExactSizeIterator<Item = &str> {
        self.atoms.iter().map(|atom| atom.symbol.as_ref())
    }

    pub fn coordinates(&self) -> impl ExactSizeIterator<Item = [Decimal; 3]> + '_ {
        self.atoms.iter().map(|atom| atom.coordinates())
    }
}

impl<'a> fmt::Display for Molecule<'a> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        writeln!(f, "{}", self.atoms.len())?;
        write!(f, "{}", self.comment)?;
        for atom in &self.atoms {
            write!(f, "\n{atom}")?;
        }
        Ok(())
    }
}

impl FromStr for Molecule<'static> {
    type Err = MoleculeParseError<'static>;
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        Molecule::parse(s)
            .map(|res| res.into_owned())
            .map_err(|err| err.into_owned())
    }
}
