# TikTok Collection Scraper API

A lightweight, production-ready backend API that scrapes TikTok collections and returns structured JSON data.

## Features

- Extracts collection name, owner, and all post URLs from a TikTok collection
- RESTful API with both POST and GET endpoints
- Uses Playwright for reliable JavaScript-rendered content scraping
- Returns JSON in the format: `{collection_name, owner, posts: ["url1", "url2"]}`

## Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright browsers:**
   ```bash
   playwright install chromium
   ```

## Usage

### Start the server:
```bash
python app.py
```

Or using uvicorn directly:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### POST `/scrape-collection`
Request body:
```json
{
  "url": "https://www.tiktok.com/@cookwithdana/collection/Korea-7227851333183916846"
}
```

#### GET `/scrape-collection?url=<tiktok_collection_url>`
Query parameter:
- `url`: The TikTok collection URL

### Response Format

```json
{
  "collection_name": "Collection Name",
  "owner": "cookwithdana",
  "posts": [
    "https://www.tiktok.com/@cookwithdana/video/1234567890",
    "https://www.tiktok.com/@cookwithdana/video/0987654321"
  ]
}
```

### Example Requests

**Using curl (POST):**
```bash
curl -X POST "http://localhost:8000/scrape-collection" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.tiktok.com/@cookwithdana/collection/Korea-7227851333183916846"}'
```

**Using curl (GET):**
```bash
curl "http://localhost:8000/scrape-collection?url=https://www.tiktok.com/@cookwithdana/collection/Korea-7227851333183916846"
```

**Using Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/scrape-collection",
    json={"url": "https://www.tiktok.com/@cookwithdana/collection/Korea-7227851333183916846"}
)
data = response.json()
print(data)
```

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Notes

- TikTok's website structure may change, which could require updates to the scraping logic
- The scraper includes delays and scrolling to ensure content loads properly
- Make sure to comply with TikTok's Terms of Service when using this scraper
- Consider implementing rate limiting for production use

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Invalid URL format
- `500`: Scraping error

## Production Deployment

The API is configured for production deployment with CORS support and environment-based port configuration.

### Recommended Platforms

**Render (Free tier available):**
1. Create account at [render.com](https://render.com)
2. Create a new Web Service
3. Connect your GitHub repository
4. Configure:
   - **Build Command**: `pip install -r requirements.txt && playwright install chromium && playwright install-deps`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT` (or use Procfile)
   - **Environment**: Python 3
5. Deploy!

**⚠️ Troubleshooting**: If your app doesn't respond, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions. Most importantly, check your Render dashboard logs!

**Railway:**
1. Create account at [railway.app](https://railway.app)
2. Create new project from GitHub
3. Railway will auto-detect Python and run the build
4. Set build command: `pip install -r requirements.txt && playwright install chromium && playwright install-deps`
5. Deploy!

**Fly.io:**
1. Install flyctl: `curl -L https://fly.io/install.sh | sh`
2. Run `fly launch`
3. Follow prompts and deploy

### Environment Variables

The API automatically uses the `PORT` environment variable if set (required by most hosting platforms). If not set, it defaults to port 8000.

### CORS Configuration

CORS is enabled by default to allow cross-origin requests. For production, consider restricting `allow_origins` in `app.py` to specific domains for better security.

### Notes for Production

- The API includes CORS middleware for browser-based requests
- Port is configured via environment variable for platform compatibility
- Playwright requires system dependencies which are installed via `playwright install-deps`
- Consider implementing rate limiting for production use
- Monitor resource usage as Playwright can be memory-intensive

