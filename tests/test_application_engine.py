from modules.automation.application_engine import ApplicationEngine

engine = ApplicationEngine()

page = engine.open_application(

    "https://boards.greenhouse.io/anthropic"

)

print("=" * 60)
print("APPLICATION ENGINE")
print("=" * 60)

button = engine.find_apply_button(page)

print("=" * 60)
print("APPLICATION ENGINE")
print("=" * 60)

print(page.title())

print()

print("Apply Button:")

print(button)

engine.close()