# Release Notes 

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
