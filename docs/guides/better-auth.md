# Better Auth Instructions for Grok Build

> **Scope:** Grok Build's TanStack Start template on `*.grok.me` and
> `*.grok-sandbox.com`.
>
> **Purpose:** One self-contained implementation and verification contract for
> enabling secure user accounts, protected routes, and per-user data with the
> template's prewired Better Auth integration.
>
> **Source snapshot:** 2026-08-25. If the current workspace's
> `.grok/skills/auth/SKILL.md` differs from this document, follow the current
> workspace because the platform contract may have changed.

## 1. Security posture

Use the smallest supported authentication surface:

- The app runs its own Better Auth at `/api/auth/*`.
- Google and X federate through the shared Grok auth broker at `auth.grok.me`.
- Local email/password is supported but disabled by default.
- Prefer Google/X broker login with local email/password left disabled unless
  the product explicitly requires application-owned passwords.
- Authentication identifies the user. Authorization must still be enforced by
  every protected server operation.
- Build real authentication. Never create demo users, hardcoded users, mock
  sessions, client-only login state, or `localStorage` authentication.

Do not describe the result as unhackable, military-grade, zero-trust, or fully
compliant. Application code cannot prevent a compromised identity provider,
phishing at the provider, malicious browser extensions, or theft of an already
authenticated device.

## 2. Supported methods and hard boundaries

Only these methods are supported:

1. Google through the Grok broker.
2. X through the Grok broker.
3. The app's own Better Auth email/password flow, only when explicitly enabled.

Do not add:

- GitHub, Apple, Discord, Microsoft, Facebook, or another provider;
- magic links;
- passkeys or WebAuthn;
- OTP or one-time codes;
- phone or SMS authentication;
- anonymous authentication;
- Clerk, Auth.js, NextAuth, Stack, Firebase Auth, Supabase Auth, Auth0, or a
  replacement authentication library.

Do not add entries to `GROK_PROVIDERS`. The broker accepts only its fixed Google
and X upstreams.

## 3. Files owned by the platform

Everything under `src/lib/auth/` is preinstalled and prewired.

| File | Purpose |
| --- | --- |
| `client.ts` | Browser-safe `signIn()`, `signOut()`, `authEnabled`, and `GROK_PROVIDERS`. |
| `server.ts` | Server-only Better Auth instance. Import only from the catch-all API route. Never edit or rewrite it. |
| `email-password.ts` | The only documented place to enable local email/password. |
| `popup.server.ts` | Server-only live-preview popup handler already mounted by the Vite plugin. |
| `providers.ts` | Fixed Google/X provider list. Do not modify it. |
| `use-current-user.ts` | `useCurrentUser()` and `useCurrentUserState()` hooks. |
| `gates.tsx` | `SignedIn`, `SignedOut`, `RedirectToSignIn`, and `UserButton`. |
| `middleware.ts` | `authMiddleware`, which supplies verified `context.userId` to server functions. |
| `verify.server.ts` | Server-only `requireUserId()` and `getSessionUser()`. |

Hard rules:

- Never edit or rewrite `src/lib/auth/server.ts`.
- Do not edit other `src/lib/auth/` files. The only documented exception is the
  single email/password flag in `email-password.ts` when that method is
  explicitly required.
- Never create `src/routes/auth/popup.tsx`. `/auth/popup` is served by the
  template's Vite plugin. A React route there opens the full app inside the
  popup and breaks broker login.
- Never edit `migrations/auth/0001_auth.sql`.
- Never recreate `vite.config.ts`, `tsconfig.json`, or the auth configuration.
- Preserve `AuthProvider` around the route outlet and preserve
  `PreviewHostBridge` in `src/routes/__root.tsx`.
- Extend the existing root route rather than replacing it wholesale.
- Use `.validator()` for server-function inputs. `.inputValidator()` is
  deprecated in this template.

## 4. Secrets and environment configuration

Never create `.env`, `.env.local`, or `.env.example` in the Grok workspace.

Live preview requires no user-created environment file. Deployment injects the
required values. Never expose a non-`VITE_` value to client code.

