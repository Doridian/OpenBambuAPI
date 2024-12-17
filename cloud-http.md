# Basics

## URL

The API is available at a base path of `https://api.bambulab.com`. All URLs below are relative to this.

## Authentication

All requests (except to the token refresh endpoint) must be made by presenting an `Authorization` header in the form of `Bearer {ACCESS_TOKEN}`.

## Login and get a token

## POST https://api.bambulab.com/v1/user-service/user/login

**Request**

Either login with password OR verification code, not both
```json
{
    "account": "<EMAIL>",
    "password":"<PASSWORD>",
    "code": "<VERIFICATION-CODE>",
}
```

**Response**

Here you grab the `accessToken` and `refreshToken` from the body of the response. They're usually valid for about 3 months.
```json
{
	"accessToken": "[REMOVED]",
	"refreshToken": "[REMOVED]", // same as token
	"loginType": "", // if empty there should be token, if 'verifyCode' you'll need to use verification code to login
	"expiresIn": 7776000, // ~ 3 Months in seconds
	... // and a few other unimportant stuff
}
```

## Requests

Request bodies must be empty for GET requests, and otherwise valid JSON

## Responses

Error responses tend to follow the following format. As do success messages for **/v1/iot-service/...**
```json
{
	"message": "success", // "success" on success, otherwise error message, may be missing
	"code": null, // Error code, integer on error
	"error": null, // Error name/type

	// If success, other map entries may be present here
}

```

# URLs

## GET /v1/user-service/my/messages

Returns list of messages, looks like a pretty bare Elasticsearch response.

Can take the optional query parameters `type`, `after` and `limit`.

**Response**
```json
{
	"hits": [
		{
			"id": 0, // [REMOVED]
			"type": 6,
			"design": null,
			"comment": null,
			"taskMessage": {
				"id": 1, // [REMOVED]
				"title": "Untitled",
				"cover": "https://bbl-us-public.oss-us-west-1.aliyuncs.com/[REMOVED]",
				"status": 2,
				"deviceId": "[REMOVED]"
			},
			"from": {
				"uid": 2, // [REMOVED]
				"name": "Doridian",
				"avatar": "https://bbl-us-public.oss-us-west-1.aliyuncs.com/avatar/[REMOVED]",
				"fanCount": 0,
				"followCount": 0,
				"likeCount": 0,
				"isFollowed": false
			},
			"createTime": "2022-11-22T02:54:12Z"
		},
        ...
    ]
}
```

## GET /v1/user-service/my/tasks

Returns list of tasks, looks like a pretty bare Elasticsearch response.

Can take the optional query parameters `deviceId`, `after` and `limit`.

**Response**
```json
{
	"total": 5,
	"hits": [
		{
			"id": 0, // [REMOVED]
			"designId": 0,
			"modelId": "[REMOVED]",
			"title": "Untitled",
			"cover": "https://bbl-us-public.oss-us-west-1.aliyuncs.com/[REMOVED]",
			"status": 2,
			"feedbackStatus": 0,
			"startTime": "2022-11-22T01:58:10Z",
			"endTime": "2022-11-22T02:54:12Z", // if endTime is within a minute of startTime, that means the file is currently printing
			"weight": 12.6,
			"costTime": 3348, // how long the print will take in seconds
			"profileId": 0, // [REMOVED]
			"plateIndex": 1,
			"deviceId": "[REMOVED]",
			"amsDetailMapping": [],
			"mode": "cloud_file"
		},
        ...
    ]
}
```

## POST /v1/user-service/my/task

Creates a task, expects a task object (see above) to be passed via the body.

## GET /v1/user-service/my/ticket/{TICKET_ID}

Returns a ticket, probably means support tickets. Don't have any to test.

## POST /v1/user-service/user/refreshtoken

> [!CAUTION]
> This endpoint will only return 401 responses now. The refresh tokens are also equal to the access tokens in all known cases, and have the same validity as well. That makes this endpoint **practically useless**

Send a valid `refreshToken` and get new tokens with new expiration times.

**Request**
```json
{
	"refreshToken": "{REFRESH_TOKEN}"
}
```

**Response**
```json
{
	"accessToken": "[REMOVED]",
	"refreshToken": "[REMOVED]",
	"expiresIn": 29501294,
	"refreshExpiresIn": 29501294
}
```

## GET /v1/design-user-service/my/preference

Fetches your user account preferences and information. Also is a mirror for `https://makerworld.com/api/v1/design-user-service/my/preference`

Useful for numeric `uid`, which when prefixed with `u_` acts as your cloud mqtt username, as this is no longer provided within access tokens.

