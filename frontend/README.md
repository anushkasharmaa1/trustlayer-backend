# TrustLayer Frontend

A lightweight React dashboard for TrustLayer built with Vite.

## Development

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Start the development server:

```bash
npm run dev
```

The app will be available at `http://localhost:3000` and will proxy `/get-score` to `http://127.0.0.1:8000`.

## Environment variables

Copy `.env.example` to `.env` to customize frontend settings:

```bash
cd frontend
copy .env.example .env
```

By default the frontend uses the internal Vite proxy, so no `VITE_API_BASE` value is required unless you want to point to a different backend URL.
