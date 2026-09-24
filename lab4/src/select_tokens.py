import csv
import random

INPUT_FILE = "data/top_50_tokens.csv"
OUTPUT_FILE = "data/selected_20_tokens.csv"

random.seed(42)

with open(INPUT_FILE, "r", encoding="utf-8", newline="") as file:
    reader = csv.reader(file)
    rows = list(reader)

# Skip header if present
data = rows[1:] if rows and rows[0][0].lower() in ("rank", "token") else rows

selected = random.sample(data, 20)

with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["token"])

    for row in selected:
        writer.writerow([row[1]])

print("Selected 20 tokens:")
for row in selected:
    print(row[1])