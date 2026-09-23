# Jingum reinspection tracker — MariaDB deployment

This is a small internal Flask application with a single-file frontend and a MariaDB database.
No frontend build step is required.

## Setup

Create the database and application user:

Edit the password placeholder in `mariadb_setup.sql`, then run it as a MariaDB administrator:

```bash
mariadb -u root -p < mariadb_setup.sql
```

Equivalent SQL:

```sql
CREATE DATABASE jingum CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'jingum'@'%' IDENTIFIED BY 'replace-with-a-strong-password';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE ON jingum.* TO 'jingum'@'%';
FLUSH PRIVILEGES;
```

Copy `.env.example` to `.env`, then set `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, and
`DB_PASSWORD`, then install the dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If an existing `data.db` must be migrated, complete the migration below **before the first
application start**. Otherwise, start the server with `python app.py`. It listens on port
8000 by default, creates the `records` table automatically, and loads `seed_data.json` only
when that table is empty.

## Running with PM2

The included ecosystem file runs the application through Waitress using the virtual
environment's Python interpreter:

```bash
npm install -g pm2
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
pm2 start ecosystem.config.js
pm2 logs Jingum_Web
pm2 save
```

On Linux, run `pm2 startup`, execute the command it prints, and run `pm2 save` again.
Set `JINGUM_PYTHON` before starting PM2 if the virtual environment is stored elsewhere.

## Migrating an existing SQLite database

Back up both databases and run:

```powershell
python migrate_sqlite_to_mariadb.py data.db
```

The migration stops if MariaDB already contains records. Use `--overwrite` only when matching
MariaDB records may safely be replaced. Keep the SQLite backup until the migrated data and UI
have been verified.

For detailed Vietnamese deployment and operations instructions, see `README_VI.md`.
