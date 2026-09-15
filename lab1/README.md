# LAB-1: Mining and Profiling a Software Repository

## 1. Objective

The objective of this lab is to understand how a software repository can be used as a source of software engineering data. In this lab, I will analyze an open-source GitHub repository and collect information about its files, source code, and Git history.

The lab focuses on understanding both the structure of the repository and its development history. I will calculate different repository-level and file-level metrics and store the collected information in structured formats such as CSV and JSON.

## 2. Problem Understanding

A software repository contains more than just source code. It also contains information about the structure of the project, different types of files, the amount of source code, and its development history.

For this lab, I will select an open-source GitHub repository and first examine its file and directory structure. I will identify source-code files and calculate metrics such as lines of code, file size, programming language, and file extension.

I will also examine the Git history of the repository to find information such as the number of commits, contributors, frequently changed files, and changes made over time.

The collected information will be used to create datasets and repository statistics, which will help in understanding how repository mining can be used for software engineering analysis.

## 3. Selected Repository

For this lab, I have selected:

**Repository:** `psf/requests`

**GitHub:** https://github.com/psf/requests

**Programming Language:** Python

## 4. Initial Approach

My initial approach is to:

1. Access and clone the selected GitHub repository.
2. Traverse the repository and identify files and directories.
3. Identify source-code files based on their file extensions.
4. Calculate file-level metrics such as LOC and file size.
5. Generate a CSV dataset containing file-level information.
6. Analyze the Git history to obtain commit and contributor information.
7. Generate repository-level statistics in JSON format.
8. Document the results, observations, challenges, and learning outcomes in this README.

