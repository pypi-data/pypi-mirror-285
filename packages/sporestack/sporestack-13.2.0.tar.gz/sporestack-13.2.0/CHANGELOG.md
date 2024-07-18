# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Deprecated features that will be removed in the next major version (14.X.X).

### CLI

- `sporestack token servers` will be removed in favor  of `sporestack server list`.

## [Unreleased]

- Nothing yet.

## [13.2.0 - 2024-07-17]

`--hostname` usage should be faster if you have a lot of servers on your token.

### Added

- Support for filtering by `hostname`, `include_deleted`, and `include_forgotten` with `api_client.servers_launched_from_token()`.
- `sporestack server list` now has `--show-deleted/--no-show-deleted`. Defaults to `--show-deleted`.

## [13.1.0 - 2024-07-08]

### Added

- Support for specifying a provider with slugs calls (`flavors()`, `operating_systems()`, and `regions()`).

## [13.0.0 - 2024-06-25]

### Notable

This release adds support for launching servers on Vultr. This is very beta! (More on the backend side of things.)

 1. You'll need to pick a suitable flavor with: `sporestack server flavors --provider vultr`
 2. You'll need to pick a suitable region with: `sporestack server region --provider vultr`
 3. You'll need to pick a suitable OS with: `sporestack server operatingsystems --provider vultr`
 4. Launch the server accordingly: `sporestack server launch --provider vultr --region (your region) --flavor (your flavor) --operating-system (your OS)`

### Added

- Vultr support!
- `flavor`, `operating_system`, and `region` properties to `client.Server()`, returning those objects.

### Breaking Changes (Library)

- `client.Client.regions()` and `api_client.APIClient.regions()` now return `list[Region]`.
- `client.Client.operating_systems()` and `api_client.APIClient.operating_systems()` now return `list[OperatingSystem]`.
- `client.Client.flavors()` and `api_client.APIClient.flavors()` now return `list[Flavor]`.
- `ServerIfnoResponse` lost the `flavor` attribute. (Refer to `flavor_slug`)

### Changed

## [12.1.1 - 2024-06-21]

### Added

- Return provider in server info display.

## [12.1.0 - 2024-06-19]

### Added

- Preliminary provider support, to specify an alternative provider other than DigitalOcean. This isn't yet implemented on the backend, but it's on the radar!

## [12.0.0 - 2024-06-19]

### Added

- Support for Cloud Init user data in the library and CLI. You can use `sporestack server launch --user-data-file ./path/to/cloud.init.user.data`
- `sporestack.exceptions.SporeStackPaymentRequiredError`

### Removed

- Specifying a token when topping up a server. The server you used to launch the token should be used for topping it up, which is the default.
- `random_machine_id()` was removed from `sporestack.utils` as it's no longer needed.
- `--local` was removed from `sporestack server list`.

### Breaking Changes (Library)

- Three enums, `Currency`, `ServerDeletedBy`, and `TokenMessageSender` were moved from `sporestack.models` to `sporestack.constants`.
- `sporestack.api_client` has changes reflecting the recent API change from `POST /server/{machine_id}/launch` to `POST /token/{token}/servers`.
- `machine_id` was removed from `server_launch()` calls.
- `sporestack.client.Server` no longer accepts a `token` argument.

### Other Changes (Library)

- `days` is no longer required. You can set `autorenew=True` or `days=int`. If `autorenew=True`, `days` should be set to `None` or ignored. You can't have `autorenew=False` and `days=None`, however.
- `~/.sporestack/servers` is no longer used and can be removed. If it does have files, however, you should back it up first just in case.

## [11.1.0 - 2024-03-16]

## Added

### Library

- `ssh_key` to `client.Client()` and to `client.Token()`. This acts as a default SSH key when launching servers this way.

### CLI

- Support for automatic per-token SSH keys (can be overridden with `--ssh-key-file` still.) To generate, run: `ssh-keygen -C "" -t ed25519 -f ~/.sporestack/sshkey/{token}/id_ed25519`
- This means that you don't have to pass `--ssh-key-file` if you are using a token that has a locally associated SSH key.
- When launching a server with `sporestack server launch`, it will suggest adding a readymade configuration to `~/.ssh/config` to utilize whatever key you selected.

