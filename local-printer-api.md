# Local Printer API (LAN)

> Documented from the [bambu-printer-manager](https://synman.github.io/bambu-printer-manager/api-reference/) project by Synman.

The local printer API is a REST interface exposed by self-hosted printer management tools (like bambu-printer-manager) that communicate with Bambu Lab printers over MQTT on the local network. This is **not** a Bambu Lab official API — it's a community-built management layer.

## Connection

The management server connects to the printer's local MQTT broker (see [mqtt.md](mqtt.md)) and exposes a REST API on a configurable local port.

## Endpoints

### Printer Status

#### GET /api/printer

Returns the complete serialized printer object with all current state.

Returns `304 Not Modified` if no live data is available.

#### GET /api/health_check

Health check endpoint. Returns 200 with printer JSON when healthy, 500 when no live data. Both include full printer state.

---

### Temperature Control

#### GET /api/set_tool_target_temp

Sets the nozzle temperature for the active extruder.

| Parameter | Type | Required | Description                                    |
| --------- | ---- | -------- | ---------------------------------------------- |
| `temp`    | int  | yes      | Target temperature in C (clamped to 0 minimum) |

For single-extruder printers sends `M104 S{temp}`. For H2D dual-extruder models sends `M104 S{temp} T{active_tool}`.

#### GET /api/set_bed_target_temp

Sets the heated bed temperature.

| Parameter | Type | Required | Description                 |
| --------- | ---- | -------- | --------------------------- |
| `temp`    | int  | yes      | Target bed temperature in C |

#### GET /api/set_chamber_target_temp

Sets the chamber temperature. Uses `SET_CHAMBER_TEMP_TARGET` + `SET_CHAMBER_AC_MODE` (mode 0 for <40C, mode 1 for >=40C).

| Parameter | Type | Required | Description                     |
| --------- | ---- | -------- | ------------------------------- |
| `temp`    | int  | yes      | Target chamber temperature in C |

---

### Fan Control

#### GET /api/set_fan_speed_target

Sets the part-cooling fan speed.

| Parameter | Type | Required | Description              |
| --------- | ---- | -------- | ------------------------ |
| `percent` | int  | yes      | Speed percentage (0-100) |

#### GET /api/set_aux_fan_speed_target

Sets the auxiliary fan speed.

| Parameter | Type | Required | Description              |
| --------- | ---- | -------- | ------------------------ |
| `percent` | int  | yes      | Speed percentage (0-100) |

#### GET /api/set_exhaust_fan_speed_target

Sets the exhaust/chamber fan speed.

| Parameter | Type | Required | Description              |
| --------- | ---- | -------- | ------------------------ |
| `percent` | int  | yes      | Speed percentage (0-100) |

---

### Print Job Control

#### GET /api/print_3mf

Starts a 3MF print job.

| Parameter     | Type   | Required | Description                                                                                                                         |
| ------------- | ------ | -------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `filename`    | string | yes      | Full SD card path to the `.3mf` file                                                                                                |
| `platenum`    | int    | no       | Plate index within the file (0-based, default: 0)                                                                                   |
| `plate`       | string | yes      | Plate type: `AUTO`, `COOL_PLATE`, `ENG_PLATE`, `HOT_PLATE`, `TEXTURED_PLATE`, `NONE`                                                |
| `use_ams`     | bool   | no       | `"true"` to enable AMS filament feeding                                                                                             |
| `ams_mapping` | string | no       | JSON-encoded array of absolute tray IDs (0-103 for 4-slot AMS, 128-135 for single-slot HT, 254 for external spool, -1 for unmapped) |
| `bl`          | bool   | no       | `"true"` to enable bed levelling                                                                                                    |
| `flow`        | bool   | no       | `"true"` to enable flow-rate calibration                                                                                            |
| `tl`          | bool   | no       | `"true"` to enable timelapse recording                                                                                              |

#### GET /api/pause_printing

Pauses the active print job.

#### GET /api/resume_printing

Resumes a paused print job.

#### GET /api/stop_printing

Cancels or stops the current print job.

#### GET /api/skip_objects

Skips specified objects during an active print.

| Parameter | Type   | Required | Description                                          |
| --------- | ------ | -------- | ---------------------------------------------------- |
| `objects` | string | yes      | Comma-separated list of `identify_id` values to skip |

Object IDs are obtained from `get_3mf_props_for_file`.

---

### Filament Management

#### GET /api/load_filament

Loads filament from a specified AMS slot or external spool.

| Parameter | Type | Required | Description                                    |
| --------- | ---- | -------- | ---------------------------------------------- |
| `slot`    | int  | yes      | AMS slot index (0-3) or 254 for external spool |

#### GET /api/unload_filament

Unloads the currently loaded filament.

#### GET /api/refresh_spool_rfid

Re-reads the RFID tag for a specific AMS slot. Only RFID-equipped Bambu spools carry tag data.

| Parameter | Type | Required | Description                             |
| --------- | ---- | -------- | --------------------------------------- |
| `slot_id` | int  | yes      | Slot position within the AMS unit (0-3) |
| `ams_id`  | int  | yes      | AMS unit ID (typically 0-3)             |

#### GET /api/set_spool_details

Sets custom filament details for an AMS tray. Sleeps 2 seconds after issuing the command.

| Parameter         | Type   | Required | Description                                                       |
| ----------------- | ------ | -------- | ----------------------------------------------------------------- |
| `tray_id`         | int    | yes      | Global tray ID (0-15 for 4-slot AMS, 254/255 for external spools) |
| `tray_info_idx`   | string | yes      | Bambu filament preset index (e.g., `GFL99`)                       |
| `tray_id_name`    | string | no       | Display name for the spool                                        |
| `tray_type`       | string | no       | Filament material type (e.g., `PLA`, `PETG-CF`)                   |
| `tray_color`      | string | no       | Spool colour as hex (e.g., `#FF5733`)                             |
| `nozzle_temp_min` | int    | no       | Minimum nozzle temp in C (-1 to leave unchanged)                  |
| `nozzle_temp_max` | int    | no       | Maximum nozzle temp in C (-1 to leave unchanged)                  |

---

### File Management (SD Card)

#### GET /api/get_sdcard_contents

Returns the cached SD card file tree. Alphabetically sorted with folders before files.

#### GET /api/refresh_sdcard_contents

Refreshes the SD card listing from the printer via FTPS.

#### GET /api/get_sdcard_3mf_files

Returns SD card tree filtered to `.3mf` files only.

#### GET /api/refresh_sdcard_3mf_files

Refreshes both the full and 3MF-only SD card caches via FTPS.

#### GET /api/delete_sdcard_file

Deletes a file or folder from the SD card.

| Parameter | Type   | Required | Description                                                 |
| --------- | ------ | -------- | ----------------------------------------------------------- |
| `file`    | string | yes      | SD card path. Trailing slash for folders (recursive delete) |

#### GET /api/make_sdcard_directory

Creates a new directory on the SD card.

| Parameter | Type   | Required | Description                     |
| --------- | ------ | -------- | ------------------------------- |
| `dir`     | string | yes      | Full path for the new directory |

#### GET /api/rename_sdcard_file

Renames or moves a file/folder on the SD card.

| Parameter | Type   | Required | Description      |
| --------- | ------ | -------- | ---------------- |
| `src`     | string | yes      | Source path      |
| `dest`    | string | yes      | Destination path |

#### POST /api/upload_file_to_host

Uploads a file to the management server's `./uploads/` directory.

**Form data:** `myFile` (file)

#### GET /api/upload_file_to_printer

Transfers a file from the server's uploads directory to the printer SD card via FTPS.

| Parameter | Type   | Required | Description                              |
| --------- | ------ | -------- | ---------------------------------------- |
| `src`     | string | yes      | Filename in `./uploads/` (basename only) |
| `dest`    | string | yes      | Full destination path on SD card         |

#### GET /api/download_file_from_printer

Downloads a file from the printer SD card.

| Parameter | Type   | Required | Description              |
| --------- | ------ | -------- | ------------------------ |
| `src`     | string | yes      | Full path on the SD card |

#### GET /api/get_3mf_props_for_file

Parses and returns metadata for a `.3mf` file.

| Parameter | Type   | Required | Description                          |
| --------- | ------ | -------- | ------------------------------------ |
| `file`    | string | yes      | Full SD card path to the `.3mf` file |
| `plate`   | int    | no       | Plate number (1-based, default: 1)   |

#### GET /api/get_current_3mf_props

Returns metadata for the currently active print job.

---

### Tool Control (Dual Extruder — H2D/H2D Pro)

#### GET /api/toggle_active_tool

Switches between right (0) and left (1) extruders.

#### GET /api/set_nozzle_details

Sets nozzle diameter and material type for the active extruder.

| Parameter         | Type   | Required | Description                                                                       |
| ----------------- | ------ | -------- | --------------------------------------------------------------------------------- |
| `nozzle_diameter` | float  | yes      | Diameter in mm: `0.2`, `0.4`, `0.6`, `0.8`                                        |
| `nozzle_type`     | string | yes      | Material: `STAINLESS_STEEL`, `HARDENED_STEEL`, `TUNGSTEN_CARBIDE`, `BRASS`, `E3D` |

#### GET /api/refresh_nozzles

Requests the printer push current nozzle info in its next status message.

---

### Detection & Safety

#### GET /api/set_buildplate_marker_detector

| Parameter | Type | Required | Description                              |
| --------- | ---- | -------- | ---------------------------------------- |
| `enabled` | bool | yes      | `"true"` enables, anything else disables |

#### GET /api/set_spaghetti_detector

| Parameter     | Type   | Required | Description                              |
| ------------- | ------ | -------- | ---------------------------------------- |
| `enabled`     | bool   | yes      | `"true"` enables, anything else disables |
| `sensitivity` | string | no       | `"low"`, `"medium"` (default), `"high"`  |

#### GET /api/set_purgechutepileup_detector

| Parameter     | Type   | Required | Description                              |
| ------------- | ------ | -------- | ---------------------------------------- |
| `enabled`     | bool   | yes      | `"true"` enables, anything else disables |
| `sensitivity` | string | no       | `"low"`, `"medium"` (default), `"high"`  |

#### GET /api/set_nozzleclumping_detector

| Parameter     | Type   | Required | Description                              |
| ------------- | ------ | -------- | ---------------------------------------- |
| `enabled`     | bool   | yes      | `"true"` enables, anything else disables |
| `sensitivity` | string | no       | `"low"`, `"medium"` (default), `"high"`  |

#### GET /api/set_airprinting_detector

| Parameter     | Type   | Required | Description                              |
| ------------- | ------ | -------- | ---------------------------------------- |
| `enabled`     | bool   | yes      | `"true"` enables, anything else disables |
| `sensitivity` | string | no       | `"low"`, `"medium"` (default), `"high"`  |

---

### AMS Control

#### GET /api/send_ams_control_command

| Parameter | Type   | Required | Description                   |
| --------- | ------ | -------- | ----------------------------- |
| `cmd`     | string | yes      | `PAUSE`, `RESUME`, or `RESET` |

#### GET /api/set_ams_user_setting

| Parameter | Type   | Required | Description                                                           |
| --------- | ------ | -------- | --------------------------------------------------------------------- |
| `setting` | string | yes      | `CALIBRATE_REMAIN_FLAG`, `STARTUP_READ_OPTION`, or `TRAY_READ_OPTION` |
| `enabled` | bool   | yes      | `"true"` enables, anything else disables                              |

---

### Advanced Settings

#### GET /api/send_gcode

Sends raw G-code commands to the printer. Use `|` to separate multiple commands (converted to newlines).

| Parameter | Type   | Required | Description      |
| --------- | ------ | -------- | ---------------- | --------------- |
| `gcode`   | string | yes      | G-code string (` | ` for newlines) |

**Warning:** Direct G-code bypasses safety interlocks.

#### GET /api/set_print_option

| Parameter | Type   | Required | Description                                                                                                                 |
| --------- | ------ | -------- | --------------------------------------------------------------------------------------------------------------------------- |
| `option`  | string | yes      | `AUTO_RECOVERY`, `FILAMENT_TANGLE_DETECT`, `SOUND_ENABLE`, `AUTO_SWITCH_FILAMENT`, `NOZZLE_BLOB_DETECT`, `AIR_PRINT_DETECT` |
| `enabled` | bool   | yes      | `"true"` enables, anything else disables                                                                                    |

#### GET /api/set_light_state

Controls chamber and column LED lights.

| Parameter | Type   | Required | Description                              |
| --------- | ------ | -------- | ---------------------------------------- |
| `state`   | string | yes      | `"on"` turns on, anything else turns off |

#### GET /api/set_speed_level

Sets the print speed profile.

| Parameter | Type   | Required | Description                                                        |
| --------- | ------ | -------- | ------------------------------------------------------------------ |
| `level`   | string | yes      | `"1"` (silent), `"2"` (standard), `"3"` (sport), `"4"` (ludicrous) |

---

### Telemetry

#### GET /api/get_all_data

Returns full telemetry history combined with current printer state.

#### GET /api/zoom_in

Zooms in on a telemetry chart (reduces visible window by 500s, minimum 500s).

| Parameter | Type   | Required | Description                                                                                                |
| --------- | ------ | -------- | ---------------------------------------------------------------------------------------------------------- |
| `name`    | string | yes      | Collection: `tool`, `bed`, `chamber`, `fan`, `aux_fan`, `exhaust_fan`, `heatbreak_fan`, `tool_0`, `tool_1` |

#### GET /api/zoom_out

Zooms out on a telemetry chart (increases visible window by 500s).

| Parameter | Type   | Required | Description                      |
| --------- | ------ | -------- | -------------------------------- |
| `name`    | string | yes      | Same collection names as zoom_in |

#### GET /api/dump_data_ds.collections

Dumps all internal data collections as JSONL (newline-delimited JSON).

---

### System & Diagnostics

#### GET /api/toggle_session

Pauses or resumes the MQTT connection.

#### GET /api/trigger_printer_refresh

Forces printer reconnection. If disconnected: `quit()` + `start_session()`. If connected: `refresh()`.

#### GET /api/toggle_verbosity

Toggles root logger between DEBUG and INFO.

| Parameter | Type | Required | Description                             |
| --------- | ---- | -------- | --------------------------------------- |
| `verbose` | bool | no       | `"true"` for verbose, default `"false"` |

#### GET /api/dump_log

Returns contents of `./output.log`.

#### GET /api/truncate_log

Clears the log file.

#### GET /api/fake_error

Test endpoint that raises `ZeroDivisionError` to test error handling.

---

### OpenAPI / Swagger

#### GET /api/openapi.json

Returns the generated OpenAPI 3.0 schema.

#### GET /api/docs

Serves Swagger UI for interactive API exploration.
