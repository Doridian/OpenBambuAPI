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

---

# Undocumented Endpoints (Discovered via Bambu Handy APK Reverse Engineering)

> **Methodology:** These endpoints were extracted via a runtime memory dump of the Bambu Handy Android APK (Dart AOT, Dart SDK 3.8.1). String constants and URL path fragments were recovered from the Dart isolate heap in process memory. HTTP methods are inferred from path semantics (e.g., `GET` for reads, `POST` for mutations) — actual methods may differ. No request or response body schemas are available.

---

## User Service

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/user-service/general/config` | General app configuration |
| GET | `/v1/user-service/latest/app` | Latest app version check |
| GET | `/v1/user-service/latest/app2` | Latest app version check (v2) |
| GET | `/v1/user-service/my/firmwarebeta` | Beta firmware program enrollment status |
| POST | `/v1/user-service/my/identity/verify` | Identity verification |
| POST | `/v1/user-service/my/logout` | Logout current session |
| GET | `/v1/user-service/my/message/{id}` | Get specific message by ID |
| GET | `/v1/user-service/my/message/count` | Unread message count |
| GET | `/v1/user-service/my/message/device/taskstatus` | Device task status messages |
| GET | `/v1/user-service/my/message/latest` | Latest messages |
| POST | `/v1/user-service/my/message/read` | Mark messages as read |
| GET | `/v1/user-service/my/model/profile` | User model/printer profile |
| GET | `/v1/user-service/my/password/verifiedstatus` | Password verification status |
| POST | `/v1/user-service/my/password/verify` | Verify current password |
| GET | `/v1/user-service/my/profile` | User profile |
| GET | `/v1/user-service/my/rating` | User rating |
| GET | `/v1/user-service/my/rating/popup` | Rating popup trigger |
| GET | `/v1/user-service/my/task/{id}` | Get specific task by ID |
| GET | `/v1/user-service/my/task/printedplates` | Printed plates history |
| GET | `/v1/user-service/my/tfa` | Two-factor authentication settings |
| GET | `/v1/user-service/my/tfa/name` | TFA device name |
| GET | `/v1/user-service/my/tfas` | List all TFA devices |
| GET | `/v1/user-service/my/totp/secret` | TOTP secret for authenticator app setup |
| POST | `/v1/user-service/my/upload` | Upload file |
| POST | `/v1/user-service/user/consent` | User consent / GDPR acknowledgement |
| POST | `/v1/user-service/user/devicetoken` | Register device push notification token |
| POST | `/v1/user-service/user/resetpassword` | Initiate password reset |
| POST | `/v1/user-service/user/sendsmscode` | Send SMS verification code |
| POST | `/v1/user-service/user/signup` | User registration |
| POST | `/v1/user-service/user/signuporlogin` | Combined signup or login |
| POST | `/v1/user-service/user/tfa/login` | Login with two-factor authentication |

---

## IoT Service

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/iot-service/api/slicer2d/settings/bbl_material/{id}` | 2D slicer material settings by ID |
| GET | `/v1/iot-service/api/user/applications/{id}` | User applications by ID |
| GET | `/v1/iot-service2/api/user/device/file_download` | Device file download (note: iot-service**2**) |

---

