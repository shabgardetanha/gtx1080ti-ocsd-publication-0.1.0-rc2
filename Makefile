.PHONY: check compile test verify

check: compile test verify

compile:
	python3 -m py_compile src/gen9_t4_ocsd.py tests/test_publisher.py

test:
	python3 -m unittest discover -s tests -v

verify:
	python3 scripts/verify_candidate.py .
