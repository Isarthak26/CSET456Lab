import csv


INPUT_FILE = "lab2/data/combined_repository_dataset.csv"


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    rows = list(reader)


print("Repository Size Analysis")
print("-" * 40)

for row in rows:
    print(
        f"{row['repository']}: "
        f"{row['total_source_files']} source files, "
        f"{row['total_loc']} LOC"
    )