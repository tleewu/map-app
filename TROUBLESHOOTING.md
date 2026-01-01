# Troubleshooting Deployment Issues

If your Render app isn't responding, follow these steps:

## 1. Check Render Logs

**Most Important Step**: Go to your Render dashboard and check the logs!

1. Log into [render.com](https://render.com)
2. Navigate to your service
3. Click on "Logs" tab
4. Look for:
   - Build errors
   - Runtime errors
   - Import errors
   - Playwright installation issues

## 2. Common Issues and Fixes

### Issue: App times out or doesn't respond

**Possible Causes:**
- Build failed (check logs)
- App crashed on startup (check logs)
- Playwright not installed correctly
- Port configuration issue

**Fix:**
- Check the Render logs first
- Verify build command in Render dashboard: `pip install -r requirements.txt && playwright install chromium && playwright install-deps`
- Verify start command: `uvicorn app:app --host 0.0.0.0 --port $PORT` OR `python app.py`

### Issue: Playwright installation fails

**Fix:**
- Make sure build command includes: `playwright install chromium && playwright install-deps`
- Check if Render's build environment has enough resources
- Try updating Playwright version in requirements.txt

### Issue: Module not found errors

**Fix:**
- Ensure `requirements.txt` includes all dependencies
- Check that build command runs `pip install -r requirements.txt`
- Verify Python version (should be 3.9+)

### Issue: Port binding errors

**Fix:**
- Make sure you're using `$PORT` environment variable or `os.environ.get("PORT")`
- Start command should use: `uvicorn app:app --host 0.0.0.0 --port $PORT`

## 3. Verify Build Configuration in Render Dashboard

Go to your service settings and verify:

**Build Command:**
```
pip install -r requirements.txt && playwright install chromium && playwright install-deps
```

**Start Command (Option 1 - using uvicorn directly):**
```
uvicorn app:app --host 0.0.0.0 --port $PORT
```

**Start Command (Option 2 - using python):**
```
python app.py
```

## 4. Test Locally First

Before deploying, test locally:
```bash
pip install -r requirements.txt
playwright install chromium
playwright install-deps
python app.py
```

Then test: `curl http://localhost:8000/health`

## 5. Render-Specific Notes

- **Free tier**: Apps sleep after 15 minutes of inactivity
- **Wake time**: First request can take 30-60 seconds
- **Build time**: Can take 5-10 minutes with Playwright
- **Memory**: Playwright uses significant memory; free tier has limits

## 6. Alternative: Use Railway or Fly.io

If Render continues to have issues, consider:
- **Railway**: Better free tier, easier Playwright support
- **Fly.io**: Good for containerized apps
- **Render Paid**: More resources, faster builds

## 7. Quick Health Check

Once deployed, test these endpoints:

1. **Health check** (fast, no scraping):
   ```bash
   curl https://your-app.onrender.com/health
   ```

2. **Root endpoint**:
   ```bash
   curl https://your-app.onrender.com/
   ```

3. **API docs** (opens in browser):
   ```
   https://your-app.onrender.com/docs
   ```

## 8. If Still Not Working

1. Check Render status page: https://status.render.com
2. Review your Render service logs
3. Try redeploying with a fresh build
4. Consider using Render's support/community forums
5. Verify your GitHub repo has all necessary files

