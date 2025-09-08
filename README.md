#  BitCode Backend

**Dropping the code. Raising the stakes.**

This is the official backend for **BitCode**—a real-time competitive programming battle platform powered by Django, Django Channels, PostgreSQL, Redis, and Judge0 for instant code execution.

---

##  1. Overview

BitCode enables real-time, head-to-head coding battles with features such as:
- Live battle rooms (1v1, squads, teams) with instant result evaluation.
- Dynamic lobby creation, joining, and chatting via WebSockets.
- Persistent, Elo-based seasonal rankings and leaderboards.
- Secure account management with email + Google OAuth.
- Scalable architecture with Redis for caching and message brokering.
- Cloud-native media handling using ImageKit.

---

##  2. Tech Stack

| Layer         | Technologies                          |
|---------------|----------------------------------------|
| Framework     | Django + Django REST Framework         |
| Real-time     | Django Channels + Redis                |
| Database      | PostgreSQL                             |
| Coder Engine  | Judge0 API                             |
| Caching       | Redis                                  |
| Media         | ImageKit (CDN-hosted storage)          |

---

##  3. Key Features & Endpoints

### Battle & Lobby (real-time via WebSockets)
- Create/join rooms.
- Broadcast coding battles and chat in real-time.
- Update live leaderboards and battle outcomes.

### REST APIs
- CRUD operations for Questions, Rooms, Users, etc.
- Leaderboard & ranking endpoints.
- Submission and code run handling.

### Authentication
- Support for both **email-based** and **Google OAuth2** authentication.
- Secure endpoints with token/session management.

### Media Uploads
- Cloud upload of user avatars, question assets, and more via ImageKit.

---

##  4. Getting Started

### Prerequisites
- Python 3.10+
- Django 4.x
- PostgreSQL
- Redis
- Judge0 API access
- ImageKit credentials
- Optional: Docker + docker-compose (if available)

### Environment Setup

Create a `.env` file with the following variables:

```dotenv
# API Endpoints
DJANGO_SECRET_KEY=your-secret-key
DATABASE_URL=postgres://bit:bitc@localhost:5432/bitcodedb

# Google OAuth2
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Judge0 API
JUDGE0_API_URL=https://compile.bitcode.live

# ImageKit Configuration
IMAGEKIT_PUBLIC_KEY=your_public_key
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/your_endpoint_id
IMAGEKIT_PRIVATE_KEY=your_private_key
