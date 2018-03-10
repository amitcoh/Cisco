# Cisco
This library contains all my scripting for Cisco devices (most of the time using Netmiko for SSH or API if it is possible)

## Parse Routing Table
I was looking for an IOS routing table parser online and found NOTHING.
Here is my version of parsing a routing table.
The command sent by ssh should be "show ip route | begin Gateway of last",
and it should be splitted to lines (using string.split('\n')).

Enjoy!
