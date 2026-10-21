"""Small contract checks, not a YAML/schema validator or runtime deployment test.
Workflow formatting is deliberately fixed. Repair configurations, not this checker.
"""
import argparse
import json
import re
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("scope", choices=["pipeline", "image", "rollback", "all"])
a = p.parse_args()
contract = json.loads(Path("release-contract.json").read_text())
workflow = Path(".github/workflows/release.yml").read_text()
production = workflow.split("  production:\n", 1)[1].split("    steps:", 1)[0]
image = json.loads(Path("k8s/deployment.json").read_text())["spec"]["template"]["spec"]["containers"][0]["image"]
target = json.loads(Path("rollback.json").read_text())["target_image"]
checks = {
    "pipeline": bool(re.search(r"^    needs: (validate|\[validate\])$", production, re.M)),
    "image": image == contract["candidate_image"],
    "rollback": target == contract["known_good_image"],
}
selected = checks if a.scope == "all" else {a.scope: checks[a.scope]}
for name, passed in selected.items():
    print(f"{name}: {'PASS' if passed else 'FAIL'}")
print("Static contract checks only; no approval, registry, cluster or deployment verified.")
raise SystemExit(0 if all(selected.values()) else 1)
