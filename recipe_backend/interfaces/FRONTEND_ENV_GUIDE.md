# Frontend Environment Guide

The frontend should read API base URL from the environment:

- Variable: `REACT_APP_API_URL`
- Example value for local dev: `http://localhost:3001`

When not set, the frontend should default to `http://localhost:3001`.

Ensure Axios client uses this as its `baseURL`, and attaches `Authorization: Bearer <token>` when the user is authenticated.
