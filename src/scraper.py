"""A little baby data scrapper."""
import requests
import sys
import re
from bs4 import BeautifulSoup


URL = "http://info.kingcounty.gov/health/ehs/foodsafety/inspections/Results.aspx"
PAYLOAD = {"Business_Name": "",
           "Business_Address": "",
           "Longitude": "",
           "Latitude": "",
           "City": "",
           "Zip_Code": "",
           "Inspection_Type": "All",
           "Inspection_Start": "",
           "Inspection_End": "",
           "Inspection_Closed_Business": "A",
           "Violation_Points": "",
           "Violation_Red_Points": "",
           "Violation_Descr": "",
           "Fuzzy_Search": "N",
           "Sort": "B"}


def get_inspection_page(**kwargs):
    """Send GET request to King County Health Inspection API.
    The request will use the kwargs to fill out the requests parameters as the
    user specifies and fill in any unspecified ones with any required default
    values.
    """
    new_params = PAYLOAD.copy()
    new_params.update(kwargs)
    response = requests.get(URL, params=new_params)
    response.raise_for_status()
    return response.content


def load_inspection_page():
    """Open the inspection_page.html and read it.
    The purpose of this function is to keep the user from having to make
    repeated requests at the KCHI API which has a tendency to not like
    the attention. It will return a bytes version and a string version
    of the HTML.
    """
    with open('inspection_page.html') as f:
        content = f.read()
        return content


def parse_source(content):
    """."""
    parsed = BeautifulSoup(content, "lxml")
    return parsed


def extract_data_listings(parsed):
    """."""
    content_id = re.compile(r'PR[\d]+~')
    return parsed.find_all('div', id=content_id)


def has_two_tds(elem):
    """."""
    tr = elem.name == "tr"
    td = elem.find_all("td")
    has_two = len(td) == 2
    return tr and has_two


def clean_data(cell):
    """."""
    clean_list = list(cell.stripped_strings)
    if clean_list != []:
        return "".join(clean_list).strip(" \n:-")
    else:
        return ""


if __name__ == "__main__":
    kwargs = {
        "Inspection_Start": "01/01/2015",
        "Inspection_End": "01/01/2017"
    }
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        content = load_inspection_page()
    else:
        content, encoding = get_inspection_page(**kwargs)
    doc = parse_source(content)
    listings = extract_data_listings(doc)
    for listing in listings:
        metadata_rows = listing.find('tbody').find_all(
            has_two_tds, recursive=False
        )
        for row in metadata_rows:
            for td in row.find_all('td', recursive=False):
                print(clean_data(td))
        print()
