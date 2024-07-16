import json
import argparse
import sys
import os
from datetime import datetime

def create_arg_parser():
    # Creates and returns the ArgumentParser object

    parser = argparse.ArgumentParser(description='A Github Markdown Coverage Report Generator')
    parser.add_argument('reportJson', type=str, help='Path to the generated json report')
    parser.add_argument('--outputDir', type=str, help='Path to where you want to save the report')
    return parser

def create_report():
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args(sys.argv[1:])

    json_report = open(parsed_args.reportJson)
    data = json.load(json_report)

    generated_on = datetime.strptime(data['summary']['generatedon'], "%Y-%m-%dT%H:%M:%SZ")
    generated_on_str = generated_on.strftime("%m/%d/%Y - %H:%M:%S")

    markdown_content = f"""# Summary

<details open><summary>Summary</summary>

|||
|:---|:---|
| Generated on: | {generated_on_str} |
| Coverage date: | {generated_on_str} |
| Parser: | {data['summary']['parser']} |
| Assemblies: | {data['summary']['assemblies']} |
| Classes: | {data['summary']['classes']} |
| Files: | {data['summary']['files']} |
| **Line coverage:** | {data['summary']['linecoverage']}% ({data['summary']['coveredlines']} of {data['summary']['coverablelines']}) |
| Covered lines: | {data['summary']['coveredlines']} |
| Uncovered lines: | {data['summary']['uncoveredlines']} |
| Coverable lines: | {data['summary']['coverablelines']} |
| Total lines: | {data['summary']['totallines']} |
| **Branch coverage:** | {data['summary']['branchcoverage']}% ({data['summary']['coveredbranches']} of {data['summary']['totalbranches']}) |
| Covered branches: | {data['summary']['coveredbranches']} |
| Total branches: | {data['summary']['totalbranches']} |
| **Method coverage:** | {data['summary']['methodcoverage']}% ({data['summary']['coveredmethods']} of {data['summary']['totalmethods']}) |
| Covered methods: | {data['summary']['coveredmethods']} |
| Total methods: | {data['summary']['totalmethods']} |

</details>
"""

    markdown_content += """
## Coverage

"""
    for project in data['coverage']['assemblies']:
        if project['coverage'] is None:
            markdown_content += f"""
<details><summary>{project['name']} - Excluded from coverage report</summary>

|**Name**|**Line**|**Method**|**Branch**|
|:---|---:|---:|---:|
|**{project['name']}**|**NA**|**NA**|**NA**|"""
        else:
            markdown_content += f"""
<details><summary>{project['name']} - {project['coverage']}%</summary>

|**Name**|**Line**|**Method**|**Branch**|
|:---|---:|---:|---:|
|**{project['name']}**|**{project['coverage']}%**|**{project['methodcoverage']}%**|**{project['branchcoverage']}%**|"""
        for classes in project['classesinassembly']:
            if classes['branchcoverage'] is None:
                classes['branchcoverage'] = 0
            markdown_content += f"""
|{classes['name']}|{classes['coverage']}%|{classes['methodcoverage']}%|{classes['branchcoverage']}%|"""
        markdown_content += "\n</details>"
    f = open(os.path.join(parsed_args.outputDir, "GithubReportSummary.md"), "w")
    f.write(markdown_content)
    print(f"GithubReportSummary.md written to {parsed_args.outputDir}")

if __name__ == "__main__":
    create_report()
