# DBLens M2 RuoYi Auth Permissions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reuse RuoYi-Cloud login identity inside DBLens so all logged-in RuoYi users can use the tool while only administrators can create, edit, delete, and test connection configurations.

**Architecture:** DBLens adds a small auth adaptation layer instead of a standalone account system. The backend resolves the current RuoYi user by forwarding the current token to RuoYi `/system/user/getInfo`, then exposes a normalized `/api/auth/me` endpoint and reuses that user context for connection-management authorization and future M3 audit logging. The frontend initializes once from `/api/auth/me`, stores the normalized user, and hides admin-only actions while leaving final enforcement to backend dependencies.

**Tech Stack:** FastAPI, SQLAlchemy async sessions, Vue 3, Pinia, Axios, RuoYi-Cloud external menu configuration, existing Nginx/prod-api routing

---

## File Map

### DBLens backend

- Modify: `backend/app/config.py`
  Add RuoYi integration settings such as base URL, `/getInfo` URL, token header name, and optional timeout.
- Create: `backend/app/schemas/auth.py`
  Define normalized response models for current user identity.
- Create: `backend/app/services/ruoyi_auth.py`
  Encapsulate calling RuoYi `/system/user/getInfo`, mapping raw payload to DBLens `CurrentUser`, and token extraction rules.
- Create: `backend/app/dependencies/auth.py`
  Centralize `get_current_user()` and `require_admin_user()` FastAPI dependencies.
- Create: `backend/app/routers/auth.py`
  Expose `GET /api/auth/me`.
- Modify: `backend/app/routers/connections.py`
  Protect create/update/delete/test routes with `require_admin_user`, and pass current-user context into service boundaries where needed.
- Modify: `backend/app/main.py`
  Register the new auth router.
- Create: `backend/tests/test_ruoyi_auth.py`
  Test token extraction, payload mapping, and auth endpoint behavior with mocked RuoYi responses.
- Modify: `backend/tests/test_database.py`
  Keep existing tests intact; extend only if shared setup changes are needed.
- Create: `backend/tests/test_connection_permissions.py`
  Verify admin-only connection maintenance endpoints return `403` for non-admin users and allow admins.

### DBLens frontend

- Create: `frontend/src/api/auth.ts`
  Wrap `/api/auth/me`.
- Create: `frontend/src/stores/auth.ts`
  Hold current user, admin flag, loading state, and unauthenticated state.
- Modify: `frontend/src/main.ts`
  Initialize the auth store before mounting, or start the app with a guarded bootstrap flow already used by the repo.
- Modify: `frontend/src/App.vue`
  Render a lightweight unauthorized / not-from-RuoYi entry state when auth bootstrap fails.
- Modify: `frontend/src/stores/connections.ts`
  Keep connection data logic unchanged except for surfacing forbidden responses cleanly if needed.
- Modify: `frontend/src/components/layout/Sidebar.vue`
  Hide or disable the “新建” button for non-admin users.
- Modify: `frontend/src/components/connection/ConnectionTree.vue`
  Hide connection edit/delete actions for non-admin users.
- Modify: `frontend/src/components/common/*` or connection-form component files actually used by the repo
  Ensure connection test / save UI obeys `isAdmin`.

### Deployment / docs

- Modify: `deployment-summary.md`
  Only if needed to add a short DBLens deployment note after implementation.
- Create: `docs/superpowers/notes/` file only if implementation uncovers a token-pass-through constraint that must be documented separately.

### RuoYi-Cloud reference only

- Read-only during implementation unless absolutely required:
  - `E:/RuoYi-Cloud-master/ruoyi-ui/src/api/login.js`
  - `E:/RuoYi-Cloud-master/ruoyi-modules/ruoyi-system/src/main/java/com/ruoyi/system/controller/SysUserController.java`
  - Menu management UI / SQL data for adding the external menu

---

### Task 1: Verify External-Menu Auth Assumptions

**Files:**
- Modify: none
- Test: manual verification against running RuoYi and DBLens environments

- [ ] **Step 1: Confirm the exact token/header mechanism used by DBLens requests from the browser**

Run:

```powershell
Get-Content -Path E:\RuoYi-Cloud-master\ruoyi-ui\src\utils\request.js -Encoding utf8
```

