# Basics

## X1 and P2S

The X1 series and P2S printers run a RTSP server that streams video over the network.

### Local RTSP Server

- **URL**: `rtsps://{PRINTER_IP}:322/streaming/live/1`
- **TLS**: [yes](./tls.md)
- **Authentication**: required
- **Username**: `bblp`
- **Password**: `dev_access_code` from a `Device` object (aka the LAN access code).

## A1 and P1

The A1 and P1 series printers run a simple TCP server that streams 1280x720 JPEG images over the network.
Integers are encoded in little-endian byte order.

### Local Video Server

- **Host**: `{PRINTER_IP}:6000`
- **TLS**: [yes](./tls.md)
- **Authentication**: required
- **Username**: `bblp`
- **Password**: `dev_access_code` from a `Device` object (aka the LAN access code).

### Authentication

This packet must be sent when connecting to the server.

| Offset | Size     | Value                                                    |
| ------ | -------- | -------------------------------------------------------- |
| 0      | 4 bytes  | Inlined Payload size (0x40)                              |
| 4      | 4 bytes  | Type (0x3000)                                            |
| 8      | 4 bytes  | Flags (0)                                                |
| 12     | 4 bytes  | 0                                                        |
| 16     | 32 bytes | Username encoded as ASCII, right-padded with null bytes. |
| 48     | 32 bytes | Password encoded as ASCII, right-padded with null bytes. |

### Header

The server sends a 16-byte header for each frame.

| Offset | Size    | Value        |
| ------ | ------- | ------------ |
| 0      | 4 bytes | Payload size |
| 4      | 4 bytes | itrack (0)   |
| 8      | 4 bytes | Flags (1)    |
| 12     | 4 bytes | 0            |

### Image

After the header, the server sends a total of `payload size` bytes containing the JPEG image.

The image data might be received in multiple chunks (e.g. up to 4096 bytes each), depending on the programming language and operating system. These chunks need to be concatenated to reconstruct the complete image.

The following magic bytes can be checked to verify that the image has been successfully received:

- Start of Image: `FF D8`
- End of Image: `FF D9`
