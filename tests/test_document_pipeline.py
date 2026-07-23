from core.career_orchestrator import CareerOrchestrator

job = {

    "company": "Microsoft",

    "title": "Business Intelligence Analyst"

}

orchestrator = CareerOrchestrator()

result = orchestrator.generate_documents(job)

print("=" * 60)
print("DOCUMENT PIPELINE")
print("=" * 60)

print(result)