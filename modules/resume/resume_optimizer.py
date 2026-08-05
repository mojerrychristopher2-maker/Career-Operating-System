class ResumeOptimizer:

    def optimize(self, profile, job, score):

        optimized = profile.copy()

        # -----------------------------
        # Skills
        # -----------------------------

        profile_skills = profile.get("skills", [])

        matched = score.get("matched_skills", [])

        missing = score.get("missing_skills", [])

        ordered_skills = []

        for skill in matched:

            if skill not in ordered_skills:
                ordered_skills.append(skill)

        for skill in profile_skills:

            if skill not in ordered_skills:
                ordered_skills.append(skill)

        optimized["skills"] = ordered_skills

        # -----------------------------
        # Dynamic Professional Summary
        # -----------------------------

        title = job.get("title", "").lower()

        if "business intelligence" in title or "bi" in title:

            optimized["summary"] = (
                "Business Intelligence professional with strong SQL, "
                "Power BI and dashboard development skills. Passionate "
                "about transforming business data into actionable insights."
            )

        elif "data analyst" in title:

            optimized["summary"] = (
                "Data Analyst experienced in SQL, Excel, Python and Power BI. "
                "Skilled in cleaning data, building dashboards and uncovering "
                "business insights."
            )

        elif "business analyst" in title:

            optimized["summary"] = (
                "Business Analyst focused on data-driven decision making, "
                "requirements gathering and business process improvement."
            )

        else:

            optimized["summary"] = (
                "Data professional passionate about analytics, reporting "
                "and business intelligence."
            )

        # -----------------------------
        # Projects
        # -----------------------------

        projects = profile.get("projects", [])

        if projects:

            if "power bi" in title or "business intelligence" in title:

                projects = sorted(

                    projects,

                    key=lambda p:
                        "power bi" not in str(p).lower()

                )

            elif "sql" in title:

                projects = sorted(

                    projects,

                    key=lambda p:
                        "sql" not in str(p).lower()

                )

            elif "excel" in title:

                projects = sorted(

                    projects,

                    key=lambda p:
                        "excel" not in str(p).lower()

                )

        optimized["projects"] = projects

        # -----------------------------
        # Everything else
        # -----------------------------

        optimized["experience"] = profile.get("experience", [])

        optimized["education"] = profile.get("education", [])

        optimized["certifications"] = profile.get("certifications", [])

        optimized["matched_skills"] = matched

        optimized["missing_skills"] = missing

        return optimized