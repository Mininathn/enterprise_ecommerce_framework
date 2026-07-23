import json
import os

workspace = os.getenv("WORKSPACE", os.getcwd())

summary_file = os.path.join(
    workspace,
    "reports",
    "dashboard",
    "summary.json"
)

html_file = os.path.join(
    workspace,
    "reports",
    "dashboard",
    "index.html"
)

with open(summary_file, encoding="utf-8") as f:
    data = json.load(f)

html = f"""
<!DOCTYPE html>
<html>
<head>

<title>Enterprise Dashboard</title>

<style>

body {{
font-family: Arial;
background:#f4f6f9;
margin:40px;
}}

h1 {{
color:#1565c0;
}}

.card {{

background:white;

padding:20px;

margin:15px 0;

border-radius:8px;

box-shadow:0 2px 10px rgba(0,0,0,.15);

}}

table {{

width:100%;

border-collapse:collapse;

}}

td,th {{

padding:10px;

border:1px solid #ddd;

}}

th {{

background:#1565c0;

color:white;

}}

.good {{

color:green;

font-weight:bold;

}}

.bad {{

color:red;

font-weight:bold;

}}

</style>

</head>

<body>

<h1>Enterprise Ecommerce ETL Framework</h1>

<div class="card">

<h2>Build Information</h2>

<table>

<tr><th>Item</th><th>Value</th></tr>

<tr><td>Build</td><td>{data["build"]["number"]}</td></tr>

<tr><td>Branch</td><td>{data["build"]["branch"]}</td></tr>

<tr><td>Commit</td><td>{data["build"]["commit"]}</td></tr>

<tr><td>Generated</td><td>{data["generated_on"]}</td></tr>

</table>

</div>

<div class="card">

<h2>Overall Test Summary</h2>

<table>

<tr>
<th>Total</th>
<th>Passed</th>
<th>Failed</th>
<th>Skipped</th>
</tr>

<tr>

<td>{data["tests"]["total"]}</td>

<td class="good">{data["tests"]["passed"]}</td>

<td class="bad">{data["tests"]["failed"]}</td>

<td>{data["tests"]["skipped"]}</td>

</tr>

</table>

</div>

<div class="card">

<h2>Module Summary</h2>

<table>

<tr>

<th>Module</th>

<th>Passed</th>

<th>Failed</th>

</tr>

<tr>

<td>API</td>

<td>{data["api"]["passed"]}</td>

<td>{data["api"]["failed"]}</td>

</tr>

<tr>

<td>Database</td>

<td>{data["database"]["passed"]}</td>

<td>{data["database"]["failed"]}</td>

</tr>

<tr>

<td>ETL</td>

<td>{data["etl"]["passed"]}</td>

<td>{data["etl"]["failed"]}</td>

</tr>

</table>

</div>

<div class="card">

<h2>Infrastructure</h2>

<table>

<tr>

<th>Docker</th>

<th>Status</th>

</tr>

<tr>

<td>Docker Engine</td>

<td>{data["docker"]["status"]}</td>

</tr>

</table>

</div>

</body>

</html>

"""

with open(html_file, "w", encoding="utf-8") as f:
    f.write(html)

print("=" * 60)
print("Enterprise HTML Dashboard Generated")
print(html_file)
print("=" * 60)