## Design Service

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/design-service/contest/list` | Design contests list |
| GET | `/v1/design-service/design/{id}` | Get design details by ID |
| GET | `/v1/design-service/design/awarded` | Awarded designs |
| GET | `/v1/design-service/design/category` | Design categories |
| GET | `/v1/design-service/design/ids` | Get designs by IDs (batch) |
| POST | `/v1/design-service/draft/sliceerror` | Report slice error for a draft |
| GET | `/v1/design-service/favorites-collections/tab` | Favorites collection tabs |
| GET | `/v1/design-service/favorites-pinned` | Pinned favorites |
| GET | `/v1/design-service/favorites/{id}` | Get favorites collection by ID |
| GET | `/v1/design-service/favorites/designs/{id}` | Designs within a favorites collection |
| GET | `/v1/design-service/favorites/v2/list/{id}` | Favorites list v2 by ID |
| POST | `/v1/design-service/hiddendesigns/like` | Like hidden designs |
| GET | `/v1/design-service/instance/{id}` | Get design instance by ID |
| GET | `/v1/design-service/my/design/favoriteslist` | My favorited designs list |
| GET | `/v1/design-service/my/design/follow` | Designs from followed designers |
| GET | `/v1/design-service/my/design/history` | Design view history |
| GET | `/v1/design-service/my/design/like` | My liked designs |
| GET | `/v1/design-service/my/favorites` | My favorites collections |
| GET | `/v1/design-service/my/favorites/{id}` | Get specific favorites collection |
| GET | `/v1/design-service/my/favorites/crowdfunding/designs` | Crowdfunding favorited designs |
| GET | `/v1/design-service/my/favorites/like/invalid` | Invalid liked favorites |
| GET | `/v1/design-service/my/favorites/listlite` | Favorites list (lightweight) |
| POST | `/v1/design-service/my/favorites/v2/like` | Like favorites v2 |
| GET | `/v1/design-service/my/instance/{id}` | My design instance by ID |
| GET | `/v1/design-service/my/instance/published` | My published instances |
| GET | `/v1/design-service/my/instance2d/published` | My published 2D instances |
| GET | `/v1/design-service/my/preset/published` | My published presets |
| GET | `/v1/design-service/my/publisheddesigns` | My published designs |
| POST | `/v1/design-service/my/quick-boost-design` | Quick boost design |
| GET | `/v1/design-service/published/{id}` | Get published design by ID |
| GET | `/v1/design-service/publisheddesigns/{params}` | Published designs listing |

---

## Design User Service

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/design-user-service/countries` | Country list |
| GET | `/v1/design-user-service/device/names` | Device names mapping |
| GET | `/v1/design-user-service/filament/config` | Filament configuration |
| DELETE | `/v1/design-user-service/my/blacklist/{id}` | Remove from blacklist |
| GET | `/v1/design-user-service/my/blacklist` | Get blacklist |
| DELETE | `/v1/design-user-service/my/blocklist/{id}` | Remove from blocklist |
| GET | `/v1/design-user-service/my/blocklist` | Get blocklist |
| GET | `/v1/design-user-service/my/filament/v2` | My filaments v2 |
| POST | `/v1/design-user-service/my/filament/v2/ams/sync` | Sync AMS filaments |
| POST | `/v1/design-user-service/my/filament/v2/batch` | Batch filament operations |
| POST | `/v1/design-user-service/my/follow/{id}` | Follow or unfollow a user |
| GET | `/v1/design-user-service/my/follow/mutual` | Mutual follows |
| GET | `/v1/design-user-service/my/im/token` | Instant messaging token |
| POST | `/v1/design-user-service/my/makerworld/init` | Initialize MakerWorld profile |
| GET | `/v1/design-user-service/my/permission` | User permissions |
| GET | `/v1/design-user-service/my/printingexperience` | Printing experience data |
| GET | `/v1/design-user-service/my/process-files` | Process files |
| GET | `/v1/design-user-service/my/profile` | User profile (MakerWorld) |
| POST | `/v1/design-user-service/my/upload` | Upload file |
| GET | `/v1/design-user-service/user/{id}` | Get user profile by ID |
| GET | `/v1/design-user-service/user/profile/{id}` | Get user profile details |
| POST | `/v1/design-user-service/user/upload/picsearch` | Image search upload |

---