## Summary

These changes should make it easier to stay private with SporeStack, conveniently, by utilizing a SSH key per token. In general, we recommend using one unique SSH key per token that you have.

## [11.0.1 - 2024-02-29]

## Fixed

- If a server is deleted during the launch wait phase, it will give up rather than trying to wait forever for an IP address that will never come.
- `--hostname` matching is smarter in case of duplicate hostnames.

## [11.0.0 - 2024-02-26]

## Changed

- Various command/help cleanups.
- If you want the CLI features, you will have to `pip install sporestack[cli]` instead of just `pip install sporestack`.
- `--no-local` is now the default for `sporestack server list`.

## Removed

- Deprecated fields from responses and requests.
- `legacy_polling=True` support for token add/topup.

## [10.8.0 - 2024-01-03]

## Added

- Support for paying invoices without polling.
- `--qr/--no-qr` to `sporestack token topup` and `sporestack token create`.
- `--wait/--no-wait` to `sporestack token topup` and `sporestack token create`.
- `sporestack token invoice` support to view an individual invoice.

## Removed

- Python 3.7 support.

## [10.7.0 - 2023-10-31]

## Added

- Added `suspended_at` to server info response object.
- Added `autorenew_servers` to token info response object.
- Added `suspended_servers` to token info response object.

## [10.6.3 - 2023-09-18]

## Changed

- Bumped httpx timeouts from 5 seconds to 60 seconds (this may be fine-tuned in the future).

## [10.6.2 - 2023-07-07]

## Changed

- Make package compatible with Pydantic v1.10.x and v2.

## [10.6.1 - 2023-07-07]

## Changed

- Mark package as being compatible with Pydantic v1.10.X. It's not yet ready with v2. Does not seem to be possible to make the release compatible with both.

## [10.6.0 - 2023-05-25]

## Added

- `sporestack server update-hostname` command.

## [10.5.0 - 2023-05-12]

## Changed

- Use fancy table output for `sporestack server list`.

## Added

- `sporestack token invoices` command.

## [10.4.0 - 2023-05-12]

## Changed

