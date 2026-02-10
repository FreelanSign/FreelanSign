"""Address formatting utility for legal terms.

# AIDEV-NOTE: Address formatting for legal terms - mirrors PDF generation pattern
"""


def format_address(
    address_line1: str | None,
    address_line2: str | None,
    city: str | None,
    postal_code: str | None,
    country: str | None,
) -> str:
    """Format address components into a single string.

    Reuses pattern from download_pdf.py for consistency.
    Returns "Adresse à compléter" if all fields are empty/None.

    Args:
        address_line1: First line of address
        address_line2: Second line of address (optional)
        city: City name
        postal_code: Postal code
        country: Country name or code

    Returns:
        Formatted address string or placeholder if all empty
    """
    # Collect non-empty address lines
    address_parts = [p for p in [address_line1, address_line2] if p and p.strip()]

    # Collect location parts (postal + city)
    location_parts = [p for p in [postal_code, city] if p and p.strip()]

    if location_parts:
        address_parts.append(" ".join(location_parts))

    # Add country if present (uppercase)
    if country and country.strip():
        address_parts.append(country.upper())

    # Return formatted address or placeholder
    return ", ".join(address_parts) if address_parts else "Adresse à compléter"