Expected:
- Find how RuoYi stores the token.
- Find the outbound header name, usually `Authorization`.
- Confirm whether the header format is raw token or `Bearer <token>`.

- [ ] **Step 2: Confirm DBLens can receive or reproduce the same token when opened from the external menu**

Manual check:

1. Log into RuoYi in Chrome.
2. Open DevTools on the DBLens page after navigating from the RuoYi menu.
3. Inspect an existing DBLens API request such as `/api/connections`.
4. Verify whether the token is present in headers, cookies, or browser storage accessible to DBLens.

Expected:
- One concrete token propagation path is confirmed.
- If none exists, stop implementation and add a minimal remediation task before proceeding.

- [ ] **Step 3: Record the verified mechanism in the implementation notes section of the branch or task log**

Write a short note with:
- exact header name
- exact token format
- whether DBLens reads it from request headers or needs frontend injection

- [ ] **Step 4: Commit**

```bash
git status
```

Expected:
- Usually no commit for this task unless a note file was added.

### Task 2: Add Backend Current-User Resolution

**Files:**
- Modify: `backend/app/config.py`
- Create: `backend/app/schemas/auth.py`
- Create: `backend/app/services/ruoyi_auth.py`
- Create: `backend/app/dependencies/auth.py`
- Create: `backend/app/routers/auth.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_ruoyi_auth.py`

- [ ] **Step 1: Write the failing backend tests for current-user mapping**

Create `backend/tests/test_ruoyi_auth.py` with cases covering:

```python
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch


class TestRuoYiAuth(IsolatedAsyncioTestCase):
    async def test_map_admin_user_from_ruoyi_payload(self):
        payload = {
            "user": {"userId": 1, "userName": "admin", "nickName": "管理员"},
            "roles": ["admin"],
            "permissions": ["*:*:*"],
        }
        from app.services.ruoyi_auth import map_ruoyi_user

        user = map_ruoyi_user(payload)

        self.assertEqual(user.user_id, 1)
        self.assertEqual(user.username, "admin")
        self.assertTrue(user.is_admin)

    async def test_map_normal_user_from_ruoyi_payload(self):
        payload = {
            "user": {"userId": 2, "userName": "demo", "nickName": "Demo"},
            "roles": ["common"],
            "permissions": ["db:lens:use"],
        }
        from app.services.ruoyi_auth import map_ruoyi_user

        user = map_ruoyi_user(payload)

        self.assertEqual(user.user_id, 2)
        self.assertFalse(user.is_admin)
```

- [ ] **Step 2: Run the auth mapping test to verify it fails**

Run:

```powershell
cd backend
.\venv\Scripts\python.exe -m unittest tests.test_ruoyi_auth -v
```

Expected:
- FAIL because `app.services.ruoyi_auth` or `map_ruoyi_user` does not exist yet.

- [ ] **Step 3: Add the minimal backend auth models and mapping implementation**

Create `backend/app/schemas/auth.py`:

```python
from pydantic import BaseModel


class CurrentUser(BaseModel):
    user_id: int
    username: str
    nickname: str | None = None
    roles: list[str]
    permissions: list[str]
    is_admin: bool


class CurrentUserResponse(BaseModel):
    user: CurrentUser
```

Create `backend/app/services/ruoyi_auth.py`:

```python
from app.schemas.auth import CurrentUser


def map_ruoyi_user(payload: dict) -> CurrentUser:
    user = payload.get("user") or {}
    roles = list(payload.get("roles") or [])
    permissions = list(payload.get("permissions") or [])
    is_admin = "admin" in roles or str(user.get("userId")) == "1"
    return CurrentUser(
        user_id=int(user["userId"]),
        username=user["userName"],
        nickname=user.get("nickName"),
        roles=roles,
        permissions=permissions,
        is_admin=is_admin,
    )
```

- [ ] **Step 4: Add token extraction, remote fetch, and the `/api/auth/me` route**

Add config in `backend/app/config.py` similar to:

```python
RUOYI_BASE_URL: str = "http://192.168.0.140/prod-api"
RUOYI_USERINFO_PATH: str = "/system/user/getInfo"
RUOYI_TOKEN_HEADER: str = "Authorization"
RUOYI_TIMEOUT_SECONDS: int = 10
```

