import os

TREE = [
    "farm-management-backend/app/__init__.py",
    "farm-management-backend/app/config.py",

    # models
    "farm-management-backend/app/models/__init__.py",
    "farm-management-backend/app/models/user.py",
    "farm-management-backend/app/models/farm.py",
    "farm-management-backend/app/models/forest.py",
    "farm-management-backend/app/models/district.py",
    "farm-management-backend/app/models/crop.py",
    "farm-management-backend/app/models/payment.py",
    "farm-management-backend/app/models/report.py",
    "farm-management-backend/app/models/other.py",

    # api root
    "farm-management-backend/app/api/__init__.py",
    "farm-management-backend/app/api/auth.py",

    # api submodules
    "farm-management-backend/app/api/farms/__init__.py",
    "farm-management-backend/app/api/farms/routes.py",
    "farm-management-backend/app/api/farms/schemas.py",

    "farm-management-backend/app/api/forests/__init__.py",
    "farm-management-backend/app/api/forests/routes.py",

    "farm-management-backend/app/api/crops/__init__.py",
    "farm-management-backend/app/api/crops/routes.py",

    "farm-management-backend/app/api/districts/__init__.py",
    "farm-management-backend/app/api/districts/routes.py",

    "farm-management-backend/app/api/users/__init__.py",
    "farm-management-backend/app/api/users/routes.py",

    "farm-management-backend/app/api/reports/__init__.py",
    "farm-management-backend/app/api/reports/farm_reports.py",
    "farm-management-backend/app/api/reports/forest_reports.py",
    "farm-management-backend/app/api/reports/certificates.py",

    "farm-management-backend/app/api/payments/__init__.py",
    "farm-management-backend/app/api/payments/routes.py",

    "farm-management-backend/app/api/qr/__init__.py",
    "farm-management-backend/app/api/qr/routes.py",

    "farm-management-backend/app/api/weather/__init__.py",
    "farm-management-backend/app/api/weather/routes.py",

    "farm-management-backend/app/api/gfw/__init__.py",
    "farm-management-backend/app/api/gfw/routes.py",

    "farm-management-backend/app/api/notifications/__init__.py",
    "farm-management-backend/app/api/notifications/routes.py",

    # services
    "farm-management-backend/app/services/__init__.py",
    "farm-management-backend/app/services/farm_service.py",
    "farm-management-backend/app/services/forest_service.py",
    "farm-management-backend/app/services/crop_service.py",
    "farm-management-backend/app/services/district_service.py",
    "farm-management-backend/app/services/payment_service.py",
    "farm-management-backend/app/services/qr_service.py",
    "farm-management-backend/app/services/weather_service.py",
    "farm-management-backend/app/services/gfw_service.py",
    "farm-management-backend/app/services/notification_service.py",
    "farm-management-backend/app/services/report_service.py",

    # middleware
    "farm-management-backend/app/middleware/__init__.py",
    "farm-management-backend/app/middleware/auth.py",
    "farm-management-backend/app/middleware/validators.py",

    # utils
    "farm-management-backend/app/utils/__init__.py",
    "farm-management-backend/app/utils/responses.py",
    "farm-management-backend/app/utils/pagination.py",
    "farm-management-backend/app/utils/date_utils.py",
    "farm-management-backend/app/utils/file_utils.py",

    # integrations
    "farm-management-backend/app/integrations/__init__.py",
    "farm-management-backend/app/integrations/dpo_payment.py",
    "farm-management-backend/app/integrations/stormglass.py",
    "farm-management-backend/app/integrations/global_forest_watch.py",
    "farm-management-backend/app/integrations/sms_provider.py",

    # tasks
    "farm-management-backend/app/tasks/__init__.py",
    "farm-management-backend/app/tasks/weather_alerts.py",
    "farm-management-backend/app/tasks/pest_alerts.py",

    # migrations
    "farm-management-backend/migrations/versions/.gitkeep",

    # tests
    "farm-management-backend/tests/__init__.py",
    "farm-management-backend/tests/test_auth.py",
    "farm-management-backend/tests/test_farms.py",

    # root files
    "farm-management-backend/.env.example",
    "farm-management-backend/.gitignore",
    "farm-management-backend/requirements.txt",
    "farm-management-backend/run.py",
    "farm-management-backend/README.md"
]


def create_structure():
    for path in TREE:
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"[DIR]   {directory}")

        if not path.endswith(".gitkeep") and not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write("")
            print(f"[FILE]  {path}")

    print("\nArborescence générée avec succès 👍")


if __name__ == "__main__":
    create_structure()
