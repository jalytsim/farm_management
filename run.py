import sys

# ── Fix (crash au démarrage) ─────────────────────────────────────────────────
# La console Windows par défaut (cp1252/cp850) ne sait pas encoder les emoji
# utilisés dans de nombreux print() du projet (✅ ❌ ⚠️ …). Sans ce correctif,
# le tout premier print() de ce type levait UnicodeEncodeError et faisait
# planter le process AVANT même que Flask ne démarre — d'où un serveur qui
# semblait "tourner" (ancien process resté ouvert) mais ne répondait plus aux
# nouvelles routes.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from app import create_app

# def list_routes(app):
#     print("\n📍 Liste des routes disponibles :")
#     for rule in app.url_map.iter_rules():
#         methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
#         print(f"{rule.endpoint:30s} [{methods}] {rule.rule}")
#     print("-" * 50)

app = create_app()

if __name__ == '__main__':
    # list_routes(app)  
    app.run(host='0.0.0.0', debug=True)
