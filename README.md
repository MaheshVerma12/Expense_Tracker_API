# Expense Tracker API — Intern Screening

A small Django REST Framework backend for tracking personal spending
(categories, expenses, date filtering, and a per-category summary).

## Your Task (read this first)

You will work with this codebase in four stages:

1. **Fix 5 bugs.** The code contains **5 intentional bugs**. Find and fix them
   all. Every hint you need is in the codebase or in this file.
2. **Add Authentication (required).** Scope expenses and categories to the
   logged-in user and protect the endpoints.
3. **Build 2 integration features (required):**
   [Currency conversion](#feature-1--currency-conversion) and
   [Budget threshold bot alerts](#feature-2--budget-threshold-bot-alerts).
   Both are specified in detail below, with example requests/responses — these
   are the hard part.
4. **Add 2 optional features** of your choice ([list below](#optional-pick-any-2)).

Config placeholders for stage 3 are already in `.env.example` — copy them into
your `.env`.

Full rules, branch naming, and submission details are in
[requirements](#full-requirements) at the bottom. Read that **before** writing
code — workflow is graded.

## What you've been given

| File / Dir                 | What it is                                              |
|----------------------------|---------------------------------------------------------|
| `expenses/`                | The app: `models.py`, `serializers.py`, `views.py`, `urls.py`, `tests.py` |
| `config/`                  | Django project settings and root URL config             |
| `postman_collection.json`  | **Ready-to-import Postman collection — every endpoint.** Use it to test and hunt bugs. |
| `.env.example`             | Template for your `.env`                                 |
| `pyproject.toml`           | Dependencies (managed by `uv`)                          |
| `manage.py`                | Django entry point                                      |

## Setup (3 commands)

Uses [uv](https://docs.astral.sh/uv/). Prefix every `manage.py` call with `uv run`.

```bash
uv sync                                  # create .venv + install deps
cp .env.example .env                     # then fill in SECRET_KEY
uv run python manage.py migrate          # set up the SQLite DB
uv run python manage.py runserver        # start at http://127.0.0.1:8000/
```

## Test the endpoints

1. Import `postman_collection.json` into Postman.
2. The `base_url` variable is preset to `http://127.0.0.1:8000`.
3. Run each request against your local server. **This is your main bug-hunting
   tool** — compare actual responses against the expected behavior below.

### Endpoints

| Method | Endpoint                 | Description                                                        |
|--------|--------------------------|-------------------------------------------------------------------|
| GET    | `/api/categories/`       | List all categories                                               |
| POST   | `/api/categories/`       | Create a category                                                 |
| GET    | `/api/expenses/`         | List expenses (filter with `?start_date=` & `?end_date=`, inclusive) |
| POST   | `/api/expenses/`         | Create an expense                                                 |
| GET    | `/api/expenses/{id}/`    | Retrieve one expense                                              |
| PUT    | `/api/expenses/{id}/`    | Update an expense                                                 |
| DELETE | `/api/expenses/{id}/`    | Delete an expense                                                 |
| GET    | `/api/expenses/summary/` | Total spent per category                                          |

## Tech stack

Python 3 · Django 5 · Django REST Framework · SQLite · python-dotenv

---

## Full Requirements

### Git workflow (graded)

- Create a new repo under **your** GitHub account.
- Default branch **must be named `trunk`** (not `main`/`master`).
- One branch + one PR per item:
  - Bug fixes → `fix/<bug-name>`
  - Features → `feature/<feature-name>`
- **Never commit fixes or features directly to `trunk`.** Merge via PR.
- Do **not** squash. Keep a clean, atomic, readable history. Push regularly.
- Each commit message must say **what** changed and **why**. Example:

  ```text
  fix(expenses): prevent negative expense amounts
  fix(api): correct serializer field mapping
  ```

### Required features

**Authentication** — expenses and categories owned by and scoped to the
authenticated user; endpoints protected (token/session auth + login).

Plus the two integration features below.

#### Feature 1 — Currency conversion

Let expenses be recorded in different currencies and reported in one base
currency, using a third-party exchange-rate API.

- Add a `currency` field to expenses (ISO code, e.g. `EUR`); `amount` stays in
  that currency.
- Reporting endpoints (e.g. `summary`) convert each amount to `BASE_CURRENCY`
  (see `.env.example`) using rates from an exchange-rate API.
- Free providers needing no key: `exchangerate.host`, `open.er-api.com`.

Example (illustrative — refine the exact shape as you see fit):

```jsonc
// POST /api/expenses/
{
  "title": "Hotel in Paris",
  "amount": "120.00",
  "currency": "EUR",
  "category": 1,
  "date": "2026-06-09"
}

// 201 Created
{
  "id": 7,
  "title": "Hotel in Paris",
  "amount": "120.00",
  "currency": "EUR",
  "category": 1,
  "date": "2026-06-09"
}
```

```jsonc
// GET /api/expenses/summary/   (BASE_CURRENCY = USD)
{
  "base_currency": "USD",
  "categories": [
    {
      "category": "Travel",
      "total": "129.60",        // 120.00 EUR converted at 1.08
      "rate": "1.08",
      "as_of": "2026-06-10"
    }
  ]
}
```

#### Feature 2 — Budget threshold bot alerts

Send a chat-bot alert when a category's spending crosses a configured limit.

- Add a per-category monthly budget limit.
- When a created/updated expense pushes that category's month-to-date total over
  its limit, send an alert via a bot (Telegram recommended — free token from
  `@BotFather`; Discord/Slack also fine). Credentials come from `.env`
  (`BOT_TOKEN`, `BOT_CHAT_ID`).

Example (illustrative — refine the exact shape as you see fit):

```jsonc
// Set a monthly limit on a category
// POST /api/categories/   (or PATCH an existing one)
{
  "name": "Dining",
  "monthly_limit": "200.00"
}
```

```jsonc
// POST /api/expenses/  — this expense pushes Dining's month total to 215.00,
// over its 200.00 limit, so an alert fires once.
{
  "title": "Dinner out",
  "amount": "45.00",
  "category": 3,
  "date": "2026-06-09"
}

// 201 Created — API responds normally; the alert is sent off the request path.
{
  "id": 12,
  "title": "Dinner out",
  "amount": "45.00",
  "category": 3,
  "date": "2026-06-09"
}
```

```text
Bot message delivered to BOT_CHAT_ID:

⚠️ Budget alert: "Dining" is over its monthly limit.
Spent 215.00 / 200.00 USD for June 2026.
```

Include **screenshots of the delivered bot alert** (the message in your
Telegram/Discord/Slack chat) in your README as proof it works.

#### Optional (pick any 2)

Recurring expenses · CSV export · Analytics dashboard · Expense
search/filtering · Monthly spending summaries · Favorite categories.

Each feature must be fully functional, follow existing API conventions, and
include validation. You may also improve the Django Admin.


### API documentation

- Update `postman_collection.json` with any new endpoints.
- Responses must carry enough data for a frontend to render views without extra
  follow-up requests.

### README write-up

In your README, add two sections:

- `## My Features` — for each feature (auth, currency conversion, bot alerts,
  and your optional one): overview, design decisions, API changes, example
  request/response, assumptions, known limits. For bot alerts, include
  **screenshots of the delivered alert**.
- `## Bugs Found and Fixed` — for each bug: description, root cause, fix, and
  commit hash.

### Submission

Submit: GitHub repo URL · updated Postman collection · updated README
(including bot-alert screenshots).

### Evaluation criteria

Commit quality · bug-fix correctness (no regressions) · feature design ·
Postman completeness · code readability · REST conventions (status codes,
response shape).

........................................................................................................................................................................................................................................................................

## My Features

### Authentication
- Overview: Token-based authentication (JWT) for all API endpoints. Users register and log in to receive JWT access and refresh tokens.
- Design decisions: Use `djangorestframework-simplejwt` for lightweight JWT support; scope all `Category` and `Expense` objects to the authenticated user via a `user` ForeignKey.
- API changes: `POST /api/auth/register/`, `POST /api/auth/login/` (returns `access` and `refresh` tokens), and protected endpoints requiring `Authorization: Bearer <token>`.
- Example request/response:

  Request:

  ```json
  POST /api/auth/login/
  {"username":"alice","password":"secret"}
  ```

  Response:

  ```json
  {"access":"<jwt>","refresh":"<jwt>"}
  ```
- Assumptions: Clients will include the `access` token in the `Authorization` header. Refresh tokens are supported.
- Known limits: No social or OAuth providers; basic username/password only.

### Currency Conversion
- Overview: Expenses may be recorded in any ISO currency; reporting endpoints convert amounts to a configured `BASE_CURRENCY`.
- Design decisions: Use free public APIs (primary `open.er-api.com`, fallback logic available), cache rates in-memory for 1 hour to reduce external calls, perform conversions with `Decimal` for accuracy.
- API changes: `GET /api/expenses/` and `GET /api/expenses/{id}/` include `converted_amount` and `conversion_rate`; `GET /api/expenses/summary/` reports totals per category converted to `BASE_CURRENCY`.
- Example response (summary):

  ```json
  {
    "base_currency": "USD",
    "categories": [
      {"category":"Travel","total":"129.60","currency_details":{"EUR":{"amount":"120.00","rate":"1.08","as_of":"2026-06-10"}}}
    ]
  }
  ```
- Assumptions: Rates are reasonably up-to-date; `.env` contains `BASE_CURRENCY` and optional `EXCHANGE_RATE_API_URL`.
- Known limits: Exchange-rate providers may rate-limit; cached rates may be stale for up to 1 hour; occasional failures fall back gracefully and mark conversions as `N/A`.

### Budget Threshold Bot Alerts
- Overview: When a category's month-to-date spending exceeds its `monthly_limit`, the system sends an asynchronous chat alert (Telegram supported).
- Design decisions: Store per-category `monthly_limit` (Decimal); after expense create/update, compute month-to-date totals converted to `BASE_CURRENCY`; if over the limit, send a Telegram message via bot in a background thread.
- API changes: No user-visible endpoint beyond standard expense create/update; configure `BOT_TOKEN` and `BOT_CHAT_ID` in `.env`.
- Example alert message:

  ```text
  ⚠️ Budget alert: "Dining" is over its monthly limit.
  Spent 215.00 / 200.00 USD for June 2026.
  ```
- Assumptions: Telegram bot token and chat id are present in environment variables; alerts are informational and sent off the request path.
- Known limits: Delivery depends on Telegram availability; no guaranteed retry/backoff implemented (errors are logged).

### Favorite Categories (optional feature)
- Overview: Mark categories as favorites and filter category lists by favorites.
- Design decisions: Add `is_favorite` Boolean on `Category`; provide a `PATCH /api/categories/{id}/favorite/` endpoint to toggle.
- API changes: `GET /api/categories/?favorite=true` filters favorites; `PATCH /api/categories/{id}/favorite/` toggles favorite state.
- Example request/response:

  ```http
  PATCH /api/categories/3/favorite/
  Authorization: Bearer <token>
  ```

  Response:

  ```json
  {"id":3,"name":"Dining","is_favorite":true}
  ```
- Assumptions: Favorites are user-scoped.
- Known limits: Simple toggle API; no ordering/prioritization of favorites.

## Bugs Found and Fixed 
(1) In views of expense_summary, there was ‘Sum’ but that django orm keyword was not imported so it was giving error.
(2) API endpoints placement in urls.py was incorrect for using api/expenses/summary endpoint as the “/expenses/<pk>” was overriding the reading of the “/expenses/summary” endpoint line in urls.py
(3) For the create category with monthly budget and create expenses with currency requirements, the necessary column was missing in the model. So, I added monthly_budget column in Category model and currency column in Expenses model. The fields in serializers for both models was added accordingly.
(4) There were two spelling mistakes which were causing 500 errors.
