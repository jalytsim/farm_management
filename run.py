from app import create_app

def list_routes(app):
    print("\n📍 Liste des routes disponibles :")
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
        print(f"{rule.endpoint:30s} [{methods}] {rule.rule}")
    print("-" * 50)

app = create_app()

if __name__ == '__main__':
    list_routes(app)  
    app.run(host='0.0.0.0', debug=True)
