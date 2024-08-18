import pickle
import json
from collections import defaultdict


def save_to_pickle(data, file_path):
    with open(file_path, 'wb') as pickle_file:
        pickle.dump(data, pickle_file)


def load_from_json(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data


def load_from_pickle(file_path):
    with open(file_path, 'rb') as pickle_file:
        data = pickle.load(pickle_file)
    return data


def save_to_json(data, file_path):
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def extract_classification_sets(drugs):
    kingdoms = defaultdict(int)
    superclasses = defaultdict(int)
    classes = defaultdict(int)

    for drug in drugs:
        classification = drug.get('classification', {})
        if classification:
            if kingdom := classification.get('kingdom'):
                kingdoms[kingdom] += 1
            if superclass := classification.get('superclass'):
                superclasses[superclass] += 1
            if class_ := classification.get('class'):
                classes[class_] += 1

    return kingdoms, superclasses, classes


data = load_from_pickle('./data/extracted-drugs.pkl')
kingdoms, superclasses, classes = extract_classification_sets(data)

# Print the sets of kingdoms, superclasses, and classes along with counts
print("Kingdoms:")
for kingdom, count in kingdoms.items():
    print(f"{kingdom}: {count} items")

print("\nSuperclasses:")
for superclass, count in superclasses.items():
    print(f"{superclass}: {count} items")

print("\nClasses:")
for class_, count in classes.items():
    print(f"{class_}: {count} items")