| Variable | Visibility | Purpose |
| --- | --- | --- |
| `VITE_AUTH_ENABLED` | Client-visible | Shipped as `"false"`; remove the key to turn real authentication on. |
| `BETTER_AUTH_URL` | Server only | Public application origin when deployed. |
| `BETTER_AUTH_SECRET` | Server only | Signs the app's own sessions. |
| `GROK_AUTH_ISSUER` | Server only | Shared broker; defaults to `https://auth.grok.me`. |
| `GROK_AUTH_CLIENT_ID` | Server only | Per-app broker client; preview has a platform fallback. |
| `GROK_AUTH_CLIENT_SECRET` | Server only | Per-app broker secret; preview has a platform fallback. |
| `DATABASE_URL` | Server only | Deployed Postgres connection. Preview falls back to embedded PGLite. |

Never log, display, return, commit, or copy passwords, cookies, bearer tokens,
authorization codes, provider responses, database URLs, or private environment
values.

## 5. Preview and deployed behavior

### Live preview

- The app is embedded in an iframe on `*.grok-sandbox.com`.
- Sign-in opens a top-level popup and federates through the platform preview
  client.
- The popup returns a session bearer to the embedded app.
- Sessions and application data use embedded PGLite.
- Restarting preview resets the embedded database.

### Deployed app

- The platform injects a per-app broker client and `DATABASE_URL`.
- Better Auth persists identities and sessions in Postgres.
- Same-origin cookies are available to top-level requests.

Both modes use real authentication. A preview visitor is signed out until they
actually sign in.

## 6. Turn authentication on

Complete all steps in this order. Adding routes alone leaves authentication in
the disabled branch.

### Step 1: Enable the flag

Delete only the `VITE_AUTH_ENABLED` key from `.grok/app-env.json`.

Before:

```json
{
  "VITE_AUTH_ENABLED": "false"
}
```

After:

```json
{}
```

Restart with the supported script:

```bash
npm run dev
```

Do not start Vite directly. The `npm run dev`, `npm run build`, and
`npm run preview` commands all load `.grok/app-env.json` through
`scripts/with-app-env.mjs`. HMR does not reload this flag.

### Step 2: Apply the auth schema

Copy the existing schema without editing it:

```bash
cp migrations/auth/0001_auth.sql migrations/0001_auth.sql
```

The migration system tracks applied migrations by basename. A database that has
already applied `0001_auth.sql` will not rerun it.

Application tables belong in new ordered files such as
`migrations/0002_accounts_extension.sql`. Never rewrite an applied migration.

### Step 3: Mount Better Auth

Create `src/routes/api/auth/$.ts`:

```ts
import { createFileRoute } from "@tanstack/react-router";
import { auth } from "@/lib/auth/server";

export const Route = createFileRoute("/api/auth/$")({
  server: {
    handlers: {
      GET: ({ request }) => auth.handler(request),
      POST: ({ request }) => auth.handler(request),
    },
  },
});
```

This route mounts `/api/auth/*` and receives the broker callback.

### Step 4: Add the login route

Create `src/routes/login.tsx`:

```tsx
import { createFileRoute } from "@tanstack/react-router";
import { GROK_PROVIDERS, authEnabled, signIn } from "@/lib/auth/client";

export const Route = createFileRoute("/login")({ component: Login });

function Login() {
  return (
    <main className="grid min-h-screen place-items-center p-6">
      <div className="w-full max-w-sm space-y-3">
        <h1 className="text-xl font-semibold">Sign in</h1>

        {authEnabled ? (
          GROK_PROVIDERS.map((provider) => (
            <button
              key={provider.providerId}
              type="button"
              onClick={() => signIn(provider.providerId, { callbackURL: "/" })}
              className="w-full cursor-pointer rounded-md border border-neutral-300 px-4 py-2 hover:bg-neutral-100 dark:border-neutral-700 dark:hover:bg-neutral-900"
            >
              Continue with {provider.label}
            </button>
          ))
        ) : (
          <p className="text-sm text-neutral-500">Sign-in is disabled.</p>
        )}
      </div>
    </main>
  );
}
```

