#!/usr/bin/env python3

# Test script for the get_reduced_status function
from metrics_collector_class import get_reduced_status, REDUCED_STATUSES


def test_get_reduced_status():
    """Test the get_reduced_status function with all provided statuses."""

    # All statuses from the user's list
    all_statuses = [
        "INITIAL",
        "Response implementation",
        "Control",
        "Triage",
        "Waiting 4 Product",
        "Waiting 4 Order",
        "Reopened",
        "Analysis and Verification",
        "Provide more information",
        "Business need assessment",
        "In Progress",
        "Waiting 4 Deployment",
        "On Hold",
        "TEST",
        "Major Upgrade",
        "Waiting for customer",
        "Audit",
        "Waiting 4 Delivery",
        "Compliant",
        "Planning",
        "Waiting 4 Fix",
        "Response planing",
        "Hibernated",
        "Contain/mitigate",
        "Waiting for Release",
        "Work on resolution",
        "Eradicate/remediate",
        "Identify",
        "Verification",
        "Training in Progress",
        "Ready for development",
    ]

    print("Testing get_reduced_status function:")
    print("=" * 50)

    # Test each status
    for status in sorted(all_statuses):
        reduced = get_reduced_status(status)
        print(f"{status:<30} -> {reduced}")

    print("\n" + "=" * 50)
    print("Testing edge cases:")

    # Test unknown status
    unknown_status = "Some Unknown Status"
    reduced = get_reduced_status(unknown_status)
    print(f"{unknown_status:<30} -> {reduced}")

    # Test empty string
    empty_status = ""
    reduced = get_reduced_status(empty_status)
    print(f"'{empty_status}':<30 -> {reduced}")

    print("\n" + "=" * 50)
    print("Summary by category:")

    # Group statuses by their reduced category
    categories = {}
    for status in all_statuses:
        reduced = get_reduced_status(status)
        if reduced not in categories:
            categories[reduced] = []
        categories[reduced].append(status)

    for category, statuses in sorted(categories.items()):
        print(f"\n{category} ({len(statuses)} statuses):")
        for status in sorted(statuses):
            print(f"  - {status}")


if __name__ == "__main__":
    test_get_reduced_status()
