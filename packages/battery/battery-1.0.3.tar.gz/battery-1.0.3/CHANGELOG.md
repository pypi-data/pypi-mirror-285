This package uses semantic versioning.

- Version 1.0.3
  - Removed `|` typing that was causing lack of support for earlier versions. Tested now to 3.9
- Version 1.0
  - Rename `active` to more precise `is_discharging`.
  - Added `minutes_to_empty` and `minutes_to_full` functions (at least one of which will be blank)
  - Added `is_charging` to complement `is_discharging`
  - Supports Linux >= 2.6.24 for all functions.
  - Added command-line interface.
  - Functions now based on terminal/powershell commands stored in `battery.toml`.

- Version 0.1
  - Initial release.
