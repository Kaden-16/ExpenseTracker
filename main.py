from website import create_app, recreate_database

# Rerun 
if __name__ == '__main__':
    app = create_app()
    recreate_database(app)
    app.run(debug=True)
