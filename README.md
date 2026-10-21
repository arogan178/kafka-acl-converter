# Kafka User ACL Converter (Strimzi 0.30 Migration Tool)

Converts Strimzi `KafkaUser` YAML files so that ACL operations are merged by resource. Strimzi 0.30 replaced the single `operation` field with an `operations` list, so one entry per operation is no longer needed. This script migrates existing ACL files to the new format in place.

Before:

```yaml
acls:
  - resource: {type: topic, name: orders}
    operation: Read
  - resource: {type: topic, name: orders}
    operation: Describe
```

After:

```yaml
acls:
  - resource: {type: topic, name: orders}
    operations: [Read, Describe]
```

## Usage

```sh
pip install -r requirements.txt

# Preview the converted YAML without touching files
python3 kafka_acl_converter.py path/to/kafkausers --dry-run

# Convert every *.yaml / *.yml file in the directory in place
python3 kafka_acl_converter.py path/to/kafkausers
```

Files are overwritten, so commit them to git (or back them up) first.

## How it works

For each YAML file in the directory:

1. Skips files without `spec.authorization`.
2. Groups ACL entries by resource name and type, collecting each entry's `operation` into an `operations` list.
3. Writes the merged ACLs back to the file.

If any ACL entry in a file has no `operation` key (for example, it is already converted), the whole file is skipped and a warning is printed.

## Requirements

- Python 3
- PyYAML

## License

[MIT](LICENSE)
