"""
You have a CIDR network address such as '123.45.67.64/27', and want to
generate a range of all the IP addresses that it represents (e.g. '123.45.67.64',
'123.45.67.65', ..., '123.45.67.95')
"""

import ipaddress


def main():
    net = ipaddress.ip_network("123.45.67.64/27")
    print("ip network:", net)
    print("Number of addresses:", net.num_addresses)
    for i, address in enumerate(net, 1):
        print(f"  {i:<2} - {address}")

    print(net[0])

    address1 = ipaddress.ip_address("123.45.67.69")
    address2 = ipaddress.ip_address("123.45.67.123")

    print(f"IP {address1} in network:", address1 in net)
    print(f"IP {address2} in network:", address2 in net)

    inet = ipaddress.ip_interface("123.45.67.73/27")
    print("ip interface:", inet)
    print("network:", inet.network)
    print("netmask:", inet.netmask)
    print("ip:", inet.ip)


if __name__ == "__main__":
    main()
