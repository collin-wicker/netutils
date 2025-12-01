"""Script to fetch the latest OUI data from IEEE and update the local OUI mappings file."""

import csv
import requests
from io import StringIO
from jinja2 import Template


def clean_text(text):
    """
    Removes double quotes from the input text.
    """
    cleaned = text.replace('"', '').strip()
    return cleaned


def fetch_oui_data():
    """Fetches the latest OUI data from the IEEE website and returns it as a dictionary."""
    url = "https://standards-oui.ieee.org/oui/oui.csv"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code >= 200 and response.status_code < 300:
        csv_data = StringIO(response.content.decode("utf-8"))
        reader = csv.DictReader(csv_data)
        oui_dict = {}
        for row in reader:
            assignment = row['Assignment'].lower()
            organization_name = row['Organization Name']
            oui_dict[assignment] = organization_name
    else:
        print(f"Failed to download OUI data. Status code: {response.status_code}")
        oui_dict = {}
    return oui_dict


def populate_template(oui_mappings: dict):
    """Populates the Jinja2 template for OUI mappings."""
    template_content = ""
    with open("oui_mappings.j2", "r") as template_file:
        template_content = template_file.read()

    template = Template(template_content)
    rendered_content = template.render(assignments=[{"oui": oui, "org": clean_text(org)} for oui, org in oui_mappings.items()])

    with open("../netutils/data_files/oui_mappings.py", "w", encoding="utf-8") as output_file:
        output_file.write(rendered_content)
    print("OUI mappings have been updated successfully.")


def sort_ouis(oui_dict):
    """
    Sorts a dictionary of 6-character hexadecimal OUI keys.
    Returns a new dictionary with keys sorted in ascending hexadecimal order.
    Example: {'A1B2C3': 'foo', '001A2B': 'bar'} -> {'001A2B': 'bar', 'A1B2C3': 'foo'}
    """
    return {k: oui_dict[k] for k in sorted(oui_dict.keys(), key=lambda x: int(x, 16))}


if __name__ == "__main__":
    oui_mappings = fetch_oui_data()
    if oui_mappings:
        oui_mappings = sort_ouis(oui_mappings)
        populate_template(oui_mappings)
