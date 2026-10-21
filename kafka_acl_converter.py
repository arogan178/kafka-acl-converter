import argparse
import glob
import os

import yaml

class OrderedDumper(yaml.SafeDumper):
    def _dict_representer(self, data):
        return self.represent_mapping('tag:yaml.org,2002:map', data.items())

OrderedDumper.add_representer(dict, OrderedDumper._dict_representer)

def merge_operations_by_resource(yaml_file):
    """
    Merge operations by resource in the given YAML file.

    Args:
        yaml_file (str): The path to the YAML file.

    Returns:
        dict: The modified data with merged operations.
    """
    with open(yaml_file, 'r') as file:
        data = yaml.safe_load(file)

    if 'authorization' not in (data or {}).get('spec', {}):
        return None

    merged_items = {}
    for item in data['spec']['authorization']['acls']:
        if 'operation' not in item:
            print(f"Skipping item {item} because it doesn't have an 'operation' File: {os.path.basename(yaml_file)}")
            return None  # skip this item if it doesn't have an 'operation' key

        resource = item['resource']
        resource_name = resource['name']
        resource_type = resource['type']
        resource_key = f"{resource_name}_{resource_type}"

        if resource_key in merged_items:
            merged_items[resource_key]['operations'].append(item['operation'])
        else:
            merged_items[resource_key] = {
                'resource': resource,
                'operations': [item['operation']]
            }

    merged_operations = list(merged_items.values())
    data['spec']['authorization']['acls'] = merged_operations
    return data


def main():
    parser = argparse.ArgumentParser(description="Merge Strimzi KafkaUser ACL operations by resource (Strimzi 0.30+ format).")
    parser.add_argument("directory", help="directory containing KafkaUser YAML files")
    parser.add_argument("--dry-run", action="store_true", help="print the converted YAML instead of overwriting files")
    args = parser.parse_args()

    files = sorted(glob.glob(os.path.join(args.directory, "*.yaml")) + glob.glob(os.path.join(args.directory, "*.yml")))
    if not files:
        print(f"No YAML files found in {args.directory}")
        return

    for file in files:
        print(f"Processing file: {file}")
        merged_data = merge_operations_by_resource(file)

        if merged_data is None:
            print(f"Skipping file {file} because it doesn't have an 'operation' key")
            continue

        if args.dry_run:
            print(yaml.dump(merged_data, Dumper=OrderedDumper))
        else:
            with open(file, 'w') as f:
                yaml.dump(merged_data, f, Dumper=OrderedDumper)


if __name__ == "__main__":
    main()
