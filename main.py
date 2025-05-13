import socket
import struct
import pandas as pd
from bisect import bisect_right

def ip_to_int(ip):
    return struct.unpack("!I", socket.inet_aton(ip))[0]

def load_location_db(path):
    df =pd.read_csv(path, header=None, names=["ip_from", "ip_to", "country_code", "region"])
    print(df.head())
    return df

def load_proxy_db(path):
    df = pd.read_csv(path, header=None, names=[
        "ip_from", "ip_to", "country_code", "country_name"
    ])
    return df

def load_asn_db(path):
    df = pd.read_csv(path, header=None, names=[
        "ip_from", "ip_to", "asn", "asn_country_code", "asn_organization"
    ])
    return df


def find_proxy(proxy_ranges, start_ips, ip_str):
    ip_int = ip_to_int(ip_str)

    idx = bisect_right(start_ips, ip_int) - 1

    if idx >= 0:
        start, end, country_code, country_name = proxy_ranges[idx]
        if start <= ip_int <= end:
            return "Proxy"

    return "No Proxy"

def find_region(location_ranges, start_ips, ip_int):
    idx = bisect_right(start_ips, ip_int) - 1

    if idx >= 0:
        start, end, country, region = location_ranges[idx]
        if start <= ip_int <= end:
            return country, region

    return None, None


if __name__ == "__main__":
    ip = "113.161.50.126"
    ip = "185.60.216.35"
    ip = "104.244.73.112"
    print(ip_to_int(ip))
    location_path = "IP2LOCATION-LITE-DB1.CSV/IP2LOCATION-LITE-DB1.CSV"
    proxy_path = "IP2PROXY-LITE-PX1.CSV/IP2PROXY-LITE-PX1.CSV"
    
    location_db = load_location_db(path=location_path)
    proxy_db = load_proxy_db(proxy_path)
    
    location_ranges = list(zip(location_db["ip_from"], location_db["ip_to"], location_db["country_code"], location_db["region"]))
    # Make sure the data is sorted by ip_from
    location_ranges.sort(key=lambda x: x[0])
    location_start_ips = [r[0] for r in location_ranges]

    proxy_ranges = list(zip(proxy_db["ip_from"], proxy_db["ip_to"], proxy_db["country_code"], proxy_db["country_name"]))
    proxy_start_ips = [r[0] for r in proxy_ranges]
    print(f"Start IPs: {location_start_ips[:5]}")  # Print first 5 start IPs for debugging

    country, region = find_region(location_ranges=location_ranges, start_ips=location_start_ips, ip_str=ip)
    print(f"Country: {country}, Region: {region}")

    proxy = find_proxy(proxy_ranges=proxy_ranges, start_ips=proxy_start_ips, ip_str=ip)
    print(f"Proxy Type: {proxy}")

    memory_bytes = location_db.memory_usage(deep=True).sum()
    print(f"Total memory usage for location_db: {memory_bytes / 1024:.2f} KB")

    memory_bytes = proxy_db.memory_usage(deep=True).sum()
    print(f"Total memory usage for proxy_db: {memory_bytes / 1024:.2f} KB")