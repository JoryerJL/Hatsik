# Requirements — Phase 2: Auth

## Overview

A user can register, verify their email, log in, log out, and recover their password. No anonymous access to the app.

**Module:** `Auth` (Django app: `accounts`)
**Depends on:** Phase 1 — Foundation (database, email infrastructure, design tokens, base UI components)

## Stitch Screens

| Screen | ID | Purpose |
|---|---|---|
| Registro de Usuario | `4e62e0c5470344a8acba2468d6b8cecd` | Registration form |
| Verificación Pendiente | `8612ccf1e1304ff9bd3a5090ddf8f9c7` | Unverified state + resend |
| Iniciar Sesión | `31616452da9645128f2c492244260487` | Login form |
| Recuperar Contraseña | `b533a824d16a4fd39fcc7135a1404392` | Password reset request + reset form |

---

## User Stories

### US-1: Registration

**As** a new user,
**I want to** create an account with my name, email, and password,
**So that** I can participate in events on Hatsik.

#### Acceptance Criteria

- [ ] Form fields: `display_name` (required), `email` (required, valid format), `password` (required, min 8 chars, at least 1 letter + 1 number).
- [ ] Email is normalized to lowercase before storage.
- [ ] Duplicate email shows generic error (does NOT reveal that the email already exists).
- [ ] On success: user created with `email_verified_at = NULL`, verification token generated (24h TTL), verification email sent.
- [ ] User is redirected to the Verificación Pendiente screen after registration.
- [ ] Password is hashed before storage (Django's default PBKDF2).
- [ ] Template matches Stitch screen `4e62e0c5470344a8acba2468d6b8cecd` and Warm Kitchen Board design tokens.

---

### US-2: Email Verification

**As** a registered user,
**I want to** verify my email via the link sent to my inbox,
**So that** I can access the app.

#### Acceptance Criteria

- [ ] Clicking the verification link marks `email_verified_at` with the current timestamp.
- [ ] Token is consumed (set `consumed_at`) — cannot be reused.
- [ ] Expired token (>24h) shows an error message with a resend option.
- [ ] Already-consumed token shows an appropriate message.
- [ ] After successful verification, user is redirected to the dashboard (or login if session expired).
- [ ] Resend button on Verificación Pendiente screen: rate-limited to 1 request per 60 seconds per user.
- [ ] Rate limit feedback: button disabled + countdown OR error toast.
- [ ] Template matches Stitch screen `8612ccf1e1304ff9bd3a5090ddf8f9c7`.

---

### US-3: Login

**As** a registered user,
**I want to** log in with my email and password,
**So that** I can access my events.

#### Acceptance Criteria

- [ ] Form fields: `email`, `password`.
- [ ] Valid credentials with verified account → session created, redirect to dashboard.
- [ ] Valid credentials with UNVERIFIED account → session created, redirect to Verificación Pendiente screen.
- [ ] Invalid credentials → generic error: "Email or password is incorrect" (do not reveal which field is wrong).
- [ ] Session uses secure HTTP-only cookie (Django session framework).
- [ ] Template matches Stitch screen `31616452da9645128f2c492244260487`.

---

### US-4: Logout

**As** an authenticated user,
**I want to** log out,
**So that** my session is ended securely.

#### Acceptance Criteria

- [ ] POST request destroys the session (Django `logout()`).
- [ ] User is redirected to the login page.
- [ ] CSRF protection on the logout endpoint.

---

### US-5: Password Recovery — Request

**As** a user who forgot their password,
**I want to** request a password reset link,
**So that** I can regain access.

#### Acceptance Criteria

- [ ] Form field: `email`.
- [ ] On submit: ALWAYS show generic success message "If this email exists, we've sent a reset link." (do not reveal if email exists).
- [ ] If email exists: generate reset token (1h TTL), send password reset email.
- [ ] Rate limit: 1 request per 60 seconds per email (server-side).
- [ ] Rate limit exceeded: show generic "please wait" message (still do not reveal email existence).
- [ ] Template matches Stitch screen `b533a824d16a4fd39fcc7135a1404392`.

---

### US-6: Password Recovery — Reset

**As** a user who received the reset link,
**I want to** set a new password,
**So that** I can log in again.

#### Acceptance Criteria

- [ ] Reset form: `new_password`, `confirm_password` — same validation as registration (min 8, 1 letter + 1 number).
- [ ] Valid token → password updated, token consumed, user redirected to login with success message.
- [ ] Expired token (>1h) → error with link to request a new reset.
- [ ] Already-consumed token → error message.
- [ ] Mismatched passwords → inline validation error.

---

### US-7: Route Protection

**As** the system,
**I want to** enforce authentication on all app routes,
**So that** no anonymous access is possible.

#### Acceptance Criteria

- [ ] ALL routes except `/login/`, `/register/`, `/verify-email/<token>/`, `/password-reset/`, and `/password-reset/<token>/` require authentication.
- [ ] Unauthenticated requests are redirected to `/login/` with `?next=` parameter preserved.
- [ ] Authenticated but UNVERIFIED users are redirected to `/verify-email/` on any protected route.
- [ ] The verification middleware allows access only to: logout, verify-email, and resend-verification endpoints.

---

## Business Rules

| Rule | Description |
|---|---|
| No anonymous access | Every interaction requires a verified account (except auth flows). |
| Email uniqueness | One account per email, case-insensitive. |
| Unverified users are contained | Can log in but are trapped in verification screen. Cannot access ANY product feature. |
| Error opacity | Never reveal whether an email exists in the system (login errors, reset, registration). |
| Token security | Store only hashes of tokens in DB. Raw tokens exist only in emails/URLs. |
| OAuth out of scope | No Google/social login in MVP. |

---

## Non-Functional Requirements

- Password hashing: Django default (PBKDF2 with SHA256).
- Session cookie: `HttpOnly`, `Secure` (in production), `SameSite=Lax`.
- CSRF protection: all POST forms use `{% csrf_token %}`.
- Rate limiting: server-side enforcement (not just UI disabling).
- Responsive: mobile-first with Tailwind breakpoints (`md:`, `lg:`).
- Accessibility: all forms have proper labels, ARIA attributes where needed, focusable elements in logical order.
