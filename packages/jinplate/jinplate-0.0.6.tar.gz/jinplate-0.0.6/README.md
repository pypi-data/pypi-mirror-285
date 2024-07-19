# jinplate

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)

A command line [Jinja2](https://github.com/pallets/jinja) renderer inspired
by [gomplate](https://github.com/hairyhenderson/gomplate)

jinplate can read from local and remote variable files in a number of formats and use them
to render a local Jinja2 template file.

jinplate uses URIs to identify how to fetch and parse Jinja2 variable files.

# Installation
```
pip install jinplate
```

To install with support for the tests and filters included with ansible, use

```
pip install jinplate[ansible]
```

# Usage

```
jinplate --help
Usage: jinplate [OPTIONS] TEMPLATE_FILE DATASOURCES...

  A command line renderer for jinja templates

  TEMPLATE_FILE is the path to a jinja template file to render

  DATASOURCES is a list of URIs to data sources supported by jinplate which
  contain the template variables. Data sources are parsed and merged into a single
  dict in the order in which they are specified.

  --jinja-ext allows specifying a comma-separated list of import paths
  containing jinja extensions. Example: --jinja-ext jinja2.ext.i18n

Options:
  --jinja-ext TEXT
  --help            Show this message and exit.
```

# Local Vars Example

test.j2
```yaml
---

key: {{ test1.key }}
arr: {{ test2.arr }}
```

vars.json
```json
{
  "test1": {
    "key": "val"
  },
  "test2": {
    "arr": [1, 2, 3]
  }
}
```

```
jinplate test.j2 "file:///$(pwd)/vars.json"

---

key: val
arr: [1, 2, 3]
```

# Remote Vars example

```
python -m http.server
```

```
jinplate test.j2 "http://127.0.0.1:8000/vars.json"

---

key: val
arr: [1, 2, 3]
```


# Supported Vars File Schemes
| URI Scheme | Plugin                         | Example                             |
|------------|--------------------------------|-------------------------------------|
| file       | `jinplate.plugins.scheme.file` | `file:////path/to/vars.yaml`        |
| http       | `jinplate.plugins.scheme.http` | `http://127.0.0.1:8000/vars`        |


# Supported Vars File Types
File types are determined by extension, but can also be overridden by appending
`+<file_type>` to the datasource URI scheme, as in `http+json://`

| File type | Matching extensions | Plugin                             | Example                                                          |
|-----------|---------------------|------------------------------------|------------------------------------------------------------------|
| json      | `.json`             | `jinplate.plugins.filetype.json`   | `http+json://127.0.0.1:8000/vars`                                |
| yaml      | `.yaml`, `.yml`     | `jinplate.plugins.filetype.yaml`   | `http://127.0.0.1:8000/vars.yml`<br>`file:////path/to/vars.yaml` |
| dotenv    | `.env`              | `jinplate.plugins.filetype.dotenv` | `file+env:////path/to/vars`                                      |