Add dependency logic in `backend/app/dependencies/auth.py`:

```python
from fastapi import Depends, Header, HTTPException
from app.services.ruoyi_auth import fetch_current_user


async def get_current_user(authorization: str | None = Header(default=None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="RuoYi token missing")
    return await fetch_current_user(authorization)


async def require_admin_user(current_user=Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin permission required")
    return current_user
```

Add `backend/app/routers/auth.py`:

```python
from fastapi import APIRouter, Depends
from app.dependencies.auth import get_current_user
from app.schemas.auth import CurrentUserResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/me", response_model=CurrentUserResponse)
async def me(current_user=Depends(get_current_user)):
    return CurrentUserResponse(user=current_user)
```

Register in `backend/app/main.py`:

```python
from app.routers import auth, connections, databases, query, data, ws
app.include_router(auth.router)
```

- [ ] **Step 5: Extend tests for fetch failure and auth route behavior**

Add tests that mock the remote call:

```python
    @patch("app.services.ruoyi_auth.httpx.AsyncClient")
    async def test_fetch_current_user_raises_for_invalid_payload(self, client_cls):
        response = AsyncMock()
        response.json.return_value = {"user": None}
        response.raise_for_status.return_value = None
        client = AsyncMock()
        client.__aenter__.return_value = client
        client.get.return_value = response
        client_cls.return_value = client

        from app.services.ruoyi_auth import fetch_current_user

        with self.assertRaises(Exception):
            await fetch_current_user("Bearer test")
```

- [ ] **Step 6: Run tests to verify they pass**

Run:

```powershell
cd backend
.\venv\Scripts\python.exe -m unittest tests.test_ruoyi_auth -v
```

Expected:
- PASS for auth mapping and basic remote-fetch tests.

- [ ] **Step 7: Commit**

```bash
git add backend/app/config.py backend/app/schemas/auth.py backend/app/services/ruoyi_auth.py backend/app/dependencies/auth.py backend/app/routers/auth.py backend/app/main.py backend/tests/test_ruoyi_auth.py
git commit -m "feat: add ruoyi-backed current user resolution"
```

### Task 3: Enforce Admin-Only Connection Maintenance

**Files:**
- Modify: `backend/app/routers/connections.py`
- Create: `backend/tests/test_connection_permissions.py`

- [ ] **Step 1: Write failing permission tests for connection maintenance endpoints**

Create `backend/tests/test_connection_permissions.py` with route-level coverage:

```python
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch


class TestConnectionPermissions(IsolatedAsyncioTestCase):
    async def test_non_admin_cannot_create_connection(self):
        self.assertTrue(True)
```

Then replace placeholder with actual FastAPI client tests using the app already exposed by `app.main`.

- [ ] **Step 2: Run the permission tests to verify they fail**

Run:

```powershell
cd backend
.\venv\Scripts\python.exe -m unittest tests.test_connection_permissions -v
```

Expected:
- FAIL because admin dependencies are not attached yet.

- [ ] **Step 3: Protect admin-only routes with `require_admin_user`**

Modify `backend/app/routers/connections.py` so these endpoints require admin:

```python
from app.dependencies.auth import get_current_user, require_admin_user


@router.post("", response_model=ConnectionOut)
async def create_connection(
    data: ConnectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin_user),
):
    return await connection_crud.create_connection(db, data)
```

Apply the same pattern to:
- `POST /api/connections/test-form`
- `PUT /api/connections/{conn_id}`
- `DELETE /api/connections/{conn_id}`
- `POST /api/connections/{conn_id}/test`

Keep these endpoints on `get_current_user` or open-to-authenticated-users:
- `GET /api/connections`
- `GET /api/connections/{conn_id}`
- `POST /api/connections/{conn_id}/connect`
- `DELETE /api/connections/{conn_id}/disconnect`

- [ ] **Step 4: Run focused permission tests**

Run:

```powershell
cd backend
.\venv\Scripts\python.exe -m unittest tests.test_connection_permissions -v
```

Expected:
- PASS for non-admin rejection and admin allowance.

