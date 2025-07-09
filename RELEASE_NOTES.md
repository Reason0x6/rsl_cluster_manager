# Release Notes 

# V2.0
---
## Summary of Changes
This major release introduces ClashScore management for Hydra and Chimera activities, enhanced UI/UX for modals, and improved data integrity features. Below are the details for each changed file.

### `models.py`
* **ClashScore Model**: Added `type` field (choices: "hydra", "chimera") and ForeignKey fields (`hydra_activity`, `chimera_activity`) to reference HydraClash and ChimeraClash activities.
* **Player Model**: Updated fields for multi-select difficulties and added JSONField for storing additional data.

### `clan_detail.html`
* **Scores Modal**: Updated modal to be full-screen and scrollable, moved JSON input form into an accordion, and added a searchable table for scores.
* **UI Enhancements**: Improved layout and readability of clan stats and activity records.

### `player_detail.html`
* **ClashScores Display**: Added a table and Chart.js graph to display player's Hydra and Chimera scores.
* **Template Logic**: Updated context variable usage for displaying scores by type.

### `player_list.html`
* **Search Bar**: Made the search bar twice as wide for better usability.
* **UI Improvements**: Enhanced modal forms for adding and importing players, including detailed JSON examples.

### `views.py`
* **create_clash_scores Endpoint**: Processes JSON input, links ClashScores to activities and players, and prevents duplicate scores for the same player/activity.
* **get_activity_scores Endpoint**: Returns scores from related `clash_scores` instead of `opponent_scores`.

### `generic_activity_form.html`
* **Opponent Scores**: Updated input fields to allow decimal values for scores.
* **JavaScript Logic**: Enhanced `updateScores` function to ensure scores are stored as decimals.

### Migrations
* **0029_clashscore_type_delete_cvcrecord.py**: Added `type` field to ClashScore model and removed unused CvCRecord model.
* **0030_clashscore_chimera_activity_and_more.py**: Added ForeignKey fields to ClashScore model for linking HydraClash and ChimeraClash activities.

### General Improvements
* **Django Admin**: Registered ClashScore and all other models for better management.
* **JavaScript**: Refactored logic for modals and tables to use precomputed JSON data for rendering.
* **Extraction Modal**: Added AI-based data extraction modal for images on the clan details page.
* **Backend Extraction Endpoint**: Updated to show actual player names in prompts and POST clan ID for extraction endpoints.

# V1.2
---
## Summary of Changes
This release includes improvements to the player management UI, sorting and import features, and minor workflow and codebase cleanups. Below are the details for each changed file.

### `publish.yml`
* **Docker Tagging**: The Docker image tag is now set to use `${{ github.ref_name }}` instead of the full output from the metadata action, ensuring more predictable and branch-specific tags.

### `models.py`
* **Player Model**: Added an explicit `Meta` class with ordering by `name` to ensure consistent player ordering throughout the application.

### `base.html`
* **Sidebar Navigation**: The "Manage Players" link now points to the player list instead of the player creation page, improving navigation consistency.

### `clan_detail.html`
* **Stats Cards**: Updated the stats section to use a compact card layout for Members, Power, Hydra, and Chimera, improving readability.
* **Player Search**: Enabled the player search input (was previously disabled).
* **Optimiser Link**: Only shows the "View Account" link if the optimiser link is not `None`.
* **Player Table Filtering**: Improved the JavaScript for filtering and paginating the player table, ensuring accurate search and pagination behavior.

### `clan_form.html`
* **Player Table Sorting**: Added sortable columns for player selection, name, and power. Default sort is by selected players.
* **Bulk Import**: Button now reads "Bulk Import Players" for clarity.
* **Sorting Logic**: Enhanced JavaScript to support sorting by selected status, name, and power.
* **UI Consistency**: Minor tweaks to table headers and import modal for clarity and usability.

### `create_siege_plan.html`
* **JSON Example**: Added a sample JSON format for siege plan creation to guide users.

### `home.html`
* **Clan Card Actions**: Updated the "View" and "Edit" buttons for a more compact, mobile-friendly layout.
* **Removed Redundant Button**: The "Manage Players" button below the clan grid was removed for a cleaner interface.

### `player_list.html`
* **Add Player Modal**: Added a modal form for adding players directly from the player list page.
* **Import Modal**: Improved the import modal with a more detailed JSON example and better error handling.
* **Table Sorting**: Added sortable columns for player name, power, and clan.
* **UI Cleanup**: Removed unused filter button and streamlined the action buttons.
* **JavaScript**: Enhanced sorting and searching logic for better UX.

### `urls.py`
* **Removed Unused Route**: The `player_create` URL pattern was removed, as player creation is now handled via modal on the player list page.

### `views.py`
* **PlayerListView**: Now supports both GET and POST, allowing player creation directly from the player list page. The context includes the player form for modal usage.
# V1.1
  - Improved login experience: After successful login, users are redirected to the home page (`/`).
  - Login page is now fully stylized and matches the application's dark theme.
  - Fixed: Login page no longer references a missing password reset URL.
  - Added `/accounts/login/` route for Django authentication.
  - All tables in the anonymous dashboard and player management are now sortable by clicking column headers.
  - Clan member tables in the anonymous dashboard are now hidden if the clan has no players.
  - Clan member tables are now displayed in a two-column grid, one table per clan, showing only player names and power.
  - Added basic clan info and clan/player tables to the anonymous dashboard after the cluster comparison graphs.
  - Anonymous dashboard now displays cluster comparison graphs (CvC, Hydra, Chimera, Siege).
  - All endpoints that create, edit, modify, or delete data now require authentication.
  - Siege position is now a dropdown (Loss/Win) in siege forms.
  - Added utility to remove a team type by name or value.

