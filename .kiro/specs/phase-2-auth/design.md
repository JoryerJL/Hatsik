# Design — Phase 2: Auth

## Architecture Decisions

### AD-1: Session-based authentication (Django sessions)

**Decision:** Use Django's built-in session framework with HTTP-only cookies. No JWT.

**Rationale:**
- ROADMAP and ARCHITECTURE_AND_STACK.md explicitly mandate Django auth + sessions.
- Server-rendered app (HTMX) — no need for stateless tokens.
- Simpler invalidation (session flush on logout).
- Secure by default: `HttpOnly`, `Secure`, `SameSite=Lax`.

**Consequence:** No API tokens infrastructure needed. Token refresh logic not applicable.

---

### AD-2: Token hashing strategy

**Decision:** Generate raw tokens with `secrets.token_urlsafe(32)`. Store only SHA-256 hashes in DB. The raw token is sent via email URL, never persisted server-side.

**Rationale:**
- If the DB is compromised, tokens cannot be used directly.
- `token_urlsafe(32)` gives 256 bits of entropy — collision-resistant.
- SHA-256 is fast enough for verification on each request.

**Implementation:**
```python
import hashlib
import secrets

raw_token = secrets.token_urlsafe(32)
token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
```

---

### AD-3: Rate limiting approach

**Decision:** Simple in-memory rate limiting using Django cache framework with a per-user/per-email key. No external service (Redis is post-MVP).

**Rationale:**
- Single container deployment (App Runner) → in-process cache is sufficient for MVP.
- Django's `LocMemCache` works for single-process Gunicorn in MVP scale.
- Key pattern: `ratelimit:{action}:{identifier}` → TTL = cooldown period.

**Upgrade path:** When Redis is added post-MVP, swap to `django.core.cache.backends.redis`.

**Endpoints rate-limited:**
| Endpoint | Key | Cooldown |
|---|---|---|
| Resend verification | `ratelimit:resend_verification:{user_id}` | 60s |
| Password reset request | `ratelimit:password_reset:{email_hash}` | 60s |

---

### AD-4: Email verification middleware

**Decision:** Custom Django middleware that intercepts all requests from authenticated-but-unverified users and redirects to `/verify-email/`.

**Rationale:**
- Centralized enforcement — no per-view decorators needed.
- Executes after `AuthenticationMiddleware` so `request.user` is available.
- Allowlist pattern: only specific paths bypass the check.

**Middleware allowlist (paths unverified users CAN access):**
- `/login/`
- `/register/`
- `/logout/`
- `/verify-email/` (and sub-paths)
- `/resend-verification/`
- `/password-reset/` (and sub-paths)
- `/static/` (assets)
- `/admin/` (staff only)

---

### AD-5: Form validation — password rules

**Decision:** Leverage Django's `AUTH_PASSWORD_VALIDATORS` (already configured in `base.py`) plus a custom validator for the "at least 1 letter + 1 number" rule.

**Custom validator:**
```python
import re
from django.core.exceptions import ValidationError

class LetterAndNumberValidator:
    """Ensures password has at least one letter and one number."""
    
    def validate(self, password, user=None):
        if not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
            raise ValidationError(
                "Password must contain at least one letter and one number.",
                code="letter_and_number_required",
            )

    def get_help_text(self):
        return "Your password must contain at least one letter and one number."
```

---

### AD-6: URL scheme

| URL Path | View | Method | Auth Required |
|---|---|---|---|
| `/register/` | `register_view` | GET/POST | No |
| `/login/` | `login_view` | GET/POST | No |
| `/logout/` | `logout_view` | POST | Yes |
| `/verify-email/` | `verify_email_pending_view` | GET | Yes (unverified) |
| `/verify-email/<token>/` | `verify_email_confirm_view` | GET | No |
| `/resend-verification/` | `resend_verification_view` | POST | Yes (unverified) |
| `/password-reset/` | `password_reset_request_view` | GET/POST | No |
| `/password-reset/<token>/` | `password_reset_confirm_view` | GET/POST | No |

**App URL namespace:** `accounts`

---

### AD-7: Template structure

```
apps/accounts/templates/accounts/
├── register.html          → Registration form
├── login.html             → Login form
├── verify-email.html      → Pending verification state + resend button
├── password-reset.html    → Request reset form
└── password-reset-confirm.html  → New password form
```

All templates extend `templates/base.html`. Form components use existing `_input.html`, `_button.html` partials from Phase 1.

---

### AD-8: HTMX interactions

| Interaction | Trigger | Target | Swap | Response |
|---|---|---|---|---|
| Resend verification | Click "Resend" button | `#resend-section` | `innerHTML` | Updated button (disabled + countdown) OR error toast |
| Form validation errors | Form submit | `#form-errors` or individual fields | `innerHTML` | Error messages partial |
| Rate limit feedback | Server response 429 | `#toast-container` | `beforeend` | Toast partial |

**Non-HTMX flows (full page):**
- Registration submit → redirect to verify-email
- Login submit → redirect to dashboard or verify-email
- Password reset submit → redirect to login with success message
- Email verification click → redirect to dashboard or login

---

## File Changes Summary

### New files

| File | Purpose |
|---|---|
| `apps/accounts/forms.py` | Registration, Login, Password Reset Request, Password Reset Confirm forms |
| `apps/accounts/views.py` | All auth views (register, login, logout, verify, reset) |
| `apps/accounts/urls.py` | URL patterns for accounts app |
| `apps/accounts/middleware.py` | `EmailVerificationMiddleware` |
| `apps/accounts/validators.py` | `LetterAndNumberValidator` |
| `apps/accounts/templates/accounts/register.html` | Registration page |
| `apps/accounts/templates/accounts/login.html` | Login page |
| `apps/accounts/templates/accounts/verify-email.html` | Verification pending page |
| `apps/accounts/templates/accounts/password-reset.html` | Password reset request page |
| `apps/accounts/templates/accounts/password-reset-confirm.html` | Password reset form page |
| `apps/accounts/templates/accounts/partials/_resend_button.html` | HTMX partial for resend |

### Modified files

| File | Change |
|---|---|
| `config/urls.py` | Add `accounts` URL include |
| `config/settings/base.py` | Add `EmailVerificationMiddleware` to MIDDLEWARE, add custom password validator, add `LOGIN_URL`, session settings, cache config |

---

## Dependencies

No new Python packages required. Everything uses:
- Django auth framework (built-in)
- Django sessions (built-in)
- Django cache (built-in LocMemCache)
- Resend SDK (already installed from Phase 1)
- `hashlib`, `secrets` (stdlib)

---

## Security Considerations

| Concern | Mitigation |
|---|---|
| Brute-force login | Rate limiting + generic error messages |
| Token leakage via DB | Only hashes stored |
| Session fixation | Django rotates session key on login by default |
| CSRF on forms | All POST forms include `{% csrf_token %}` |
| XSS in error messages | Django template auto-escaping |
| Email enumeration | All responses are generic (register, login, reset) |
| Token in URL (referer leak) | Verification/reset tokens consumed on first use; short TTL |

---

## Testing Strategy

| Layer | What to test | Tool |
|---|---|---|
| Unit | Token generation/hashing, validators, form validation | `pytest` + `pytest-django` |
| Integration | View responses, redirects, session creation, middleware | Django `TestCase` with `Client` |
| Email | Verify email sending is called with correct args | Mock `resend.Emails.send` |
| Rate limiting | Verify 60s cooldown enforced | Time mocking (`freezegun` or `time_machine`) |
