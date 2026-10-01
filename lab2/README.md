# Lab 2 – Repository Mining, Data Cleaning and Dataset Preparation

## 1. Introduction

Lab 2 focuses on extracting, cleaning, and integrating data from multiple open-source repositories. The lab demonstrates practical software engineering data mining techniques by extracting source code metrics and commit history information from real-world repositories, then combining this data into a unified dataset for further analysis. The objective is to understand how repository mining can be automated and how raw data can be cleaned and integrated to create meaningful datasets for software engineering research and analysis.

---

## 2. Objectives

The lab successfully completed the following objectives:

1. Mine source code data from five open-source repositories
2. Mine commit history data from five open-source repositories
3. Extract and identify relevant source code attributes (file path, language, lines of code, file size)
4. Extract and identify relevant commit attributes (commit hash, author, date, message, files changed, insertions, deletions)
5. Clean raw source code data by removing duplicates, handling invalid entries, and validating numeric fields
6. Clean raw commit history data by removing duplicates, validating commit hashes, and validating date formats and numeric fields
7. Create a commit summary aggregating statistics by repository
8. Integrate source code and commit history data into a combined dataset
9. Generate output datasets in CSV format suitable for further analysis

---

## 3. Repositories

The following five repositories were mined and analyzed:

1. **Flask** (`pallets/flask`)
   - Web framework for Python
   - Source files mined: 83 files
   - Commits analyzed: 5,598 commits

2. **Requests** (`psf/requests`)
   - HTTP library for Python
   - Source files mined: 37 files
   - Commits analyzed: 6,734 commits

3. **Pytest** (`pytest-dev/pytest`)
   - Testing framework for Python
   - Source files mined: 274 files
   - Commits analyzed: 19,050 commits

4. **FastAPI** (`fastapi/fastapi`)
   - Modern web framework for building APIs with Python
   - Source files mined: 1,142 files
   - Commits analyzed: 7,811 commits

5. **Scikit-learn** (`scikit-learn/scikit-learn`)
   - Machine learning library for Python
   - Source files mined: 1,058 files
   - Commits analyzed: 38,733 commits

---

## 4. Project Structure

```
lab2/
├── README.md
├── data/
│   ├── source_code_raw.csv           (raw source code data - 2,594 rows)
│   ├── source_code_clean.csv         (cleaned source code data - 2,594 rows)
│   ├── commit_history_raw.csv        (raw commit history - 77,927 rows)
│   ├── commit_history_clean.csv      (cleaned commit history - 77,927 rows)
│   ├── commit_summary.csv            (aggregated commit statistics - 5 rows)
│   └── combined_repository_dataset.csv (integrated dataset - 5 rows)
└── src/
    ├── repositories.py               (repository URLs configuration)
    ├── mine_source_code.py           (extracts source code data)
    ├── mine_commit_history.py        (extracts commit history data)
    ├── clean_source_code.py          (cleans source code dataset)
    ├── clean_commit_history.py       (cleans commit history dataset)
    ├── create_commit_summary.py      (aggregates commit statistics)
    ├── create_combined_dataset.py    (integrates datasets)
    ├── analyze_repository_size.py    (displays repository statistics)
    └── __pycache__/                  (compiled Python cache)
```

---

## 5. Data Mining

### Source Code Dataset

**Purpose:**
The source code dataset captures file-level metrics from each repository, allowing analysis of code structure, language distribution, and code volume.

**Extraction Process:**
- Traverses the repository file system (excluding `.git` directory)
- Identifies source code files by extension (`.py`, `.js`, `.jsx`, `.java`, `.cpp`, `.c`, `.h`, `.hpp`)
- Maps file extensions to programming languages
- Counts lines of code (LOC) for each file by reading the file and counting non-empty lines
- Records file size in bytes

**Attributes Extracted:**
- `repository`: Name of the repository
- `file_path`: Relative path to the source file within the repository
- `language`: Programming language (e.g., Python, JavaScript, Java, C++, C, C/C++)
- `extension`: File extension (e.g., `.py`, `.js`)
- `loc`: Lines of code (count of non-empty lines)
- `size_bytes`: File size in bytes

**Output Files:**
- `source_code_raw.csv` (2,594 rows): Contains all extracted source code records
- `source_code_clean.csv` (2,594 rows): Cleaned and validated source code records

### Commit History Dataset

