# Basics

Some Bambu printers expose a file-transfer protocol on TCP `6000`, distinct
from the FTPS server on port `990`. It carries directory listing, upload,
download, and delete operations against the printer's storage.

The same TCP port (`6000`) is used by the A1 and P1 series for [video
streaming](./video.md) instead — the role appears to be model-dependent.

## Transport

- **Host**: `{PRINTER_IP}:6000`
- **TLS**: [yes](./tls.md) (observed: TLS 1.2, `ECDHE-RSA-AES256-GCM-SHA384`)
- **Authentication**: required, single packet immediately after the TLS handshake

### Auth packet

A 64-byte fixed-size packet:

| Offset | Length | Field |
|-------:|-------:|-------|
| `0x00` | 8      | `bblp\0\0\0\0` (literal) |
| `0x08` | 32     | `dev_access_code` (the 8-char LAN access code, zero-padded) |
| `0x28` | 24     | reserved (zero) |

Observed reply on success: nothing (the server proceeds straight to accepting framed messages).

## Framing

After auth, each message is a 16-byte header followed by a JSON body. All integers little-endian.

| Offset | Length | Field          | Notes                                 |
|-------:|-------:|----------------|---------------------------------------|
| `0x00` | 4      | `payload_size` | length of the JSON body in bytes      |
| `0x04` | 4      | `sequence`     | client-chosen request id, echoed back |
| `0x08` | 4      | `cmdtype`      | command class (see below)             |
| `0x0c` | 4      | `mtype`        | message kind: `0x3001` control, `0x3003` start-of-data |

The JSON body is the canonical envelope used elsewhere on the printer:

```json
// request
{ "cmdtype": <int>, "sequence": <int>, "req": { … } }

// reply
{ "cmdtype": <int>, "sequence": <int>, "result": <int>, "reply": { … } }
```

`result == 0` indicates success; other values are command-specific.

## Commands (`cmdtype` values observed)

| `cmdtype` | Name                    | Direction | Notes |
|----------:|-------------------------|-----------|-------|
| `1`       | `LIST_INFO`             | req/reply | Directory listing. |
| `2`       | `SUB_FILE`              | req/reply | Subscribe to file change notifications. |
| `3`       | `FILE_DEL`              | req/reply | Delete a file. |
| `4`       | `FILE_DOWNLOAD`         | streaming | Reply uses additional `mtype 0x3003` frames carrying file chunks. |
| `5`       | `FILE_UPLOAD`           | streaming | Same shape as download, in reverse. |
| `7`       | `REQUEST_MEDIA_ABILITY` | req/reply | Probe for which media features the printer supports. |

These names match the symbols in Bambu's open-source `bambu_net_oss`
reference implementation (`LocalControlTunnel.cpp`).

## Caveats

- On H2S firmware `01.02.00.00`, `LIST_INFO` (cmdtype `1`) returns
  `{ "cmdtype": 0xFFFFFFFF, "mtype": 0x3001, "result": 2 }`. The opcode
  appears to have been retired on that firmware; other H2 firmwares were
  not tested.
- A1 (and possibly P1-series) printers serve [MJPEG video](./video.md) on
  TCP `6000` instead of this protocol, so probing the port is not a
  reliable feature-detect.
