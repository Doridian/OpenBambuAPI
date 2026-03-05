# MakerWorld / Design Services API

> Reverse-engineered from Bambu Handy app (v3.x) via live traffic capture  
> These endpoints are **not documented** in the original OpenBambuAPI  
> Base URL: `https://api.bambulab.com/v1`  
> Also accessible via: `https://makerworld.com/api/v1` (Cloudflare-protected)

## Overview

MakerWorld is Bambu Lab's 3D model sharing platform. The app communicates with **8 microservices** for content discovery, social features, and model management. All endpoints require Bearer JWT authentication.

---

## Design Service (`/design-service/`)

3D model management — designs (models), instances (print profiles), favorites, downloads.

### GET /v1/design-service/design/{designId}

Get full design details including title, creator, instances, tags, images.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `designId` | path | yes | Numeric design ID |
| `trafficSource` | query | no | Analytics source: `browse`, `recommend`, `search` |
| `visitHistory` | query | no | `true` to log page visit |

**Response includes:**
- `id` — design ID
- `title` — design title
- `designCreator` — `{ name, uid, avatar }`
- `instances[]` — array of print instances
  - `id` — instance ID (needed for download)
  - `isDefault` — boolean
  - `title` — instance name
  - `plates[]` — plate configurations
- `tags[]` — category tags
- `likeCount`, `downloadCount`, `commentCount`
- `images[]` — gallery image URLs

```bash
curl -s "https://api.bambulab.com/v1/design-service/design/2416782?trafficSource=browse&visitHistory=true" \
  -H "Authorization: Bearer $TOKEN"
```

### GET /v1/design-service/design/{designId}/remixed

Get designs that are remixes of a given design.

### POST /v1/design-service/design/{designId}/like

Like/unlike a design (toggle). No request body needed.

### GET /v1/design-service/instance/{instanceId}/f3mf

Download a 3MF file for a design instance.

| Parameter | Type | Description |
|-----------|------|-------------|
| `instanceId` | path | Instance ID from design details |
| `type` | query | `preview` (metadata only) or `download` (full 3MF binary) |

**Download workflow:**
1. Fetch design details → get default instance ID
2. Call with `type=download` → receive 3MF binary

```bash
# Preview (metadata)
curl -s "https://api.bambulab.com/v1/design-service/instance/2650240/f3mf?type=preview" \
  -H "Authorization: Bearer $TOKEN"

# Download (full 3MF file)
curl -sOJ "https://api.bambulab.com/v1/design-service/instance/2650240/f3mf?type=download" \
  -H "Authorization: Bearer $TOKEN"
```

### GET /v1/design-service/favorites/designs/{userId}

Get a user's favorited designs.

| Parameter | Type | Description |
|-----------|------|-------------|
| `userId` | path | Numeric user ID |
| `offset` | query | Pagination offset |
| `limit` | query | Page size (default 20) |

### GET /v1/design-service/my/design/favoriteslist

Check if specific designs are in the current user's favorites.

| Parameter | Type | Description |
|-----------|------|-------------|
| `designId` | query | Design ID to check |

### GET /v1/design-service/my/design/like

Get designs the current user has liked. Supports `offset` and `limit` query params.

### GET /v1/design-service/my/favorites/listlite

Lightweight endpoint returning only IDs of all favorited designs.

### GET /v1/design-service/draft/sliceerror

Get draft designs that had slicing errors.

---

## Design User Service (`/design-user-service/`)

Extends the existing `/design-user-service/my/preference` endpoint (already documented in [cloud-http.md](cloud-http.md)).

### GET /v1/design-user-service/my/profile

Get the current user's MakerWorld profile (distinct from `/my/preference`).

| Parameter | Type | Description |
|-----------|------|-------------|
| `immediacy` | query | `true` for non-cached response |

### GET /v1/design-user-service/my/follow/mutual

Get mutual follows (users who follow you and you follow back).

### GET /v1/design-user-service/my/permission

Check user permissions.

| Parameter | Type | Description |
|-----------|------|-------------|
| `permType` | query | `0` = general permissions, `6` = upload permission |

---

## Design Recommend Service (`/design-recommend-service/`)

### GET /v1/design-recommend-service/my/for-you

Personalized design recommendations ("For You" feed).

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | query | Number of results (default 20) |
| `offset` | query | Pagination offset |
| `seed` | query | Randomization seed (`0` for fresh results) |
| `acceptTypes` | query | Comma-separated content type IDs |