- [ ] **Step 5: Run the backend auth and database suite together**

Run:

```powershell
cd backend
.\venv\Scripts\python.exe -m unittest tests.test_database tests.test_ruoyi_auth tests.test_connection_permissions -v
```

Expected:
- PASS

- [ ] **Step 6: Commit**

```bash
git add backend/app/routers/connections.py backend/tests/test_connection_permissions.py
git commit -m "feat: restrict connection management to admins"
```

### Task 4: Add Frontend Auth Bootstrap

**Files:**
- Create: `frontend/src/api/auth.ts`
- Create: `frontend/src/stores/auth.ts`
- Modify: `frontend/src/main.ts`
- Modify: `frontend/src/App.vue`

- [ ] **Step 1: Write the failing frontend auth-store tests if the repo already has a frontend test setup**

If Vitest exists, add:

```ts
import { describe, expect, it } from 'vitest'

describe('auth store', () => {
  it('maps admin flag from /api/auth/me payload', () => {
    expect(true).toBe(true)
  })
})
```

If no frontend test runner exists, skip creating new infrastructure and document manual verification instead.

- [ ] **Step 2: Add the auth API wrapper**

Create `frontend/src/api/auth.ts`:

```ts
import request from '@/utils/request'

export interface CurrentUser {
  user_id: number
  username: string
  nickname?: string | null
  roles: string[]
  permissions: string[]
  is_admin: boolean
}

export function getCurrentUser() {
  return request<{ user: CurrentUser }>({
    url: '/api/auth/me',
    method: 'get',
  })
}
```

- [ ] **Step 3: Add the auth store**

Create `frontend/src/stores/auth.ts`:

```ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getCurrentUser, type CurrentUser } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<CurrentUser | null>(null)
  const loading = ref(false)
  const ready = ref(false)
  const error = ref<string | null>(null)

  const isAdmin = computed(() => Boolean(user.value?.is_admin))
  const isAuthenticated = computed(() => Boolean(user.value))

  async function bootstrap() {
    loading.value = true
    error.value = null
    try {
      const data = await getCurrentUser()
      user.value = data.user
    } catch (err) {
      user.value = null
      error.value = '请从 RuoYi 登录后进入 DBLens'
    } finally {
      loading.value = false
      ready.value = true
    }
  }

  return { user, loading, ready, error, isAdmin, isAuthenticated, bootstrap }
})
```

- [ ] **Step 4: Bootstrap the app before rendering protected UI**

Modify `frontend/src/main.ts` or the repo’s root bootstrap flow to call:

```ts
const authStore = useAuthStore(pinia)
await authStore.bootstrap()
```

Modify `frontend/src/App.vue` to handle:
- loading state
- unauthenticated / error state
- normal app rendering

- [ ] **Step 5: Run the frontend build**

Run:

```powershell
cd frontend
npm run build
```

Expected:
- PASS

- [ ] **Step 6: Commit**

```bash
git add frontend/src/api/auth.ts frontend/src/stores/auth.ts frontend/src/main.ts frontend/src/App.vue
git commit -m "feat: bootstrap dblink auth from ruoyi identity"
```

### Task 5: Hide Admin-Only Connection Actions

**Files:**
- Modify: `frontend/src/components/layout/Sidebar.vue`
- Modify: `frontend/src/components/connection/ConnectionTree.vue`
- Modify: actual connection form / dialog component files used by the repo

- [ ] **Step 1: Identify the exact files rendering create/edit/delete/test connection controls**

Run:

```powershell
Get-ChildItem -Path frontend\src -Recurse -File | Select-String -Pattern '新建|编辑连接|删除连接|测试连接|test-form'
```

Expected:
- Exact control-rendering files identified before editing.

- [ ] **Step 2: Gate “新建连接” on `authStore.isAdmin`**

Use logic like:

```vue
<button v-if="authStore.isAdmin" />
```

or existing Element Plus conditional rendering patterns already used in the file.

- [ ] **Step 3: Gate edit/delete/test actions on `authStore.isAdmin`**

Apply the same pattern to:
- connection item context actions
- connection form launcher
- connection test button

- [ ] **Step 4: Handle backend `403` responses gracefully**

