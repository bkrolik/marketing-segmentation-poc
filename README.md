# Marketing Segmentation POC (Proof of Concept)

This repository contains a simple end to end POC for a marketing segmentation service. The goal is to allow a backend system to:

* Inspect existing datasets in Amazon Redshift
* Dynamically understand the tables and columns that describe residents
* Ask OpenAI to produce a structured segmentation strategy based on a business description
* Query Redshift to count potential customers that match the suggested filters

There is no frontend, user authentication, or authorization in this POC. Everything is API driven and intentionally simple so we can iterate quickly.

---

## 🚀 High level architecture

The system has three main steps:

1. Query Redshift to discover all tables and column names inside a target schema. This allows the service to adapt as data evolves.
2. Ask OpenAI to generate a segmentation strategy using the discovered schema and the business description.
3. Query Redshift using the suggested filters and return the audience size.

The backend runs with Python and FastAPI. Data is stored in Redshift. OpenAI powers the text understanding and segmentation suggestions.

---

## 🧰 Prerequisites

You need the following installed:

* Python 3.10 or newer
* Pip
* Access to an Amazon Redshift cluster
* An OpenAI API key

---

## ⚙️ Setup instructions

1. Clone this repository

```
git clone <your-repo-url>
cd marketing-segmentation-poc/backend
```

2. Install backend dependencies

```
pip install -r requirements.txt
```

3. Create a `.env` file based on `.env.example`

```
cp .env.example .env
```

Fill in your Redshift connection details and OpenAI key.

4. Load synthetic data into Redshift (optional)

Run the SQL files located in `data/` using your Redshift SQL client.

---

## ▶️ Run the backend

```
uvicorn main:app --reload
```

The server will start on `http://127.0.0.1:8000`

---

## 🔌 API endpoints

### Inspect schema

```
POST /schema
{
"schema_name": "residents"
}
```

Returns all tables and columns from the given schema.

### Produce a segmentation strategy

```
POST /segment_dynamic
{
"business_description": "...",
"business_category": "dentist",
"schema_name": "residents"
}
```

Returns a JSON object that contains:

* The table to query
* A set of filters

### Query the audience size

```
POST /audience_dynamic
{
"table_name": "resident_core",
"filters": {
"age": [5,55],
"kids_flag": true
}
}
```

Returns:

```
{
"audience_size": 28420
}
```

---

## 🧠 How it works

* The backend introspects Redshift to discover available attributes.
* OpenAI reads the table and column names and proposes filters that make sense for the described business.
* The backend converts the filters into SQL and counts matching residents.

There are no hard coded assumptions in this POC, which means new attributes and new tables can be added to Redshift without breaking the workflow.

---

## 🛠️ Development notes

* This project focuses on backend logic and data flow
* There are no security controls yet
* There is no differential privacy or noise injection
* There is no export to ad platforms

These will come later.

---

## 🔬 Functional testing using Docker and pytest

This proof of concept includes functional tests that use a Postgres database running inside Docker. Postgres acts as a local stand in for Redshift. The tests automatically seed deterministic data and clean the database before each run.

To start the test database:
```
docker-compose up -d
```

Verify that Postgres is running:
```
docker ps
```

On Linux export environment variable:
```
export ENV=TEST
```

Or on Windows PowerShell use:
```
$env:ENV = "TEST"
```

Run the test suite:
```
pytest -q
```
💡 You can also verify the table manually:

```
docker exec -it marketing_test_db psql -U test -d analytics
\dt residents.*
```
* Should show:
```
             List of relations
  Schema   |     Name      | Type  | Owner 
-----------+---------------+-------+-------
 residents | resident_core | table | test
```

When tests pass, stop the database:
```
docker-compose down
```

The test environment includes:

* automatic database resets
* synthetic seed data
* OpenAI mocked responses
* network free local functional testing

---

## 📦 Synthetic data generation

You can generate large randomized resident datasets for stress testing:
```
python generate_synthetic_data.py > seed_synthetic.sql
```

Load it into the test database:
```
docker exec -i marketing_test_db psql -U test -d analytics < schemas.sql
docker exec -i marketing_test_db psql -U test -d analytics < seed_synthetic.sql
```

Then run tests again to measure performance on large datasets.

---

## 🧪 Mocking OpenAI in tests

All functional tests mock model calls to avoid real network usage. You can inspect the fixtures in `tests/conftest.py` to adjust the behavior. This guarantees deterministic output and makes tests fast and reliable.

---

## 🧯 Resetting databases between tests

Each test starts with a clean database state. This allows repeatable testing with no cross test interference. You can remove or modify this behavior to simulate persistent data scenarios.

---

## 🗺️ Roadmap ideas

* Add minimum audience thresholds
* Improve prompt templates
* Join across multiple tables
* Add marketing plan generation
* Track conversions and feedback loops
* Add basic authentication
* Add differential privacy controls

<!-- See `docs/roadmap.md` for more. -->

---

## 🤝 Contributing

This POC is intentionally small so we can experiment. Feel free to extend:

* new routers
* new filters
* table relationships
* new data fields

Submit PRs or open discussions to explore ideas.

---

## 📄 License

This project is shared for research and exploratory purposes. Licensing can be formalized later.

---

