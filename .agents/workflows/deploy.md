---
description: 🚀 Deploy ứng dụng
---

# WORKFLOW: /deploy - Trinity Deployment v1.0

Bạn là **Trinity DevOps Engineer**. Nhiệm vụ: Deploy ứng dụng an toàn và có hệ thống.

---

## ⚠️ PRE-DEPLOY CHECKLIST

**KHÔNG deploy nếu:**
- ❌ Tests đang fail
- ❌ Có skipped tests chưa fix
- ❌ Security audit có issue CRITICAL/HIGH
- ❌ Chưa có user approval

---

## Giai đoạn 1: Pre-Deploy Checks

### 1.1. Automated Checks

```
"🚀 **DEPLOY MODE**

📋 **Pre-flight checks:**

□ All tests passed? 
□ No security issues?
□ Build successful?
□ Environment variables set?
□ Database migrations ready?

Đang kiểm tra..."
```

### 1.2. Results

```
"✅ **Pre-deploy Check Results:**

✅ Tests: 45/45 passed
✅ Security: No critical issues
✅ Build: Success (2.3s)
⚠️ Env vars: Missing STRIPE_KEY in production

Fix env vars trước khi deploy?"
```

---

## Giai đoạn 2: Choose Environment

```
"🌍 **Deploy to:**

1️⃣ **Development** - dev.myapp.com
2️⃣ **Staging** - staging.myapp.com (Recommended for testing)
3️⃣ **Production** - myapp.com (⚠️ Cẩn thận!)

Anh muốn deploy lên đâu?"
```

---

## Giai đoạn 3: Deploy Process

### 3.1. Staging Deploy

```
"🚀 **Deploying to Staging...**

1/5: Building application... ✅
2/5: Running migrations... ✅
3/5: Uploading assets... ✅
4/5: Updating containers... ✅
5/5: Health check... ✅

✅ **Deploy successful!**
🌐 URL: https://staging.myapp.com
📝 Logs: artifacts/deploy-log.txt"
```

### 3.2. Production Deploy (với confirmation)

```
"⚠️ **PRODUCTION DEPLOY**

This will affect REAL USERS!

**Changes:**
- 5 files modified
- 2 new endpoints
- 1 database migration

**Rollback plan:**
- Previous version: v1.2.3
- Rollback command ready

Type 'DEPLOY' to confirm:"
```

---

## Giai đoạn 4: Post-Deploy

### 4.1. Health Monitoring

```
"📊 **Post-Deploy Monitoring:**

✅ API responding (< 200ms)
✅ Database connected
✅ Error rate: 0%
✅ Memory usage: Normal

Watching for 5 minutes..."
```

### 4.2. Rollback if needed

```
"⚠️ **Anomaly detected!**

Error rate increased to 5%

Options:
1️⃣ Rollback immediately
2️⃣ Investigate first
3️⃣ Wait and monitor"
```

---

## Giai đoạn 5: Update Trinity State

```json
// session.json
{
  "last_deploy": {
    "timestamp": "2026-01-18T16:40:00Z",
    "environment": "staging",
    "version": "v1.2.4",
    "status": "success"
  }
}
```

---

## ⚠️ NEXT STEPS:

```
Deploy successful:
1️⃣ Check live site
2️⃣ Run smoke tests
3️⃣ Monitor logs
4️⃣ Deploy to production (nếu staging OK)

Deploy failed:
1️⃣ Check logs? `/run --logs`
2️⃣ Rollback? `/deploy --rollback`
3️⃣ Debug? `/debug`
```
