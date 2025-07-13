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

# RSL Clan Manager Project

## Overview
The RSL Clan Manager is a Django-based application designed to manage clans, players, and scores for Hydra and Chimera clashes. This guide will walk you through setting up the project using Docker.

## Prerequisites
Before you begin, ensure you have the following installed:

- Docker: [Install Docker](https://docs.docker.com/get-docker/)
- Docker Compose (optional): [Install Docker Compose](https://docs.docker.com/compose/install/)

## Setup Instructions

### Step 1: Clone the Repository
Clone the project repository to your local machine:

```bash
git clone https://github.com/Reason0x6/rsl_cluster_manager.git
cd rsl_cluster_manager
```

### Step 2: Build the Docker Image
Build the Docker image for the project:

```bash
docker build -t rsl-clan-manager .
```

### Step 3: Create a Volume for the Database
Create a Docker volume to persist the SQLite database:

```bash
docker volume create rsl-clan-manager-db
```

### Step 4: Run the Container
Run the Docker container, mounting the volume at `/app/db`. If this is the first time setting up the application, enable the `FIRST_TIME_SETUP` flag to create the database:

```bash
docker run -d \
  -p 8000:8000 \
  -v rsl-clan-manager-db:/app/db \
  -e FIRST_TIME_SETUP=true \
  --name rsl-clan-manager \
  rsl-clan-manager
```

For subsequent runs, you can omit the `FIRST_TIME_SETUP` flag:

```bash
docker run -d \
  -p 8000:8000 \
  -v rsl-clan-manager-db:/app/db \
  --name rsl-clan-manager \
  rsl-clan-manager
```

### Step 5: Access the Application
Once the container is running, you can access the application at:

```
http://localhost:8000
```

### Step 6: Manage the Database
The SQLite database file is stored in the mounted volume at `/app/db`. You can access it using SQLite tools or by inspecting the volume:

```bash
docker inspect rsl-clan-manager-db
```

## Additional Commands

### Stop the Container
To stop the running container:

```bash
docker stop rsl-clan-manager
```

### Remove the Container
To remove the container:

```bash
docker rm rsl-clan-manager
```

### Rebuild the Image
If you make changes to the code and need to rebuild the image:

```bash
docker build -t rsl-clan-manager .
```

### Logs
To view the container logs:

```bash
docker logs rsl-clan-manager
```

## Environment Variables

The application requires the following environment variables to be set:

- `GOOGLE_API_KEY`: API key for Google services. This is mandatory.
- `DJANGO_SECRET_KEY`: Secret key for Django. If not set, the default value in `settings.py` will be used (Insecure).
- `DJANGO_ALLOWED_HOSTS`: Comma-separated list of allowed hosts. If not set, the default value in `settings.py` will be used.
- `DJANGO_CSRF_TRUSTED_ORIGINS`: Comma-separated list of trusted origins for CSRF protection. If not set, the default value in `settings.py` will be used.

### Example

To set these variables in a Docker container, use the `-e` flag:

```bash
docker run -d \
  -p 8000:8000 \
  -v rsl-clan-manager-db:/app/db \
  -e GOOGLE_API_KEY=your-google-api-key \
  -e DJANGO_SECRET_KEY=your-django-secret-key \
  -e DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1 \
  -e DJANGO_CSRF_TRUSTED_ORIGINS=https://localhost,https://127.0.0.1 \
  -e GOOGLE_API_KEY=12345678-ABCDEF
  --name rsl-clan-manager \
  rsl-clan-manager
```

## Notes
- Ensure the `SECRET_KEY` in `settings.py` is updated for production.
- For production, consider using a more robust database like PostgreSQL.
- Update `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` in `settings.py` to match your deployment environment.

## Troubleshooting
If you encounter issues, check the following:

- Ensure Docker is running.
- Verify the volume is correctly mounted.
- Check the container logs for errors:

```bash
docker logs rsl-clan-manager
```

For further assistance, consult the [Django documentation](https://docs.djangoproject.com/en/stable/) or the [Docker documentation](https://docs.docker.com/).