Prefer a fixed same-origin callback such as `/`. If dynamic return paths are
required, accept only normalized application-owned paths beginning with one
slash. Reject absolute URLs, protocol-relative URLs, backslashes, schemes,
encoded bypasses, control characters, traversal, and login/logout redirect
loops.

### Step 5: Provide sign-out

Render `UserButton` for signed-in users:

```tsx
import { SignedIn, SignedOut, UserButton } from "@/lib/auth/gates";

export function AuthActions() {
  return (
    <div>
      <SignedOut>
        <a href="/login">Sign in</a>
      </SignedOut>
      <SignedIn>
        <UserButton />
      </SignedIn>
    </div>
  );
}
```

Use `UserButton` or `signOut()` from `@/lib/auth/client`. Never call
`authClient.signOut()` directly: in preview it can leave the bearer attachment
active and make the visitor appear signed in after logout.

Catch sign-out failure. A login flow without a reliable logout path is not
complete.

### Step 6: Protect existing data

Do not give rows created before authentication to the first user who signs in.
Explicitly map ownership, quarantine the rows, or recreate known development
data with authorization.

Every private server function must use `authMiddleware`, and every database read
and mutation must include the verified user identity.

## 7. Reading and gating the current user

`useCurrentUser()` is for display only. Its `null` value can mean either loading
or signed out. Never redirect based on it alone.

Use `useCurrentUserState()` for guards:

```tsx
import { useCurrentUserState } from "@/lib/auth/use-current-user";
import { RedirectToSignIn } from "@/lib/auth/gates";

export function ProtectedPage() {
  const { user, isPending } = useCurrentUserState();

  if (isPending) {
    return <div className="min-h-32 animate-pulse rounded-lg bg-black/10" />;
  }

  if (!user) {
    return <RedirectToSignIn />;
  }

  return <main>Protected content</main>;
}
```

Rules:

- Wait for `isPending` to clear before treating `user: null` as signed out.
- Render a same-sized skeleton while pending to avoid layout shift, hydration
  mismatch, and a signed-out flash.
- Guard at stable layout or page-shell boundaries instead of repeatedly gating
  leaf components.
- Prefer `RedirectToSignIn`, which uses TanStack navigation, over
  `window.location.href`.
- Client guards protect presentation only. Server functions still require
  authentication and authorization.

## 8. Optional zero-flash deployed SSR

Deployed top-level requests can resolve the same-origin session cookie during
server rendering:

```tsx
import { createServerFn } from "@tanstack/react-start";

const fetchSessionUser = createServerFn({ method: "GET" }).handler(async () => {
  const { getSessionUser } = await import("@/lib/auth/verify.server");
  const user = await getSessionUser();
  return user ? { id: user.id, email: user.email } : null;
});
```

Merge this into the existing root route's `beforeLoad`; do not replace the
existing `head()`, `PreviewHostBridge`, `AuthProvider`, outlet, or scripts.

Live preview may still resolve the session client-side because its session can
ride the popup bearer handoff. Continue gating on `isPending` in both modes.

The template already enables Better Auth's session cookie cache, allowing
`/api/auth/get-session` to answer from the cookie where available.

## 9. Protect per-user data on the server

Use `authMiddleware` on every server function that touches private data:

```ts
import { createServerFn } from "@tanstack/react-start";
import { getSql } from "@/lib/db";
import { authMiddleware } from "@/lib/auth/middleware";

export const listTodos = createServerFn({ method: "GET" })
  .middleware([authMiddleware])
  .handler(async ({ context }) => {
    const sql = await getSql();

    return sql<{ id: number; title: string; done: boolean }>`
      select id, title, done
      from todos
      where user_id = ${context.userId}
      order by id desc
    `;
  });

export const addTodo = createServerFn({ method: "POST" })
  .validator((title: string) => title.trim())
  .middleware([authMiddleware])
  .handler(async ({ context, data: title }) => {
    if (!title) return;

    const sql = await getSql();
    await sql`
      insert into todos (user_id, title)
      values (${context.userId}, ${title})
    `;
  });
```

