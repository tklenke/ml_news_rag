#!/usr/bin/env python3
# Test the complete pipeline to verify sorting and deduplication

from keyword_builder import (
    aggregate_keywords,
    merge_keyword_lists,
    filter_noise_keywords,
    sort_keywords
)

# Simulate LLM output with duplicates and unsorted
llm_output = [
    ["firewall", "engine", "cowling"],
    ["aluminum", "firewall", "epoxy"],  # duplicate "firewall"
    ["wing", "aluminum", "cowling"],    # duplicate "aluminum", "cowling"
]

# Existing keywords (from file)
existing = ["canard", "epoxy", "fuel"]  # "epoxy" will be duplicate

print("=== Testing Pipeline ===\n")

# Step 1: Aggregate (should deduplicate and lowercase)
print("Step 1: Aggregate keywords from LLM output")
print(f"Input: {llm_output}")
unique_keywords = aggregate_keywords(llm_output)
print(f"Output (Set): {unique_keywords}")
print(f"Count: {len(unique_keywords)} (should be 6 unique)")
print()

# Step 2: Merge with existing
print("Step 2: Merge with existing keywords")
print(f"Existing: {existing}")
merged = merge_keyword_lists(existing, unique_keywords)
print(f"Merged (Set): {merged}")
print(f"Count: {len(merged)} (should be 8 unique)")
print()

# Step 3: Filter noise
print("Step 3: Filter noise keywords")
filtered = filter_noise_keywords(merged)
print(f"Filtered (Set): {filtered}")
print(f"Count: {len(filtered)} (should still be 8, no noise words)")
print()

# Step 4: Sort
print("Step 4: Sort alphabetically")
sorted_keywords = sort_keywords(filtered)
print(f"Sorted (List): {sorted_keywords}")
print()

# Step 5: Verify alphabetization
print("Step 5: Verify alphabetization")
is_sorted = sorted_keywords == sorted(sorted_keywords)
print(f"Is alphabetically sorted? {is_sorted}")
print()

# Step 6: Write to file and verify
print("Step 6: Write to file and read back")
test_file = "test_pipeline_output.txt"
with open(test_file, 'w') as f:
    for keyword in sorted_keywords:
        f.write(f"{keyword}\n")
print(f"Wrote to {test_file}")

# Read back and verify
with open(test_file, 'r') as f:
    lines = [line.strip() for line in f if line.strip()]

print(f"Read back: {lines}")
print(f"Matches sorted list? {lines == sorted_keywords}")
print(f"Is alphabetically sorted? {lines == sorted(lines)}")
print()

print("=== Pipeline Test Complete ===")
if is_sorted and lines == sorted_keywords:
    print("✓ All checks passed - pipeline works correctly!")
else:
    print("✗ FAILED - pipeline has bugs")
