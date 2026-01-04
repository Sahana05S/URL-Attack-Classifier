from core.pipeline import analyze_urls

print("test_pipeline.py is running")

results = analyze_urls([
    "http://test.com/index.php?id=1' OR 1=1--",
    "https://www.google.com"
])

print("RESULTS:", results)

for r in results:
    print(r)
