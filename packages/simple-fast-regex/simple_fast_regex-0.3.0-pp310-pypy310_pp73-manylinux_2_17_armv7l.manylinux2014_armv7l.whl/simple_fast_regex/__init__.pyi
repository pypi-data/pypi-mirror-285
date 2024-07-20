from typing import List

class RegexEngine:
    raw_patterns: List[str]
    compiled_patterns: List

    def __init__(self, raw_patterns: List[str]) -> None:
        """
        Creates a new RegexEngine object.
        
        Arguments:
        raw_patterns -- A list of raw Regex patterns to compile.
        """
        ...

    def get_raw_patterns(self) -> List[str]:
        """
        Returns the raw patterns that were compiled.
        
        Returns:
        A list of raw patterns.
        """
        ...

    def get_pattern_matches(self, content: str) -> List[int]:
        """
        Runs the compiled patterns against the provided content.
        
        Arguments:
        content -- The content to match against.
        
        Returns:
        A list of indexes of the patterns that matched the content.
        """
        ...
