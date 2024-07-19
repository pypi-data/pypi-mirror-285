import json
import argparse
import sys
import os
from datetime import datetime

from .models import map_json_to_model

def create_arg_parser():
    parser = argparse.ArgumentParser(description='A Github Markdown Coverage Report Generator')
    parser.add_argument('reportJson', type=str, help='Path to the generated json report')
    parser.add_argument('--outputDir', type=str, help='Path to where you want to save the report')
    parser.add_argument('--llc', type=bool, help='Log the total line coverage percentage')
    parser.add_argument('--lmc', type=bool, help='Log the total method coverage percentage')
    return parser

def create_report():
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args(sys.argv[1:])

    with open(parsed_args.reportJson) as json_report:
        coverage_data = map_json_to_model(json_report.read())

    generated_on = datetime.strptime(coverage_data.summary.generatedon, "%Y-%m-%dT%H:%M:%SZ")
    generated_on_str = generated_on.strftime("%m/%d/%Y - %H:%M:%S")

    markdown_content = f"""# Summary

<details open><summary>Summary</summary>

|||
|:---|:---|
| Generated on: | {generated_on_str} |
| Coverage date: | {generated_on_str} |
| Parser: | {coverage_data.summary.parser} |
| Assemblies: | {coverage_data.summary.assemblies} |
| Classes: | {coverage_data.summary.classes} |
| Files: | {coverage_data.summary.files} |
| **Line coverage:** | {coverage_data.summary.linecoverage}% ({coverage_data.summary.coveredlines} of {coverage_data.summary.coverablelines}) |
| Covered lines: | {coverage_data.summary.coveredlines} |
| Uncovered lines: | {coverage_data.summary.uncoveredlines} |
| Coverable lines: | {coverage_data.summary.coverablelines} |
| Total lines: | {coverage_data.summary.totallines} |
| **Branch coverage:** | {coverage_data.summary.branchcoverage}% ({coverage_data.summary.coveredbranches} of {coverage_data.summary.totalbranches}) |
| Covered branches: | {coverage_data.summary.coveredbranches} |
| Total branches: | {coverage_data.summary.totalbranches} |
| **Method coverage:** | {coverage_data.summary.methodcoverage}% ({coverage_data.summary.coveredmethods} of {coverage_data.summary.totalmethods}) |
| Covered methods: | {coverage_data.summary.coveredmethods} |
| Total methods: | {coverage_data.summary.totalmethods} |

</details>
"""

    markdown_content += """
## Coverage

"""
    for project in coverage_data.coverage.assemblies:
        if project.coverage is None:
            markdown_content += f"""
<details><summary>{project.name} - Excluded from coverage report</summary>

|**Name**|**Line**|**Method**|**Branch**|
|:---|---:|---:|---:|
|**{project.name}**|**NA**|**NA**|**NA**|"""
        else:
            markdown_content += f"""
<details><summary>{project.name} - {project.coverage}%</summary>

|**Name**|**Line**|**Method**|**Branch**|
|:---|---:|---:|---:|
|**{project.name}**|**{project.coverage}%**|**{project.methodcoverage}%**|**{project.branchcoverage}%**|"""
        for class_ in project.classesinassembly:
            branch_coverage = class_.branchcoverage if class_.branchcoverage is not None else 0
            markdown_content += f"""
|{class_.name}|{class_.coverage}%|{class_.methodcoverage}%|{branch_coverage}%|"""
        markdown_content += "\n</details>"

    output_path = os.path.join(parsed_args.outputDir, "GithubReportSummary.md")
    with open(output_path, "w") as f:
        f.write(markdown_content)
    print(f"GithubReportSummary.md written to {parsed_args.outputDir}")
    if parsed_args.llc:
        print(coverage_data.summary.linecoverage)
    if parsed_args.lmc:
        print(coverage_data.summary.methodcoverage)

if __name__ == "__main__":
    create_report()