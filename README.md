Quick start (Windows / CMD)
git clone https://github.com/<your-user>/<your-repo>.git
cd <your-repo>

py -m venv .venv
call .venv\Scripts\activate
py -m pip install --upgrade pip
pip install -r requirements.txt

Configure env vars

Create a file named .env in the repo root:

DJANGO_SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

STRIPE_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxxxxxx
STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxx


Setup database
py manage.py makemigrations
py manage.py migrate
py manage.py createsuperuser
py manage.py runserver 8080

Stripe (test mode)

Use Stripe test keys in .env.
Test card: 4242 4242 4242 4242, any future expiry, any CVC, any ZIP.
