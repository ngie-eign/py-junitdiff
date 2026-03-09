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