**Content type IDs:**
| ID | Type |
|----|------|
| `0` | 3D Model |
| `2` | Remix |
| `3` | Article |
| `5` | Collection |
| `6` | Tutorial |

```bash
curl -s "https://api.bambulab.com/v1/design-recommend-service/my/for-you?limit=20&offset=0&seed=0&acceptTypes=0,2,5,6,3" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Comment Service (`/comment-service/`)

Comments, ratings, and direct messaging for designs.

### GET /v1/comment-service/commentandrating

Get comments and ratings for a design.

| Parameter | Type | Description |
|-----------|------|-------------|
| `designId` | query | Design ID |
| `offset` | query | Pagination offset |
| `limit` | query | Page size (default 20) |
| `type` | query | `0` = all |
| `sort` | query | `0` = newest first |

```bash
curl -s "https://api.bambulab.com/v1/comment-service/commentandrating?designId=2416782&offset=0&limit=20&type=0&sort=0" \
  -H "Authorization: Bearer $TOKEN"
```

### GET /v1/comment-service/comment/{commentId}/detail

Get a single comment with full details.

### GET /v1/comment-service/comment/{commentId}/reply

Get replies to a comment.

| Parameter | Type | Description |
|-----------|------|-------------|
| `commentId` | path | Parent comment ID |
| `limit` | query | Max replies (default 10) |
| `after` | query | Reply ID cursor for forward pagination |
| `msgCommentReplyId` | query | Load context around a specific reply |

### POST /v1/comment-service/comment/{commentId}/like

Like a comment (toggle).

### POST /v1/comment-service/comment/{commentId}/reply

Post a reply to a comment.

### GET /v1/comment-service/rating/inst/{instanceId}

Get rating data for a specific design instance.

### GET /v1/comment-service/messagesession/list

Get message sessions (direct messages inbox).

| Parameter | Type | Description |
|-----------|------|-------------|
| `userSelect` | query | `all` or specific filter |
| `typeSelect` | query | `all` or specific filter |
| `projectScope` | query | `0` = general, `2` = MakerWorld |
| `offset` | query | Pagination offset |
| `limit` | query | Page size |

---

## Search Service (`/search-service/`)

Design discovery, navigation categories, trending, and related content.

### GET /v1/search-service/homepage/nav

Get homepage navigation structure (categories, featured sections).

### GET /v1/search-service/recommand/youlike

Get "recommended for you" designs.

> **Note:** The API has a typo — it's `recommand`, not `recommend`.

### GET /v1/search-service/select/design/nav

Browse designs by navigation category.

| Parameter | Type | Description |
|-----------|------|-------------|
| `navKey` | query | Category key (see table below) |
| `offset` | query | Pagination offset |
| `limit` | query | Page size (default 20) |

**Known category keys:**

| navKey | Category |
|--------|----------|
| `Trending` | Trending designs |
| `category_400` | Toys & Games |
| `category_800` | Home & Living |

```bash
# Trending designs
curl -s "https://api.bambulab.com/v1/search-service/select/design/nav?navKey=Trending&offset=0&limit=20" \
  -H "Authorization: Bearer $TOKEN"
