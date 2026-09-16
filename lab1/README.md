
````markdown
# LAB-1: Mining and Profiling a Software Repository

## 1. Objective

The objective of this lab is to understand how a software repository can be used as a source of software engineering data.

In this lab, I analyze an open-source GitHub repository, collect repository and source-code metrics, mine its Git history, and store the results in CSV and JSON formats.

---

## 2. Problem Understanding

A software repository contains more than source code. It also contains information about project structure, file types, source-code size, contributors, commits, and development history.

The aim of this lab is to programmatically analyze these different aspects and convert the collected information into structured datasets that can be used for further software engineering analysis.

---

## 3. Selected Repository

**Repository:** `psf/requests`  
**GitHub:** https://github.com/psf/requests  
**Language:** Python

The Requests repository was selected because it is a real-world open-source Python project with source code, tests, documentation, configuration files, and a large Git history.

---

## 4. Project Structure

```text
CSET456Lab/
└── lab1/
    ├── src/
    │   ├── mine_repo.py
    │   ├── repository_inventory.py
    │   ├── generate_dataset.py
    │   ├── git_history.py
    │   └── generate_stats.py
    │
    ├── data/
    │   ├── file_dataset.csv
    │   └── commit_history.csv
    │
    ├── output/
    │   └── repository_stats.json
    │
    └── README.md
````

### File Description

* `mine_repo.py` – clones the selected GitHub repository.
* `repository_inventory.py` – analyzes files, directories, source files, LOC, and file types.
* `generate_dataset.py` – generates the file-level CSV dataset.
* `git_history.py` – mines Git commits, contributors, file changes, and development history.
* `generate_stats.py` – combines inventory and Git-history results into JSON.
* `file_dataset.csv` – stores file-level source-code metrics.
* `commit_history.csv` – stores monthly commit activity.
* `repository_stats.json` – stores combined repository statistics.
* `README.md` – contains the lab explanation, results, and observations.

The `psf/requests` repository used for analysis is cloned separately at:

```text
~/repository_mining/requests
```

---

## 5. Methodology

The analysis was performed in the following stages:

1. Clone the `psf/requests` repository.
2. Traverse the repository using Python.
3. Ignore the `.git` directory.
4. Identify Python source files.
5. Calculate LOC and file-level metrics.
6. Generate `file_dataset.csv`.
7. Mine Git history for commits and contributor information.
8. Generate `commit_history.csv`.
9. Combine the results into `repository_stats.json`.
10. Document the results and observations.

---

## 6. Repository Inventory Results

| Metric                  | Result |
| ----------------------- | -----: |
| Total files             |    128 |
| Total directories       |     25 |
| Source-code files       |     37 |
| Programming language    | Python |
| Total LOC               | 12,032 |
| Average LOC/source file | 325.19 |

### Largest Source Files

| File                       |   LOC |
| -------------------------- | ----: |
| `tests/test_requests.py`   | 3,094 |
| `src/requests/models.py`   | 1,184 |
| `src/requests/utils.py`    | 1,155 |
| `tests/test_utils.py`      | 1,013 |
| `src/requests/sessions.py` |   920 |

---

## 7. File-Level Dataset

The file-level dataset is stored in:

```text
data/file_dataset.csv
```

It contains:

```text
file_path,language,extension,loc,size_bytes
```

The dataset contains information for the 37 identified Python source files.

---

## 8. Git History Results

The Git history analysis produced:

| Metric                             |        Result |
| ---------------------------------- | ------------: |
| Total commits                      |         6,494 |
| Total contributors                 |           790 |
| Most active contributor            | Kenneth Reitz |
| Commits by most active contributor |         3,148 |
| Total additions                    |       161,373 |
| Total deletions                    |       132,208 |
| Average additions/commit           |         24.85 |
| Average deletions/commit           |         20.36 |

Frequently changed files included:

| File                   | Changes |
| ---------------------- | ------: |
| `requests/models.py`   |     717 |
| `test_requests.py`     |     366 |
| `requests/sessions.py` |     335 |
| `HISTORY.rst`          |     319 |
| `requests/utils.py`    |     271 |

Monthly commit information is stored in:

```text
data/commit_history.csv
```

---

## 9. JSON Output

The combined repository statistics are stored in:

```text
output/repository_stats.json
```

The JSON contains two main sections:

```text
repository_inventory
git_history
```

---

## 10. Observations

* The repository contains many different file types besides Python source files.
* 37 Python files contain 12,032 physical lines of code.
* Some test files are among the largest files in the repository.
* Git history provides information that cannot be obtained by looking only at the current source tree.
* Frequently changed files show areas of repeated development activity.
* CSV and JSON formats make the mined information easier to reuse for further analysis.

---

## 11. Challenges and Limitations

* `.git` had to be excluded from the normal repository inventory.
* Source-code identification is currently based on the `.py` extension.
* LOC represents physical lines and includes comments and blank lines.
* Git contributor information depends on the author names recorded in Git history.
* File-change frequency does not explain the reason or importance of a change.

---

## 12. Learning Outcomes

Through this lab, I learned how to:

* Programmatically access and traverse a GitHub repository.
* Calculate basic repository and source-code metrics.
* Generate file-level datasets using CSV.
* Execute Git commands from Python.
* Mine commits, contributors, and file changes from Git history.
* Store combined analysis results in JSON.
* Understand the difference between source-code analysis and repository mining.
* Maintain the development process using meaningful Git commits.

---

## 13. Conclusion

In this lab, I developed a Python-based repository-mining workflow for the `psf/requests` repository.

The analysis covered both the current repository structure and its Git development history. The collected information was converted into two CSV datasets and one JSON output, providing a structured view of the repository and its evolution.

```

This is the version I'd use — **detailed enough for your professor/viva, but not unnecessarily huge.**

One thing before the final commit: **check that the numbers in this README match your final JSON/CSV outputs**, especially the Git-history metrics.
```
