# data-analyst — Skill for Data Analysis

## Trigger

Use when the user asks to:
- "Analyze this data" or "generate insights"
- "Create charts" or "visualize data"
- "Query a database" or "write SQL"
- "Process CSV/Excel" or "clean data"
- "Generate a report" from data

## Description

Transform raw data into actionable insights using Python's standard library and zero-dependency tools. Covers SQL queries, CSV processing, visualization (SVG), statistical analysis, and automated reporting.

## Procedure

### 1. Load and Explore Data

**CSV with stdlib:**
```python
import csv
from collections import Counter, defaultdict

# Read CSV
with open('data.csv', newline='') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Quick stats
print(f"Total rows: {len(rows)}")
print(f"Columns: {rows[0].keys() if rows else 'None'}")

# Count occurrences
counts = Counter(row['category'] for row in rows)
print(counts.most_common(5))

# Group by column
grouped = defaultdict(list)
for row in rows:
    grouped[row['category']].append(row)
```

**JSON data:**
```python
import json
from pathlib import Path

data = json.loads(Path('data.json').read_text())
print(f"Records: {len(data)}")
```

### 2. SQL Queries (sqlite3 — stdlib)

```python
import sqlite3

# Create in-memory database
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# Create table
cursor.execute('''
    CREATE TABLE sales (
        id INTEGER PRIMARY KEY,
        product TEXT,
        amount REAL,
        date TEXT
    )
''')

# Insert data
sales = [
    ('Widget A', 100.0, '2026-06-01'),
    ('Widget B', 150.0, '2026-06-02'),
    ('Widget A', 200.0, '2026-06-03'),
]
cursor.executemany('INSERT INTO sales (product, amount, date) VALUES (?, ?, ?)', sales)
conn.commit()

# Query
print("Total sales by product:")
cursor.execute('''
    SELECT product, SUM(amount), COUNT(*), AVG(amount)
    FROM sales
    GROUP BY product
''')
for row in cursor.fetchall():
    print(f"  {row[0]}: ${row[1]:.2f} ({row[2]} sales, avg ${row[3]:.2f})")

# Time-based analysis
print("\nSales by month:")
cursor.execute('''
    SELECT strftime('%Y-%m', date) as month, SUM(amount)
    FROM sales
    GROUP BY month
''')
for row in cursor.fetchall():
    print(f"  {row[0]}: ${row[1]:.2f}")
```

### 3. Data Visualization (SVG — zero dependencies)

```python
# svg_chart.py — generate bar chart as SVG
import xml.etree.ElementTree as ET

def create_bar_chart(data, title="Chart", width=600, height=400):
    """data: [(label, value), ...]"""
    max_val = max(v for _, v in data)
    bar_width = (width - 100) / len(data) - 10
    
    svg = ET.Element('svg', width=str(width), height=str(height), 
                     xmlns='http://www.w3.org/2000/svg')
    
    # Title
    title_elem = ET.SubElement(svg, 'text', x=str(width/2), y='30',
                                style='text-anchor: middle; font-size: 18px;')
    title_elem.text = title
    
    # Bars
    for i, (label, value) in enumerate(data):
        x = 50 + i * (bar_width + 10)
        bar_height = (value / max_val) * (height - 100)
        y = height - 50 - bar_height
        
        # Bar rect
        ET.SubElement(svg, 'rect', x=str(x), y=str(y),
                      width=str(bar_width), height=str(bar_height),
                      fill='#4CAF50')
        
        # Label
        label_elem = ET.SubElement(svg, 'text', x=str(x + bar_width/2),
                                    y=str(height - 30),
                                    style='text-anchor: middle; font-size: 12px;')
        label_elem.text = label
        
        # Value
        val_elem = ET.SubElement(svg, 'text', x=str(x + bar_width/2),
                                  y=str(y - 5),
                                  style='text-anchor: middle; font-size: 12px;')
        val_elem.text = str(value)
    
    return ET.tostring(svg, encoding='unicode')

# Usage
sales_data = [('Jan', 150), ('Feb', 230), ('Mar', 180), ('Apr', 320)]
svg = create_bar_chart(sales_data, "Monthly Sales")
with open('chart.svg', 'w') as f:
    f.write(svg)
print("Chart saved to chart.svg")
```

### 4. Statistical Analysis

