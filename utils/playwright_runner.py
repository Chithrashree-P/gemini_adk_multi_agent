# import subprocess
# import json
# import os

# def run_tests(test_path, output_dir):
#     result = {
#         "passed": 0,
#         "failed": 0,
#         "errors": 0,
#         "total": 0,
#         "status": "UNKNOWN"
#     }

#     try:
#         report_file = os.path.join(output_dir, "pytest_report.json")

#         cmd = [
#             "pytest",
#             test_path,
#             "--json-report",
#             f"--json-report-file={report_file}",
#             "-v"
#         ]

#         subprocess.run(cmd, check=False)

#         # Read pytest report
#         if os.path.exists(report_file):
#             with open(report_file, "r", encoding="utf-8") as f:
#                 data = json.load(f)

#             summary = data.get("summary", {})
#             result["passed"] = summary.get("passed", 0)
#             result["failed"] = summary.get("failed", 0)
#             result["errors"] = summary.get("errors", 0)
#             result["total"] = summary.get("total", 0)

#             result["status"] = "PASS" if result["failed"] == 0 and result["errors"] == 0 else "FAIL"

#     except Exception as e:
#         result["status"] = "ERROR"
#         result["error_message"] = str(e)

#     return result

import subprocess
import json
import os


def run_tests(test_path, output_dir):
    result = {
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "total": 0,
        "status": "UNKNOWN",
        "logs": ""   
    }

    try:
        os.makedirs(output_dir, exist_ok=True)

        report_file = os.path.join(output_dir, "pytest_report.json")

        cmd = [
            "pytest",
            test_path,
            "--json-report",
            f"--json-report-file={report_file}",
            "-v"
        ]

        # Capture logs
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        result["logs"] = process.stdout + "\n" + process.stderr

        # Read pytest JSON report
        if os.path.exists(report_file):
            with open(report_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            summary = data.get("summary", {})

            result["passed"] = summary.get("passed", 0)
            result["failed"] = summary.get("failed", 0)
            result["errors"] = summary.get("errors", 0)
            result["total"] = summary.get("total", 0)

            result["status"] = (
                "PASS"
                if result["failed"] == 0 and result["errors"] == 0
                else "FAIL"
            )
        else:
            result["status"] = "ERROR"
            result["logs"] += "\n pytest_report.json not found"

    except Exception as e:
        result["status"] = "ERROR"
        result["error_message"] = str(e)

    return result
#pytest output/tests/test_generated.py -s