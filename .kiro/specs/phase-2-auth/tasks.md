# Tasks — Phase 2: Auth

## Implementation Order

Tasks are ordered by dependency. Each task is a logical work unit that produces a testable, committable result.

---

### Task 1: Settings & Configuration

**Files:** `config/settings/base.py`, `config/settings/local.py`

- [ ] 1.1 Add `LOGIN_URL = "/login/"` and `LOGIN_REDIRECT_URL = "/events/"` to `base.py`.
- [ ] 1.2 Add session settings: `SESSION_COOKIE_HTTPONLY = True`, `SESSION_COOKIE_SECURE` (True in production, False in local), `SESSION_COOKIE_SAMESITE = "Lax"`, `SESSION_COOKIE_AGE = 1209600` (2 weeks).
- [ ] 1.3 Add cache configuration (`LocMemCache`) for rate limiting.
- [ ] 1.4 Add `LetterAndNumberValidator` to `AUTH_PASSWORD_VALIDATORS`.
- [ ] 1.5 Verify settings load correctly: `python manage.py check`.

**Commit:** `feat(accounts): configure session, cache, and password validation settings`

---

### Task 2: Password Validator

**Files:** `apps/accounts/validators.py`

- [ ] 2.1 Create `LetterAndNumberValidator` class with `validate()` and `get_help_text()`.
- [ ] 2.2 Write unit tests: valid passwords pass, invalid (no letter, no number, empty) fail.

**Commit:** `feat(accounts): add letter-and-number password validator`

---

### Task 3: Forms

**Files:** `apps/accounts/forms.py`

- [ ] 3.1 Create `RegisterForm`: fields `display_name`, `email`, `password`, `password_confirm`. Validates password match and runs password validators.
- [ ] 3.2 Create `LoginForm`: fields `email`, `password`. No Django ModelForm — plain form.
- [ ] 3.3 Create `PasswordResetRequestForm`: field `email`.
- [ ] 3.4 Create `PasswordResetConfirmForm`: fields `new_password`, `new_password_confirm`. Runs password validators.
- [ ] 3.5 Write unit tests for each form: valid input passes, invalid input shows correct errors.

**Commit:** `feat(accounts): add registration, login, and password reset forms`

---

### Task 4: Registration View & Template

**Files:** `apps/accounts/views.py`, `apps/accounts/templates/accounts/register.html`

- [ ] 4.1 Create `register_view` (function-based): GET renders form, POST validates, creates user, generates token, sends verification email, redirects to verify-email.
- [ ] 4.2 Handle duplicate email gracefully (generic error, no email enumeration).
- [ ] 4.3 Create `register.html` template matching Stitch screen `4e62e0c5470344a8acba2468d6b8cecd`: form fields, error display, link to login.
- [ ] 4.4 Write integration tests: successful registration, duplicate email, invalid password, form validation errors.

**Commit:** `feat(accounts): implement registration view and template`

---

### Task 5: Email Verification Views & Template

**Files:** `apps/accounts/views.py`, `apps/accounts/templates/accounts/verify-email.html`, `apps/accounts/templates/accounts/partials/_resend_button.html`

- [ ] 5.1 Create `verify_email_pending_view` (GET): shows the "check your email" screen with resend button. Only for authenticated unverified users.
- [ ] 5.2 Create `verify_email_confirm_view` (GET with `<token>` param): validates token hash, checks expiry, marks `email_verified_at`, consumes token, redirects to dashboard/login.
- [ ] 5.3 Create `resend_verification_view` (POST, HTMX): checks rate limit (60s), generates new token, sends email, returns partial with disabled button.
- [ ] 5.4 Create `verify-email.html` template matching Stitch screen `8612ccf1e1304ff9bd3a5090ddf8f9c7`.
- [ ] 5.5 Create `_resend_button.html` partial for HTMX swap.
- [ ] 5.6 Write integration tests: valid token verifies, expired token shows error, consumed token shows error, resend rate limit enforced, resend after cooldown succeeds.

**Commit:** `feat(accounts): implement email verification flow`

---

### Task 6: Login & Logout Views