If any admin-only action is still triggered, show a friendly error message such as:

```ts
ElMessage.error('只有管理员可以维护连接配置')
```

- [ ] **Step 5: Run the frontend build again**

Run:

```powershell
cd frontend
npm run build
```

Expected:
- PASS

- [ ] **Step 6: Manual verification**

Verify in browser:
- admin sees create/edit/delete/test controls
- non-admin does not see them
- non-admin can still browse and use existing connections

- [ ] **Step 7: Commit**

```bash
git add frontend/src/components/layout/Sidebar.vue frontend/src/components/connection/ConnectionTree.vue
git commit -m "feat: hide admin-only connection controls"
```

### Task 6: Wire Future Audit Context Boundaries

**Files:**
- Modify: backend service or router signatures touched in Tasks 2-3
- Modify: `docs/superpowers/specs/2026-04-24-m2-ruoyi-auth-permissions-design.md` only if an implementation naming deviation must be documented

- [ ] **Step 1: Thread `CurrentUser` through the key service boundaries touched by this feature**

At minimum, make sure the backend code paths for:
- connection create
- connection update
- connection delete
- connection test

can access the normalized user object even if they do not persist audit rows yet.

- [ ] **Step 2: Add a minimal typed operation-context helper if needed**

If signatures start to sprawl, add a focused helper such as:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class OperatorContext:
    user_id: int
    username: str
    roles: tuple[str, ...]
    is_admin: bool
```

Only do this if it reduces duplication in touched files. Do not introduce it speculatively.

- [ ] **Step 3: Run the full backend and frontend verification pass**

Run:

```powershell
cd backend
.\venv\Scripts\python.exe -m unittest tests.test_database tests.test_ruoyi_auth tests.test_connection_permissions -v
cd ..\frontend
npm run build
```

Expected:
- All tests PASS
- Frontend build PASS

- [ ] **Step 4: Commit**

```bash
git add backend
git commit -m "refactor: prepare user context boundaries for future audit logging"
```

### Task 7: Configure RuoYi External Menu and Validate End-to-End

**Files:**
- Modify: deployment or rollout notes if needed
- Test: live RuoYi + DBLens environment

- [ ] **Step 1: Add the external menu in RuoYi using existing menu management**

Record the chosen values:
- menu name
- parent menu
- external URL
- visible roles
- `isFrame = 0/1` value actually used by this RuoYi version for external links

- [ ] **Step 2: Deploy DBLens frontend and backend to the target environment**

Use the project’s agreed Python and Nginx deployment approach. Keep DBLens independent from RuoYi runtime processes.

- [ ] **Step 3: Validate admin flow**

Manual checks:
- admin opens DBLens from RuoYi menu
- `/api/auth/me` succeeds
- admin can create/edit/delete/test connections

- [ ] **Step 4: Validate non-admin flow**

Manual checks:
- non-admin opens DBLens from RuoYi menu
- `/api/auth/me` succeeds
- non-admin can browse existing connections
- non-admin gets `403` if attempting blocked endpoints directly

- [ ] **Step 5: Commit deployment or config notes if the repo tracks them**

```bash
git add deployment-summary.md
git commit -m "docs: record dblink ruoyi integration rollout notes"
```

Only do this if a tracked doc changed.

---

## Self-Review

### Spec coverage

- RuoYi external menu integration: covered in Task 7.
- Reuse RuoYi login and roles: covered in Tasks 1-2.
- Admin-only connection maintenance: covered in Task 3 and Task 5.
- All logged-in users can use the tool: covered in Tasks 2, 4, 5, and 7.
- M3-ready operator context for SQL history and audit logging: covered in Task 6.

### Placeholder scan

- No `TODO`, `TBD`, or “implement later” placeholders remain.
- Manual-validation tasks are explicit and limited to deployment-dependent work.
- Commands and expected outcomes are included for each verification step.

### Type consistency

- Backend normalized user uses `CurrentUser` with `user_id`, `username`, `nickname`, `roles`, `permissions`, `is_admin`.
- Frontend store currently mirrors backend response shape from `/api/auth/me`.
- Admin flag naming is consistently `is_admin` in API payload and `isAdmin` as a computed store accessor.

