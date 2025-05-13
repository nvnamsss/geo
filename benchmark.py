import pandas as pd
import time
import sys
import os
import random
from main import ip_to_int, load_location_db, load_proxy_db, find_region, find_proxy
from tqdm import tqdm

def load_dataset():
    df = pd.read_csv("geolite2-country-ipv4-num.csv", header=None, names=["ip_from", "ip_to", "country_code"])
    return df

def evaluate_accuracy(location_ranges, location_start_ips, test_cases):
    """Evaluate accuracy with known test cases"""
    correct = 0
    for ip, expected_country in test_cases:
        country, _ = find_region(location_ranges, location_start_ips, ip)
        print(f"IP: {ip}, Expected: {expected_country}, Found: {country}")
        if country and expected_country and country.upper() == expected_country.upper():
            correct += 1
        
    
    return correct / len(test_cases) * 100

if __name__ == "__main__":
    print("Running benchmark for IP lookup functionality...")
    
    # Load databases
    print("Loading databases...")
    location_path = "IP2LOCATION-LITE-DB1.CSV/IP2LOCATION-LITE-DB1.CSV"
    
    location_db = load_location_db(path=location_path)
    
    # Prepare data structures for lookup
    location_ranges = list(zip(location_db["ip_from"], location_db["ip_to"], location_db["country_code"], location_db["region"]))
    location_ranges.sort(key=lambda x: x[0])
    location_start_ips = [r[0] for r in location_ranges]

    # Load dataset
    dataset = load_dataset()
    dataset_ranges = list(zip(dataset["ip_from"], dataset["ip_to"], dataset["country_code"]))
    dataset_ranges.sort(key=lambda x: x[0])
    # Generate test cases from dataset
    print("Generating test cases...")
    test_cases = []
    for ip_from, ip_to, country_code in tqdm(dataset_ranges, desc="Preparing test cases"):
        for ip in range(ip_from, ip_to + 1):
            if random.random() < 0.3:  # Sample ~30% of IPs to keep test set manageable
               test_cases.append((ip, country_code))
        # # Sample random IPs from ranges
        # if random.random() < 0.3:  # Sample ~1% of ranges to keep test set manageable
        #     random_ip = random.randint(ip_from, ip_to)
        #     test_cases.append((random_ip, country_code))

    test_size = 100000
    # Limit test cases if needed
    if len(test_cases) > test_size:
        random.shuffle(test_cases)
        test_cases = test_cases[:test_size]

    print(f"Generated {len(test_cases)} test cases")

    # Run accuracy evaluation
    print("Evaluating accuracy...")
    accuracy = evaluate_accuracy(location_ranges, location_start_ips, test_cases)
    print(f"Accuracy: {accuracy:.2f}%")