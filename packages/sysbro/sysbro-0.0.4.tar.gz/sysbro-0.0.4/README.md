# 🦆 sysbro 🦆
[![Build](https://github.com/polsala/sysbro/actions/workflows/build.yml/badge.svg)](https://github.com/polsala/sysbro/actions/workflows/build.yml)

![duck](https://github.com/user-attachments/assets/742f0587-5fcb-4a86-9546-06737868c43c)

## Welcome to sysbro!


sysbro is your new favorite tool for managing server processes, PostgreSQL transactions, and Redis keys, with a touch of humor and fun! Based on the "SysDuck :duck:" label, we bring you the power of ducks and muscle!

## Features

- **Process Monitoring**: Analyze and manage system processes. View RAM and CPU usage, and kill processes if necessary.
- **PostgreSQL Monitoring**: Monitor locks and idle transactions. Kill queries that are idle for more than 150 minutes.
- **Config File Parsing**: Parse configuration files for database and Redis variables.
- **Redis Key Cleanup**: Clean Redis keys with idle time greater than a specified threshold.

## Installation

```bash
pip install sysbro
```

## Usage

### Command Line Interface (CLI)

sysbro provides a simple and intuitive CLI for managing your server processes, PostgreSQL transactions, and Redis keys.

```bash
sysbro --help
```

## Examples
### Monitor Processes

```bash
sysbro monitor_processes
```

### Terminate a Process
```bash
sysbro terminate_process 1234
```

### Suggest Process Termination

```bash
sysbro suggest_process_termination 20
```

### Read Config

```bash
sysbro read_config path/to/config.ini
```

### Clean Idle PostgreSQL Transactions

```bash
sysbro clean_idle_transactions '{"dbname": "testdb", "user": "testuser", "password": "testpass", "host": "localhost"}' 150
```

### Clean Idle Redis Keys

```bash
sysbro clean_redis localhost 6379 0 rq 604800
```

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License
MIT
