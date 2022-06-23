from webapp import create_app

app = create_app()

# Run the web appilcation only if we run this file
if __name__ == '__main__':

    # Automatically rerun the web application if changes are made
    app.run(debug=True)