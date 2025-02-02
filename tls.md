# TLS Certificates

When working with cloud or local printer APIs, proper certificate validation is essential to prevent man-in-the-middle (MITM) attacks.

## Example Code

See the [examples folder](./examples/) for Python and Node.js.
This is the easiest way to get started without worrying about the technical details.

## Who issued the certificate?

The most basic check is to ensure that the certificate is issued by a trusted Certificate Authority (CA).

### Cloud

Typically automatically validated by libraries.

- These certificates are issued by `DigiCert, Inc.`.

### Printer

Configure your MQTT/FTP/TLS libraries to trust [BBL CA](./examples/ca_cert.pem).

- The certificate in your printer is issued by Bambu Lab.

## Who is the certificate issued to?

This is another important check to ensure you are not only communicating with _any_ server, but the _correct_ server.

Certificates contain a common name (CN) field that specifies the host name of the server.

### Cloud

Typically automatically validated by libraries.

- Example: certificate contains `CN=*.mqtt.bambulab.com`, you connect to `us.mqtt.bambulab.com`

### Printer

Requires [Server Name Indication (SNI)](https://en.wikipedia.org/wiki/Server_Name_Indication).

- Example: certificate contains `CN=<printer's serial number>`, you connect to `192.168.0.5`
- Not all libraries support SNI, in this case you need to manually check the common name or disable host name validation at your own risk.

## Common Errors

**Do not** disable all SSL/TLS validations when encountering errors like the following. If it's not clear how to fix it, please open an issue at the libraries you are using or at [OpenBambuAPI](https://github.com/Doridian/OpenBambuAPI/issues/new).

- ```text
  [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain
  ```

  This errors can happen when connecting to a printer without trusting the Bambu Lab CA.

  **Fix**: Refer to [Who issued the certificate?](#who-issued-the-certificate)

- ```text
  [ERR_TLS_CERT_ALTNAME_INVALID]: Hostname/IP does not match certificate's altnames: IP: 192.168.0.5 is not in the cert's list

  [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: IP address mismatch, certificate is not valid for '192.168.0.1'
  ```

  These errors can happen when connecting to a printer without configuring SNI.

  **Fix**: Refer to [Who is the certificate issued to?](#who-is-the-certificate-issued-to)

- ```text
  [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: CA cert does not include key usage extension
  ```

  This error can happen when using python 3.13+ to connect to a printer.

  **Workaround**: Refer to note about [VERIFY_X509_STRICT](https://docs.python.org/3/library/ssl.html#ssl.create_default_context).
