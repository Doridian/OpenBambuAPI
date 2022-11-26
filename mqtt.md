# Basics

All messages on the MQTT broker are JSON encoded

There is two ways to connect to the MQTT broker

## Cloud MQTT server

URL: `mqtt://us.mqtt.bambulab.com:8883`

TLS: **yes**

Authentication: **required**

**Username:** `u_{USER_ID}`, where the user id can be grabbed by cracking your own `{ACCESS_TOKEN}` (which is a JWT) and reading its `preferred_username` field.

**Password:** `{ACCESS_TOKEN}` (the entire JWT, no prefix or suffix)

## Local MQTT server

URL: `mqtt://{PRINTER_IP}:1883`

TLS: **no**

Authentication: **disabled**

Wildcard subscriptions with `#` possible

# Topics

## device/{DEVICE_ID}/report

For information from the device to the slicer, including responses to commands

## device/{DEVICE_ID}/request

For commands to the device from the slicer

# Requests and reports

## Overview

**Request structure**

```json
{
    "{TYPE}": {
        "sequence_id": "0", // Incremented by 1 on each command
        "command": "{COMMAND}",
        ...
    }
}
```

**Report structure**

```json
{
    "{TYPE}": {
        "sequence_id": "0", // Same as the one sent in the request
        "command": "{COMMAND}",

        "result": "success", // Case insensitive!
        "reason": "", // Might not be present for some commands

        ... // All parameters from the original command
    }
}
```

## info.get_version

Get current version of printer

**Request**

```json
{
    "info": {
        "sequence_id": "0",
        "command": "get_version"
    }
}
```

**Report**

```json
{
    "info": {
        "command": "get_version",
        "module": [
            {
                "hw_ver": "",
                "name": "ota",
                "sn": "",
                "sw_ver": "01.01.01.00"
            },
            {
                "hw_ver": "AP05",
                "name": "rv1126",
                "sn": "[REDACTED]",
                "sw_ver": "00.00.14.74"
            },
            {
                "hw_ver": "TH07",
                "name": "th",
                "sn": "[REDACTED]",
                "sw_ver": "00.00.03.79"
            },
            {
                "hw_ver": "MC07",
                "name": "mc",
                "sn": "[REDACTED]",
                "sw_ver": "00.00.10.48/00.00.10.48"
            },
            {
                "hw_ver": "",
                "name": "xm",
                "sn": "",
                "sw_ver": "00.00.00.00"
            }
        ],
        "sequence_id": "0"
    }
}
```

## pushing.pushall

Unknown, probably a request for the printer to report its full status

**Request**

```json
{
    "pushing": {
        "sequence_id": "0",
        "command": "pushall"
    }
}
```

**Report**

No response, pushes a bunch of `mc_print` type reports if the printer has any in queue

## upgrade.upgrade_confirm

Part of firmware upgrade process

**Request**

```json
{
    "upgrade": {
        "sequence_id": "0",
        "command": "upgrade_confirm",
        "src_id": 1 // src_id is always 1 for the slicer
    }
}
```

**Report**

TODO


## upgrade.consistency_confirm

Part of firmware upgrade process

**Request**

```json
{
    "upgrade": {
        "sequence_id": "0",
        "command": "consistency_confirm",
        "src_id": 1 // src_id is always 1 for the slicer
    }
}
```

**Report**

TODO

## upgrade.start

Part of firmware upgrade process

**Request**

```json
{
    "upgrade": {
        "sequence_id": "0",
        "command": "start",
        "src_id": 1, // src_id is always 1 for the slicer
        "url": "...",
        "module": "ota", // ota or ams
        "version": "",
    }
}
```

**Report**

TODO

## print.stop

Stops a print. Sent with QoS of **1** for higher priority.

**Request**

```json
{
    "print": {
        "sequence_id": "0",
        "command": "stop",
        "param": "", // Always empty
    }
}
```

**Report**

See basic structure

## print.pause

Pauses a print. Sent with QoS of **1** for higher priority.

**Request**

```json
{
    "print": {
        "sequence_id": "0",
        "command": "pause",
        "param": "", // Always empty
    }
}
```

**Report**

See basic structure

## print.resume

Resumes a print. Sent with QoS of **1** for higher priority.

**Request**