**Response**
```json
{
    "uid": 0000000000, // [REMOVED]
    "name": "name", // [REMOVED]
    "handle": "handle", // [REMOVED]
    "avatar": "url", // [REMOVED]
    "bio": "",
    "links": [
        "url1", // [REMOVED]
        "url2" // [REMOVED]
    ],
    "backgroundUrl": "url", // [REMOVED]
    ... // various unimportant account settings and values, all 0 or 1 for values
}
```

## GET /v1/iot-service/api/slicer/resource

Returns a bunch of resources, downloadable things for the slicer.

Takes optional query arguments in the form of `type=version` to check for a type at that version. This is used for downloading the networking and camera plugins.

Known types (with example version) are: 
- `slicer/plugins/cloud=01.01.00.00`

**Response**
```json
{
	"message": "success",
	"code": null,
	"error": null,
	"software": {
		"type": null,
		"version": "01.03.00.25",
		"description": "[Improvements]\n1. Show the print sequence in label when printing in by-object sequence\n\n[Bugs Fixed]\n1. Fixed a possible collision issue when printing in by-object sequence\n2. Fixed an empty layer issue after adding modifier\n3. Fixed an issue where \"Can't find my device\" link does not work on macOS\n4. Fixed a crash issue after entering Assembly View\n5. Fixed an issue where there may be some unexpected color lines generated in multi-color model\n6. Fixed a crash issue when performing a mandatory firmware updating\n7. Fixed a slicing performance issue when there are more than 10 colors in the same layer",
		"url": "https://upgrade-file.bambulab.com/studio/software/01.03.00.25/Bambu_Studio_win-v01.03.00.25.exe",
		"force_update": false
	},
	"guide": null,
	"resources": [
		{
			"type": "slicer/plugins/cloud",
			"version": "01.01.00.11",
			"description": "",
			"url": "https://upgrade-file.bambulab.com/studio/plugins/01.01.00.11/win_01.01.00.11.zip",
			"force_update": false
		}
	]
}
```

## GET /v1/iot-service/api/slicer/setting?version={SLICER_VERSION}

Returns a list of possible slicer profiles (`print`, `printer` and `material`) to query.

**Response**
```json
{
	"message": "success",
	"code": null,
	"error": null,
	"print": {
		"public": [
			{
				"setting_id": "GP001",
				"version": "01.03.00.13",
				"name": "0.08mm Extra Fine @BBL X1C",
				"nickname": null,
				"filament_id": null
			},
			{
				"setting_id": "GP002",
				"version": "01.03.00.13",
				"name": "0.12mm Fine @BBL X1C",
				"nickname": null,
				"filament_id": null
			},
            ...
		],
		"private": []
	},
	"printer": {
		"public": [
			{
				"setting_id": "GM001",
				"version": "01.03.00.13",
				"name": "Bambu Lab X1 Carbon 0.4 nozzle",
				"nickname": null,
				"filament_id": null
			},
			{
				"setting_id": "GM003",
				"version": "01.03.00.13",
				"name": "Bambu Lab X1 0.4 nozzle",
				"nickname": null,
				"filament_id": null
			},
            ...
		],
		"private": []
	},
	"filament": {
		"public": [
			{
				"setting_id": "GFSB98",
				"version": "01.03.00.13",
				"name": "Generic ASA",
				"nickname": null,
				"filament_id": "GFB98"
			},
			{
				"setting_id": "GFSC99_00",
				"version": "01.03.00.13",
				"name": "Generic PC @0.2 nozzle",
				"nickname": null,
				"filament_id": "GFC99"
			},
			{
				"setting_id": "GFSC99",
				"version": "01.03.00.13",
				"name": "Generic PC",
				"nickname": null,
				"filament_id": "GFC99"
			},
            ...
		],
		"private": [
			{
				"setting_id": "[REMOVED]",
				"version": "1.3.0.13",
				"name": "PolyLite ASA",
				"nickname": null,
				"filament_id": null
			},
            ...
		]
	}
}
```

## GET /v1/iot-service/api/slicer/setting/{SETTING_ID}

Gets the full data of a slicer setting by its id.

**Response**
```json
{
	"message": "success",
	"code": null,
	"error": null,
	"public": true,
	"version": "01.00.03.08",
	"type": "print",
	"name": "0.12mm Fine @BBL X1C",
	"nickname": null,
	"base_id": null,
	"setting": {
		"from": "system",
		"name": "0.12mm Fine @BBL X1C",
		"type": "process",
		"version": "01.00.03.08",
		"inherits": "fdm_process_bbl_0.12",
		"model_id": [
			"BL-P001",
			"BL-P002"
		],
		...
		"wipe_tower_no_sparse_layers": "0",
		"support_base_pattern_spacing": "2.5",
		"support_interface_top_layers": "2",
		"compatible_printers_condition": "",
		"support_interface_loop_pattern": "0",
		"support_interface_bottom_layers": "2",
		"internal_solid_infill_line_width": "0.45"
	},
	"filament_id": null
}
```

