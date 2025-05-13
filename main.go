package main

import (
	"encoding/binary"
	"encoding/csv"
	"fmt"
	"net"
	"os"
	"runtime"
	"sort"
	"strconv"
)

// IPRange represents a range of IP addresses with associated location data
type IPRange struct {
	IPFrom      uint32
	IPTo        uint32
	CountryCode string
	Region      string
}

// Convert IP string to uint32
func ipToInt(ipStr string) (uint32, error) {
	ip := net.ParseIP(ipStr)
	if ip == nil {
		return 0, fmt.Errorf("invalid IP address: %s", ipStr)
	}
	ip = ip.To4()
	if ip == nil {
		return 0, fmt.Errorf("not an IPv4 address: %s", ipStr)
	}
	return binary.BigEndian.Uint32(ip), nil
}

// Load database from CSV file
func loadDB(path string) ([]IPRange, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, fmt.Errorf("error opening file: %v", err)
	}
	defer file.Close()

	reader := csv.NewReader(file)
	records, err := reader.ReadAll()
	if err != nil {
		return nil, fmt.Errorf("error reading CSV: %v", err)
	}

	ranges := make([]IPRange, 0, len(records))
	for _, record := range records {
		if len(record) < 4 {
			continue
		}
		ipFrom, err := strconv.ParseUint(record[0], 10, 32)
		if err != nil {
			continue
		}
		ipTo, err := strconv.ParseUint(record[1], 10, 32)
		if err != nil {
			continue
		}

		ranges = append(ranges, IPRange{
			IPFrom:      uint32(ipFrom),
			IPTo:        uint32(ipTo),
			CountryCode: record[2],
			Region:      record[3],
		})
	}

	// Print the first 5 rows for verification
	fmt.Println("First 5 records:")
	for i := 0; i < 5 && i < len(ranges); i++ {
		fmt.Printf("%d: %d-%d, %s, %s\n", i, ranges[i].IPFrom, ranges[i].IPTo, ranges[i].CountryCode, ranges[i].Region)
	}

	return ranges, nil
}

// Find region for a given IP address
func findRegion(ranges []IPRange, ipStr string) (string, string, error) {
	ipInt, err := ipToInt(ipStr)
	if err != nil {
		return "", "", err
	}

	// Binary search implementation
	idx := sort.Search(len(ranges), func(i int) bool {
		return ranges[i].IPFrom > ipInt
	}) - 1

	if idx >= 0 && idx < len(ranges) {
		r := ranges[idx]
		if r.IPFrom <= ipInt && ipInt <= r.IPTo {
			return r.CountryCode, r.Region, nil
		}
	}

	return "", "", fmt.Errorf("region not found for IP: %s", ipStr)
}

func main() {
	ip := "113.161.50.126"
	ipInt, err := ipToInt(ip)
	if err != nil {
		fmt.Println("Error converting IP:", err)
		return
	}
	fmt.Printf("IP as integer: %d\n", ipInt)

	path := "IP2LOCATION-LITE-DB1.CSV/IP2LOCATION-LITE-DB1.CSV"
	ranges, err := loadDB(path)
	if err != nil {
		fmt.Println("Error loading database:", err)
		return
	}

	// Sort ranges by IP start address
	sort.Slice(ranges, func(i, j int) bool {
		return ranges[i].IPFrom < ranges[j].IPFrom
	})

	country, region, err := findRegion(ranges, ip)
	if err != nil {
		fmt.Println(err)
		return
	}
	fmt.Printf("Country: %s, Region: %s\n", country, region)

	// Approximate memory usage calculation
	var memStats runtime.MemStats
	runtime.ReadMemStats(&memStats)
	fmt.Printf("Total memory usage: %.2f KB\n", float64(memStats.Alloc)/1024)
}
