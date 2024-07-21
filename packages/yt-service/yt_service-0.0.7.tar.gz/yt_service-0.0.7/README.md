# yt-service Usage Guide

## Overview
`yt-service` is a command-line utility designed to manage and control a video downloading service. This guide provides details on available options and their usage.

## Command Syntax
```
yt-service [OPTIONS]
```

## Options

| Option                  | Description                                             | Default Value               |
|-------------------------|---------------------------------------------------------|-----------------------------|
| `--host TEXT`           | Service IP address                                      | `0.0.0.0`                   |
| `--port INTEGER`        | Service port                                            | `8000`                      |
| `--proxy TEXT`          | Proxy server address                                    | `socks5://127.0.0.1:1086`   |
| `--download-dir PATH`   | Directory where downloads will be stored                | `~/YTDownload`              |
| `-s, --signal [install\|start\|stop\|status\|rm]` | Send signal to the service (install, start, stop, status, remove) |                             |
| `--help`                | Show help message and exit                              |                             |

## Example Usage

### Start the Service
To start the service with the default settings:

```sh
yt-service --host 0.0.0.0 --port 8000
```

### Change the Download Directory

To specify a different download directory:

```sh
yt-service --download-dir /path/to/download
```

### Use a Different Proxy Server

To use a different proxy server:

```sh
yt-service --proxy socks5://new.proxy.address:port
```

### Manage Service Signals

- **Install the service**:
  ```sh
  yt-service -s install
  ```
- **Start the service**:
  ```sh
  yt-service -s start
  ```
- **Stop the service**:
  ```sh
  yt-service -s stop
  ```
- **Check service status**:
  ```sh
  yt-service -s status
  ```
- **Remove the service**:
  ```sh
  yt-service -s rm
  ```

### Display Help

To display the help message with detailed information about the options:

```sh
yt-service --help
```

## Conclusion

This guide provides a comprehensive overview of the `yt-service` command-line utility. By using the provided options and examples, users can effectively manage and control the video downloading service according to their specific requirements.

## Deploy

~~~bash
pip install build twine
python -m build
twine upload dist/*
~~~