Mandatory rules:

- Derive identity only from `context.userId` or the server-only verifier.
- Never trust a client-supplied `userId`, `ownerId`, email, role, or tenant.
- Scope every `SELECT`, `UPDATE`, `DELETE`, and `UPSERT` by the verified user.
- Put ownership in the mutation predicate:

  ```sql
  update todos
  set title = $1
  where id = $2 and user_id = $3
  ```

- Use `user_id TEXT NOT NULL`, not UUID, and add an index.
- Use the database only inside server functions or server loaders.
- Signed-out requests must fail with `UnauthorizedError` and status 401.
- Authenticated callers lacking authorization should receive 403 or an
  intentionally non-disclosing 404 according to the application's contract.
- UI visibility and client route guards never authorize database operations.

Example application migration:

```sql
-- migrations/0002_todos.sql
create table if not exists todos (
  id         serial primary key,
  user_id    text not null,
  title      text not null,
  done       boolean not null default false,
  created_at timestamptz not null default now()
);

create index if not exists todos_user_id_idx on todos (user_id);
```

## 10. Authorization and privileged roles

Authentication answers who the user is. It does not automatically grant access
to an object, tenant, administrative route, export, job, or destructive action.

- Default every new user to least privilege.
- Never make the first registrant an administrator.
- Never trust a role submitted by the browser.
- Never derive permanent authorization solely from display name or email.
- Keep reusable role and ownership checks in server-only policy helpers.
- Include tenant identity in queries, caches, jobs, exports, and file paths when
  the application is multi-tenant.
- Role assignment must be an explicit owner-controlled or already-authorized
  server operation.
- Do not invent an admin system if the product does not require one.

## 11. Optional local email/password

Keep local email/password disabled unless the user explicitly requests it.

Enable it by editing only:

```ts
// src/lib/auth/email-password.ts
export const emailAndPasswordEnabled = true;
```

Then use the existing client:

```ts
import { authClient } from "@/lib/auth/client";

await authClient.signUp.email({
  name,
  email,
  password,
});

await authClient.signIn.email({
  email,
  password,
});
```

Do not:

- rewrite `server.ts`;
- add `emailAndPassword` as a plugin entry;
- invent a second Better Auth configuration;
- create another migration for the password column;
- disable CSRF or origin validation to fix an error.

The copied Better Auth schema already includes the password column.

If the server returns `Invalid origin`, open the app from a supported origin:

- `*.grok-sandbox.com`;
- `http://localhost:8080`;
- `http://127.0.0.1:8080`;
- loopback `[::1]` on port 8080.

Do not weaken `trustedOrigins` or edit `server.ts`.

## 12. Existing protections to preserve

The platform integration already provides:

- a headless broker holding the Google/X upstream secrets;
- application-local sessions rather than upstream provider tokens;
- `__Host-` cookie behavior;
- trusted-origin enforcement;
- Fetch Metadata sibling isolation;
- provider-token isolation on the broker;
- session cookie caching.

Do not duplicate, replace, or weaken these controls. Verify their runtime
behavior where access permits.

The P2P multiplayer system is not an authorization boundary: peers can lie and
learn each other's network addresses. Never trust peer identity, room
membership, scores, or messages for application permissions.

If the app calls the xAI API, keep `XAI_API_KEY` server-only. Protect expensive
operations with `authMiddleware`, per-user limits, bounded retries, and caching.

## 13. Verification checklist

Do not call authentication complete from source inspection or a passing build.

### Source and configuration

- [ ] No new auth library or provider was added.
- [ ] No `.env`, `.env.local`, or `.env.example` was created.
- [ ] No secret, password, token, cookie, private environment, or hardcoded user
      appears in source, browser code, logs, or the handoff.
- [ ] `src/lib/auth/server.ts`, provider configuration, popup handling, and the
      source auth migration remain unchanged.
