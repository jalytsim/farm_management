# ═══════════════════════════════════════════════════════════════════════
# Seed script — Full EUDR HS Code table (Annex I, Regulation (EU) 2023/1115)
# Run once: `python seed_hscodes.py` (from project root, next to app/)
# Legal source: Annex I of Regulation (EU) 2023/1115
# ═══════════════════════════════════════════════════════════════════════
from app import create_app, db
from app.models import HSCode

EUDR_HS_CODES = [
    # ── Cattle ───────────────────────────────────────────────────────
    ("0102 21", "Live cattle, pure-bred breeding animals", "Cattle", False),
    ("0102 29", "Live cattle, other", "Cattle", False),
    ("0201", "Meat of cattle, fresh or chilled", "Cattle", True),
    ("0202", "Meat of cattle, frozen", "Cattle", True),
    ("0206 10", "Edible offal of cattle, fresh or chilled", "Cattle", True),
    ("0206 22", "Edible cattle livers, frozen", "Cattle", True),
    ("0206 29", "Edible cattle offal (excluding tongues and livers), frozen", "Cattle", True),
    ("1602 50", "Other prepared or preserved meat, meat offal or blood, of cattle", "Cattle", True),
    ("4101", "Raw hides and skins of cattle (fresh, salted, dried, limed, pickled or otherwise preserved)", "Cattle", True),
    ("4104", "Tanned or crust hides and skins of cattle, without hair on", "Cattle", True),
    ("4107", "Leather of cattle, further prepared after tanning or crusting", "Cattle", True),

    # ── Cocoa ────────────────────────────────────────────────────────
    ("1801", "Cocoa beans, whole or broken, raw or roasted", "Cocoa", False),
    ("1802", "Cocoa shells, husks, skins and other cocoa waste", "Cocoa", False),
    ("1803", "Cocoa paste, whether or not defatted", "Cocoa", False),
    ("1804", "Cocoa butter, fat and oil", "Cocoa", False),
    ("1805", "Cocoa powder, not containing added sugar or other sweetening matter", "Cocoa", False),
    ("1806", "Chocolate and other food preparations containing cocoa", "Cocoa", False),

    # ── Coffee ───────────────────────────────────────────────────────
    ("0901", "Coffee, roasted or not, decaffeinated or not; coffee husks and skins; coffee substitutes", "Coffee", False),

    # ── Oil palm ─────────────────────────────────────────────────────
    ("1207 10", "Palm nuts and kernels", "Oil palm", False),
    ("1511", "Palm oil and its fractions, refined or not, not chemically modified", "Oil palm", False),
    ("1513 21", "Crude palm kernel and babassu oil and their fractions", "Oil palm", False),
    ("1513 29", "Palm kernel and babassu oil and their fractions (excluding crude oil)", "Oil palm", False),
    ("2306 60", "Oilcake and other solid residues from the extraction of palm nut or kernel fats or oils", "Oil palm", False),
    ("2905 45", "Glycerol, with a purity of 95% or more", "Oil palm", True),
    ("2915 70", "Palmitic acid, stearic acid, their salts and esters", "Oil palm", False),
    ("2915 90", "Saturated acyclic monocarboxylic acids (palm derivatives)", "Oil palm", False),
    ("3823 11", "Stearic acid, industrial", "Oil palm", False),
    ("3823 12", "Oleic acid, industrial", "Oil palm", False),
    ("3823 19", "Industrial monocarboxylic fatty acids; acid oils from refining", "Oil palm", False),
    ("3823 70", "Industrial fatty alcohols", "Oil palm", False),

    # ── Rubber ───────────────────────────────────────────────────────
    ("4001", "Natural rubber, balata, gutta-percha, guayule, chicle, in primary forms or plates/sheets/strip", "Rubber", False),
    ("4005", "Compounded rubber, unvulcanised, in primary forms or in plates/sheets/strip", "Rubber", True),
    ("4006", "Unvulcanised rubber in other forms (rods, tubes, profile shapes)", "Rubber", True),
    ("4007", "Vulcanised rubber thread and cord", "Rubber", True),
    ("4008", "Plates, sheets, strips, rods and profile shapes of vulcanised rubber (non-hard)", "Rubber", True),
    ("4010", "Conveyor or transmission belts or belting, of vulcanised rubber", "Rubber", True),
    ("4011", "New pneumatic tyres, of rubber", "Rubber", True),
    ("4012", "Retreaded or used pneumatic tyres; solid or cushion tyres, treads and flaps", "Rubber", True),
    ("4013", "Inner tubes, of rubber", "Rubber", True),
    ("4015", "Articles of apparel and clothing accessories of vulcanised rubber (non-hard)", "Rubber", True),
    ("4016", "Other articles of vulcanised rubber (non-hard)", "Rubber", True),
    ("4017", "Hard rubber (ebonite) in all forms, including waste and scrap; articles of hard rubber", "Rubber", True),

    # ── Soya ─────────────────────────────────────────────────────────
    ("1201", "Soya beans, whether or not broken", "Soya", False),
    ("1208 10", "Soya bean flour and meal", "Soya", False),
    ("1507", "Soya-bean oil and its fractions, refined or not, not chemically modified", "Soya", False),
    ("2304", "Oilcake and other solid residues from the extraction of soya-bean oil", "Soya", False),

    # ── Wood ─────────────────────────────────────────────────────────
    ("4401", "Fuel wood, wood chips, sawdust and wood waste and scrap", "Wood", False),
    ("4402", "Wood charcoal, agglomerated or not", "Wood", False),
    ("4403", "Wood in the rough, stripped of bark or not, roughly squared or not", "Wood", False),
    ("4404", "Hoopwood; split poles; piles, pickets and stakes of wood", "Wood", False),
    ("4405", "Wood wool; wood flour", "Wood", False),
    ("4406", "Railway or tramway sleepers (cross-ties) of wood", "Wood", False),
    ("4407", "Wood sawn or chipped lengthwise, sliced or peeled, thickness exceeding 6mm", "Wood", False),
    ("4408", "Veneer sheets for plywood or similar laminated wood, thickness not exceeding 6mm", "Wood", False),
    ("4409", "Wood continuously shaped along edges, ends or faces (tongued, grooved, moulded, etc.)", "Wood", False),
    ("4410", "Particle board, OSB and similar board of wood or ligneous materials", "Wood", False),
    ("4411", "Fibreboard of wood or other ligneous materials", "Wood", False),
    ("4412", "Plywood, veneered panels and similar laminated wood", "Wood", False),
    ("4413", "Densified wood, in blocks, plates, strips or profile shapes", "Wood", False),
    ("4414", "Wooden frames for paintings, photographs, mirrors or similar objects", "Wood", False),
    ("4415", "Packing cases, boxes, crates and similar packings of wood; pallets", "Wood", False),
    ("4416", "Casks, barrels, vats, tubs and other coopers' products of wood", "Wood", False),
    ("4417", "Tools, tool handles, broom or brush bodies and handles, of wood", "Wood", False),
    ("4418", "Builders' joinery and carpentry of wood, including cellular wood panels", "Wood", False),
    ("4419", "Tableware and kitchenware, of wood", "Wood", False),
    ("4420", "Wood marquetry and inlaid wood; caskets, cases, statuettes and ornaments of wood", "Wood", False),
    ("4421", "Other articles of wood", "Wood", False),
    ("47", "Wood pulp (paper and paperboard of Chapter 47)", "Wood", True),
    ("48", "Paper and paperboard (Chapter 48, excluding bamboo-based and recovered products)", "Wood", True),
    ("49", "Printed books, newspapers, pictures and other products of the printing industry", "Wood", True),
    ("9401", "Seats (other than heading 9402), of wood, and their parts", "Wood", True),
    ("9403 30", "Wooden office furniture", "Wood", False),
    ("9403 40", "Wooden kitchen furniture", "Wood", False),
    ("9403 50", "Wooden bedroom furniture", "Wood", False),
    ("9403 60", "Other wooden furniture", "Wood", False),
    ("9403 91", "Parts of wooden furniture", "Wood", False),
    ("9406 10", "Prefabricated buildings of wood", "Wood", False),
]


def seed():
    app = create_app()
    with app.app_context():
        created, skipped = 0, 0
        for code, desc, commodity, is_ex in EUDR_HS_CODES:
            if HSCode.query.filter_by(code=code).first():
                skipped += 1
                continue
            db.session.add(HSCode(
                code=code, description=desc,
                eudr_commodity=commodity, is_ex_code=is_ex
            ))
            created += 1
        db.session.commit()
        print(f"Done: {created} HS codes created, {skipped} already existed (skipped). Total EUDR entries: {len(EUDR_HS_CODES)}")


if __name__ == '__main__':
    seed()