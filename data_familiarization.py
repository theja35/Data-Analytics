import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Load raw_dataset.csv and print a basic data familiarization summary.'
    )
    parser.add_argument(
        '--path',
        type=Path,
        default=Path(__file__).with_name('raw_dataset.csv'),
        help='Path to the CSV file to analyze. Defaults to raw_dataset.csv next to this script.',
    )
    return parser.parse_args()


def load_csv(path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
    if not path.exists():
        raise FileNotFoundError(f'CSV file not found: {path}')

    with path.open(newline='', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        header = reader.fieldnames or []
        rows = [row for row in reader]

    return header, rows


def is_number(value: str) -> bool:
    if value == '':
        return False
    try:
        float(value)
        return True
    except ValueError:
        return False


def summarize_data(header: List[str], rows: List[Dict[str, str]]) -> Dict[str, object]:
    column_stats = {}
    total_rows = len(rows)

    for key in header:
        values = [row[key] for row in rows]
        missing_count = sum(1 for value in values if value == '')
        unique_values = set(values)

        numeric_values = [float(value) for value in values if is_number(value)]
        numeric_summary = None
        if numeric_values:
            numeric_summary = {
                'min': min(numeric_values),
                'max': max(numeric_values),
                'mean': sum(numeric_values) / len(numeric_values),
                'count': len(numeric_values),
            }

        most_common = Counter(value for value in values if value != '').most_common(10)

        column_stats[key] = {
            'missing': missing_count,
            'unique': len(unique_values),
            'most_common': most_common,
            'numeric_summary': numeric_summary,
        }

    return {
        'rows': total_rows,
        'columns': header,
        'column_stats': column_stats,
        'sample_rows': rows[:5],
    }


def print_summary(summary: Dict[str, object]) -> None:
    print('Data Familiarization Summary')
    print('===========================')
    print(f"Rows: {summary['rows']}")
    print(f"Columns: {len(summary['columns'])} -> {', '.join(summary['columns'])}")
    print()

    for column in summary['columns']:
        stats = summary['column_stats'][column]
        print(f"Column: {column}")
        print(f"  Missing values: {stats['missing']}")
        print(f"  Unique values: {stats['unique']}")
        if stats['numeric_summary'] is not None:
            numeric = stats['numeric_summary']
            print(f"  Numeric summary:")
            print(f"    count: {numeric['count']}")
            print(f"    min: {numeric['min']}")
            print(f"    max: {numeric['max']}")
            print(f"    mean: {numeric['mean']:.4f}")
        if stats['most_common']:
            preview = ', '.join(f"{value} ({count})" for value, count in stats['most_common'][:5])
            print(f"  Top values: {preview}")
        print()

    print('Sample rows:')
    for sample in summary['sample_rows']:
        print(sample)


if __name__ == '__main__':
    args = parse_args()
    header, rows = load_csv(args.path)
    summary = summarize_data(header, rows)
    print_summary(summary)
