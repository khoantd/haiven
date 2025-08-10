# `HAIVEN-CLI Quickstart Guide`
The `haiven-cli` is a command line interface that provides a set of commands for indexing files, and creating knowledge packages.

### HAIVEN-CLI Installation
Run the [install_dev_dependencies](../install_dev_dependencies.sh) script to install the necessary dependencies for the cli.

```console
$ ./install_dev_dependencies.sh
```

### Setup the CLI configuration
This will allow the cli to use the api keys and embedding models you have defined in the app configuration file.
```console
$ haiven-cli init --config-path <CONFIG_PATH> --env-path <ENV_PATH>
```
- CONFIG_PATH being the app config yaml definition

    By default you can use the one located at the following path `$(pwd)/app/config.yaml`

- ENV_PATH being the path to the app environment variable file definition

    By default you can use the one located at the following path `$(pwd)/app/.env`


### Index all files in the source directory
This will convert the files you want to rely on into embeddings and store them in the knowledge package directory.

```console
$ haiven-cli index-all-files <SOURCE_DIR>  --description <DESCRIPTION> --embedding-model <EMBEDDING_MODEL> --output-dir <KNOWLEDGE_ROOT_DIR>/embeddings
```
- SOURCE_DIR being the path to the source directory containing the files you want to index.
- DESCRIPTION being a description of the ensemble files you want to index.
- EMBEDDING_MODEL being the embedding model you want to use for indexing.
- KNOWLEDGE_ROOT_DIR being the path to the knowledge pack root directory.

#### Input

- PDF files: Will be indexed page by page, as they are
- CSV files: Will index contents based on column titles in the first row of the file. Expected mandatory columns are
  - content: The text content
  - metadata.title: The title to be displayed to the user (e.g. the title of the article or document)
  - metadata.source: The source of the document (e.g. a URL)
  - metadata.authors: The authors of the document

___
# `haiven-cli`

**Usage**:

```console
$ haiven-cli [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `index-all-files`: Index all files in a directory to a given...
* `index-file`: Index single file to a given destination...
* `init`: Initialize the config file with the given...
* `set-config-path`: Set the config path in the config file.
* `set-env-path`: Set the env path in the config file.


## `haiven-cli index-all-files`

Index all files in a directory to a given destination directory.

**Usage**:

```console
$ haiven-cli index-all-files [OPTIONS] SOURCE_DIR
```

**Arguments**:

* `SOURCE_DIR`: [required]

**Options**:

* `--output-dir TEXT`: [default: new_knowledge_base]
* `--embedding-model TEXT`: [default: openai]
* `--description TEXT`
* `--config-path TEXT`
* `--help`: Show this message and exit.

## `haiven-cli index-file`

Index single file to a given destination directory.

**Usage**:

```console
$ haiven-cli index-file [OPTIONS] SOURCE_PATH
```

**Arguments**:

* `SOURCE_PATH`: [required]

**Options**:

* `--embedding-model TEXT`: [default: openai]
* `--config-path TEXT`
* `--description TEXT`
* `--output-dir TEXT`: [default: new_knowledge_base]
* `--help`: Show this message and exit.

## `haiven-cli init`

Initialize the config file with the given config and env paths.

**Usage**:

```console
$ haiven-cli init [OPTIONS]
```

**Options**:

* `--config-path TEXT`
* `--env-path TEXT`
* `--help`: Show this message and exit.

## `haiven-cli set-config-path`

Set the config path in the config file.

**Usage**:

```console
$ haiven-cli set-config-path [OPTIONS]
```

**Options**:

* `--config-path TEXT`
* `--help`: Show this message and exit.

## `haiven-cli set-env-path`

Set the env path in the config file.

**Usage**:

```console
$ haiven-cli set-env-path [OPTIONS]
```

**Options**:

* `--env-path TEXT`
* `--help`: Show this message and exit.