**Purpose:**
The commit history dataset captures development activity at the commit level, enabling analysis of code changes, contributor activity, and development trends.

**Extraction Process:**
- Uses Git command (`git log --all --date=iso --pretty=format:%H|%an|%ad|%s --numstat`) to extract commit information
- Parses the output to identify individual commits and associated file changes
- Aggregates additions and deletions at the commit level
- Counts the number of files changed per commit

**Attributes Extracted:**
- `repository`: Name of the repository
- `commit_hash`: Unique Git commit SHA-1 hash
- `author`: Name of the commit author
- `date`: Commit date in ISO format (YYYY-MM-DD HH:MM:SS ±HHMM)
- `message`: Commit message/description
- `files_changed`: Number of files changed in the commit
- `insertions`: Total lines added in the commit
- `deletions`: Total lines deleted in the commit

**Output Files:**
- `commit_history_raw.csv` (77,927 rows): Contains all extracted commit records
- `commit_history_clean.csv` (77,927 rows): Cleaned and validated commit records

---

## 6. Data Cleaning

### Source Code Data Cleaning

**Cleaning Process:**
- **Remove empty file paths:** Records with empty or whitespace-only file paths are excluded
- **Validate numeric fields:** Lines of code and file size are validated as integers; records with non-integer values are excluded
- **Remove duplicates:** Records with identical (repository, file_path) pairs are treated as duplicates and only the first occurrence is retained

**Original vs. Cleaned:**
- Records before cleaning: 2,594
- Records after cleaning: 2,594
- Records removed: 0

**Retained Attributes:**
All attributes from the raw dataset are retained because they are all relevant:
- Repository and file path identify the source file location
- Language and extension classify the file type
- LOC and size provide code volume metrics

### Commit History Data Cleaning

**Cleaning Process:**
- **Remove empty repository or commit hash:** Records with empty or whitespace-only repository names or commit hashes are excluded
- **Validate date format:** Commit dates must conform to the ISO 8601 format (YYYY-MM-DD HH:MM:SS ±HHMM); records with invalid dates are excluded
- **Validate numeric fields:** Files changed, insertions, and deletions are validated as integers; records with non-integer values are excluded
- **Remove duplicate commits:** Commits with identical (repository, commit_hash) pairs are treated as duplicates and only the first occurrence is retained (commit hashes are unique within a repository)

**Original vs. Cleaned:**
- Records before cleaning: 77,927
- Records after cleaning: 77,927
- Records removed: 0

**Retained Attributes:**
All attributes from the raw dataset are retained:
- Repository, commit hash, author, and date identify the commit
- Message provides context about the changes
- Files changed, insertions, and deletions quantify the extent of changes

---

## 7. Dataset Integration

### Commit Summary Dataset

**Purpose:** Aggregates commit-level statistics at the repository level.

**Process:**
- Iterates through the cleaned commit history dataset
- Groups commits by repository
- Aggregates total commits, files changed, insertions, and deletions for each repository
- Calculates averages: average files changed per commit, average insertions per commit, average deletions per commit

**Output:** `commit_summary.csv` (5 rows, one per repository)

**Attributes:**
- `repository`: Repository name
- `total_commits`: Total number of commits
- `total_files_changed`: Total files changed across all commits
- `total_insertions`: Total lines added across all commits
- `total_deletions`: Total lines deleted across all commits
- `avg_files_changed_per_commit`: Average files changed per commit
- `avg_insertions_per_commit`: Average insertions per commit
- `avg_deletions_per_commit`: Average deletions per commit

### Combined Repository Dataset

**Purpose:** Integrates source code and commit history statistics into a unified dataset for comparative analysis.

**Integration Process:**
1. Aggregates source code statistics by repository:
   - Total source files
   - Total lines of code
   - Total size in bytes
   - Average LOC per file

2. Retrieves corresponding commit statistics from the commit summary dataset

3. Combines both datasets into a single row per repository

**Output:** `combined_repository_dataset.csv` (5 rows, one per repository)

**Attributes:**
- `repository`: Repository name
- `total_source_files`: Total number of source code files
- `total_loc`: Total lines of code across all source files
- `total_size_bytes`: Total size of all source files in bytes
- `avg_loc_per_file`: Average lines of code per source file
- `total_commits`: Total number of commits
- `total_files_changed`: Total files changed across all commits
- `total_insertions`: Total lines added across all commits
- `total_deletions`: Total lines deleted across all commits
- `avg_files_changed_per_commit`: Average files changed per commit
- `avg_insertions_per_commit`: Average insertions per commit
- `avg_deletions_per_commit`: Average deletions per commit

