#!/usr/bin/env python3
"""
WHOIS Lookup Terminal Tool
Usage: python whois_lookup.py domain1.com domain2.com domain3.com
       python whois_lookup.py -f input.txt
       python whois_lookup.py --export csv domain1.com domain2.com
"""

import argparse
import asyncio
import csv
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import whois
except ImportError:
    print("❌ Error: python-whois library is required. Install with: pip install python-whois")
    sys.exit(1)

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class WhoisLookupTool:
    def __init__(self, rate_limit: float = 0.5, max_workers: int = 5):
        self.rate_limit = rate_limit
        self.max_workers = max_workers
        self.domain_pattern = re.compile(
            r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        )
    
    def validate_domains(self, domains: List[str]) -> List[str]:
        """Validate and clean domain list"""
        valid_domains = []
        for domain in domains:
            domain = domain.strip().lower()
            if domain and self.domain_pattern.match(domain):
                valid_domains.append(domain)
            elif domain:
                print(f"{Colors.YELLOW}⚠️  Skipping invalid domain: {domain}{Colors.END}")
        return valid_domains
    
    def safe_extract_date(self, date_field):
        """Safely extract date from whois data"""
        if not date_field:
            return None
        
        try:
            if isinstance(date_field, list):
                return str(date_field[0]) if date_field else None
            else:
                return str(date_field)
        except (IndexError, TypeError):
            return str(date_field) if date_field else None

    def safe_extract_list(self, list_field):
        """Safely extract list from whois data"""
        if not list_field:
            return []
        
        try:
            if isinstance(list_field, (list, tuple)):
                return list(list_field)
            else:
                return [str(list_field)]
        except (TypeError, AttributeError):
            return []

    def perform_whois_lookup(self, domain: str) -> Dict[str, Any]:
        """Perform whois lookup for a single domain"""
        try:
            # Rate limiting
            time.sleep(self.rate_limit)
            
            print(f"{Colors.CYAN}🔍 Looking up: {domain}{Colors.END}")
            whois_data = whois.whois(domain)
            
            result = {
                "domain": domain,
                "registrar": getattr(whois_data, 'registrar', None),
                "creation_date": self.safe_extract_date(getattr(whois_data, 'creation_date', None)),
                "expiration_date": self.safe_extract_date(getattr(whois_data, 'expiration_date', None)),
                "updated_date": self.safe_extract_date(getattr(whois_data, 'updated_date', None)),
                "name_servers": self.safe_extract_list(getattr(whois_data, 'name_servers', None)),
                "status": self.safe_extract_list(getattr(whois_data, 'status', None)),
                "registrant_name": getattr(whois_data, 'name', None),
                "registrant_organization": getattr(whois_data, 'org', None),
                "registrant_country": getattr(whois_data, 'country', None),
                "admin_email": getattr(whois_data, 'admin_email', None),
                "tech_email": getattr(whois_data, 'tech_email', None),
                "error": None
            }
            
            print(f"{Colors.GREEN}✅ {domain} -> {result.get('registrar', 'Unknown registrar')}{Colors.END}")
            return result
            
        except Exception as e:
            error_msg = str(e)
            print(f"{Colors.RED}❌ {domain} -> Error: {error_msg}{Colors.END}")
            return {
                "domain": domain,
                "registrar": None,
                "creation_date": None,
                "expiration_date": None,
                "updated_date": None,
                "name_servers": [],
                "status": [],
                "registrant_name": None,
                "registrant_organization": None,
                "registrant_country": None,
                "admin_email": None,
                "tech_email": None,
                "error": error_msg
            }

    def lookup_domains(self, domains: List[str]) -> List[Dict[str, Any]]:
        """Perform parallel whois lookups"""
        valid_domains = self.validate_domains(domains)
        
        if not valid_domains:
            print(f"{Colors.RED}❌ No valid domains provided{Colors.END}")
            return []
        
        print(f"\n{Colors.HEADER}{Colors.BOLD}🚀 Starting WHOIS lookup for {len(valid_domains)} domains{Colors.END}")
        print(f"{Colors.BLUE}Rate limit: {self.rate_limit}s between requests{Colors.END}")
        print(f"{Colors.BLUE}Max workers: {self.max_workers}{Colors.END}\n")
        
        start_time = time.time()
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(executor.map(self.perform_whois_lookup, valid_domains))
        
        end_time = time.time()
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 Completed in {end_time - start_time:.2f} seconds{Colors.END}\n")
        
        return results

    def print_results_table(self, results: List[Dict[str, Any]]):
        """Print results in a formatted table"""
        if not results:
            return
        
        print(f"{Colors.HEADER}{Colors.BOLD}📊 RESULTS{Colors.END}")
        print("=" * 80)
        
        # Table header
        print(f"{Colors.BOLD}{'Domain':<25} {'Registrar':<30} {'Status':<15}{Colors.END}")
        print("-" * 80)
        
        # Table rows
        for result in results:
            domain = result['domain']
            registrar = result.get('registrar', 'Unknown')[:28] if result.get('registrar') else 'Unknown'
            
            if result.get('error'):
                status_color = Colors.RED
                status = "Error"
            elif result.get('registrar'):
                status_color = Colors.GREEN
                status = "Success"
            else:
                status_color = Colors.YELLOW
                status = "No Data"
            
            print(f"{domain:<25} {registrar:<30} {status_color}{status:<15}{Colors.END}")
        
        print("-" * 80)
        
        # Summary
        success_count = sum(1 for r in results if r.get('registrar') and not r.get('error'))
        error_count = sum(1 for r in results if r.get('error'))
        no_data_count = len(results) - success_count - error_count
        
        print(f"{Colors.GREEN}✅ Successful: {success_count}{Colors.END}")
        print(f"{Colors.RED}❌ Errors: {error_count}{Colors.END}")
        print(f"{Colors.YELLOW}⚠️  No Data: {no_data_count}{Colors.END}")

    def print_detailed_results(self, results: List[Dict[str, Any]]):
        """Print detailed results for each domain"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}📋 DETAILED RESULTS{Colors.END}")
        print("=" * 80)
        
        for i, result in enumerate(results, 1):
            domain = result['domain']
            print(f"\n{Colors.BOLD}{i}. {domain.upper()}{Colors.END}")
            print("-" * 40)
            
            if result.get('error'):
                print(f"{Colors.RED}❌ Error: {result['error']}{Colors.END}")
                continue
            
            # Display key information
            info_items = [
                ("Registrar", result.get('registrar')),
                ("Created", result.get('creation_date')),
                ("Expires", result.get('expiration_date')),
                ("Updated", result.get('updated_date')),
                ("Registrant", result.get('registrant_name')),
                ("Organization", result.get('registrant_organization')),
                ("Country", result.get('registrant_country')),
                ("Admin Email", result.get('admin_email')),
                ("Tech Email", result.get('tech_email')),
            ]
            
            for label, value in info_items:
                if value:
                    if label == "Registrar":
                        print(f"{Colors.CYAN}{label}:{Colors.END} {Colors.BOLD}{value}{Colors.END}")
                    else:
                        print(f"{Colors.CYAN}{label}:{Colors.END} {value}")
            
            # Name servers
            if result.get('name_servers'):
                print(f"{Colors.CYAN}Name Servers:{Colors.END}")
                for ns in result['name_servers'][:5]:  # Show first 5
                    print(f"  • {ns}")
            
            # Status
            if result.get('status'):
                print(f"{Colors.CYAN}Status:{Colors.END} {', '.join(result['status'][:3])}")

    def export_to_csv(self, results: List[Dict[str, Any]], filename: str):
        """Export results to CSV file"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'domain', 'registrar', 'creation_date', 'expiration_date', 'updated_date',
                'registrant_name', 'registrant_organization', 'registrant_country',
                'admin_email', 'tech_email', 'name_servers', 'status', 'error'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                row = result.copy()
                # Convert lists to strings
                row['name_servers'] = '; '.join(result.get('name_servers', []))
                row['status'] = '; '.join(result.get('status', []))
                writer.writerow(row)
        
        print(f"{Colors.GREEN}✅ Results exported to: {filename}{Colors.END}")

    def export_to_json(self, results: List[Dict[str, Any]], filename: str):
        """Export results to JSON file"""
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(results, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"{Colors.GREEN}✅ Results exported to: {filename}{Colors.END}")

