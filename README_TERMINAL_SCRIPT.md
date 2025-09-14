# WHOIS Lookup Terminal Script

A powerful command-line tool for performing WHOIS lookups on multiple domains with parallel processing, rate limiting, and export capabilities.

## 🚀 Features

- **Parallel Processing**: Lookup multiple domains simultaneously with configurable worker threads
- **Rate Limiting**: Built-in rate limiting to avoid being blocked by WHOIS servers
- **Multiple Input Methods**: Command line arguments or text file input
- **Export Options**: Export results to CSV or JSON format
- **Detailed Output**: Choose between summary table or detailed information view
- **Colorized Output**: Beautiful terminal colors for better readability
- **Error Handling**: Graceful handling of invalid domains and lookup failures
- **Domain Validation**: Automatic validation and filtering of domain names

## 📦 Requirements

```bash
pip install python-whois
```

## 📖 Usage

### Basic Usage

```bash
# Lookup single domain
python whois_lookup.py google.com

# Lookup multiple domains
python whois_lookup.py google.com facebook.com github.com

# Read domains from file
python whois_lookup.py -f domains.txt

# Show detailed information
python whois_lookup.py --detailed google.com facebook.com

# Export to CSV
python whois_lookup.py --export csv google.com facebook.com

# Export to JSON
python whois_lookup.py --export json google.com facebook.com

# Custom rate limiting and workers
python whois_lookup.py --rate-limit 1.0 --workers 3 google.com facebook.com
```

### Command Line Options

```
positional arguments:
  domains               Domain names to lookup

options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Read domains from text file
  --export {csv,json}   Export results to file
  --detailed            Show detailed results
  --rate-limit RATE_LIMIT
                        Delay between requests in seconds (default: 0.5)
  --workers WORKERS     Maximum concurrent workers (default: 5)
```

## 📝 Input Format

### Command Line
Space-separated domain names:
```bash
python whois_lookup.py google.com facebook.com github.com
```

### Text File
Create a text file with domains separated by spaces or newlines:

**domains.txt:**
```
google.com facebook.com
github.com
stackoverflow.com twitter.com
linkedin.com reddit.com
```

Then run:
```bash
python whois_lookup.py -f domains.txt
```

## 📊 Output Formats

### Summary Table (Default)
```
📊 RESULTS
================================================================================
Domain                    Registrar                      Status         
--------------------------------------------------------------------------------
google.com                MarkMonitor Inc.               Success        
facebook.com              RegistrarSafe, LLC             Success        
github.com                MarkMonitor, Inc.              Success        
--------------------------------------------------------------------------------
✅ Successful: 3
❌ Errors: 0
⚠️  No Data: 0
```

### Detailed Output (--detailed)
```
📋 DETAILED RESULTS
================================================================================

1. GOOGLE.COM
----------------------------------------
Registrar: MarkMonitor Inc.
Created: 1997-09-15 04:00:00
Expires: 2028-09-14 04:00:00
Updated: 2019-09-09 15:39:04
Name Servers:
  • NS1.GOOGLE.COM
  • NS2.GOOGLE.COM
  • NS3.GOOGLE.COM
  • NS4.GOOGLE.COM
Status: clientDeleteProhibited, clientTransferProhibited, clientUpdateProhibited
```

### CSV Export
Generates a CSV file with columns:
- domain, registrar, creation_date, expiration_date, updated_date
- registrant_name, registrant_organization, registrant_country
- admin_email, tech_email, name_servers, status, error

### JSON Export
Generates a JSON file with complete structured data for each domain.

## 🔧 Configuration Options

### Rate Limiting
Control the delay between WHOIS requests to avoid being blocked:
```bash
# 1 second delay between requests
python whois_lookup.py --rate-limit 1.0 google.com facebook.com

# 0.2 second delay (faster but higher risk)
python whois_lookup.py --rate-limit 0.2 google.com facebook.com
```

### Concurrent Workers
Control how many domains are processed simultaneously:
```bash
# Use 10 concurrent workers (be careful with rate limiting)
python whois_lookup.py --workers 10 --rate-limit 1.0 domain1.com domain2.com

# Use only 2 workers (more conservative)
python whois_lookup.py --workers 2 google.com facebook.com
```

## 🎯 Example Use Cases

### 1. Quick Domain Check
```bash
python whois_lookup.py mywebsite.com
```

### 2. Bulk Domain Analysis
```bash
python whois_lookup.py -f competitor_domains.txt --detailed --export csv
```

### 3. Domain Portfolio Management
```bash
python whois_lookup.py --export json \
  domain1.com domain2.com domain3.com \
  --rate-limit 1.0 --workers 3
```

### 4. Registrar Research
```bash
python whois_lookup.py --detailed \
  google.com facebook.com github.com \
  amazon.com microsoft.com apple.com
```

## 📂 File Structure

```
whois_lookup.py          # Main script
sample_domains.txt       # Example domains file
whois_results_*.csv      # Generated CSV exports
whois_results_*.json     # Generated JSON exports
```

## 🚨 Important Notes

1. **Rate Limiting**: Always use appropriate rate limiting to avoid being blocked by WHOIS servers
2. **Respect Terms**: Be respectful of WHOIS server resources and terms of service
3. **Error Handling**: The script gracefully handles invalid domains and network errors
4. **Large Batches**: For very large domain lists, consider breaking them into smaller batches

## 🎨 Color Legend

- 🔍 **Cyan**: Lookup in progress
- ✅ **Green**: Successful lookup
- ❌ **Red**: Error or failure
- ⚠️ **Yellow**: Warning or no data
- 📊 **Purple**: Headers and titles
- 🔹 **Blue**: Information and settings

## 🔧 Troubleshooting

### Common Issues

1. **"python-whois library is required"**
   ```bash
   pip install python-whois
   ```

2. **Too many errors/timeouts**
   - Increase `--rate-limit` value
   - Decrease `--workers` count

3. **No data returned for valid domains**
   - Some domains may have restricted WHOIS data
   - This is normal behavior, not an error

4. **File not found**
   - Check file path and permissions
   - Ensure file exists and is readable

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve this tool.

## 📄 License

This script is provided as-is for educational and research purposes.