- `pip install sporestack[cli]` recommended if you wish to use CLI features. This will be required in version 11.
- Implement [Rich](https://github.com/Textualize/rich) for much prettier output on `token info`, `server regions`, `server flavors`, and `server operating-systems`. Other commands to follow.

## [10.3.0 - 2023-05-12]

## Added

- `regions` to `APIClient` and `Client`.
- `sporestack server regions` command.

## [10.2.0 - 2023-05-03]

## Changed

- Updated client to support new `forgotten_at` field and `deleted_by`.

## [10.1.2 - 2023-04-14]

## Fixed

- HTTP 4XX errors now raise a `SporeStackUserError` instead of `SporeStackServerError`.

## [10.1.1 - 2023-04-14]

## Added

- `burn_rate_cents` to `TokenInfo` to replace `burn_rate`.
- `burn_rate_usd` to `TokenInfo`.

## Changed

- `sporestack token info` will now show burn rate in dollar amount ($0.00) instead of cents.

## Fixed

- `sporestack server operating-systems` was updated to the new API behavior. (Unfortunately, was a breaking change.)

## [10.1.0 - 2023-04-14]

## Added

- `token_info()` to `APIClient`.
- `info()` to `Client.token`.
- `changelog()` to `APIClient`.
- `changelog()` to `Client`.
- `sporestack token info` command.

## Improved

- Improved some docstrings and help messages.

## [10.0.1 - 2023-04-13]

## Fixed

- Fixed critical issue on Python versions earlier than 3.10.

## [10.0.0 - 2023-04-12]

## Changed

- No more `retry` options in `api_client`. Use try/except for `SporeStackServerError`, instead, to retry on 500s.
- Exception messages may be improved.

## [9.1.1 - 2023-04-12]

### Changed

- Bug fix with `default_factory` issue.

## [9.1.0 - 2023-03-28]

### Added

- Token messages support.
- `deleted_at` field in Server Info respones.

### Changed

- Fixes to be compatible with API updates.

## [9.0.0 - 2023-02-08]

### Added

- `Client` added to `client`
- `/server/quote` support
- `--no-wait` option for `sporestack server launch` to not wait for an IP address to be assigned.

### Changed

- Now uses `httpx` instead of `requests`

## [8.0.0 - 2023-02-07]

### Changed

- `api_client` now exposes methods under APIClient()
- `client` added with Server and Token.
- CLI reworked some. `sporestack server info` now returns plain text info. `sporestack server json` returns info in JSON format.

## [7.3.0 - 2022-11-28]

### Fixed

- Fixed broken `sporestack server topup` after API changes.

## [7.2.1 - 2022-11-01]

### Changed

- Fixed on Python 3.7 and 3.8.

## [7.2.0 - 2022-11-01]

### Changed

- Use new format for new tokens.

## [7.1.2 - 2022-11-01]

### Changed

- Fixed launch output with recent API changes.

## [7.1.1 - 2022-09-29]

### Changed

- Fixed hostname related bug when launching a server.

## [7.1.0 - 2022-09-27]

### Added

- `sporestack server autorenew-enable/disable`

### Changed

- Show autorenew status and associated token in `sporestack server list` (not in all cases, however)

## [7.0.0 - 2022-09-07]

### Added

- `sporestack server list` now accepts `--local` or `--no-local`.
- `sporestack server operating-systems`

### Changed

- `sporestack server` subcommands take `--hostname` or `--machine-id`.
- `sporestack server flavors` output is slightly more readable.

### Removed

- `sporestack server delete` (in favor of: `sporestack server destroy`)
- `sporestack server get-attribute`

## [6.2.0 - 2022-09-07]

### Added

- Allow for new *beta* `--autorenew` feature with `sporestack server launch`.

### Changed

- No longer save server JSON to disk for new servers.

## [6.1.0 - 2022-06-14]

### Changed

- Use servers launched by token endpoint in `sporestack server list`.
- Send server hostname to SporeStack API at launch time.

## [6.0.3 - 2022-04-22]

### Changed

- Bug fixes.

## [6.0.2 - 2022-04-22]

### Changed

- Replace setuptools with flit.

## [6.0.1 - 2022-04-22]

### Changed

- Use `requests` session for improved performance, in particular for `sporestack server list`.

## [6.0.0 - 2022-04-14]

### Fixed

- Use specified API endpoint for `sporestack server list` command.

## [6.0.0a3 - 2022-04-05]

### Removed

- Get rid of deprecated TokenEnable usage.

## [6.0.0a2 - 2022-04-01]

### Added

- `--quote` / `--no-quote` to launch/topup. Prompt by default if price to draw from token is acceptable.

### Removed

- affiliate_amount

### Fixed

- Protect files in ~/.sporestack with aggressive `umask`.

## [6.0.0a1 - 2022-03-31]

Remember to backup your ~/.sporestack folder as any tokens you generate will be stored there!

### Changed

- Now token-centric. You can only use `sporestack` to launch or topup servers from a token.
- `sporestack launch/info/topup`, etc, moved to `sporestack server launch/info/topup`, etc.
- `--token` argument takes the name of the token, and not the key. Defaults to `primary`.
- `--ssh-key-file` now defaults to `~/.ssh/id_rsa.pub`.
- Import generated tokens from the key with: `sporestack token import (token reference name, default is primary) --key (the token key in hex format)`

### Added

- New token commands: `sporestack token create/list`

## [5.2.3 - 2022-03-30]

### Added

- Use `~/.sporestack/servers` instead of `~/.sporestack`. Will migrate existing servers automatically.

## [5.2.2 - 2022-02-24]

### Added

- Better `sporestack list` expired server handling.

## [5.2.1 - 2022-02-10]

### Added

- New, 32 character machine ID format. (Old, 64 hex character format still supported.)
- CHANGELOG.md in Keep a Changelog format.

## [5.2.0 - 2022-01-31]

### Added

- `sporestack rebuild` command.

## [5.1.2 - 2021-10-18]

### Added

- Send `sporestack-python/version` in Use-Agent header.