def read_domains_from_file(filepath: str) -> List[str]:
    """Read domains from a text file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        domains = []
        for line in content.split('\n'):
            line_domains = line.strip().split()
            domains.extend([d.strip() for d in line_domains if d.strip()])
        
        return domains
    except FileNotFoundError:
        print(f"{Colors.RED}❌ File not found: {filepath}{Colors.END}")
        return []
    except Exception as e:
        print(f"{Colors.RED}❌ Error reading file: {e}{Colors.END}")
        return []

def main():
    parser = argparse.ArgumentParser(
        description="WHOIS Lookup Tool - Get registrar information for domains",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python whois_lookup.py google.com facebook.com
  python whois_lookup.py -f domains.txt
  python whois_lookup.py --export csv google.com facebook.com
  python whois_lookup.py --detailed google.com
  python whois_lookup.py --rate-limit 1.0 --workers 3 google.com facebook.com
        """
    )
    
    parser.add_argument('domains', nargs='*', help='Domain names to lookup')
    parser.add_argument('-f', '--file', help='Read domains from text file')
    parser.add_argument('--export', choices=['csv', 'json'], help='Export results to file')
    parser.add_argument('--detailed', action='store_true', help='Show detailed results')
    parser.add_argument('--rate-limit', type=float, default=0.5, 
                       help='Delay between requests in seconds (default: 0.5)')
    parser.add_argument('--workers', type=int, default=5,
                       help='Maximum concurrent workers (default: 5)')
    
    args = parser.parse_args()
    
    # Get domains from arguments or file
    domains = []
    if args.file:
        domains = read_domains_from_file(args.file)
    elif args.domains:
        domains = args.domains
    else:
        parser.print_help()
        return
    
    if not domains:
        print(f"{Colors.RED}❌ No domains provided{Colors.END}")
        return
    
    # Initialize tool
    tool = WhoisLookupTool(rate_limit=args.rate_limit, max_workers=args.workers)
    
    # Perform lookups
    results = tool.lookup_domains(domains)
    
    if not results:
        return
    
    # Display results
    if args.detailed:
        tool.print_detailed_results(results)
    else:
        tool.print_results_table(results)
    
    # Export if requested
    if args.export:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        if args.export == 'csv':
            filename = f"whois_results_{timestamp}.csv"
            tool.export_to_csv(results, filename)
        elif args.export == 'json':
            filename = f"whois_results_{timestamp}.json"
            tool.export_to_json(results, filename)

if __name__ == "__main__":
    main()