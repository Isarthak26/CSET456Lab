
````markdown
# CSET456 Lab 1 — Mining and Profiling a Software Repository

## 1. Lab Information

| Item | Details |
|---|---|
| Course | CSET456 - Software Engineering |
| Lab | Lab 1 |
| Title | Mining and Profiling a Software Repository |
| Repository | `psf/requests` |
| Primary Language | Python |

---

## 2. Objective

The objective of this lab is to understand how a software repository can be used as a source of software engineering data.

The lab focuses on analyzing an open-source repository, extracting repository and source-code metrics, mining Git history, and storing the collected information in structured CSV and JSON formats.

The main objectives are:

- Analyze repository structure.
- Identify source-code files.
- Calculate lines of code and file-level metrics.
- Analyze file-type distribution.
- Generate a file-level dataset.
- Mine Git commit history.
- Analyze contributors and frequently changed files.
- Analyze monthly commit activity.
- Generate machine-readable JSON statistics.
- Understand the difference between source-code analysis and repository mining.

---

## 3. Problem Understanding

A software repository contains more than just source code. It also contains tests, documentation, configuration files, metadata, and information about the development process.

The current repository structure can provide information such as the number of files, directories, programming languages, lines of code, file sizes, and file types.

Git history provides another source of information. It can be used to identify commits, contributors, frequently changed files, additions, deletions, and development activity over time.

Manually collecting these metrics from a large repository would be inefficient. Therefore, Python scripts were developed to automate the repository-mining process.

---

## 4. Selected Repository

The repository selected for this lab is:

**Repository:** `psf/requests`

**GitHub:** https://github.com/psf/requests

**Primary Language:** Python

The Requests repository was selected because it is a real-world open-source Python project with source code, tests, documentation, configuration files, and a large Git history.

---

## 5. Approach

The analysis was performed in multiple stages:

1. Clone the selected GitHub repository.
2. Traverse the repository programmatically.
3. Ignore the `.git` directory.
4. Identify Python source files.
5. Calculate repository-level and file-level metrics.
6. Generate a file-level CSV dataset.
7. Analyze Git history.
8. Generate monthly commit-history data.
9. Generate combined JSON statistics.
10. Document the results and observations.

The overall workflow is:

```text
GitHub Repository
       ↓
Clone Repository
       ↓
Repository Traversal
       ↓
Repository Inventory
       ↓
File-Level Dataset
       ↓
Git History Mining
       ↓
CSV + JSON Outputs
       ↓
Analysis and Observations
````

---

## 6. Project Structure

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
```

### Source Files

| File                      | Purpose                                       |
| ------------------------- | --------------------------------------------- |
| `mine_repo.py`            | Clones the selected repository                |
| `repository_inventory.py` | Calculates repository and source-code metrics |
| `generate_dataset.py`     | Generates the file-level CSV dataset          |
| `git_history.py`          | Mines Git history and development information |
| `generate_stats.py`       | Generates combined JSON statistics            |

### Generated Files

| File                    | Purpose                                        |
| ----------------------- | ---------------------------------------------- |
| `file_dataset.csv`      | File-level source-code metrics                 |
| `commit_history.csv`    | Monthly commit activity                        |
| `repository_stats.json` | Combined repository and Git-history statistics |

The Requests repository used for analysis is cloned separately at:

```text
~/repository_mining/requests
```

---

## 7. Repository Inventory

Repository inventory was implemented using Python's `os.walk()` function.

The `.git` directory was excluded because it contains Git's internal metadata rather than normal project files.

The inventory collects:

* Total files.
* Total directories.
* Source-code files.
* Programming-language distribution.
* File-type distribution.
* Total lines of code.
* Average LOC per source file.
* Largest source files.

---

## 8. Source-Code Identification

For this lab, Python files were treated as source-code files.

The source-code mapping used by the program is:

```text
.py → Python
```

This approach was selected because Python is the primary language of the Requests repository.

The analysis identified **37 Python source files**.

---

## 9. Repository Inventory Results

| Metric                  | Result |
| ----------------------- | -----: |
| Total files             |    128 |
| Total directories       |     25 |
| Python source files     |     37 |
| Total LOC               | 12,032 |
| Average LOC/source file | 325.19 |

The total LOC represents physical lines in the identified Python files.

The calculation includes code, comments, blank lines, and documentation strings.

---

## 10. Largest Source Files

The five largest Python source files were:

| File                       |   LOC |
| -------------------------- | ----: |
| `tests/test_requests.py`   | 3,094 |
| `src/requests/models.py`   | 1,184 |
| `src/requests/utils.py`    | 1,155 |
| `tests/test_utils.py`      | 1,013 |
| `src/requests/sessions.py` |   920 |

The files were sorted according to their physical line count.

---

## 11. File-Type Distribution

The repository contains several types of files besides Python source code.

Examples include:

```text
.py
.md
.rst
.yml
.yaml
.txt
.toml
.ini
.html
.css
.svg
.png
.pem
.crt
.csr
.cnf
```

This shows that a software repository contains many different artifacts required for development, testing, documentation, configuration, and supporting functionality.

---

## 12. File-Level Dataset

The file-level dataset is generated using:

```text
src/generate_dataset.py
```

The generated dataset is stored at:

```text
data/file_dataset.csv
```

The CSV contains the following fields:

```text
file_path
language
extension
loc
size_bytes
```

### Column Description

| Column       | Description                      |
| ------------ | -------------------------------- |
| `file_path`  | Relative path of the source file |
| `language`   | Programming language             |
| `extension`  | File extension                   |
| `loc`        | Physical number of lines         |
| `size_bytes` | File size in bytes               |

