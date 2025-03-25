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


### Create context structure
This will create a knowledge package structure for a given context name which will allow you to tailor the applicatioin to your specific needs.


```console
$ haiven-cli create-context --context-name <CONTEXT_NAME> --kp-root <KNOWLEDGE_ROOT_DIR>
```
- CONTEXT_NAME being the name of the context you want to create a knowledge package for.
- KNOWLEDGE_ROOT_DIR being the path to the knowledge pack root directory.

this should result in a context structure being created within your knowledge package root directory  withthe following structure:
```
<KNOWLEDGE_ROOT_DIR>
├── embeddings
├── prompts
└──contexts
  └──<CONTEXT_NAME>
    ├── architecture.md
    ├── domain.md
    └── embeddings
```

### Index all files in the source directory
This will convert the files you want to rely on into embeddings and store them in the knowledge package directory.

```console
$ haiven-cli index-all-files <SOURCE_DIR>  --description <DESCRIPTION> --embedding-model <EMBEDDING_MODEL> --output-dir <KNOWLEDGE_ROOT_DIR>/contexts/<CONTEXT_NAME>/embeddings
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

#### Output
For each file in the source directory a markdown file and a .kb folder should be created in the embeddings directory. Following the structure below:

```
<KNOWLEDGE_ROOT_DIR>
├── embeddings
├── prompts
└──contexts
  └──<CONTEXT_NAME>
    ├── architecture.md
    ├── domain.md
    └── embeddings
      ├── file1.md
      └── file1.kb
```

## Vector Store Configuration

By default, HAIVEN uses FAISS as the vector store. You can configure it to use Qdrant instead by adding the following to your config.yaml:

```yaml
vector_store:
  type: "qdrant"
  settings:
    url: "http://localhost:6333"  # Your Qdrant server URL
    collection_name: "haiven"     # Optional, defaults to "haiven"

# Your existing configuration...
embeddings:
  - id: "text-embedding-ada-002"
    name: "Ada"
    provider: "OpenAI"
    config:
      api_key: "${OPENAI_API_KEY}"
```

### Setting up Qdrant

1. Install Qdrant using Docker:
```bash
docker run -p 6333:6333 qdrant/qdrant
```

2. Or install the standalone server:
```bash
curl -L https://github.com/qdrant/qdrant/releases/latest/download/qdrant-x86_64-unknown-linux-gnu.tar.gz | tar xz
./qdrant
```

3. Install the Python client:
```bash
pip install qdrant-client
```

The vector store configuration will be used for all indexing operations. You can switch between FAISS and Qdrant by updating the configuration file.

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

* `create-context`: Create a context package base structure.
* `index-all-files`: Index all files in a directory to a given...
* `index-file`: Index single file to a given destination...
* `init`: Initialize the config file with the given...
* `set-config-path`: Set the config path in the config file.
* `set-env-path`: Set the env path in the config file.

## `haiven-cli create-context`

Create a context package base structure.

**Usage**:

```console
$ haiven-cli create-context [OPTIONS]
```

**Options**:

* `--context-name TEXT`
* `--kp-root TEXT`
* `--help`: Show this message and exit.

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
