# ComputeNest-CLI

## Project Description
`computenest-cli` is a command-line tool that integrates the creation, updating, and deployment of artifacts, as well as the creation and updating of services within the ComputeNest framework. It allows users to manage their services, construct artifacts, and handle custom operations, such as custom image creation.

## Requirements
- Python >= 3.6

## Installation
`computenest-cli` can be installed using the pip package manager.

```shell
# Install the computenest-cli 
pip install computenest-cli
```

## Usage
To use `computenest-cli`, simply run the corresponding command with the required parameters. Each command comes with a `--help` option to display help information about the command's usage.

### Importing Services

```shell
computenest-cli import --file_path $FILE_PATH --access_key_id $ACCESS_KEY_ID --access_key_secret $ACCESS_KEY_SECRET
```

Replace `$FILE_PATH` with the path to your `config.yaml`, and `$ACCESS_KEY_ID` and `$ACCESS_KEY_SECRET` with your AccessKey ID and AccessKey Secret respectively.

Optional parameters for `import` command:

| Parameter        | Description                            | Example Value            |
| ---------------- | -------------------------------------- | ------------------------ |
| `service_name`   | Name of the service                    | `my-service`             |
| `version_name`   | Name of the service version            | `v1.0`                   |
| `icon`           | Custom icon URL for the service        | `https://xxx/icon.png`   |
| `desc`           | Description of the service             | `Sample service`         |
| `update_artifact`| Whether the artifact needs updating    | `True` or `False`        |

### Exporting Services

```shell
computenest-cli export --region_id $REGION_ID --service_name $SERVICE_NAME --file_path $FILE_PATH --access_key_id $ACCESS_KEY_ID --access_key_secret $ACCESS_KEY_SECRET
```

Set `$REGION_ID` and `$SERVICE_NAME` with your targeted Region ID and Service Name, and `$FILE_PATH` with the desired output path of the configuration file.

### Generating Files or Projects

```shell
computenest-cli generate --type "file" --file_path $TEMPLATE_PATH --parameters '{}' --output_path $OUTPUT_PATH -y
```

Add `-y` to bypass overwrite confirmation prompts if the output file already exists.

| Parameter         | Description                                      |
| ----------------- | ------------------------------------------------ |
| `--type`          | The type of generation (`file` or `project`).    |
| `--file_path`     | File path to the template.                       |
| `--parameters`    | JSON string of parameters to apply to the template |
| `--parameter_path`| Path to a JSON or YAML file containing parameters |
| `--output_path`   | Path for the output generated file or project.   |
|  `-y`     | Confirm overwriting of the output file without prompt. |

### Getting Help

To obtain help for a specific command, add `--help` after the command:

```shell
computenest-cli import --help
```

## How to Get the AccessKey Pair

Follow the instructions to create an AccessKey pair: [Create an AccessKey pair](https://www.alibabacloud.com/help/en/ram/user-guide/create-an-accesskey-pair)
