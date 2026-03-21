# kobweb-showcase-data-prototype

## Showcase Management Commands

`resources/showcase/showcased-sites.json` acts as a database, storing user submissions. It is modified not directly, but by GitHub Actions driven by GitHub Issues, following the official GitHub IssueOps pattern.

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