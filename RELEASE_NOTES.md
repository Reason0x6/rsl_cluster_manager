# Release Notes 
#V1.0

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
