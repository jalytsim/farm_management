"""
seed_orders.py — commandes de démonstration pour tester les écrans de vente.

À placer à la RACINE du projet, à côté de run.py / wsgi.py.

    python seed_orders.py            # crée ~60 commandes sur 120 jours
    python seed_orders.py 150        # crée 150 commandes
    python seed_orders.py --clean    # supprime UNIQUEMENT les données de test

Deux garde-fous importants :

  1. Chaque commande créée porte `dpo_trans_ref = "SEED-<uuid>"`. C'est la
     marque qui permet de tout supprimer proprement plus tard. Aucune vraie
     commande ne peut être touchée par --clean.

  2. Le script NE TOUCHE PAS AU STOCK et n'écrit aucun StockMovement. Des
     commandes fictives ne doivent pas vider ton catalogue réel. En
     contrepartie, la colonne « stock restant » du tableau des produits
     vendus reflétera ton stock réel, pas un stock diminué par ces ventes —
     c'est voulu.

Ne jamais lancer ce script en production.
"""

import random
import sys
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from app import create_app, db
from app.models import EcoProduct, EcoOrder, EcoOrderItem

SEED_PREFIX = "SEED-"

# Répartition réaliste des statuts. La majorité des paniers aboutit, mais il
# faut assez d'abandons et d'annulations pour que le camembert et le taux de
# paiement aient du sens à l'écran.
STATUS_WEIGHTS = [
    ('delivered', 32),
    ('shipped', 18),
    ('paid', 20),
    ('pending', 14),
    ('payment_failed', 6),
    ('cancelled', 6),
    ('refunded', 4),
]

FIRST_NAMES = ['Grace', 'Samuel', 'Aina', 'Miora', 'Tiana', 'Joseph', 'Hanta',
               'Rivo', 'Naina', 'Faniry', 'Lova', 'Sitraka', 'Anja', 'Toky']
LAST_NAMES = ['Rakoto', 'Andria', 'Rasoa', 'Randria', 'Ranaivo', 'Razafy',
              'Nakato', 'Okello', 'Mwangi', 'Otieno']
CITIES = ['Antananarivo', 'Mahajanga', 'Toamasina', 'Fianarantsoa',
          'Kampala', 'Nairobi', 'Hamburg', 'Rotterdam', 'Melbourne']


def weighted_status():
    population = [s for s, _ in STATUS_WEIGHTS]
    weights = [w for _, w in STATUS_WEIGHTS]
    return random.choices(population, weights=weights, k=1)[0]


def random_quantity(product):
    """Une quantité que le produit accepterait réellement.

    On respecte min_order_qty et order_step : un lot part entier, un vrac au
    pas configuré. Le tableau des produits vendus afficherait sinon des
    quantités impossibles pour ce mode de vente.
    """
    minimum = Decimal(str(product.min_order_qty or 1))
    step = Decimal(str(product.order_step or 1))

    if product.sale_mode == 'lot':
        return minimum

    steps = random.randint(0, 6)
    return minimum + step * steps


def clean(app):
    with app.app_context():
        orders = EcoOrder.query.filter(
            EcoOrder.dpo_trans_ref.like(f"{SEED_PREFIX}%")).all()

        if not orders:
            print("Aucune commande de test à supprimer.")
            return

        count = len(orders)
        for order in orders:
            # Les EcoOrderItem partent en cascade (cascade='all, delete-orphan'
            # sur la relation), rien à supprimer à la main.
            db.session.delete(order)
        db.session.commit()
        print(f"{count} commandes de test supprimées.")


def seed(app, target):
    with app.app_context():
        products = EcoProduct.query.filter_by(is_active=True).all()

        if not products:
            print("Aucun produit actif en base. Crée d'abord quelques produits "
                  "dans /ecoshopmanager, puis relance ce script.")
            return

        print(f"{len(products)} produits actifs trouvés. "
              f"Création de {target} commandes…")

        now = datetime.utcnow()
        created = 0

        for _ in range(target):
            # Étalement sur 120 jours, avec une densité plus forte sur le mois
            # récent : une courbe parfaitement plate ne ressemble à aucune
            # boutique réelle et rend les variations en % illisibles.
            if random.random() < 0.45:
                days_ago = random.randint(0, 30)
            else:
                days_ago = random.randint(31, 120)

            created_at = now - timedelta(
                days=days_ago,
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )

            # Toutes les lignes d'une commande doivent partager la devise :
            # c'est la règle appliquée par _build_order_items au vrai checkout.
            first = random.choice(products)
            same_currency = [p for p in products if p.currency == first.currency]
            line_count = min(random.randint(1, 3), len(same_currency))
            chosen = random.sample(same_currency, line_count)

            status = weighted_status()
            name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            slug = name.lower().replace(' ', '.')

            order = EcoOrder(
                user_id=None,
                guest_name=name,
                guest_email=f"{slug}@example.com",
                guest_phone=f"+261 3{random.randint(0, 9)} "
                            f"{random.randint(10, 99)} "
                            f"{random.randint(100, 999)} {random.randint(10, 99)}",
                shipping_address=f"{random.randint(1, 120)} Rue du Commerce, "
                                 f"{random.choice(CITIES)}",
                total_amount=Decimal('0'),
                currency=first.currency,
                status=status,
                payment_method='dpo',
                dpo_trans_ref=f"{SEED_PREFIX}{uuid.uuid4().hex[:12]}",
                date_created=created_at,
                date_updated=created_at,
            )
            db.session.add(order)
            db.session.flush()

            total = Decimal('0')
            for product in chosen:
                qty = random_quantity(product)
                # unit_price est GELÉ à l'achat dans le vrai flux : on fait
                # varier légèrement le prix pour que la moyenne affichée dans
                # le tableau des produits vendus ne soit pas une constante.
                jitter = Decimal(str(round(random.uniform(0.92, 1.12), 2)))
                unit_price = (Decimal(str(product.price)) * jitter).quantize(Decimal('0.01'))

                db.session.add(EcoOrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=qty,
                    unit_price=unit_price,
                    unit=product.unit,
                ))
                total += unit_price * qty

            order.total_amount = total.quantize(Decimal('0.01'))
            created += 1

        db.session.commit()
        print(f"{created} commandes créées.")
        print(f"Pour tout supprimer plus tard : python {sys.argv[0]} --clean")


if __name__ == '__main__':
    app = create_app()

    if '--clean' in sys.argv:
        clean(app)
    else:
        count = 60
        for arg in sys.argv[1:]:
            if arg.isdigit():
                count = int(arg)
        seed(app, count)