```python
import statistics
from collections import Counter

data = [12, 15, 18, 21, 24, 15, 18, 12, 15, 21]

print(f"Mean: {statistics.mean(data):.2f}")
print(f"Median: {statistics.median(data):.2f}")
print(f"Mode: {statistics.mode(data)}")
print(f"Std Dev: {statistics.stdev(data):.2f}")
print(f"Min: {min(data)}, Max: {max(data)}")
print(f"Range: {max(data) - min(data)}")

# Percentiles
data_sorted = sorted(data)
n = len(data_sorted)
for p in [25, 50, 75]:
    idx = int(n * p / 100)
    print(f"{p}th percentile: {data_sorted[idx]}")

# Frequency distribution
freq = Counter(data)
print(f"\nFrequency: {dict(freq)}")
```

### 5. Generate Reports

```python
import json
from datetime import datetime
from pathlib import Path

def generate_report(data, title="Data Report"):
    report = {
        "title": title,
        "generated_at": datetime.now().isoformat(),
        "summary": {},
        "details": data
    }
    
    # Compute summary stats
    if isinstance(data, list) and data:
        numeric_cols = []
        for key in data[0].keys():
            try:
                values = [float(row[key]) for row in data if row[key]]
                if values:
                    numeric_cols.append((key, values))
            except (ValueError, TypeError):
                pass
        
        for col, values in numeric_cols:
            report["summary"][col] = {
                "count": len(values),
                "sum": sum(values),
                "avg": sum(values) / len(values),
                "min": min(values),
                "max": max(values)
            }
    
    return report

# Save as JSON
report = generate_report(rows, "Sales Analysis")
Path('report.json').write_text(json.dumps(report, indent=2))
```

**Markdown report:**
```python
def generate_markdown_report(data, title="Report"):
    lines = [f"# {title}", f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"]
    
    lines.append("## Summary\n")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total Records | {len(data)} |")
    
    lines.append("\n## Details\n")
    lines.append(f"| {' | '.join(data[0].keys())} |")
    lines.append(f"| {' | '.join(['---'] * len(data[0]))} |")
    for row in data[:10]:  # First 10 rows
        lines.append(f"| {' | '.join(str(v) for v in row.values())} |")
    
    return '\n'.join(lines)
```

### 6. Data Cleaning

```python
# Clean CSV data
def clean_csv(input_file, output_file):
    with open(input_file, newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    
    cleaned = []
    for row in rows:
        # Remove empty rows
        if not any(row.values()):
            continue
        
        # Strip whitespace
        for key in row:
            if row[key]:
                row[key] = row[key].strip()
        
        # Normalize case
        if 'email' in row and row['email']:
            row['email'] = row['email'].lower()
        
        # Remove duplicates (simple check)
        if row not in cleaned:
            cleaned.append(row)
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned)
    
    print(f"Cleaned: {len(rows)} → {len(cleaned)} rows")
```

## Checklist

- [ ] Data loaded and parsed correctly
- [ ] Missing/null values identified and handled
- [ ] Data types are correct (numbers not strings)
- [ ] Duplicates removed if applicable
- [ ] Outliers identified and documented
- [ ] Summary statistics calculated
- [ ] Visualizations created (if helpful)
- [ ] Report generated with key findings
- [ ] Data saved in clean format

## Examples

**Complete data analysis pipeline:**
```python
import csv
import json
import sqlite3
from collections import defaultdict
from datetime import datetime

# 1. Load CSV
with open('sales.csv') as f:
    rows = list(csv.DictReader(f))

# 2. Clean
for row in rows:
    row['amount'] = float(row['amount'])
    row['quantity'] = int(row['quantity'])

# 3. Analyze
by_product = defaultdict(lambda: {'sales': 0, 'revenue': 0})
for row in rows:
    p = row['product']
    by_product[p]['sales'] += row['quantity']
    by_product[p]['revenue'] += row['amount']

# 4. Report
report = {
    'generated': datetime.now().isoformat(),
    'total_records': len(rows),
    'total_revenue': sum(r['amount'] for r in rows),
    'by_product': dict(by_product)
}

with open('analysis_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print("Analysis complete. See analysis_report.json")
```

## See Also

- `skills/doc-generator/SKILL.md` — Generate professional READMEs and docs
- `skills/benchmark-runner/SKILL.md` — Performance measurement
- `skills/test-automation/SKILL.md` — Test your data pipelines

---

*Last verified: 2026-06-26*