## Design Recommend Service

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/design-recommend-service/my/for-you` | Personalized design recommendations |

---

## Community Service

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/community-service/exclusive-designs` | Exclusive community designs |
| GET | `/v1/community-service/my/post` | My posts |
| GET | `/v1/community-service/my/post/comment` | Comments on my posts |
| GET | `/v1/community-service/my/post/following` | Posts from followed users |
| GET | `/v1/community-service/my/post/like` | My liked posts |
| POST | `/v1/community-service/post` | Create a post |
| GET | `/v1/community-service/post/{id}` | Get post by ID |
| GET | `/v1/community-service/post/for-you` | For-you post feed |
| GET | `/v1/community-service/post/search` | Search posts |
| GET | `/v1/community-service/tag/{id}` | Get tag by ID |
| GET | `/v1/community-service/tag/hot` | Hot / trending tags |
| GET | `/v1/community-service/tag/suggest` | Suggested tags |
| GET | `/v1/community-service/user/{id}` | Community user profile |
| POST | `/v1/community-service/vote/cast/{id}` | Cast vote on item |
| GET | `/v1/community-service/who-to-follow` | Suggested users to follow |

---

## Comment Service

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/comment-service/comment` | Create a comment |
| GET | `/v1/comment-service/comment/{id}` | Get or delete comment by ID |
| POST | `/v1/comment-service/commentandrating` | Submit comment and rating combined |
| POST | `/v1/comment-service/community/comment` | Create a community comment |
| GET | `/v1/comment-service/community/comment/{id}` | Get community comment by ID |
| POST | `/v1/comment-service/community/commentreply` | Reply to a community comment |
| GET | `/v1/comment-service/community/commentreply/{id}` | Get community comment reply |
| GET | `/v1/comment-service/community/rootcomment/{id}` | Get root community comment |
| GET | `/v1/comment-service/community/{id}` | Community item comments |
| POST | `/v1/comment-service/message` | Send direct message |
| GET | `/v1/comment-service/message/{id}` | Get message by ID |
| GET | `/v1/comment-service/messagesession/list` | Message sessions list |
| POST | `/v1/comment-service/messagesession/read` | Mark message session as read |
| GET | `/v1/comment-service/pinned/comment` | Pinned comments |
| GET | `/v1/comment-service/rating/{id}` | Get rating by ID |
| POST | `/v1/comment-service/rating/customize` | Submit custom rating |
| GET | `/v1/comment-service/rating/inst/{id}` | Rating for design instance |
| GET | `/v1/comment-service/rating/my` | My ratings |
| GET | `/v1/comment-service/rating/reply/{id}` | Rating reply by ID |
| GET | `/v1/comment-service/rating/reply/reply/{id}` | Reply to rating reply |
| GET | `/v1/comment-service/ratingreply/{id}` | Rating reply (alternate path) |

---

## IM Service

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/im-service/msg` | Send instant message |

---

## Search Service

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/search-service/cfg2` | Search configuration v2 |
| GET | `/v1/search-service/design/{id}` | Search design by ID |
| GET | `/v1/search-service/homepage/nav` | Homepage navigation config |
| GET | `/v1/search-service/recommand/youlike` | Recommended designs for you |
| GET | `/v1/search-service/search/user` | Search users |
| GET | `/v1/search-service/searchlist` | Search listing |
| GET | `/v1/search-service/select/all` | Select all search results |
| GET | `/v1/search-service/select/design/nav` | Design navigation search |
| GET | `/v1/search-service/select/design2` | Design search v2 |
| GET | `/v1/search-service/select/favorites` | Search favorites |
| GET | `/v1/search-service/select/user/top` | Top users |
| GET | `/v1/search-service/suggest` | Search suggestions |
| GET | `/v1/search-service/suggest2` | Search suggestions v2 |

---

## Hub Service

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/hub-service/academy/client/course/categories/tree/app` | Academy course category tree |

---

## Task Service

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/task-service/task/{id}` | Get task by ID |
| GET | `/v1/task-service/user/taskv2` | User tasks v2 |
| GET | `/v1/task-service/user/taskv2/displayPopup/{id}` | Task popup display |
| GET | `/v1/task-service/usertask/display/beginnerGuide/{id}` | Beginner guide display |

---

## Operation Service

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/operation-service/apphomepage` | App homepage content |
| GET | `/v1/operation-service/bbl/activity` | BBL activities and events |
| GET | `/v1/operation-service/configuration` | App configuration |
| GET | `/v1/operation-service/contest/{id}` | Contest details by ID |
| GET | `/v1/operation-service/contest/awardlist` | Contest award list |
| GET | `/v1/operation-service/contest/preview` | Contest preview |
| GET | `/v1/operation-service/favorites-collections/cfg` | Favorites collections config |
| GET | `/v1/operation-service/official/guide/{id}` | Official guide by ID |
| GET | `/v1/operation-service/official/guides` | Official guides list |
| GET | `/v1/operation-service/popularcreators` | Popular creators |
| GET | `/v1/operation-service/support/list` | Support resources list |
| POST | `/v1/operation-service/userContestDesign` | User contest design submission |

