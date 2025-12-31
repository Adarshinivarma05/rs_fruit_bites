# 🍎 RS Fruit Bites - Owner Dashboard

A modern, production-ready management system for RS Fruit Bites business, built with **Clean Architecture**, **Poetry**, **PostgreSQL**, and **Streamlit**.

## 🏗️ Architecture

This project follows **Clean Architecture** principles with clear separation of concerns:

```
src/
├── core/              # Core configuration and database
│   ├── config.py      # Pydantic settings management
│   └── database.py    # SQLAlchemy setup and session management
├── models/            # Database models (SQLAlchemy ORM)
│   ├── customer.py
│   ├── attendance.py
│   ├── payment.py
│   └── audit.py
├── repositories/      # Data access layer
│   ├── customer_repository.py
│   ├── attendance_repository.py
│   ├── payment_repository.py
│   └── audit_repository.py
└── services/          # Business logic layer
    ├── customer_service.py
    ├── attendance_service.py
    ├── payment_service.py
    └── report_service.py
```

### Key Benefits
- ✅ **Separation of Concerns** - Clear boundaries between layers
- ✅ **Testability** - Easy to unit test each layer independently
- ✅ **Maintainability** - Changes in one layer don't affect others
- ✅ **Type Safety** - Full type hints with mypy validation
- ✅ **Real-time Sync** - All edits immediately persist to PostgreSQL

## ✨ Features

### 📊 Dashboard
- Real-time metrics (customers, attendance, extra bowls)
- Pending bills overview with calculations
- Quick access to key business data

### 👥 Customer Management
- Add/edit/delete customers with validation
- Subscription plans (Basic/Medium/Premium)
- Custom rate support
- Soft delete (deactivate) and hard delete with audit
- **All edits sync to database immediately**

### 🗓 Attendance Tracking
- Daily attendance marking (Present/Absent/Extra)
- Extra bowls tracking per customer
- Automatic billing period adjustment for absences
- Historical attendance reports

### 💸 Payment Management
- Record payments with multiple methods
- Payment history and analytics
- Customer-wise payment tracking
- Export to CSV

### 📈 Reports & Analytics
- Date range reports for attendance and payments
- Pending bills calculation with detailed breakdown
- Export capabilities for all reports
- Dashboard metrics and KPIs

### 🕰 Past Members
- View inactive customers
- Reactivate functionality
- Historical records maintenance

### 🗑 Audit Logs
- Complete audit trail for deletions
- Compliance and tracking
- Export audit logs

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+**
- **PostgreSQL 12+**
- **Poetry** (Python dependency management)

### Installation

1. **Install Poetry** (if not already installed)
```powershell
# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -

# Or use pip
pip install poetry
```

2. **Install Dependencies**
```powershell
cd c:\Workspace\RS-Fruit-Bites
poetry install
```

3. **Setup PostgreSQL Database**
```sql
-- Open PostgreSQL (psql or pgAdmin)
CREATE DATABASE rs_fruit_bites;
```

4. **Configure Environment**
```powershell
# Copy example environment file
copy .env.example .env

# Edit .env with your PostgreSQL credentials
# DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/rs_fruit_bites
```

5. **Initialize Database**
```powershell
poetry run python -c "from src.core.database import init_db; init_db()"
```

6. **Run the Application**
```powershell
poetry run streamlit run app.py
```

Visit **http://localhost:8501** in your browser.

## 📦 Project Structure

```
RS-Fruit-Bites/
├── src/                      # Source code
│   ├── core/                 # Core configuration
│   ├── models/               # Database models
│   ├── repositories/         # Data access layer
│   └── services/             # Business logic
├── tests/                    # Test suite
├── alembic/                  # Database migrations
│   └── versions/             # Migration files
├── app.py                    # Streamlit application
├── pyproject.toml            # Poetry configuration
├── alembic.ini               # Alembic configuration
├── Makefile                  # Common commands
├── .env.example              # Environment template
└── README_NEW.md             # This file
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/rs_fruit_bites

# Application
APP_NAME=RS Fruit Bites
DEBUG=false

# Business Logic
BASIC_RATE=40.0
MEDIUM_RATE=60.0
PREMIUM_RATE=80.0
```

### Poetry Commands

```powershell
# Install dependencies
poetry install

# Add new dependency
poetry add package-name

# Add dev dependency
poetry add --group dev package-name

# Update dependencies
poetry update

# Run commands in virtual environment
poetry run python script.py

# Activate virtual environment
poetry shell
```

## 🛠️ Development

### Available Commands (Makefile)

```powershell
# Install dependencies
make install

# Run application
make run

# Run tests
make test

# Format code
make format

# Lint code
make lint

# Clean cache files
make clean

# Create database migration
make migrate msg="your migration message"

# Apply migrations
make upgrade

# Initialize database
make init-db
```

### Running Tests

```powershell
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src

# Run specific test file
poetry run pytest tests/test_customer_service.py -v
```

### Code Quality

```powershell
# Format code with Black
poetry run black src/ tests/ app.py

# Lint with Ruff
poetry run ruff check src/ tests/ app.py

# Type check with mypy
poetry run mypy src/

# Setup pre-commit hooks
poetry run pre-commit install
```

## 🗄️ Database Management

