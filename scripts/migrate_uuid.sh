#!/usr/bin/env bash

if [ $# -ne 1 ]; then
  echo "Usage: $0 /path/to/iou.db"
  exit 1
fi

DB_PATH=$1
backup_db="${DB_PATH}.$(date "+%Y%m%d.%H%M%S")"


# 1. Dump the database, and save only INSERT operations on user tables and some django tables:

for table in \
  auth_user \
  auth_user_groups \
  auth_user_user_permissions \
  django_admin_log \
  django_session \
  iou_debt; do

  sqlite3 "${DB_PATH}" -cmd ".mode insert" -cmd ".headers on" "SELECT * FROM $table" \
    | sed "s/INSERT INTO \"table\"/INSERT INTO \"$table\"/"
done > iou.dump

# 2. Delete the database.
mv "${DB_PATH}" "${backup_db}"

# 3. Migrate the database up to, and not including, the addition of the uuid field:

python manage.py migrate iou 0003
python manage.py migrate admin
python manage.py migrate sessions

# 4. Import the dump:

cat iou.dump |sqlite3 "${DB_PATH}"

# 5. Finish the migrations to add the uuid field:

python manage.py migrate
