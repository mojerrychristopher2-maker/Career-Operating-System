#!/usr/bin/env python3
"""Ad-hoc verification for role matcher behavior."""

import sys, os, tempfile, textwrap, subprocess

temp_script = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=r'C:\Users\mojer\AppData\Local\Temp').name

with open(temp_script, 'w') as f:
    f.write(textwrap.dedent("""
        import sys, os
        sys.path.insert(0, r'C:\\Users\\mojer\\Documents\\Codex\\2026-07-20\\bui\\outputs\\mojerry-career-os')

        from modules.intelligence.role_matcher import RoleMatcher

        matcher = RoleMatcher()

        # Positive target roles (should accept)
        positive_roles = [
            "Data Analyst",
            "Junior Data Analyst",
            "Business Intelligence Analyst",
            "BI Analyst",
            "Business Intelligence Developer",
            "BI Developer",
            "Reporting Analyst",
            "Power BI Analyst",
            "Power BI Developer",
            "Business Analyst",
            "Data Reporting Analyst",
            "Junior BI Analyst",
            "Junior Business Analyst"
        ]

        # Negative roles (should reject)
        negative_roles = [
            "Software Engineer",
            "Full Stack Engineer",
            "Backend Engineer",
            "Frontend Engineer",
            "DevOps Engineer",
            "ML Engineer",
            "Research Engineer",
            "Research Scientist",
            "Hardware Engineer",
            "Engineering Manager",
            "Engineering Director"
        ]

        print("=== POSITIVE ROLES ===")
        positive_failures = []
        for title in positive_roles:
            score = matcher.score(title)
            passed = score['score'] > 0
            status = "✅" if passed else "❌"
            print(f"{status} {title}: score={score['score']} role={score['role']} family={score['family']}")
            if not passed:
                positive_failures.append(title)

        print("\\n=== NEGATIVE ROLES ===")
        negative_failures = []
        for title in negative_roles:
            score = matcher.score(title)
            passed = score['score'] == 0
            status = "✅" if passed else "❌"
            print(f"{status} {title}: score={score['score']} role={score['role']} family={score['family']}")
            if not passed:
                negative_failures.append(title)

        print("\\n=== SUMMARY ===")
        print(f"Positive roles failed: {len(positive_failures)} -> {positive_failures}")
        print(f"Negative roles failed: {len(negative_failures)} -> {negative_failures}")

        if not positive_failures and not negative_failures:
            print("\\n✅ ALL TESTS PASSED")
            sys.exit(0)
        else:
            print("\\n❌ SOME TESTS FAILED")
            sys.exit(1)
    """))

# Run the verification script
result = subprocess.run([sys.executable, temp_script], capture_output=True, text=True, timeout=30)

# Clean up
os.unlink(temp_script)

print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr[:500])
print(f"\nExit Code: {result.returncode}")