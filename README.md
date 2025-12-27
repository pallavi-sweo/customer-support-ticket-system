# Customer Support Ticket System (FastAPI + MySQL + Streamlit)

## Tech Stack
- Backend: Python FastAPI
- ORM: SQLAlchemy 2.0
- Auth: JWT (bcrypt password hashing)
- DB: MySQL
- Frontend: Streamlit
- Quality: black, flake8, pylint, pytest

## Features
- User signup/login
- Create and view tickets (RBAC enforced)
- Ticket listing with pagination + filters
- Replies thread per ticket
- Admin-only status update with strict transitions

## Roles
- USER (Customer): create tickets, view own tickets, reply to own tickets
- ADMIN (Support Agent): view all tickets, reply to any, update ticket status

## Ticket Status Workflow
- OPEN -> IN_PROGRESS or CLOSED
- IN_PROGRESS -> RESOLVED or CLOSED
- RESOLVED -> CLOSED
- CLOSED is terminal

## Database Schema (SQL)
### users
- id (PK)
- email (unique, indexed)
- password_hash
- role
- created_at

### tickets
- id (PK)
- user_id (FK -> users.id)
- subject
- description
- status (indexed)
- priority
- created_at (indexed)
- updated_at

### ticket_replies
- id (PK)
- ticket_id (FK -> tickets.id)
- author_id (FK -> users.id)
- message
- created_at (indexed)

Indexes:
- tickets.status, tickets.created_at

## Setup

### Backend
1. Create `.env` in `backend/`:
   - DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/tickets_db
   - JWT_SECRET=...
   - (optional) BOOTSTRAP_ADMIN_EMAIL, BOOTSTRAP_ADMIN_PASSWORD
2. Install deps:
   ```bash
   cd backend
   pip install -r requirements.txt