# V1.0

## Features

- **Player Management**
  - Add, edit, delete, and import players.
  - Bulk player import via JSON with validation and error feedback.
  - Assign players to clans and manage their team types.
  - Inline editing of player data in the manage cluster view.

- **Clan Management**
  - Create, edit, and view clans.
  - Assign/remove players to/from clans, ensuring each player is only in one clan at a time.
  - Track clan boss levels, hydra/chimera requirements, and CVC thresholds.

- **Activities Tracking**
  - Record and edit CvC, Hydra, Chimera, and Siege activities for each clan.
  - Custom forms for each activity type, including date pickers and dropdowns.
  - Siege position input as a Win/Loss dropdown.
  - Hydra/Chimera activity supports multi-clan score entry.

- **Siege Plans**
  - Create, assign, export, and delete siege plans for clans.
  - Assign players and team types to siege posts.

- **Arena Teams**
  - Manage arena teams for each player, linked to their available team types.

- **Cluster Dashboard**
  - Dashboard with summary stats for all clans.
  - Visual charts for CvC, Hydra, Chimera, and Siege performance over time.
  - Recent siege plans and quick navigation.

- **User Experience**
  - Responsive, modern UI with Tailwind CSS and FontAwesome icons.
  - Modal dialogs for importing players.
  - Search, filter, and sort functionality for player and clan lists.
  - Pagination for large player and siege plan lists.

- **Admin & Utilities**
  - Django admin integration for all models.
  - Management command to create initial team types.
  - Utility to remove team types by name or display value.

## Bug Fixes & Improvements

- Robust JSON import with clear error messages for invalid data.
- Ensured player-clan relationships are always consistent.
- Improved deletion flows for players, activities, and siege plans.
- Added date pickers and dropdowns for better data entry.
- Fixed issues with CSRF token handling in AJAX requests.
- Improved accessibility and keyboard navigation.

## Upgrade Notes

- Run migrations to update models and fields.
- Use the management command to initialize team types if upgrading from an earlier version.
- Review and update your JSON import data to match the documented format.

---

Thank you for using Raid Clan Manager!

# V0.1

## Features & Improvements

- **Player Management Table**
  - Editable player management table with inline saving and auto-refresh after changes.
  - Table layout improved for compactness and clarity.
  - Conditional styling for selected clan tabs.
  - Multi-select support for hydra/chimera difficulties.
  - Clan selection now updates both the player's clan and the clan's player list.

- **Team Types**
  - Management command `create_team_types` to initialize all team types.
  - Added a management command to remove orphaned team types from players.
  - Improved `TeamType.__str__` to avoid KeyError for missing choices.
  - Added utility to clean up player-team type relations for deleted team types.

- **Clans & Players**
  - Fixed reverse accessor clashes for ForeignKey and ManyToMany relations.
  - Improved synchronization between `Player.clan` and `Clan.players`.
  - Added support for nullable clan fields and proper handling in forms/views.

- **General**
  - Improved error handling for decimal fields and empty values.
  - Added instructions for running management commands and Django shell.
  - Docker instructions for running `app.py` on container start.

## Bug Fixes

- Fixed KeyError in `TeamType.__str__` when a team type is missing from choices.
- Fixed Django system check errors for reverse accessor clashes.
- Fixed issues with saving empty decimal fields.
- Fixed issues where changing a player's clan did not update the clan's player list.
- Fixed template errors with Python-style inline if/else in Django templates.

## DevOps

- Added management commands for team type creation and orphan cleanup.
- Provided Docker and docker-compose instructions for app startup.

---

*For details on any feature or fix, see the corresponding commit or file change.*

# Release Notes

## v0.2

### Features & Improvements

- **Dashboard Graphs:**  
  Added interactive graphs to the home dashboard comparing clans' CvC, Hydra, Chimera, and Siege points over time.  
  Uses Chart.js with date-fns adapter for time-based axes.

- **Player Management Table:**  
  Editable player management table with inline saving and auto-refresh after changes.  
  Improved table layout for compactness and clarity.

- **Team Types Management:**  
  Management command `create_team_types` to initialize all team types.  
  Added utility to remove orphaned team types from players.

- **Clans & Players:**  
  Fixed reverse accessor clashes for ForeignKey and ManyToMany relations.  
  Improved synchronization between `Player.clan` and `Clan.players`.  
  Added support for nullable clan fields and proper handling in forms/views.

- **General:**  
  Improved error handling for decimal fields and empty values.  
  Added instructions for running management commands and Django shell.  
  Docker instructions for running `app.py` on container start.

### Bug Fixes

- Fixed Chart.js date adapter error and date format warning on the home dashboard graphs.
- Fixed KeyError in `TeamType.__str__` when a team type is missing from choices.
- Fixed Django system check errors for reverse accessor clashes.
- Fixed issues with saving empty decimal fields.
- Fixed issues where changing a player's clan did not update the clan's player list.
- Fixed template errors with Python-style inline if/else in Django templates.
- Fixed Django template errors related to default filters and RelatedManager iteration.
- Improved ManyToMany and ForeignKey related_name usage to avoid Django system check errors.

---

*For details on any feature or fix, see the corresponding commit or file change.*
