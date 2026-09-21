"""What this namespace is known to render against.

The package does not ship ECharts and does not depend on it, so there is no
dependency specifier anywhere stating which versions work. That leaves the
question unanswered unless it is answered here, and a consumer choosing what
to bundle has no other place to look.

This is a statement about the `echarts` namespace, not about the package: a
second backend would state its own range beside this one.
"""

#: The ECharts versions this namespace is known to render against.
#:
#: A range rather than a pin. The package reads one global and calls nothing,
#: so it is compatible with far more than it is tested against, and pinning
#: would claim a precision the package neither has nor wants.
ECHARTS_SUPPORTED_VERSIONS = ">=6.0,<7.0"

#: The exact version `<c-echarts.cdn />` loads.
#:
#: Pinned, not floating. A range in a script tag cannot carry an integrity
#: hash, and an unpinned third-party script is a different file on any given
#: day.
ECHARTS_CDN_VERSION = "6.1.0"

#: Subresource integrity hash for that exact file, base64 sha384.
#:
#: Computed from the bytes the CDN serves. The browser refuses the script if
#: what arrives does not hash to this, which is what keeps a compromised or
#: substituted CDN from running arbitrary code on a page that trusted it.
ECHARTS_CDN_INTEGRITY = "sha384-C2iskrW/uPW46KzOjrvJIQo4YkV8lkD+QS0CrDN18IIPIpT/g2USu8bTP3nvmIAD"

#: Where that file comes from.
ECHARTS_CDN_URL = (
    f"https://cdn.jsdelivr.net/npm/echarts@{ECHARTS_CDN_VERSION}/dist/echarts.min.js"
)
