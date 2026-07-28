# Career OS Architecture

## Vision

Career OS is a modular autonomous career agent.

The `agent` package is responsible only for orchestration.

All business logic lives inside `modules`.

---

## Pipeline

CareerWorkers

↓

JobCrawler

↓

RuleJobParser

↓

CandidateScorer

↓

JobRanker

↓

TopJobsSelector

↓

AI Job Analyzer

↓

Resume Tailor

↓

Cover Letter Generator

↓

Application Package Builder

↓

Browser Automation

↓

Application Tracker

↓

Career Dashboard

---

## Module Responsibilities

### agent/

Coordinates the workflow.

Contains no business logic.

---

### modules/discovery/

Finds jobs.

Extracts job links.

Downloads job pages.

---

### modules/intelligence/

Extracts structured information.

Scores candidates.

Uses AI only when required.

---

### modules/ranking/

Ranks discovered jobs.

Selects the best opportunities.

---

### modules/resume/

Creates tailored resumes.

Optimizes ATS keywords.

Generates summaries.

---

### modules/automation/

Automates browser applications.

Tracks application progress.

---

## Design Principles

- Single Responsibility Principle
- Modular architecture
- AI only after ranking
- No duplicate pipelines
- Business logic belongs in modules
- Agent is an orchestrator only
- Every module should be independently testable