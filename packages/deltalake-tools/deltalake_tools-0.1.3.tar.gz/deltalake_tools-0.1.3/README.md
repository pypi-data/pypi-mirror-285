# Deltalake Tools

## Introduction

A set of easy to use tools for deltalake, with a command line interface.
You don't need this if you're already using delta-rs (deltalake).

Inspired by the Amazon AWS cli tool.  

However, if you use pyspark and your distributed query engine requires a _last_checkpoint file, then this is an easy way to get just that.

Delta Table Commands currently supported:
- compact
- vacuum
- create-checkpoint
- table-version


## Getting started

Install

```shell
pip install deltalake-tools
```
__check out [astral's](https://astral.sh/) rye, uv and ruff projects__

(uv is a blazingly fast drop-in replacement for pip.)
```shell
uv install deltalake-tools
```

If you prefer rye:
```shell
rye add deltalake-tools
```

## Usage
help
```shell
(.venv)) test-runner$ deltalake-tools table-version /tmp/delta_table_test
10
(.venv)) test-runner$
```

table-version
```shell
(.venv)) test-runner$ deltalake-tools -h
Usage: deltalake-tools [OPTIONS] COMMAND [ARGS]...

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  compact
  create-checkpoint
  table-version
  vacuum
(.venv)) test-runner$
```


## Contribute

