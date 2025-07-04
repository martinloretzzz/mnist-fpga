import json
from collections import Counter
import matplotlib.pyplot as plt

def extract_leaf_values(node):
    leaf_values = []
    if isinstance(node, list):
        for child in node:
            leaf_values.extend(extract_leaf_values(child))
    elif isinstance(node, dict):
        if "leaf" in node:
            leaf_values.append(node["leaf"])
        if "children" in node:
            for child in node["children"]:
                leaf_values.extend(extract_leaf_values(child))
    return leaf_values

file_path = "model.json"
data = json.load(open(file_path, 'r'))

leaf_values = extract_leaf_values(data)

plt.figure(figsize=(16, 6))
plt.hist(leaf_values, bins=50, edgecolor='black', color='#4C78A8', alpha=0.7, density=False)

plt.xlabel('Leaf Value', fontsize=12, labelpad=10)
plt.ylabel('Frequency', fontsize=12, labelpad=10)
plt.title('Distribution of Leaf Scores in a Boosted Tree', fontsize=14, pad=15)

plt.grid(True, alpha=0.2, linestyle='--')
# plt.yscale('log')
# plt.xscale('log')
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.tight_layout()

output_image = "histogram.png"
plt.savefig(output_image, dpi=300, bbox_inches='tight')
plt.close()

print(f"Histogram saved as '{output_image}'")

print(f"Tree count: {len(data)}")

print(f"Min: {min(leaf_values)}, Max: {max(leaf_values)}")

print(f"Total values: {len(leaf_values)}")
zero_value_count = len([v for v in leaf_values if v == 0.0])
print(f"Zero values: {zero_value_count} ({100 * zero_value_count / len(leaf_values):.2f}%), Nonzero: {len(leaf_values) - zero_value_count}")

leaf_counter = dict(Counter(leaf_values))
count_map = {k: leaf_counter[k] for k in sorted(leaf_counter.keys())}
print(f"Leaf value counts: {count_map}")
print(f"Count of discrete values: {len(count_map)}")

discrete_leaf_values = [
    *[-(2**e) for e in range(0, -6 - 1, -1)],
    0,
    *[2**e for e in range(-6, 1 + 1)],
]
print(f"Discrete leaf values: {discrete_leaf_values}")