### Using Alembic for Migrations

```powershell
# Create a new migration
poetry run alembic revision --autogenerate -m "Add new column"

# Apply migrations
poetry run alembic upgrade head

# Rollback one migration
poetry run alembic downgrade -1

# View migration history
poetry run alembic history

# View current revision
poetry run alembic current
```

### Database Schema

**customers**
- `id` - Primary key
- `name` - Unique customer name
- `area`, `mobile` - Contact information
- `subscription` - Plan type (Basic/Medium/Premium)
- `custom_rate` - Custom monthly rate
- `start_date`, `end_date` - Subscription period
- `status` - active/inactive
- `created_at`, `updated_at` - Timestamps

**attendance**
- `id` - Primary key
- `date`, `name` - Unique constraint
- `subscription`, `status` - Attendance details
- `extra_bowls` - Extra servings count
- `created_at` - Timestamp

**payments**
- `id` - Primary key
- `date`, `name`, `amount` - Payment details
- `method` - Payment method (Cash/GPay/PhonePe/Other)
- `remarks`, `month` - Additional info
- `created_at` - Timestamp

**audit_logs**
- `id` - Primary key
- `action`, `details` - Action tracking
- `timestamp` - When action occurred

**deleted_members**
- Complete customer record backup
- `deleted_at`, `reason` - Deletion audit

## 🔒 Security Best Practices

- ✅ Environment variables for sensitive data
- ✅ PostgreSQL authentication
- ✅ No hardcoded credentials
- ✅ Audit logging for all critical operations
- ✅ Soft delete with recovery option
- ✅ Hard delete with permanent audit trail

## 📊 Usage Examples

### Adding a Customer
```python
from src.core.database import get_db_context
from src.services import CustomerService

with get_db_context() as db:
    service = CustomerService(db)
    customer = service.create_customer(
        name="John Doe",
        area="Downtown",
        mobile="1234567890",
        subscription="Premium",
        custom_rate=1500.0
    )
```

### Marking Attendance
```python
from datetime import date
from src.services import AttendanceService

with get_db_context() as db:
    service = AttendanceService(db)
    service.mark_attendance(
        attendance_date=date.today(),
        name="John Doe",
        subscription="Premium",
        status="Present",
        extra_bowls=2
    )
```

### Recording Payment
```python
from src.services import PaymentService

with get_db_context() as db:
    service = PaymentService(db)
    service.record_payment(
        payment_date=date.today(),
        name="John Doe",
        amount=1500.0,
        method="GPay",
        remarks="Monthly payment"
    )
```

## 🚀 Deployment

### Local Development
```powershell
poetry run streamlit run app.py
```

### Production Deployment

**Recommended Platforms:**
- **Streamlit Cloud** - Easiest, free tier available
- **Heroku** - With Heroku Postgres add-on
- **Railway** - Modern platform with managed PostgreSQL
- **AWS** - EC2 + RDS PostgreSQL
- **DigitalOcean** - App Platform + Managed Database

**Environment Setup:**
1. Set `DATABASE_URL` environment variable
2. Install dependencies: `poetry install --no-dev`
3. Run migrations: `poetry run alembic upgrade head`
4. Start app: `poetry run streamlit run app.py`

### Docker Deployment (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev

COPY . .

CMD ["poetry", "run", "streamlit", "run", "app.py"]
```

## 🧪 Testing

The project includes comprehensive tests:

```powershell
# Run all tests
poetry run pytest

# Run with coverage report
poetry run pytest --cov=src --cov-report=html

# Run specific test
poetry run pytest tests/test_customer_service.py::test_create_customer -v
```

## 📝 Migration from Old System

If you have existing data in SQLite:

1. Keep the old `migrate_to_postgres.py` script
2. Run: `poetry run python migrate_to_postgres.py`
3. Verify data in PostgreSQL
4. Archive old SQLite database

## 🛠️ Maintenance

### Backup Database
```powershell
# Backup
pg_dump -U postgres rs_fruit_bites > backup_$(Get-Date -Format "yyyyMMdd").sql

# Restore
psql -U postgres rs_fruit_bites < backup_20231230.sql
```

### Update Dependencies
```powershell
# Check for updates
poetry show --outdated

# Update all
poetry update

# Update specific package
poetry update package-name
```

## 🤝 Contributing

1. Follow the existing code structure
2. Write tests for new features
3. Run `make format` and `make lint` before committing
4. Use meaningful commit messages

## 📄 License

Private project for RS Fruit Bites business operations.

## 🆘 Troubleshooting

### Poetry Issues
```powershell
# Clear cache
poetry cache clear pypi --all

# Reinstall dependencies
poetry install --no-cache
```

### Database Connection Issues
```powershell
# Check PostgreSQL is running
pg_isready

# Test connection
psql -U postgres -d rs_fruit_bites
```

### Import Errors
```powershell
# Ensure you're in poetry shell or use poetry run
poetry shell
python app.py

# Or
poetry run streamlit run app.py
```

## 📞 Support

For issues or questions:
1. Check PostgreSQL logs
2. Review application logs in Streamlit
3. Verify `.env` configuration
4. Ensure database is initialized

---

**Built with ❤️ using Clean Architecture, Poetry, PostgreSQL & Streamlit**
