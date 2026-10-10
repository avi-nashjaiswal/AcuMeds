#!/usr/bin/env python3
"""Reset a user's password in the shared SQLite database.

Usage examples:
  python scripts/reset_db_password.py --username admin
  python scripts/reset_db_password.py --email admin@example.com --password "NewP@ssw0rd"

This script updates the `password_hash` field in the `users` table using
Werkzeug's `generate_password_hash` with `pbkdf2:sha256` to match the app.
"""
import argparse
import sqlite3
import sys
from getpass import getpass
from pathlib import Path

try:
    from werkzeug.security import generate_password_hash
except Exception as e:
    print("Please run this script inside your project virtualenv where 'werkzeug' is installed.")
    raise


DEFAULT_DB = Path(__file__).resolve().parents[2] / 'admin_system' / 'database' / 'pharmacy.db'


def parse_args():
    p = argparse.ArgumentParser(description='Reset a user password in the AcuMeds SQLite DB')
    p.add_argument('--db', default=str(DEFAULT_DB), help='Path to SQLite DB (default: admin_system/database/pharmacy.db)')
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument('--username', help='Username to update')
    group.add_argument('--email', help='Email to update')
    p.add_argument('--password', help='New password (if omitted, will prompt)')
    return p.parse_args()


def main():
    args = parse_args()
    db_path = Path(args.db)
    if not db_path.exists():
        print(f"Database not found: {db_path}")
        sys.exit(2)

    if args.password:
        new_password = args.password
    else:
        new_password = getpass('Enter new password: ')
        confirm = getpass('Confirm new password: ')
        if new_password != confirm:
            print('Passwords do not match. Aborting.')
            sys.exit(3)

    hashed = generate_password_hash(new_password, method='pbkdf2:sha256')

    where_clause = ''
    params = None
    if args.username:
        where_clause = 'username = ?'
        params = (hashed, args.username)
    else:
        where_clause = 'email = ?'
        params = (hashed, args.email)

    sql = f"UPDATE users SET password_hash = ? WHERE {where_clause}"

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(f"SELECT id, username, email FROM users WHERE {where_clause}", (params[1],))
    row = cur.fetchone()
    if not row:
        print('No matching user found. Nothing changed.')
        conn.close()
        sys.exit(4)

    user_id, username, email = row
    print(f"Updating password for user id={user_id}, username={username}, email={email}")
    cur.execute(sql, params)
    conn.commit()
    conn.close()
    print('Password updated. Please restart the Flask app if it is running.')


if __name__ == '__main__':
    main()