---

## 8. Dataset Statistics

### Source Code Statistics

| Metric | Value |
|--------|-------|
| Total source code records | 2,594 |
| Records from all 5 repositories combined | Yes |
| Languages identified | Python, JavaScript, Java, C++, C, C/C++ |
| Total LOC across all repositories | 604,234 |
| Total file size across all repositories | 25,114,162 bytes (~25.1 MB) |

**Breakdown by Repository:**

| Repository | Total Files | Total LOC | Avg LOC/File |
|------------|-------------|-----------|-------------|
| Flask | 83 | 14,085 | 169.7 |
| Requests | 37 | 9,841 | 265.97 |
| Pytest | 274 | 98,325 | 358.85 |
| FastAPI | 1,142 | 97,754 | 85.6 |
| Scikit-learn | 1,058 | 384,229 | 363.17 |

### Commit History Statistics

| Metric | Value |
|--------|-------|
| Total commit records | 77,927 |
| Total commits across all repositories | 77,927 |
| Date range | From earliest to latest commit in each repository |

**Breakdown by Repository:**

| Repository | Total Commits | Files Changed | Insertions | Deletions | Avg Files/Commit | Avg Insertions/Commit | Avg Deletions/Commit |
|------------|--------------|---------------|-----------|-----------|-----------------|----------------------|----------------------|
| Flask | 5,598 | 9,364 | 119,425 | 81,641 | 1.67 | 21.33 | 14.58 |
| Requests | 6,734 | 8,413 | 166,659 | 136,771 | 1.25 | 24.75 | 20.31 |
| Pytest | 19,050 | 47,698 | 679,187 | 488,471 | 2.5 | 35.65 | 25.64 |
| FastAPI | 7,811 | 32,505 | 832,341 | 433,709 | 4.16 | 106.56 | 55.53 |
| Scikit-learn | 38,733 | 103,384 | 4,020,694 | 3,395,463 | 2.67 | 103.81 | 87.66 |

---

## 9. Implementation

### Script Descriptions

#### `repositories.py`
- **Purpose:** Defines the URLs of the five repositories to be mined
- **Input:** None (configuration file)
- **Output:** Python list of repository URLs
- **Key Variable:** `REPOSITORIES` - list of GitHub repository URLs

#### `mine_source_code.py`
- **Purpose:** Extracts source code metrics from repositories
- **Input:** 
  - Repository URLs from `repositories.py`
  - Cloned repository directories in `lab2_repositories/`
- **Output:** `lab2/data/source_code_raw.csv`
- **Process:**
  - Traverses repository file system
  - Identifies source code files by extension
  - Counts lines of code for each file
  - Records file path, language, extension, LOC, and file size

#### `mine_commit_history.py`
- **Purpose:** Extracts commit history from Git repositories
- **Input:**
  - Repository URLs from `repositories.py`
  - Cloned repository directories in `lab2_repositories/`
- **Output:** `lab2/data/commit_history_raw.csv`
- **Process:**
  - Runs `git log` command on each repository
  - Parses commit metadata and file changes
  - Aggregates insertions and deletions per commit
  - Records commit hash, author, date, message, and change statistics

#### `clean_source_code.py`
- **Purpose:** Cleans and validates source code dataset
- **Input:** `lab2/data/source_code_raw.csv`
- **Output:** `lab2/data/source_code_clean.csv`
- **Cleaning Rules:**
  - Remove records with empty file paths
  - Validate LOC and file size as integers
  - Remove duplicate (repository, file_path) pairs

#### `clean_commit_history.py`
- **Purpose:** Cleans and validates commit history dataset
- **Input:** `lab2/data/commit_history_raw.csv`
- **Output:** `lab2/data/commit_history_clean.csv`
- **Cleaning Rules:**
  - Remove records with empty repository or commit hash
  - Validate date format (ISO 8601: YYYY-MM-DD HH:MM:SS ±HHMM)
  - Validate files changed, insertions, and deletions as integers
  - Remove duplicate (repository, commit_hash) pairs

