# py-junitdiff

Simple JUnit XML test case report summary tool.

## Installation

### pipenv

```bash
% pipenv install .
```

### pipx

```bash
% pipx install .
```

## Usage

### Compare `file1.xml` and `file2.xml` at a testcase level

```bash
% junitdiff file1.xml file2.xml
```

### Compare `file1.xml` and `file2.xml` at a testsuite level

**Important**: please note that testsuite results might not be expressed by all
tools, e.g., `kyua report-junit`.

```bash
% junitdiff --diff-level=testsuite file1.xml file2.xml
```

### Compare Output from Two Runs of `kyua test -k /usr/tests/bin/sh/Kyuafile`

```bash
% kyua test -r results1.db -k /usr/tests/bin/sh/Kyuafile
% kyua test -r results2.db -k /usr/tests/bin/sh/Kyuafile
% kyua report-junit -r results1.db -o results1.xml
% kyua report-junit -r results2.db -o results2.xml
% junitdiff --diff-level=testcase results1.xml results2.xml
```
