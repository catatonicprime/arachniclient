# arachniclient

Arachni REST client to control arachni vulnerability scanners.

## Usage

Command Line Interface (CLI) options may be listed:

```sh
arachni-client --help
```

## Examples

Adding a scan:

```sh
arachni-client --url "https://[target server]/"
```

Listing currently running scans:

```sh
arachni-client --list
```

Fetching a report from a running or completed scan in a zipped HTML format:

```sh
arachni-client --report [scan id] --format html.zip
```
