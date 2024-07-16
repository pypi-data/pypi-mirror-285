# Targeting Platform

![Pypi Version](https://img.shields.io/pypi/v/targeting-platform)
![Python Version](https://img.shields.io/pypi/pyversions/targeting-platform)
![License](https://img.shields.io/pypi/l/targeting-platform)

## Prerequsites

To use module following tools need to be configured:

- **Redis** - is used for caching platform information (catalog of lineitems/adgroups e.g.) and locks. It depends on amount of information in your platform but as a starting point 1Gb memory will be enough. For now only single entrypoint is supported. Prefix for cache keys is `PLATFORM_CACHE_` (set in [CACHE_KEYS_PREFIX](https://gitlab.com/dsp6802915/targeting_platform/-/tree/main/src/targeting_platform/utils_cache.py#L62)) and for locks `PLATFORM_LOCK_` ([LOCK_KEYS_PREFIX](https://gitlab.com/dsp6802915/targeting_platform/-/tree/main/src/targeting_platform/utils_cache.py#L63)).

### Credentials for platforms

Each platform has it's own format of credentials. You need to obtaint credetantial before starting to use platforms thorugh this module.

#### DV360 (dv360)

Requires service account private key (whole JSON for service account). E.g.

```JSON
{
    "type": "service_account",
    "project_id": "",
    "private_key_id": "",
    "private_key": "-----BEGIN PRIVATE KEY-----\n\n-----END PRIVATE KEY-----\n",
    "client_email": "",
    "client_id": "",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": ""
}
```

#### Meta (Facebook) (meta)

Example of credentails (`app_scoped_system_user_id` is required for detailed access validation):

```JSON
{
    "access_token": "",
    "app_scoped_system_user_id":
}
```

#### The Trade Desk (ttd)

Example of credentials (login and password is required for automatic token renewal):

```JSON
{
    "PartnerId": "",
    "token": "",
    "Login": "",
    "Password": ""
}
```

## Platforms

### DV360

Library works as with normal lineitems as with YouTube through [SDF](https://developers.google.com/display-video/api/structured-data-file/format). In case of passing lineitem id for YouTube (in array all ids should be either for normal or YouTube lineitems) methods will return Pandas DataFrame with prepared data - you need to get CSV from it and manually upload to Google.

### Meta

While testing/using you can receive Rate Limit (set by [Meta Marketing API](https://developers.facebook.com/docs/marketing-apis/rate-limiting/)) - you need to monitor your limits before operations. For current implementaion (probably will be chnaged in future releases) there is no retries and exceptions - you simply get empty result (means set/chnaged nothing).

## How to use

See examples in [integration tests](https://gitlab.com/dsp6802915/targeting_platform/-/tree/main/tests/integration).

You can adopt these tests by placing appropriate sectet files into folder `secrets`.

## Locks

To prevent simultanous updating of the same placements in the platform locks are used. While you are calling clear, pause, delete and set operations lock will be acquired and released in the end of the operation (or after 1 hour in case of any error). If method can't acquire lock it will return empty results (no exception raised).