#### `create_commit_summary.py`
- **Purpose:** Aggregates commit statistics by repository
- **Input:** `lab2/data/commit_history_clean.csv`
- **Output:** `lab2/data/commit_summary.csv`
- **Process:**
  - Groups cleaned commits by repository
  - Aggregates totals and calculates averages
  - Creates one row per repository with repository-level commit statistics

#### `create_combined_dataset.py`
- **Purpose:** Integrates source code and commit history datasets
- **Input:**
  - `lab2/data/source_code_clean.csv`
  - `lab2/data/commit_summary.csv`
- **Output:** `lab2/data/combined_repository_dataset.csv`
- **Process:**
  - Aggregates source code statistics by repository
  - Merges with commit summary statistics
  - Calculates derived metrics (e.g., average LOC per file)
  - Creates one row per repository with combined metrics

#### `analyze_repository_size.py`
- **Purpose:** Displays repository size and code volume statistics
- **Input:** `lab2/data/combined_repository_dataset.csv`
- **Output:** Console output displaying repository statistics
- **Process:**
  - Reads the combined dataset
  - Prints total source files and LOC for each repository

---

## 10. How to Run

### Prerequisites

- Python 3.x
- Git installed on the system
- Access to the cloned repositories in the `lab2_repositories/` directory (created in Lab 1)

### Execution Order

The scripts must be run in the following order to generate all datasets:

**Step 1: Mine Source Code Data**
```bash
cd /Users/sarthakbordia/devops\ lab/CSET456Lab
python lab2/src/mine_source_code.py
```
Output: `lab2/data/source_code_raw.csv`

**Step 2: Mine Commit History Data**
```bash
python lab2/src/mine_commit_history.py
```
Output: `lab2/data/commit_history_raw.csv`

**Step 3: Clean Source Code Data**
```bash
python lab2/src/clean_source_code.py
```
Output: `lab2/data/source_code_clean.csv`

**Step 4: Clean Commit History Data**
```bash
python lab2/src/clean_commit_history.py
```
Output: `lab2/data/commit_history_clean.csv`

**Step 5: Create Commit Summary**
```bash
python lab2/src/create_commit_summary.py
```
Output: `lab2/data/commit_summary.csv`

**Step 6: Create Combined Dataset**
```bash
python lab2/src/create_combined_dataset.py
```
Output: `lab2/data/combined_repository_dataset.csv`

**Step 7 (Optional): Analyze Repository Size**
```bash
python lab2/src/analyze_repository_size.py
```
Output: Console display of repository statistics

### Using Virtual Environment (if applicable)

If a Python virtual environment is used:
```bash
source /path/to/venv/bin/activate
python lab2/src/mine_source_code.py
# ... run other scripts
deactivate
```

---

## 11. Output Files

| File | Rows | Description |
|------|------|-------------|
| `source_code_raw.csv` | 2,594 | Raw source code metrics extracted from all repositories |
| `source_code_clean.csv` | 2,594 | Cleaned and validated source code metrics |
| `commit_history_raw.csv` | 77,927 | Raw commit history extracted from Git logs |
| `commit_history_clean.csv` | 77,927 | Cleaned and validated commit history |
| `commit_summary.csv` | 5 | Repository-level commit statistics (one row per repository) |
| `combined_repository_dataset.csv` | 5 | Integrated dataset with both source code and commit statistics |

All CSV files are formatted with headers and are suitable for further analysis using data analysis tools (e.g., pandas, Excel, data visualization tools).

---

## 12. Conclusion

Lab 2 successfully demonstrates the complete data pipeline for software repository mining and analysis. The lab extracted source code and commit history data from five real-world open-source Python repositories (Flask, Requests, Pytest, FastAPI, and Scikit-learn), cleaned the raw datasets by removing duplicates and validating data integrity, and integrated the disparate data sources into a unified combined dataset. The resulting datasets provide valuable metrics for understanding repository characteristics, code volume, and development activity patterns, forming a foundation for further software engineering research and analysis.

The combined dataset reveals significant variations in repository size and development activity:
- **Scikit-learn** has the largest codebase (1,058 source files, 384,229 LOC) with the most commits (38,733)
- **FastAPI** shows high development velocity (106.56 avg insertions per commit)
- **Requests** has the smallest source file count (37 files) but high code density (265.97 avg LOC per file)
- **Pytest** balances code volume and commit activity with 274 files and 19,050 commits

These datasets are now ready for further statistical analysis, visualization, and software engineering research tasks.
