# Fully GitHub-hosted database prototype

*A prototype (proof of concept) of a fully GitHub-hosted JSON database, demonstrating how to use GitHub Issue Forms as a user-facing frontend and GitHub Actions as a backend, following the official IssueOps pattern.*

### Customization Disclaimer
This repository is a specific implementation (in this case, for a website showcase), not a library. 

It is not easily customizable; there is no file defining the database schema or automated workflow generation. 

To adapt this prototype for other uses, you must directly modify the Python parsing logic, the Issue Form template, and the GitHub Action workflows.

## The User Submission Pipeline

Instead of hosting a custom web form and external database, this repository relies entirely on **user-created GitHub Issues** for data entry. When a user wants to submit an entry (in this case, a website), they simply fill out the repository's structured Issue Form.

`resources/showcase/showcased-sites.json` acts as the persistent database storing these user submissions. It is not modified directly, but rather through automated workflows triggered by maintainer comments on the user's issue.

## Showcase Management Commands

Maintainers review submissions and use specific commands to trigger database updates. 

The available commands (full reference below) are:
- `/approve`
- `/revoke`

Execution is strictly limited to users with `OWNER`, `COLLABORATOR`, or `MEMBER` roles.

Workflows are concurrency-locked (processed sequentially) to prevent git push race conditions or merge conflicts when multiple issues are managed simultaneously.

### Command Reference

Type the following commands as a standalone comment on a Showcase Submission issue to trigger the bot.

| Command    | Outcome State | Description                                                                                                | Bot Response                                                               |
|:-----------|:--------------|:-----------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------|
| `/approve` | **Added**     | Parses the issue form, validates critical fields (Name, URL, Image), and appends the new site to the JSON. | ✅ The site has been approved and added to the showcase.                    |
| `/approve` | **Updated**   | The issue ID already exists in the JSON, but the form data has changed. Overwrites the existing entry.     | ✅ The site has been successfully updated in the showcase.                  |
| `/approve` | **Unchanged** | The parsed form data perfectly matches the existing JSON entry. Skips the git commit.                      | ✅ Nothing has changed since the last submission, keeping the last version. |
| `/approve` | **Failed**    | Form is missing a critical field or the markdown parser failed. Halts execution.                           | ❌ Approval Failed: [Reason].                                               |
| `/revoke`  | **Revoked**   | Locates the dictionary matching the current issue ID and removes it from the JSON.                         | ✅ The site has been successfully revoked and removed from the showcase.    |
| `/revoke`  | **Not Found** | The issue ID is not present in the JSON. Skips the git commit.                                             | ✅ There is no submission to revoke for this issue.                         |

**Note on Image Parsing:** The bot extracts the primary image (currently limited to the first image found) directly from the raw markdown body by searching for the auto-generated `src=` HTML attribute wrapping the image link. This natively supports standard GitHub image uploads.

**Note on Security:** User input is passed to the scripts strictly via environment variables, mitigating the risk of code injection attacks through form fields.

## Directory Structure

```text
.github/
├── ISSUE_TEMPLATE/
│   └── submit-site.yml         # The "Frontend": GitHub Issue Form template users fill out
├── scripts/
│   ├── approve_showcase.py     # Parses issue data, validates fields, and updates the JSON
│   └── revoke_showcase.py      # Removes an entry from the JSON based on the issue ID
└── workflows/
    ├── approve.yml             # GitHub Action triggered by the `/approve` comment
    └── revoke.yml              # GitHub Action triggered by the `/revoke` comment

resources/showcase/
└── showcased-sites.json        # The "Database": Stores all approved submissions
```