**Files:** `apps/accounts/views.py`, `apps/accounts/templates/accounts/login.html`

- [ ] 6.1 Create `login_view`: GET renders form. POST authenticates, creates session, redirects to dashboard (verified) or verify-email (unverified).
- [ ] 6.2 Handle `?next=` parameter: redirect there after successful login if present.
- [ ] 6.3 Create `logout_view` (POST only): destroys session, redirects to login.
- [ ] 6.4 Create `login.html` template matching Stitch screen `31616452da9645128f2c492244260487`: form fields, error display, links to register and password reset.
- [ ] 6.5 Write integration tests: valid login (verified), valid login (unverified redirects), invalid credentials, next parameter preserved, logout destroys session.

**Commit:** `feat(accounts): implement login and logout views`

---

### Task 7: Password Recovery Views & Templates

**Files:** `apps/accounts/views.py`, `apps/accounts/templates/accounts/password-reset.html`, `apps/accounts/templates/accounts/password-reset-confirm.html`

- [ ] 7.1 Create `password_reset_request_view`: GET renders form. POST checks rate limit, generates token if email exists, sends email. ALWAYS shows generic success message.
- [ ] 7.2 Create `password_reset_confirm_view`: GET validates token and renders form. POST validates new password, updates user, consumes token, redirects to login.
- [ ] 7.3 Create `password-reset.html` template matching Stitch screen `b533a824d16a4fd39fcc7135a1404392`.
- [ ] 7.4 Create `password-reset-confirm.html` template (reuses same Stitch screen style).
- [ ] 7.5 Write integration tests: request sends email, request with non-existent email still shows success, rate limit enforced, valid token resets password, expired/consumed token shows error.

**Commit:** `feat(accounts): implement password recovery flow`

---

### Task 8: Email Verification Middleware

**Files:** `apps/accounts/middleware.py`, `config/settings/base.py`

- [ ] 8.1 Create `EmailVerificationMiddleware`: after `AuthenticationMiddleware` in stack.
- [ ] 8.2 Logic: if user is authenticated AND `email_verified_at` is None AND path is NOT in allowlist → redirect to `/verify-email/`.
- [ ] 8.3 Allowlist: `/login/`, `/register/`, `/logout/`, `/verify-email/`, `/resend-verification/`, `/password-reset/`, `/static/`, `/admin/`.
- [ ] 8.4 Add middleware to `MIDDLEWARE` in `base.py` (after `AuthenticationMiddleware`).
- [ ] 8.5 Write integration tests: unverified user accessing `/events/` is redirected to verify-email, verified user passes through, unauthenticated user passes through (handled by `login_required`).

**Commit:** `feat(accounts): add email verification enforcement middleware`

---

### Task 9: URL Configuration

**Files:** `apps/accounts/urls.py`, `config/urls.py`

- [ ] 9.1 Create `apps/accounts/urls.py` with `app_name = "accounts"` and all URL patterns from design AD-6.
- [ ] 9.2 Include accounts URLs in `config/urls.py` at root level (no prefix — paths are `/login/`, `/register/`, etc.).
- [ ] 9.3 Verify all URL names resolve correctly: `python manage.py show_urls` or manual test.

**Commit:** `feat(accounts): wire URL configuration`

---

### Task 10: Integration Verification

- [ ] 10.1 Run full test suite: `pytest` — all tests pass.
- [ ] 10.2 Run linting: `ruff check .` — no errors.
- [ ] 10.3 Run Django system check: `python manage.py check` — no issues.
- [ ] 10.4 Manual smoke test: register → receive email (or check console) → verify → login → logout → password reset flow.
- [ ] 10.5 Verify all 4 Stitch screens are implemented and match design tokens.
- [ ] 10.6 Verify unverified user is blocked from all product routes.
- [ ] 10.7 Verify generic error messages don't leak email existence.

**Commit:** `test(accounts): integration verification pass`

---

## Summary

| Metric | Value |
|---|---|
| Total tasks | 10 |
| Total subtasks | ~37 |
| Estimated files created | 11 |
| Estimated files modified | 3 |
| New Python packages | 0 |
| Commit count | 10 |
