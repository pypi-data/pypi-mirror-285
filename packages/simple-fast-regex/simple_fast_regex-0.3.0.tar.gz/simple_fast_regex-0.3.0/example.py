import simple_fast_regex as sfr

engine = sfr.RegexEngine(["test", "this pattern doesn't exist"])
text = "This is a test"

print(engine.get_pattern_matches(text))  # [0], meaning the first pattern was found