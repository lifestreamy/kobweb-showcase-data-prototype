import json
import os

# Get the issue number to revoke
issue_id = int(os.environ['ISSUE_NUMBER'])
file_path = 'resources/showcase/showcased-sites.json'

# Read the current array
with open(file_path, 'r') as file:
    sites = json.load(file)

original_length = len(sites)

# Keep only the sites that don't match this issue ID
updated_sites = [site for site in sites if site.get('issueNumber') != issue_id]

# Save the filtered array back to the file if length changed, else "Not Found" status will be commented
if len(updated_sites) < original_length:
    with open(file_path, 'w') as file:
        json.dump(updated_sites, file, indent=2)
    action_result = "revoked"
else:
    action_result = "not_found"

with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
    f.write(f"action_result={action_result}\n")