---

## Point Service

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/point-service/boost/boostdesign` | Boost a design |
| GET | `/v1/point-service/boost/boostingright` | Check boosting rights |
| POST | `/v1/point-service/boost/quickboostdesign` | Quick boost a design |
| GET | `/v1/point-service/giftcard/selfBuiltStatus` | Gift card self-built status |
| GET | `/v1/point-service/point-bill/my` | My points bill / transaction history |
| GET | `/v1/point-service/product/listTaskOptionsV2` | Task options for earning points v2 |
| GET | `/v1/point-service/product/pointShops` | Points shops listing |
| GET | `/v1/point-service/product/products` | Products listing |
| POST | `/v1/point-service/redeem` | Redeem points |
| GET | `/v1/point-service/redeem/detail` | Redemption details |
| GET | `/v1/point-service/redeem/history` | Redemption history |
| POST | `/v1/point-service/redeem/task/multi` | Multi-task redemption |
| POST | `/v1/point-service/redeemPointByTask` | Redeem points by completing a task |
| POST | `/v1/point-service/redeemProductByTask` | Redeem product by completing a task |
| GET | `/v1/point-service/summary` | Points balance summary |

---

## Report Service

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/report-service/community/report` | Report community content |
| GET | `/v1/report-service/my/appeal` | My appeals |
| GET | `/v1/report-service/my/appealed` | Appealed reports |
| GET | `/v1/report-service/my/claim` | My IP claims |
| GET | `/v1/report-service/my/defense` | My defenses |
| POST | `/v1/report-service/my/ip-infringement-report` | Submit IP infringement report |
| GET | `/v1/report-service/my/report` | My report |
| GET | `/v1/report-service/my/reports` | My reports list |
| GET | `/v1/report-service/report/classification` | Report classifications |

---

## Aftersale Service

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/aftersale-service/makerworld/classification` | MakerWorld support ticket classifications |
| POST | `/v1/aftersale-service/makerworld/create` | Create MakerWorld support ticket |
| GET | `/v1/aftersale-service/makerworld/list` | MakerWorld support tickets list |
| GET | `/v1/aftersale-service/makerworld/rateurl/{id}` | Rate MakerWorld support URL |
| GET | `/v1/aftersale-service/makerworld/replylanguage` | Reply language preference |
| GET | `/v1/aftersale-service/makerworld/totalunreadcount` | Total unread MakerWorld ticket count |
| GET | `/v1/aftersale-service/makerworld/trouble/{id}` | Get MakerWorld support ticket by ID |
| GET | `/v1/aftersale-service/robot/ai/key/list` | AI support key list |
| GET | `/v1/aftersale-service/trouble/check/snvalid` | Validate printer serial number |
| POST | `/v1/aftersale-service/trouble/classification/ai` | AI-assisted trouble classification |
| GET | `/v1/aftersale-service/trouble/classificationv2` | Trouble classification v2 |
| POST | `/v1/aftersale-service/trouble/create` | Create trouble ticket |
| DELETE | `/v1/aftersale-service/trouble/draft/delete` | Delete draft ticket |
| POST | `/v1/aftersale-service/trouble/draft/save` | Save draft ticket |
| GET | `/v1/aftersale-service/trouble/hmscode` | HMS error code lookup |
| GET | `/v1/aftersale-service/trouble/list` | Trouble tickets list |
| GET | `/v1/aftersale-service/trouble/material` | Material-related trouble info |
| GET | `/v1/aftersale-service/trouble/model` | Model-related trouble info |
| GET | `/v1/aftersale-service/trouble/rateurl/{id}` | Rate trouble ticket URL |
| GET | `/v1/aftersale-service/trouble/recentlycommoninfo` | Recently common trouble info |
| GET | `/v1/aftersale-service/trouble/region` | Region selection |
| GET | `/v1/aftersale-service/trouble/totalunreadcount` | Total unread trouble ticket count |
| GET | `/v1/aftersale-service/trouble/trouble/{id}` | Get trouble ticket details by ID |

---

# Infrastructure

> Discovered via Bambu Handy APK runtime memory dump.

## API Environments

| Environment | Base URL |
|-------------|----------|
| Production | `https://api.bambulab.com/v1/` |
| Pre-production (US) | `https://api-pre-us.bambulab.net/v1/` |
| Pre-production | `https://api-pre.bambulab.net/v1/` |
| QA | `https://api-qa.bambulab.net/v1/` |
| Dev | `https://api-dev.bambulab.net/v1/` |
| Stress testing | `https://api-stress.bambulab.net/v1/` |

