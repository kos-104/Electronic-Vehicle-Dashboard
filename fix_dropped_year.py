import pathlib, re

path = pathlib.Path("tab1_salesRedo.py")
t = path.read_text(encoding="utf-8", errors="ignore")

# Replace the entire assignment RHS from: dropped_year = int( ... )  up to the closing )
pattern = r"dropped_year\s*=\s*int\(\s*sharp_drops\.tail\(1\)\s*\[\"Year\"\]\.iloc\s*.*?\)\s*"
replacement = 'dropped_year = int(sharp_drops.tail(1)["Year"].iloc<a href="" class="citation-link" target="_blank" style="vertical-align: super; font-size: 0.8em; margin-left: 3px;">[0]</a>)'

t2, n = re.subn(pattern, replacement, t, flags=re.DOTALL)

if n == 0:
    raise SystemExit("Could not find the dropped_year assignment pattern to replace.")

path.write_text(t2, encoding="utf-8")
print("Fixed dropped_year occurrences:", n)
