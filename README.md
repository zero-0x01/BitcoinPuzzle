Bitcoin Address Brute-Force Checker
===================================

This script attempts to brute-force Bitcoin private keys and match them with a given Bitcoin address or address fragment. It uses multi-threading to speed up the process and the secp256k1 elliptic curve for Bitcoin key/address generation.

⚠️ Disclaimer: This script is for educational and research purposes only. Unauthorized access to others' wallets is illegal and unethical.

Features
--------
- Generates random private key ranges within specified bounds.
- Converts private keys into both compressed and uncompressed Bitcoin addresses.
- Checks if generated addresses match a hardcoded target substring.
- Uses multithreading for performance.
- Logs matches to Found.txt.

Requirements
------------
- Python 3.6+
- secp256k1 library (as ice in the script)

Installation
------------
Install the required package:

    pip install secp256k1

Or if you're using the custom ice implementation, ensure ice.py is in your working directory or installed.

Usage
-----
Simply run the script:

    python script.py

The script will:

1. Continuously generate private key ranges.
2. For each private key in the range:
    - Derive compressed and uncompressed Bitcoin addresses.
    - Check for a match against the hardcoded address substring.
    - Log matches to Found.txt.

Output
------
Matches are printed to the console and appended to Found.txt:

    Private key: <hex> | Compressed Address: <addr> | Uncompressed Address: <addr>

Example Match Output:

    Private key: 00000...123 | Compressed Address: 1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ | Uncompressed Address: 1ABC...

Customization
-------------
Target Address:

Update the following line to the address or address fragment you want to search for:

    base = ('1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ')

Range and Threads:

Edit these values in the main() function:

    count = 5000          # How many keys per loop
    thread_count = 50     # Thread pool size

You can also change min and max values for the keyspace range.

Performance Tips
----------------
- Ensure your CPU can handle the number of threads you assign.
- Running this script will consume CPU heavily.
- Consider using PyPy or Cython for performance boosts if needed.

Legal Notice
------------
This software is intended for educational and research purposes only. Do NOT use it for malicious purposes. Misuse of this tool is your responsibility.