## GET /v1/iot-service/api/user/bind

This lists devices "bound" to the current user. As in, all your devices.

**Response**
```json
{
	"message": "success",
	"code": null,
	"error": null,
	"devices": [
		{
			"dev_id": "[REMOVED]",
			"name": "3DP-00M-000",
			"online": true,
			"print_status": "SUCCESS",
			"dev_model_name": "BL-P001",
			"dev_product_name": "X1 Carbon",
			"dev_access_code": "[REMOVED]\n"
		}
	]
}
```

## PATCH /v1/iot-service/api/user/device/info

This is to update device info. Likely only the name.

**Request**
```json
{
	"dev_id": "{DEVICE_ID}",
	...
}
```

**Response**
```json
{
	"message": "success",
	"code": null,
	"error": null
}
```

## GET /v1/iot-service/api/user/device/version?dev_id={DEVICE_ID}

Queries information about firmware version and updates for a device.

**Response**
```json
{
	"message": "success",
	"code": null,
	"error": null,
	"devices": [
		{
			"dev_id": "00M00A280102436",
			"version": "01.01.01.00",
			"firmware": [
				{
					"version": "01.01.01.00",
					"force_update": false,
					"url": "https://upgrade-file.bambulab.com/device/BL-P001/01.01.01.00/product/ota-v01.01.01.00-20221012091123.json.sig",
					"description": "## version ota01.01.01.00：\n### 【Improvements】\n1. [System] Differentiated between SD card not inserted prompts and SD card not formatted prompts.\n2. [System] Added support for Bambu Handy to browse more than 20 timelapse videos.\n3. [System] Updated some HMS contents.\n4. [Algorithm] Added support for automatic micro lidar calibration when micro lidar parameter drift is detected.\n5. [AMS] Added support for pausing printing and providing a popup message when filament or spools are stuck when printing with an AMS. After solving the issue manually, printing can be resumed by clicking the \"Retry\" button.\n### 【Bugs fixed】\n1. [System] Fixed the issue where the screen flashes a pop-up without content when logs are being uploaded through Bambu Handy.\n2. [Algorithm] Fixed the ota01.01.00.00 issue where the maximum acceleration was set to 5000mm/s² after the first layer inspection function, which caused the estimated print time to be inaccurate. This version returns the original print quality and acceleration values as ota01.00.00.00.\n3. [Algorithm] Fixed the issue where timelapse exposure may be abnormal and the first several frames may be dropped on some printers.\n4. [AMS] Reduced the probability of reading RFID again when AMS is idle."
				}
			],
			"ams": []
		}
	]
}
```

## GET /v1/iot-service/api/user/notification?action={ACTION}&ticket={TICKET_ID}

`ACTION` must be either `upload` or `import_mesh`

## GET /v1/iot-service/api/user/print

This accepts the optional query parameter `force`, which the slicer always sets to `true`.

The response is the current status of the printer.

**Response**
```json
{
	"message": "success",
	"code": null,
	"error": null,
	"devices": [
		{
			"dev_id": "[REMOVED]",
			"dev_name": "3DP-00M-000",
			"dev_model_name": "BL-P001",
			"dev_product_name": "X1 Carbon",
			"dev_online": true,
			"dev_access_code": "[REMOVED]\n",
			"task_id": null,
			"task_name": null,
			"task_status": null,
			"model_id": null,
			"project_id": null,
			"profile_id": null,
			"start_time": null,
			"prediction": null,
			"progress": null,
			"thumbnail": null
		}
	]
}
```

## GET /v1/iot-service/api/user/profile/{PROFILE_ID}?model_id={MODEL_ID}

Queries the details of a profile for a certain model, likely for profile deviations?

```json
{
	"message": "success",
	"code": null,
	"error": null,
	"profile_id": "[REMOVED]",
	"model_id": "[REMOVED]",
	"status": "ACTIVE",
	"name": "Untitled",
	"content": null,
	"create_time": "2022-11-22 09:58:04",
	"update_time": "2022-11-22 09:58:09",
	"context": {
		"compatibility": {
			"dev_model_name": "BL-P001",
			"dev_product_name": "X1 Carbon",
			"nozzle_diameter": 0.4
		},
		"pictures": null,
		"configs": [
			{
				"name": "project_settings.config",
				"dir": "Metadata",
				"url": "https://model-file.bambulab.com/[REMOVED]"
			},
			{
				"name": "model_settings.config",
				"dir": "Metadata",
				"url": "https://model-file.bambulab.com/[REMOVED]"
			},
			{
				"name": "slice_info.config",
				"dir": "Metadata",
				"url": "https://model-file.bambulab.com/[REMOVED]"
			}
		],
		"plates": [
			{
				"index": 1,
				"thumbnail": {
					"name": "plate_1.png",
					"dir": "Metadata",
					"url": "https://model-file.bambulab.com/[REMOVED]"
				},
				"prediction": 3348,
				"weight": 12.6,
				"gcode": {
					"name": null,
					"dir": null,
					"url": null
				},
				"filaments": [
					{
						"id": "1",
						"type": "PLA",
						"color": "#00AE42",
						"used_m": "4.16",
						"used_g": "12.60"
					}
				]
			}
		],
		"materials": [
			{
				"color": "00AE42",
				"material": "PLA"
			}
		],
		"auxiliary_pictures": [],
		"auxiliary_bom": [],
		"auxiliary_guide": [],
		"auxiliary_other": []
	},
	"filename": "[REMOVED]",
	"url": "https://model-file.bambulab.com/[REMOVED]",
	"md5": "[REMOVED]",
	"keystore_xml": null
}
```

