from server.config import create_app

app = create_app()


print("Registered routes:")
for rule in app.url_map.iter_rules():
    print(rule)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
