
# About mdtablegen

This is a Python module to generate Markdown tables. Specifically the
Markdown dialect that HL docgen (and derivatives) speak. A few existing
Python Markdown generator libraries don't exactly do this.

# Example Output

```
+---------------+----------+-----------+----------------------+----------------------------+
| Address       | Port     | Service   | Fingerprint          | Comments                   |
+===============+==========+===========+======================+============================+
| 172.22.150.88 | 443/tcp  | ssl|http  | Some httpd           | Here's a comment           |
+---------------+----------+-----------+----------------------+----------------------------+
| 172.22.150.88 | 8089/tcp | ssl|http  | Some httpd           |                            |
+---------------+----------+-----------+----------------------+----------------------------+
| 172.22.30.10  | 53/tcp   | domain    | (unknown banner: ... | This looks interesting     |
+---------------+----------+-----------+----------------------+----------------------------+
| 172.22.30.119 | 22/tcp   | ssh       | ProFTPD mod_sftp ... |                            |
```

