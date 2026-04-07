import json
import os
import sys


def fail(msg):
    print(f"::error::{msg}")
    with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
        f.write(f"error_msg={msg}\n")
    sys.exit(1)


# Helper for extracting text from the zentered JSON structure
def get_text(key):
    field = parsed_data.get(key, {})
    if isinstance(field, dict):
        text = field.get('text', '')
        return '' if text.strip(' _*') == 'No response' else text
    if isinstance(field, list):
        return ';'.join(field)
    return '' if field.strip(' _*') == 'No response' else str(field)


parsed_data_str = os.environ.get('PARSED_DATA', '{}')

try:
    parsed_data = json.loads(parsed_data_str)
    if isinstance(parsed_data, str):
        parsed_data = json.loads(parsed_data)
except Exception as e:
    fail(f"Failed to parse JSON data from GitHub Action: {e}")

issue_id = int(os.environ['ISSUE_NUMBER'])

# Format URL (Auto-append https:// if missing ; remove <> around links that GitHub can put)
raw_site_url = get_text('live-url').strip().strip('<>')
# work around GitHub automatically putting []() brackets around urls
if '](' in raw_site_url:
    raw_site_url = raw_site_url.split('](', 1)[1].split(')', 1)[0].strip()
clean_site_url = raw_site_url if raw_site_url.startswith(('http://', 'https://')) else f"https://{raw_site_url}"

raw_body = os.environ.get('RAW_ISSUE_BODY', '')
clean_image_url = ""

if 'src="' in raw_body:
    src_value = raw_body.split('src="', 1)[1].split('"', 1)[0].strip()
    if '](' in src_value:
        clean_image_url = src_value.split('](', 1)[1].split(')', 1)[0].strip()
    else:
        clean_image_url = src_value

# Format features (tags are inputted having been split with a semicolon ";")
features = get_text('core-features')
custom_features = get_text('other-keywords')
raw_features = f"{features};{custom_features}"
clean_tags = [tag.strip() for tag in raw_features.split(';') if tag.strip() != 'None' and tag.strip()]

site_name = get_text('project-name').strip()

# Validation: check for empty critical fields
if not site_name:
    fail("Validation Failed: Site name cannot be empty.")

if not clean_site_url or clean_site_url == "https://":
    fail("Validation Failed: Invalid or missing Site URL.")

if not clean_image_url:
    fail("Validation Failed: Invalid or missing Image URL.")

# Build the new site dict
new_site = {
    "issueNumber": issue_id,
    "name": site_name,
    "url": clean_site_url,
    "imageUrl": clean_image_url,
    "description": get_text('project-description').strip(),
    "tags": clean_tags
}

file_path = 'resources/showcase/showcased-sites.json'

# Read current JSON array, append the new site, save
with open(file_path, 'r') as file:
    sites = json.load(file)

existing_index = next((i for i, site in enumerate(sites) if site.get("issueNumber") == issue_id), -1)

if existing_index >= 0:
    if sites[existing_index] == new_site:
        action_result = "unchanged"
    else:
        sites[existing_index] = new_site
        action_result = "updated"
else:
    sites.append(new_site)
    action_result = "added"

if action_result != "unchanged":
    with open(file_path, 'w') as file:
        json.dump(sites, file, indent=2)

with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
    f.write(f"action_result={action_result}\n")