```json
{
    "print": {
        "sequence_id": "0",
        "command": "resume",
        "param": "", // Always empty
    }
}
```

**Report**

See basic structure

## print.ams_change_filament

Tells printer to perform a filament change using AMS.

**Request**

```json
{
    "print": {
        "sequence_id": "0",
        "command": "ams_change_filament",
        "target": 0, // ID of filament tray
        "curr_temp": 0, // Old print temperature
        "tar_temp": 0 // New print temperature
    }
}
```

**Report**

TODO

## print.ams_user_setting

Changes the AMS settings of the given unit.

**Request**

```json
{
    "print": {
        "sequence_id": "0",
        "command": "ams_user_setting",
        "ams_id": 0, // Index of the AMS
        "startup_read_option": true, // Read RFID on startup
        "tray_read_option": true // Read RFID on insertion
    }
}
```

**Report**

TODO

## print.ams_filament_setting

Changes the setting of the given filament in the given AMS.

**Request**

```json
{
    "print": {
        "sequence_id": "0",
        "command": "ams_filament_setting",
        "ams_id": 0, // Index of the AMS
        "tray_id": 0, // Index of the tray
        "tray_info_idx": "", // Probably the setting ID of the filament profile
        "tray_color": "00112233", // Formatted as hex RRGGBBAA (alpha is always FF)
        "nozzle_temp_min": 0, // Minimum nozzle temp for filament (in C)
        "nozzle_temp_max": 0, // Maximum nozzle temp for filament (in C)
        "tray_type": "PLA" // Type of filament, such as "PLA" or "ABS"
    }
}
```

**Report**

TODO

## print.ams_control

Gives basic control commands for the AMS.

**Request**

```json
{
    "print": {
        "sequence_id": "0",
        "command": "ams_control",
        "param": "resume" // "resume", "reset" or "pause"
    }
}
```

**Report**

TODO

## print.print_speed

Set print speed to one of the 4 presets.

**Request**

```json
{
    "print": {
        "sequence_id": "0",
        "command": "print_speed",
        "param": "2" // Print speed level as a string
                     // 1 = silent
                     // 2 = standard
                     // 3 = sport
                     // 4 = ludicrous
    }
}
```

**Report**

See basic structure

## print.gcode_file

Print a gcode file. This takes absolute paths.

**Request**

```json
{
    "print": {
        "sequence_id": "0",
        "command": "gcode_file",
        "param": "filename.gcode" // Filename (on the printer's filesystem) to print
    }
}
```

**Report**

See basic structure

## print.gcode_line

Send raw GCode to the printer.

**Request**

```json
{
    "print": {
        "sequence_id": "0",
        "command": "gcode_line",
        "param": "M420", // Gcode to execute, can use \n for multiple lines
        "user_id": "1234" // Optional
    }
}
```

**Report**

See basic structure

## print.calibration

Starts calibration process.

**Note:** Some printers might need `gcode_file` with `/usr/etc/print/auto_cali_for_user.gcode` instead!

**Request**

```json
{
    "print": {
        "sequence_id": "0",
        "command": "calibration"
    }
}
```

**Report**

TODO

## print.unload_filament

Unloads the filament.

**Note:** Some printers might need `gcode_file` with `/usr/etc/print/filament_unload.gcode` instead!

**Request**

```json
{
    "print": {
        "sequence_id": "0",
        "command": "unload_filament"
    }
}
```

**Report**

```json
{
    // TODO
}
```

## system.ledctrl

Controls the LEDs of the printer.

**Request**

```json
{
    "system": {
        "sequence_id": "0",
        "command": "ledctrl",
        "led_node": "chamber_light", // Either "chamber_light" or "work_light"
        "led_mode": "on", // "on", "off" or "flashing"

        // The below effects are only used for "flashing" mode
        // but required to be present always
        "led_on_time": 500, // LED on time in ms
        "led_off_time": 500, // LED off time in ms
        "loop_times":  1, // How many times to loop
        "interval_time": 1000 // Looping interval
    }
}
```

**Report**

See basic structure

## camera.ipcam_record_set

Turns on or off creating a recording of prints.

**Request**

```json
{
    "camera": {
        "sequence_id": "0",
        "command": "ipcam_record_set",
        "control": "enable" // "enable" or "disable"
    }
}
```

**Report**