The dataset contains records for the 37 identified Python source files.

---

## 13. Git History Mining

Git history was analyzed using:

```text
src/git_history.py
```

The program executes Git commands through Python's `subprocess` module.

The analysis collects:

* Total commits.
* Total contributors.
* Most active contributor.
* Frequently changed files.
* Monthly commit activity.
* Total additions.
* Total deletions.
* Average additions per commit.
* Average deletions per commit.

---

## 14. Git History Results

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

---

## 15. Frequently Changed Files

The five frequently changed files identified from Git history were:

| File                   | Number of Changes |
| ---------------------- | ----------------: |
| `requests/models.py`   |               717 |
| `test_requests.py`     |               366 |
| `requests/sessions.py` |               335 |
| `HISTORY.rst`          |               319 |
| `requests/utils.py`    |               271 |

These values show how frequently the paths appeared in historical file-change records.

They do not indicate the importance or reason behind each change.

---

## 16. Monthly Commit History

Git commit dates were grouped by month.

The resulting dataset is stored in:

```text
data/commit_history.csv
```

The dataset contains:

```text
month
commit_count
```

Each row represents a month and the number of commits recorded during that month.

This dataset can be used for further analysis or visualization of repository activity over time.

---

## 17. JSON Output

The final combined statistics are generated using:

```text
src/generate_stats.py
```

The output is stored at:

```text
output/repository_stats.json
```

The JSON contains two major sections:

```text
repository_inventory
git_history
```

This provides a machine-readable representation of both the current repository structure and its development history.

---

## 18. Observations

The analysis produced several useful observations:

* The repository contains many different file types in addition to source code.
* 37 Python files contain 12,032 physical lines.
* Some of the largest files are test files.
* Git history provides information that cannot be obtained from the current file structure alone.
* Frequently changed files can be identified through Git history.
* Monthly commit data provides information about development activity over time.
* CSV and JSON formats make the collected information suitable for further analysis.

---

## 19. Source-Code Analysis vs Repository Mining

Source-code analysis focuses on the current contents and structure of source files.

Examples include:

```text
LOC
File size
Programming language
File extension
```

Repository mining provides a broader view by also analyzing development history.

Examples include:

```text
Commits
Contributors
File changes
Additions
Deletions
Monthly activity
```

Therefore, repository mining combines information about the software itself with information about how the software has been developed.

---

## 20. Challenges

Several challenges were encountered during implementation.

### Repository Traversal

The repository contains many different file types, so the program needed to distinguish source files from other repository artifacts.

### Git Metadata

The `.git` directory needed to be excluded from normal repository inventory calculations.

### File Reading

Some repository files are not plain text files. Therefore, the source-code analysis was restricted to recognized Python files.

### Large Git History

The Requests repository contains thousands of commits, making automated Git commands more suitable than manual inspection.

---

## 21. Limitations

The current implementation has some limitations:

* Source-code identification is based on the `.py` extension.
* LOC represents physical lines rather than logical statements.
* Comments and blank lines are included in the LOC count.
* Contributor counts depend on author names recorded in Git.
* File-change frequency does not explain the reason or importance of a change.
* The analysis represents the repository state available when the scripts were executed.

---

## 22. Testing

Each major stage was executed and tested before proceeding to the next stage.

The repository inventory was tested to verify:

* File count.
* Directory count.
* Source-file count.
* LOC.
* Average LOC.
* Largest source files.
* File-type distribution.

The file-level CSV was generated and checked for the expected columns.

Git history was executed to verify commit and contributor information.

The monthly commit CSV was generated successfully.

Finally, the repository inventory and Git-history results were combined into the JSON output.

---

## 23. Git Development Process

The lab was developed incrementally.

The general development process was:

```text
Initial Structure
      ↓
Repository Inventory
      ↓
File-Level Dataset
      ↓
Git History Mining
      ↓
Commit History Dataset
      ↓
JSON Statistics
      ↓
Documentation
```

Meaningful Git commits were used after completing major stages.

Examples of the commit-message format include:

```text
docs(lab1): add initial lab structure and understanding
feat(lab1): add repository inventory
feat(lab1): generate file-level dataset
feat(lab1): add git history mining
docs(lab1): finalize lab documentation
```

This keeps the development history organized and understandable.

---

## 24. Learning Outcomes

Through this lab, I learned how to:

* Analyze an open-source software repository.
* Traverse directories programmatically using Python.
* Identify source-code files.
* Calculate repository-level metrics.
* Calculate file-level metrics.
* Generate CSV datasets.
* Execute Git commands from Python.
* Extract commit and contributor information.
* Analyze file-change activity.
* Group commits by month.
* Calculate additions and deletions.
* Generate structured JSON output.
* Understand repository mining concepts.
* Maintain a meaningful Git development history.

---

## 25. Final Output

The completed Lab 1 contains:

```text
lab1/
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
```

---

## 26. Conclusion

This lab demonstrated how an open-source software repository can be treated as a source of software engineering data.

The `psf/requests` repository was analyzed from both structural and historical perspectives.

The structural analysis provided information about files, directories, source-code size, file types, and large source files.

The Git-history analysis provided information about commits, contributors, frequently changed files, monthly activity, additions, and deletions.

The collected information was stored in CSV and JSON formats.

Overall, the lab provided practical experience with repository traversal, software metrics, Git history mining, structured dataset generation, and reproducible software engineering analysis.

```
```
