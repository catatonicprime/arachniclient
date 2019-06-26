# arachniclient
Arachni REST client to control arachni vulnerability scanners.

# Usage
Command Line Interface (CLI) options may be listed:

```
arachni-client --help
```

## Examples:
Adding a scan:
```
arachni-client --url "https://[target server]/"
```

Listing currently running scans:
```
arachni-client --list
```

Fetching a report from a running or completed scan in a zipped HTML format:
```
arachni-client --report [scan id] --format html.zip
```
