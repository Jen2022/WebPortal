import os

def delete_migrations():
    for root, dirs, files in os.walk('.'):
        if 'migrations' in dirs:
            migration_dir = os.path.join(root, 'migrations')
            for filename in os.listdir(migration_dir):
                if filename != '__init__.py' and filename.endswith('.py'):
                    file_path = os.path.join(migration_dir, filename)
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")

if __name__ == "__main__":
    delete_migrations()