See basic structure

## camera.ipcam_timelapse

Turns on or off creating a timelapse of prints.

**Request**

```json
{
    "camera": {
        "sequence_id": "0",
        "command": "ipcam_timelapse",
        "control": "enable" // "enable" or "disable"
    }
}
```

**Report**

See basic structure


## xcam.xcam_control_set

Configures the XCam (camera AI features, including Micro LIDAR features).

**Request**

```json
{
    "camera": {
        "sequence_id": "0",
        "command": "xcam_control_set",
        "module_name": "first_layer_inspector", // "first_layer_inspector" or "spaghetti_detector"
        "control": true, // Enable the module
        "print_halt": false // Cause the module to halt the print on error
    }
}
```

**Report**

See basic structure

# Unsolicited (or semi-solicited) reports

## print.push_status

Reports printer status

```json
{
    "print": {
        "ams": {
            "ams": [],
            "ams_exist_bits": "0",
            "ams_new_detect_flag": false,
            "insert_flag": true,
            "power_on_flag": false,
            "tray_exist_bits": "0",
            "tray_is_bbl_bits": "0",
            "tray_now": "255",
            "tray_read_done_bits": "0",
            "tray_reading_bits": "0",
            "tray_tar": "255",
            "version": 0
        },
        "ams_rfid_status": 6,
        "ams_status": 0,
        "bed_target_temper": 25.0,
        "bed_temper": 25.0,
        "big_fan1_speed": "0",
        "big_fan2_speed": "0",
        "chamber_temper": 24.0,
        "command": "push_status",
        "cooling_fan_speed": "0",
        "fail_reason": "0",
        "force_upgrade": false,
        "gcode_file": "",
        "gcode_file_prepare_percent": "0",
        "gcode_start_time": "0",
        "gcode_state": "IDLE",
        "heatbreak_fan_speed": "0",
        "hms": [],
        "home_flag": 0,
        "hw_switch_state": 1,
        "ipcam": {
            "ipcam_dev": "1",
            "ipcam_record": "disable",
            "timelapse": "disable"
        },
        "lifecycle": "product",
        "lights_report": [
            {
                "mode": "on",
                "node": "chamber_light"
            },
            {
                "mode": "flashing",
                "node": "work_light"
            }
        ],
        "mc_percent": 0,
        "mc_print_error_code": "0",
        "mc_print_stage": "1",
        "mc_print_sub_stage": 0,
        "mc_remaining_time": 0,
        "mess_production_state": "active",
        "nozzle_target_temper": 25.0,
        "nozzle_temper": 25.0,
        "online": {
            "ahb": false,
            "rfid": false
        },
        "print_error": 0,
        "print_gcode_action": 0,
        "print_real_action": 0,
        "print_type": "",
        "profile_id": "",
        "project_id": "",
        "sdcard": true,
        "sequence_id": "2021",
        "spd_lvl": 2,
        "spd_mag": 100,
        "stg": [],
        "stg_cur": -1,
        "subtask_id": "",
        "subtask_name": "",
        "task_id": "",
        "upgrade_state": {
            "ahb_new_version_number": "",
            "ams_new_version_number": "",
            "consistency_request": false,
            "dis_state": 0,
            "err_code": 0,
            "force_upgrade": false,
            "message": "",
            "module": "null",
            "new_version_state": 2,
            "ota_new_version_number": "",
            "progress": "0",
            "sequence_id": 0,
            "status": "IDLE"
        },
        "upload": {
            "file_size": 0,
            "finish_size": 0,
            "message": "Good",
            "oss_url": "",
            "progress": 0,
            "sequence_id": "0903",
            "speed": 0,
            "status": "idle",
            "task_id": "",
            "time_remaining": 0,
            "trouble_id": ""
        },
        "wifi_signal": "-45dBm",
        "xcam": {
            "first_layer_inspector": true,
            "print_halt": false,
            "spaghetti_detector": true
        },
        "xcam_status": "0"
    }
}
```

## mc_print.push_info

Reports log lines of the printer. Can be requested with the `pushing.pushall` request.

```json
{
    "mc_print": {
        "command": "push_info",
        "param": "[LINK] GcodeLine (8) l=15 from 0600 ok: M106 P2 S255 \n\n",
        "sequence_id": "107"
    }
}
```
