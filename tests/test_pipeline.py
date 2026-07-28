from core.pipeline import Pipeline

pipeline = Pipeline()

job = pipeline.run()

print("\n")
print("=" * 60)
print("TOP JOB")
print("=" * 60)

print(job)