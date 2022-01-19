# Ragtime

Ragtime is a social app created with Flask for users to post new "music" as a composition. Register an account and start sharing your compositions on the blog or follow other users to see their work!

## Migrations
Whenever a database migration needs to be made. Run the following commands
```bash
flask db migrate
```
This will generate a new migration script. Then run
```bash
flask db upgrade
```
To apply the migration.

For a full migration command reference, run flask db --help.