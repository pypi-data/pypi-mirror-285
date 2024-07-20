# Prop2PO

Prop2PO package converts a java property file into a Gettext PO file.

## Installation

You can install the package from pypi. 

```shell
pip install prop2po
```

## Usage

```shell
# Basic use of the package
prop2po messages.properties messages.po
```

The available options are

| Name       | Shortcut | Type | Explanation                 |
|------------|----------|------|-----------------------------|
| --language | -l       | TEXT | Language of the translation |
| --project  | -p       | TEXT | Name of the project         |
| --encoding | -e       | TEXT | Encoding of the file        |


```shell
# Print help
prop2po --help
```