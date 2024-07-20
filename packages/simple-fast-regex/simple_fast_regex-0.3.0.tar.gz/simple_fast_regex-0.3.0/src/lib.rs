use pyo3::prelude::*;
use rayon::prelude::*;
use regex::Regex;

/// This item will get inited with a list of patterns from the JSON file.
#[pyclass(name = "RegexEngine")]
pub struct RegexEngine {
    raw_patterns: Vec<String>,
    compiled_patterns: Vec<Regex>,
}

#[pymethods]
impl RegexEngine {
    /// Creates a new `RegexEngine` object.
    ///
    /// Parallization is done using the `rayon` crate.
    ///
    /// ### Arguments
    /// * `raw_patterns` - A list of raw Regex patterns to compile.
    #[new]
    fn new(raw_patterns: Vec<String>) -> Self {
        let compiled_patterns: Vec<Regex> = raw_patterns
            .par_iter()
            .filter_map(|pattern| Regex::new(pattern).ok())
            .collect();

        RegexEngine {
            raw_patterns,
            compiled_patterns,
        }
    }

    /// Returns the raw patterns that were compiled.
    ///
    /// ### Returns
    /// A list of raw patterns.
    #[getter]
    fn get_raw_patterns(&self) -> Vec<String> {
        self.raw_patterns.clone()
    }

    /// Runs the compiled patterns against the provided content.
    ///
    /// ### Arguments
    /// * `content` - The content to match against.
    ///     
    /// ### Returns
    /// A list of indexes of the patterns that matched the content.
    fn get_pattern_matches(&self, content: String) -> Vec<usize> {
        self.compiled_patterns
            .par_iter()
            .enumerate()
            .filter_map(|(index, regex)| {
                if regex.is_match(&content) {
                    return Some(index);
                }
                None
            })
            .collect()
    }
}

#[pymodule]
#[pyo3(name = "simple_fast_regex")]
fn simple_fast_regex(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<RegexEngine>()?;
    Ok(())
}