```

### GET /v1/search-service/design/{designId}/relate

Get designs related to a specific design.

| Parameter | Type | Description |
|-----------|------|-------------|
| `designId` | path | Design ID |
| `offset` | query | Pagination offset |
| `limit` | query | Page size |
| `scene` | query | Relation scene (`1` = similar) |

---

## Operation Service (`/operation-service/`)

App-level configuration and dynamic content.

### GET /v1/operation-service/apphomepage

Get app homepage configuration (banners, featured content, section ordering).

### GET /v1/operation-service/configuration

Get app-wide configuration (feature flags, URLs, global settings).

---

## Aftersale Service (`/aftersale-service/`)

### GET /v1/aftersale-service/trouble/totalunreadcount

Get count of unread support trouble tickets.

### GET /v1/aftersale-service/makerworld/totalunreadcount

Get count of unread MakerWorld-related support items.

---

## Point Service (`/point-service/`)

### GET /v1/point-service/boost/boostdesign

Get boost status for a design (points-based promotion system).

| Parameter | Type | Description |
|-----------|------|-------------|
| `designId` | query | Design ID |

---

## Report Service (`/report-service/`)

### GET /v1/report-service/report/classification

Get report/moderation classification options.

| Parameter | Type | Description |
|-----------|------|-------------|
| `source` | query | Report source: `message`, `design`, etc. |

---

## Task Service (`/task-service/`)

### GET /v1/task-service/user/taskv2/multi

Get multiple onboarding/achievement task statuses.

| Parameter | Type | Description |
|-----------|------|-------------|
| `taskNames` | query | Comma-separated: `app_newbie_task_v2`, `app_newbie_task_v3` |

---

## Analysis Service (`/analysis-st/`)

### GET /v1/analysis-st/tag/

Get user analytics/tracking tags.

| Parameter | Type | Description |
|-----------|------|-------------|
| `UID` | query | User analytics UUID |

---

## Additional User Service Endpoints

These extend the existing [user-service docs](cloud-http.md#get-v1user-servicemymessages).

### GET /v1/user-service/my/message/count

Get unread message count across all categories.

### GET /v1/user-service/my/message/latest

Get the most recent message.

### POST /v1/user-service/my/message/read

Mark messages as read.

### GET /v1/user-service/my/message/device/taskstatus

Get device task notification status (for badge counts).

### POST /v1/user-service/my/message/device/tasks/read

Mark device task notifications as read.

### GET /v1/user-service/my/messages (extended)

The existing `/my/messages` endpoint supports these `type` values:

| type | Category |
|------|----------|
| `1` | System notifications |
| `2` | Comment notifications |
| `3` | Like notifications |
| `4` | Follow notifications |
| `5` | Print task notifications |

### GET /v1/user-service/my/task/{taskId}

Get a specific print task by ID (distinct from `/iot-service/api/user/task/{taskId}`).

### GET /v1/user-service/my/task/printedplates

Get printed plate info for a design instance.

| Parameter | Type | Description |
|-----------|------|-------------|
| `instanceId` | query | Design instance ID |

### GET /v1/user-service/my/model/profile

Get model/printer profile linked to user.

| Parameter | Type | Description |
|-----------|------|-------------|
| `profileId` | query | Profile ID |
| `modelId` | query | Printer model ID (e.g., `US932767835d32ea`) |

### POST /v1/user-service/user/devicetoken

Register device push notification token (FCM/APNs).

### GET /v1/user-service/latest/app

Check for app updates. Returns latest version info.

---

## Common Patterns

### Pagination

All list endpoints use `offset` + `limit` pagination:

```
?offset=0&limit=20    # First page
?offset=20&limit=20   # Second page
```

### Resource IDs

| Resource | Format | Example |
|----------|--------|---------|
| User ID | Numeric (10 digits) | `3469901296` |
| Design ID | Numeric (7 digits) | `2416782` |
| Instance ID | Numeric (7 digits) | `2650240` |
| Comment ID | Numeric (7 digits) | `4177733` |
| Task ID | Numeric (9 digits) | `788462557` |
| Profile ID | Numeric (9 digits) | `635995371` |
| Printer serial | `{region}{hex}` | `USf86740b8413939` |
| Analytics UID | UUID v1 | `65c31ea0-cd74-11ed-b18f-39cf197fa3d4` |

### Event/Telemetry Service

The app sends analytics events to a separate domain:

- `POST https://event.bblmw.com/app2/home` — Home screen events
- `POST https://event.bblmw.com/app2/makerworld` — MakerWorld browsing events

### IP Geolocation

On startup, the app calls:
```
GET http://ip-api.com/json/?fields=status,message,continent,continentCode,...
```
Used for regional content serving.

---

## Complete Print-from-MakerWorld Workflow

```
1. Browse      → GET /search-service/select/design/nav?navKey=Trending
2. View design → GET /design-service/design/{designId}
3. Check fav   → GET /design-service/my/design/favoriteslist?designId={id}
4. Get ratings → GET /comment-service/commentandrating?designId={id}
5. Download    → GET /design-service/instance/{instanceId}/f3mf?type=download
6. Upload      → FTP to printer SD card (port 990, FTPS)
7. Print       → MQTT command on device/{serial}/request
```

---

## Discovery Method

These endpoints were reverse-engineered from the Bambu Handy Flutter app using:

1. **APK static analysis** — jadx decompilation + URL pattern extraction
2. **Live traffic capture** — Flutter Dio interceptor logs via `adb logcat -s flutter:*`
3. **Token extraction** — Heap dump scan for JWT tokens
4. **Tooling**: [apkre](https://github.com/schwarztim/bambu-mcp) automated API discovery
