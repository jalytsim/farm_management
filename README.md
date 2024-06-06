# Farm Management System

This project is a Flask-based web application for managing farms, creating QR codes, and visualizing data on maps. It includes authentication, QR code generation, and dynamic data visualization.

## Project Structure

```plaintext
farm_management/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── farm.py
│   │   ├── qr.py
│   │   ├── map.py
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   ├── templates/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── home.html
│   │   ├── codeQr.html
│   │   ├── index.html
│   │   ├── dynamic.html
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── qr_generator.py
│   │   ├── map_utils.py
├── config.py
├── run.py
├── requirements.txt
├── .env
└── README.md
```
## Setup

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/farm_management.git
    cd farm_management
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

4. Set up the environment variables in a `.env` file:
    ```
    SECRET_KEY=your_secret_key
    DATABASE_URL=mysql://username:password@localhost/qrcode
    ```

5. Run the application:
    ```sh
    python run.py
    ```

## Features

- User Authentication
- Farm Management
- QR Code Generation
- Data Visualization on Maps

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
