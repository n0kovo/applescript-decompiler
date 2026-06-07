.PHONY: test coverage-report clean

test:
	python -m pytest tests/ -v

coverage-report:
	@python -m pytest tests/test_opcodes.py::test_coverage_report -s -q 2>&1 | grep -E "(\.scpt|unhandled)"

clean:
	rm -rf tests/_build tests/__pycache__ .pytest_cache
