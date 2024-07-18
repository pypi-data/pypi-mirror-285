# Python 3 library and CLI for [SporeStack](https://sporestack.com) ([SporeStack Tor Hidden Service](http://spore64i5sofqlfz5gq2ju4msgzojjwifls7rok2cti624zyq3fcelad.onion))

[Changelog](CHANGELOG.md)

## Requirements

* Python 3.8-3.11 (and likely newer)

## Running without installing

* Make sure [pipx](https://pipx.pypya.io) is installed.
* `pipx run 'sporestack[cli]'`

## Installation with pipx

* Make sure [pipx](https://pipx.pypya.io) is installed.
* `pipx install 'sporestack[cli]'`

## Traditional installation

* Recommended: Create and activate a virtual environment, first.
* `pip install sporestack` (Run `pip install 'sporestack[cli]'` if you wish to use the command line `sporestack` functionality and not just the Python library.)

## Usage Examples

* Recommended: Make sure you're on the latest stable version comparing `sporestack version` with git tags in this repository, or releases on [PyPI](https://pypi.org/project/sporestack/).
* `sporestack token create --dollars 20 --currency xmr`
* `sporestack token list`
* `sporestack token info`
* `sporestack server launch --hostname SomeHostname --operating-system debian-12 --days 1  # Will use ~/.ssh/id_rsa.pub as your SSH key, by default`
(You may also want to consider passing `--region` to have a non-random region. This will use the "primary" token by default, which is the default when you run `sporestack token create`.)
* `sporestack server stop --hostname SomeHostname`
* `sporestack server stop --machine-id ss_m_...  # Or use --machine-id to be more pedantic.`
* `sporestack server start --hostname SomeHostname`
* `sporestack server autorenew-enable --hostname SomeHostname`
* `sporestack server autorenew-disable --hostname SomeHostname`
* `sporestack server list`
* `sporestack server delete --hostname SomeHostname`

## Notes

* If you want to communicate with the SporeStack API using Tor, set this environment variable: `SPORESTACK_USE_TOR_ENDPOINT=1`. Verify which endpoint is in use with `sporestack api-endpoint`.

## Developing

* `pipenv install --deploy --dev`
* `pipenv run make test`
* `pipenv run make format` to format files and apply ruff fixes.

## Licence

[Unlicense/Public domain](LICENSE.txt)
