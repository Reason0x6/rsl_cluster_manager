# Raid Clan Manager

A Django web application for managing Raid: Shadow Legends clans, players, activities, and siege plans.

## Features

- **Player Management:** Add, edit, delete, and import players. Assign team types and clans.
- **Clan Management:** Create, edit, and view clans. Assign/remove players, track boss levels, and manage thresholds.
- **Activity Tracking:** Record and edit CvC, Hydra, Chimera, and Siege activities for each clan.
- **Siege Plans:** Create, assign, export, and delete siege plans for clans.
- **Arena Teams:** Manage arena teams for each player, linked to their available team types.
- **Dashboard:** Overview of all clans, recent activities, and performance charts.
- **Bulk Import:** Import players in bulk via JSON.
- **Modern UI:** Responsive design with Tailwind CSS and FontAwesome icons.

## Getting Started

### Prerequisites

- Python 3.8+
- Django 3.2+
- PostgreSQL (recommended for JSON fields)
- Node.js (for Tailwind CSS, optional if using CDN)

### Installation

1. **Clone the repository:**
   ```
   git clone https://github.com/yourusername/raid-clan-manager.git
   cd raid-clan-manager
   ```

2. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

3. **Configure your database** in `settings.py`.

4. **Apply migrations:**
   ```
   python manage.py migrate
   ```

5. **Create initial team types:**
   ```
   python manage.py create_team_types
   ```

6. **Create a superuser:**
   ```
   python manage.py createsuperuser
   ```

7. **Run the development server:**
   ```
   python manage.py runserver
   ```

8. **Access the app:**  
   Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

## Usage

- Use the sidebar to navigate between clans, players, siege plans, and dashboards.
- Import players using the "Import Players" button and paste your JSON data.
- Manage player data and clan assignments from the "Manage Cluster" page.
- Record activities and siege results from each clan's detail page.

## Development

- **Static files:** Uses Tailwind CSS via CDN for rapid prototyping.
- **Custom management commands:** See `clans/management/commands/`.
- **Extensible models:** Add new activity types or player fields as needed.

## Contributing

Pull requests are welcome! Please open an issue first to discuss your ideas.

## License

MIT License

---

*This project is not affiliated with Plarium or Raid: Shadow Legends.*
