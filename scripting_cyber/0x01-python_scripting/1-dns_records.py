#!/usr/bin/env python3
"""
DNS record enumerations using dnspython
"""

# pip install dnspython
import dns.resolver


def query_dns_records(domain_name):
    """
    Query Multiple DNS record types for a given domain.
    Args:
        domain_name (str): The domain name to query.
    Returns:
        dict: A dictionary containing the DNS answers for each record type.
              Example: {'A': answers_object, 'MX': answers_object}
              Only successful queries are included.
              Returns an empty dict if no records can be resolved.
    """

    record_types = ["A", "AAAA", "MX", "NS", "TXT", "SOA"]
    results = {}

    for record_type in record_types:
        try:
            answers = dns.resolver.resolve(domain_name, record_type)
            results[record_type] = answers
        except (
            dns.resolver.NoAnswer,
            dns.resolver.NXDOMAIN,
            dns.resolver.NoNameservers,
        ):
            # If no answer is found for this record type, skip it
            continue
        except Exception as e:
            # Handle any other unexpected exceptions
            results[record_type] = f"Error: {e}"
    return results


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 1-dns_records.py <domain_name>")
        sys.exit(1)
    domain_name = sys.argv[1]
    results = query_dns_records(domain_name)
    for record_type, answers in results.items():
        print(f"{record_type} Records:")
        if isinstance(answers, str):
            print(f"  {answers}")
        else:
            for rdata in answers:
                print(f"  {rdata}")
    
    print("\n\nResults dictionary:\n", results)
