# Classifying IP addresses

Read this when a request asks for external/public or internal/private IP addresses.

"External/public IP" and "internal/private IP" are derived properties, not requirements for a
dedicated status column. Inspect the live schema and values for the actual IP column first. Unless
the dataset documents another policy, treat RFC1918 IPv4 (`10/8`, `172.16/12`, `192.168/16`),
loopback, link-local, unspecified, multicast, and shared CGNAT (`100.64/10`) as non-external; apply
analogous IPv6 ULA/link-local/loopback/unspecified/multicast rules. Documentation/reserved examples
such as `198.51.100.0/24` and `203.0.113.0/24` are not RFC1918 internal addresses, so do not
silently discard them unless the dataset explicitly defines them as non-external fixtures. Match the
exact stored representation; do not apply IPv4 rules to IPv6, host:port, URL, or CIDR strings
without validating them. Use a positive pattern where supported, or `IN` only from an exhaustive
value set. A limited/sample table cannot prove a complement; if the value set is truncated or the
query cannot express the classification, report that limitation instead of claiming a complete
collection.