## GET /v1/iot-service/api/user/project

Queries a list of projects for the current user.

**Response**
```json
{
	"message": "success",
	"code": null,
	"error": null,
	"projects": [
		{
			"project_id": "[REMOVED]",
			"user_id": "[REMOVED]",
			"model_id": "[REMOVED]",
			"status": "ACTIVE",
			"name": "Untitled",
			"content": "null",
			"create_time": "2022-11-22 09:58:04",
			"update_time": "2022-11-22 09:58:10"
		},
		...
	]
}
```

## GET /v1/iot-service/api/user/project/{PROJECT_ID}

Gets full details about a single project.

**Response**
```json
{
	"message": "success",
	"code": null,
	"error": null,
	"project_id": "[REMOVED]",
	"user_id": "[REMOVED]",
	"model_id": "[REMOVED]",
	"status": "ACTIVE",
	"name": "Untitled",
	"content": null,
	"create_time": "2022-11-22 09:58:04",
	"update_time": "2022-11-22 09:58:10",
	"profiles": [
		{
			"profile_id": "[REMOVED]",
			"model_id": "[REMOVED]",
			"status": "ACTIVE",
			"name": "Untitled",
			"content": "{}",
			"create_time": "2022-11-22 09:58:04",
			"update_time": "2022-11-22 09:58:09",
			"context": {
				"compatibility": {
					"dev_model_name": "BL-P001",
					"dev_product_name": "X1 Carbon",
					"nozzle_diameter": 0.4
				},
				"pictures": null,
				"configs": [
					{
						"name": "project_settings.config",
						"dir": "Metadata",
						"url": "https://model-file.bambulab.com/[REMOVED]"
					},
					{
						"name": "model_settings.config",
						"dir": "Metadata",
						"url": "https://model-file.bambulab.com/[REMOVED]"
					},
					{
						"name": "slice_info.config",
						"dir": "Metadata",
						"url": "https://model-file.bambulab.com/[REMOVED]"
					}
				],
				"plates": [
					{
						"index": 1,
						"thumbnail": {
							"name": "plate_1.png",
							"dir": "Metadata",
							"url": "https://model-file.bambulab.com/[REMOVED]"
						},
						"prediction": 3348,
						"weight": 12.6,
						"gcode": {
							"name": null,
							"dir": null,
							"url": null
						},
						"filaments": [
							{
								"id": "1",
								"type": "PLA",
								"color": "#00AE42",
								"used_m": "4.16",
								"used_g": "12.60"
							}
						]
					}
				],
				"materials": [
					{
						"color": "00AE42",
						"material": "PLA"
					}
				],
				"auxiliary_pictures": [],
				"auxiliary_bom": [],
				"auxiliary_guide": [],
				"auxiliary_other": []
			}
		}
	],
	"download_url": null,
	"download_md5": null,
	"keystore_xml": null,
	"upload_url": null,
	"upload_ticket": null
}
```

## GET /v1/iot-service/api/user/task/{TASK_ID}

Gets information about a task. So far this has always yielded a 403 even on my own tasks.

**Response**
```json
{
	"message": "permission denied",
	"code": 8,
	"error": "Resource forbidden",
	"parent": null,
	"model_id": null,
	"project_id": null,
	"profile_id": null,
	"status": null,
	"name": null,
	"content": null,
	"context": null,
	"create_time": null,
	"update_time": null,
	"sub_task": null,
	"subtask": null,
	"est": null,
	"url": null,
	"md5": null
}
```

## POST /v1/iot-service/api/user/ttcode

Gets the TTCode for the printer. This is used for authentication to the webcam stream.

**Request**
```json
{
	"dev_id": "{DEVICE_ID}"
}
```

**Response**
```json
{
	"message": "success",
	"code": null,
	"error": null,
	"ttcode": "[REMOVED]",
	"passwd": "[REMOVED]",
	"authkey": "[REMOVED]"
}
```
