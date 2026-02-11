# 2026-02-11 Daily Worklog

## 🛠️ Troubleshooting & Deployment

### 🔴 Service Instability (AliCloud)
- **Incident**: Backend service (`uvicorn main_v2:app`) keeps terminating shortly after startup.
- **Observation**:
  - Validated that a rogue process `uvicorn app.main:app` (old code) keeps reappearing (PID 1063309, etc.).
  - This suggests an automated process manager (Supervisor, Systemd, PM2, or Cron) is enforcing the old version, causing port conflicts or killing my new process.
- **Action Required**:
  - Identify and disable the persistence mechanism for `app.main`.
  - Re-deploy `main_v2` with `stardust` endpoint.

### 📊 Frontend Feature
- **Task**: Implement `/expenses/stardust` endpoint for "DataArt" visualization.
- **Status**: Code written and uploaded, but service unstable due to the conflict above.