- [ ] `AuthProvider` and `PreviewHostBridge` remain in the root shell.
- [ ] Application migrations are ordered and existing applied migrations were
      not rewritten.

### Commands

Run against the live development server:

```bash
npm run check:auth
```

Interpretation:

- exit 0: the running server and next build agree about the auth flag;
- exit 1: they disagree;
- exit 2: the check could not observe the live server.

Then run the project's focused checks and:

```bash
npm run build
```

After rebuilding, stop any old preview and start a fresh one:

```bash
npm run preview
```

A running preview serves the previous build until restarted.

### Authentication behavior

- [ ] Signed-out protected reads and mutations return 401.
- [ ] Login starts the correct Google/X broker flow.
- [ ] Cancelling or failing provider login creates no session.
- [ ] A successful login resolves the expected application identity.
- [ ] Hard reload does not bounce a signed-in user to login.
- [ ] Pending state does not flash signed-out or protected content.
- [ ] `/auth/popup` does not render the React application shell.
- [ ] Logout uses `UserButton` or the prewired `signOut()` wrapper.
- [ ] Protected server calls fail after logout, including after browser back.
- [ ] Expired or invalid sessions fail closed without a redirect loop.

### Authorization and isolation

Use two separate test identities when safe:

- [ ] User A cannot list, read, update, delete, export, or trigger jobs for user
      B's objects.
- [ ] Forged `userId`, `ownerId`, email, role, and tenant input is ignored or
      rejected.
- [ ] Mutations contain ownership predicates.
- [ ] Cache and prefetch keys do not cross users.
- [ ] Administrative and bulk operations have separate server authorization.

### Browser and protocol checks

- [ ] Malicious return paths are rejected, including absolute URLs,
      protocol-relative URLs, encoded schemes, backslashes, traversal, and loops.
- [ ] Cross-origin state-changing requests fail without weakening protections.
- [ ] Browser URLs, console, DOM, storage, analytics, and network response bodies
      expose no token or secret.
- [ ] Deployed cookies are inspected without printing their values: `Secure`,
      `HttpOnly`, expected `SameSite`, `Path=/`, no broad `Domain`, and valid
      `__Host-` prefix behavior.

### Desktop and mobile browser QA

Development preview:

```bash
mkdir -p /workspace/screenshots
node scripts/browser-smoke.mjs \
  http://127.0.0.1:8080/ \
  /workspace/screenshots/app-builder-preview.png
```

Built preview:

```bash
node scripts/browser-smoke.mjs \
  http://127.0.0.1:8081/ \
  /workspace/screenshots/app-builder-built.png \
  --baseline /workspace/screenshots/app-builder-preview.json
```

Inspect both desktop and mobile screenshots. Check console errors, page errors,
horizontal overflow, login, loading, failure, signed-in, and signed-out states.

## 14. Completion and handoff

Report:

1. the identity provider, application session, server, and database trust
   boundaries;
2. exact files and migrations changed;
3. protected routes and server functions;
4. how every private table is scoped;
5. positive and denial-path test results;
6. browser states verified on desktop and mobile;
7. remaining inherited provider or platform limitations;
8. owner actions still required;
9. separate statuses for source edits, migration, provider configuration,
   deployment, commit, push, and production verification.

Building locally does not authorize or prove platform deployment. If real
provider login or deployed cookie inspection requires owner interaction, record
the exact manual procedure and expected result instead of fabricating proof.

## 15. Underlying platform sources

This single document consolidates the current contracts from:

- `.grok/skills/auth/SKILL.md`;
- `.grok/skills/auth/references/wiring.md`;
- `.grok/skills/auth/references/sign-in-methods.md`;
- `.grok/skills/auth/references/prewired-and-env.md`;
- `.grok/skills/auth/references/session-ui.md`;
- `.grok/skills/auth/references/per-user-data.md`;
- `.grok/skills/neon/SKILL.md`;
- `.grok/references/data-and-auth.md`;
- `.grok/references/scaffold.md`;
- `.grok/references/deploy-target.md`;
- `.grok/references/browser-qa.md`.

The current workspace files remain authoritative if the platform changes.
