# Koltrast

Koltrast is a small module that splits a time interval into multiple, shorter intervals.

It was made to help simplify the process of backfilling pipelines.

## How to install

```sh
pip install koltrast
```

## Example usage

```python
import koltrast

intervals = koltrast.generate_intervals(
    since="2014-06-01", until="2014-06-09", chunk="day"
)

for interval in intervals:
    print(interval)
```

results in:
```
```
