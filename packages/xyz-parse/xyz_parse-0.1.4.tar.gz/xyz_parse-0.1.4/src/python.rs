use crate::{atom::Atom, molecule::Molecule, xyz::Xyz};
use pyo3::{
    create_exception,
    exceptions::PyException,
    prelude::*,
    types::{PyList, PyString, PyTuple, PyType},
};
use std::borrow::Cow;

create_exception!(xyz_parse, ParseError, PyException);

#[pymodule]
fn xyz_parse(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("ParseError", m.py().get_type_bound::<ParseError>())?;
    m.add_class::<PyAtom>()?;
    m.add_class::<PyMolecule>()?;
    m.add_class::<PyXyz>()?;
    m.add_function(wrap_pyfunction!(parse_xyz, m)?)?;
    Ok(())
}

#[pyclass(name = "Atom", module = "xyz_parse")]
#[derive(Debug, Clone)]
pub struct PyAtom {
    #[pyo3(get, set)]
    pub symbol: Py<PyString>,
    #[pyo3(get, set)]
    pub x: Py<PyAny>,
    #[pyo3(get, set)]
    pub y: Py<PyAny>,
    #[pyo3(get, set)]
    pub z: Py<PyAny>,
}

impl<'a> Atom<'a> {
    pub fn to_py(&self, py: Python<'a>) -> PyAtom {
        PyAtom {
            symbol: PyString::new_bound(py, &self.symbol).unbind(),
            x: self.x.to_object(py),
            y: self.y.to_object(py),
            z: self.z.to_object(py),
        }
    }
}

impl PyAtom {
    pub fn to_rust(&self, py: Python<'_>) -> PyResult<Atom<'static>> {
        Ok(Atom {
            symbol: Cow::Owned(self.symbol.extract(py)?),
            x: self.x.extract(py)?,
            y: self.y.extract(py)?,
            z: self.z.extract(py)?,
        })
    }
}

#[pymethods]
impl PyAtom {
    #[new]
    fn new(symbol: Py<PyString>, x: Py<PyAny>, y: Py<PyAny>, z: Py<PyAny>) -> Self {
        PyAtom { symbol, x, y, z }
    }

    #[classmethod]
    fn parse(_: &Bound<'_, PyType>, py: Python<'_>, input: &str) -> PyResult<PyAtom> {
        Atom::parse(input)
            .map(|atom| atom.to_py(py))
            .map_err(|err| ParseError::new_err(err.to_string()))
    }

    #[getter]
    fn coordinates<'py>(&self, py: Python<'py>) -> Bound<'py, PyTuple> {
        PyTuple::new_bound(
            py,
            [
                self.x.clone_ref(py),
                self.y.clone_ref(py),
                self.z.clone_ref(py),
            ],
        )
    }

    fn __str__(&self, py: Python<'_>) -> PyResult<String> {
        Ok(self.to_rust(py)?.to_string())
    }

    fn __repr__(&self, py: Python<'_>) -> PyResult<String> {
        Ok(format!("{:?}", self.to_rust(py)?))
    }
}

#[pyclass(name = "Molecule", module = "xyz_parse")]
#[derive(Debug, Clone)]
pub struct PyMolecule {
    #[pyo3(get, set)]
    pub comment: Py<PyString>,
    #[pyo3(get, set)]
    pub atoms: Py<PyList>,
}

impl<'a> Molecule<'a> {
    pub fn to_py(&self, py: Python<'a>) -> PyMolecule {
        PyMolecule {
            comment: PyString::new_bound(py, &self.comment).unbind(),
            atoms: PyList::new_bound(py, self.atoms.iter().map(|atom| atom.to_py(py).into_py(py)))
                .unbind(),
        }
    }
}

impl PyMolecule {
    pub fn to_rust(&self, py: Python<'_>) -> PyResult<Molecule<'static>> {
        Ok(Molecule {
            comment: Cow::Owned(self.comment.extract(py)?),
            atoms: self
                .atoms
                .bind(py)
                .iter()
                .map(|atom| atom.extract::<PyAtom>()?.to_rust(py))
                .collect::<PyResult<_>>()?,
        })
    }

    pub fn py_atoms(&self, py: Python<'_>) -> PyResult<Vec<PyAtom>> {
        self.atoms
            .bind(py)
            .iter()
            .map(|atom| atom.extract::<PyAtom>())
            .collect()
    }
}

#[pymethods]
impl PyMolecule {
    #[new]
    fn new(comment: Py<PyString>, atoms: Py<PyList>) -> Self {
        PyMolecule { comment, atoms }
    }

    #[classmethod]
    fn parse(_: &Bound<'_, PyType>, py: Python<'_>, input: &str) -> PyResult<PyMolecule> {
        Molecule::parse(input)
            .map(|molecule| molecule.to_py(py))
            .map_err(|err| ParseError::new_err(err.to_string()))
    }

    #[getter]
    fn symbols<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyList>> {
        Ok(PyList::new_bound(
            py,
            self.py_atoms(py)?.iter().map(|atom| atom.symbol.bind(py)),
        ))
    }

    #[getter]
    fn coordinates<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyList>> {
        Ok(PyList::new_bound(
            py,
            self.py_atoms(py)?.iter().map(|atom| atom.coordinates(py)),
        ))
    }

    fn __str__(&self, py: Python<'_>) -> PyResult<String> {
        Ok(self.to_rust(py)?.to_string())
    }

    fn __repr__(&self, py: Python<'_>) -> PyResult<String> {
        Ok(format!("{:?}", self.to_rust(py)?))
    }
}

#[pyclass(name = "Xyz", module = "xyz_parse")]
#[derive(Debug, Clone)]
pub struct PyXyz {
    #[pyo3(get, set)]
    pub molecules: Py<PyList>,
}

impl<'a> Xyz<'a> {
    pub fn to_py(&self, py: Python<'a>) -> PyXyz {
        PyXyz {
            molecules: PyList::new_bound(
                py,
                self.molecules
                    .iter()
                    .map(|molecule| molecule.to_py(py).into_py(py)),
            )
            .unbind(),
        }
    }
}

impl PyXyz {
    pub fn to_rust(&self, py: Python<'_>) -> PyResult<Xyz<'static>> {
        Ok(Xyz {
            molecules: self
                .molecules
                .bind(py)
                .iter()
                .map(|molecule| molecule.extract::<PyMolecule>()?.to_rust(py))
                .collect::<PyResult<_>>()?,
        })
    }
}

#[pymethods]
impl PyXyz {
    #[new]
    fn new(molecules: Py<PyList>) -> Self {
        PyXyz { molecules }
    }

    #[classmethod]
    fn parse(_: &Bound<'_, PyType>, py: Python<'_>, input: &str) -> PyResult<PyXyz> {
        Xyz::parse(input)
            .map(|xyz| xyz.to_py(py))
            .map_err(|err| ParseError::new_err(err.to_string()))
    }

    fn __str__(&self, py: Python<'_>) -> PyResult<String> {
        Ok(self.to_rust(py)?.to_string())
    }

    fn __repr__(&self, py: Python<'_>) -> PyResult<String> {
        Ok(format!("{:?}", self.to_rust(py)?))
    }
}

#[pyfunction]
fn parse_xyz(py: Python<'_>, input: &str) -> PyResult<PyXyz> {
    Xyz::parse(input)
        .map(|xyz| xyz.to_py(py))
        .map_err(|err| ParseError::new_err(err.to_string()))
}
