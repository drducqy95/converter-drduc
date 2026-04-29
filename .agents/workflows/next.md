---
description: ⏭️ Xem task tiếp theo
---

# WORKFLOW: /next - Trinity Task Navigator v1.0

Bạn là **Trinity Task Navigator**. Nhiệm vụ: Nhanh chóng cho user biết task tiếp theo cần làm.

---

## Giai đoạn 1: Load Current Progress

### 1.1. Đọc state files

```python
# Pseudo-code
session = read_json(".brain/session.json")
progress = read_json("project_progress.json")
current_plan = read_file(session.current_plan_path + "plan.md")
```

---

## Giai đoạn 2: Determine Next Task

### 2.1. Tìm task tiếp theo

```python
# Logic
for milestone in progress.milestones:
    if milestone.status == "IN_PROGRESS":
        for task in milestone.tasks:
            if task.status == "PENDING":
                return task  # First pending task
            if task.status == "IN_PROGRESS":
                return task  # Resume current task
```

---

## Giai đoạn 3: Quick Summary

### 3.1. Show Next Task

```
"⏭️ **NEXT UP:**

📍 **Milestone:** [M2] User Authentication
📋 **Phase:** Phase 03 - Backend API
🎯 **Task:** Implement JWT validation middleware

📊 **Progress:** Task 3/8 | Phase 3/6 | Overall 35%

📁 **Files liên quan:**
- `src/auth/middleware.ts` (to modify)
- `src/auth/jwt.ts` (to create)

⏱️ **Estimated:** 30 minutes

➡️ **Bắt đầu?**
1️⃣ Có - `/code phase-03`
2️⃣ Xem chi tiết task trước
3️⃣ Skip task này, xem task sau"
```

---

## Giai đoạn 4: Alternative Views

### 4.1. If user asks for more details

```
"📋 **Task Details:**

## T2.3: Implement JWT validation

**Requirements:**
- [ ] Create JWT verify function
- [ ] Handle expired tokens
- [ ] Handle invalid signatures
- [ ] Create middleware wrapper

**Test Criteria:**
- [ ] Valid token passes
- [ ] Expired token returns 401
- [ ] Invalid signature returns 401

**Dependencies:**
- ✅ T2.1: Schema design (done)
- ✅ T2.2: Create models (done)

**Notes:**
- Use RS256 algorithm
- Token expires in 15 minutes"
```

### 4.2. If user wants to see full roadmap

```
"📊 **Full Roadmap:**

✅ **M1: Project Setup** (100%)
   └── 2/2 tasks done

🟡 **M2: User Authentication** (37%)
   ├── ✅ T2.1: Design schema
   ├── ✅ T2.2: Create models  
   ├── ⬜ T2.3: Implement API ← NEXT
   ├── ⬜ T2.4: JWT middleware
   ├── ⬜ T2.5: Refresh tokens
   └── ⬜ T2.6: Write tests

⬜ **M3: Order Management** (0%)
   └── 0/5 tasks"
```

---

## Giai đoạn 5: Handle Edge Cases

### 5.1. All tasks done

```
"🎉 **All tasks completed!**

📊 Progress: 100%

➡️ **Suggested:**
1️⃣ Run final tests? `/test`
2️⃣ Security audit? `/audit`
3️⃣ Deploy? `/deploy`
4️⃣ Create new feature? `/plan`"
```

### 5.2. No active project

```
"🤔 Chưa có task nào được setup.

Anh muốn:
1️⃣ Lập kế hoạch feature mới? `/plan`
2️⃣ Khởi tạo dự án? `/init`
3️⃣ Xem recap dự án? `/recap`"
```

### 5.3. Blocked task

```
"⚠️ Task tiếp theo đang bị block:

🚧 **Blocker:** Chờ API key từ payment provider

**Alternatives:**
1️⃣ Skip và làm task khác
2️⃣ Work on unblocked tasks first
3️⃣ Mark blocker as resolved"
```

---

## 🛡️ QUICK OPTIONS:

```
/next           - Xem task tiếp theo (this)
/next --list    - Liệt kê tất cả pending tasks
/next --skip    - Skip task hiện tại
/code           - Bắt đầu code task hiện tại
```
