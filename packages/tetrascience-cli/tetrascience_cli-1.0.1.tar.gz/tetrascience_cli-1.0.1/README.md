# ts-cli <!-- omit in toc -->

Tetrascience CLI

## Version <!-- omit in toc -->

v1.0.1

## Table of Contents <!-- omit in toc -->
<details>
<summary>Show</summary>

- [Install](#install)
- [Usage](#usage)
  - [Create an artifact](#create-an-artifact)
  - [Publish an artifact](#publish-an-artifact)
    - [API Configuration](#api-configuration) 
    - [IDS Validation](#ids-validation)
- [Documentation](#documentation)
- [Changelog](#changelog)
  - [v1.0.1](#v101)
  - [v1.0.0](#v100)

</details>

## Intro

`ts-cli` allows you to interface with the Tetrascience Data Platform from the comfort of your shell

### Example

Create and publish a new task script:

```bash
ts-cli config save ~/Downloads/ts-cfg.json
ts-cli init task-script
ts-cli publish
```

## Install

```
pip install tetrascience-cli
```

## Usage

### Create an artifact

Using an IDS, Protocol, Task Script or "All-in-one" template

```bash
ts-cli init <template-type>
```

To set up the artifact's configuration interactively, use the `--interactive` or `-i` flag.

```bash
ts-cli init --interactive
```

### Publish an artifact

Including IDS, Protocol, and Task Script artifacts from their source code

```bash
ts-cli publish
```

The artifact's type, namespace, slug and version are automatically read from its `manifest.json`
file if it exists.  
To set up the artifact's configuration interactively, use the `--interative` or `-i` flag. Examples:

```bash
ts-cli publish --interactive
```

![An example of publishing an artifact using interactive mode](./docs/figures/interactive-mode-example.gif)

#### API Configuration

An API configuration is required.
This can be the API configuration JSON file (`cfg.json`) found on the Tetra Data Platform.

```json
{
	"api_url": "https://api.tetrascience.com/v1",
	"auth_token": "your-token",
	"org": "your-org",
	"ignore_ssl": false
}
```

This configuration can be referred to explicitly in the command line.
Example:

```bash
ts-cli publish --config cfg.json
```

Or saved to a specific profile.

```bash
ts-cli config save cfg.json --profile dev
ts-cli publish --profile dev
```

To apply the API configuration to all your projects automatically,
save your configuration file globally

```bash
ts-cli config save cfg.json --global
ts-cli publish
```

#### IDS Validation

When uploading IDS artifact, validation will be performed using `ts-ids-validator` package.
Validation failures for IDS will be printed to the console.

## Documentation

Click [here](docs/README.md) for `--help` and a development guide 

## Changelog

### v1.0.1

- Fix a crash on startup

### v1.0.0

- Initial release
- Includes the `init`, `publish` and `config` commands