## MQTT Brokers

| Broker | Notes |
|--------|-------|
| `cn.mqtt.bambulab.com` | China region |
| `us.mqtt.bambulab.com` | US region |
| `mqtt.bambu-lab.com` | Legacy / global |
| `stress-us.mqtt.bambu-lab.com` | Stress testing |

### MQTT Log Topics

```
/logs/mqtt/{deviceId}
/logs/mqtt/device_ids
/logs/mqtt/status/{deviceId}
```

## Internal Portals

| Host | Purpose |
|------|---------|
| `portal-dev.bambulab.net` | Developer portal |
| `portal-pre.bambulab.net` | Pre-production portal |
| `portal-qa.bambulab.net` | QA portal |
| `makerhub-dev.bambulab.net` | MakerWorld hub dev |
| `makerhub-pre.bambulab.net` | MakerWorld hub pre-production |
| `makerhub-pre-us.bambulab.net` | MakerWorld hub pre-production (US) |
| `makerhub-qa.bambulab.net` | MakerWorld hub QA |

## Support Domains

| Domain | Notes |
|--------|-------|
| `support.bambulab.com` | Production (global) |
| `support.bambulab.cn` | Production (China) |
| `pre-support.bambulab.net` | Pre-production |
| `pre-support-us.bambulab.net` | Pre-production (US) |
| `test-support.bambulab.net` | Test environment |

## Store Domains

| Domain | Region |
|--------|--------|
| `us.store.bambulab.com` | United States |
| `eu.store.bambulab.com` | Europe |
| `uk.store.bambulab.com` | United Kingdom |
| `ca.store.bambulab.com` | Canada |
| `au.store.bambulab.com` | Australia |
| `jp.store.bambulab.com` | Japan |
| `asia.store.bambulab.com` | Asia |
| `test2.store.bambulab.com` | Test / staging |

## Feature Flags and Telemetry

| Path | Description |
|------|-------------|
| `/api/client-sdk/toggles` | Feature flag toggles (Unleash-compatible) |
| `/api/events` | Client event tracking |

## TUTK Camera Protocol

The Bambu Handy app uses ThroughTek Kalay (TUTK) for P2P camera streaming to printers. Key details:

| Component | Notes |
|-----------|-------|
| SDK Libraries | `libIOTCAPIs`, `libAVAPIs`, `libTUTKGlobalAPIs` |
| Connection | `IOTC_Connect_ByUID_Parallel`, `IOTC_Connect_ByUIDEx` |
| Auth Modes | `AV_AUTH_PASSWORD`, `AV_AUTH_TOKEN`, `AV_SECURITY_DTLS` |
| Data Modes | `IOTC_DATA_TRANSMIT_INTEGRITY_MODE`, `IOTC_DATA_TRANSMIT_COMPATIBILITY_MODE`, `IOTC_DATA_TRANSMIT_ADAPTATION_MODE` |
| Region Config | `TUTK_SDK_Set_Region` |
