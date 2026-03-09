# 🚀 NEXUS-OS API Documentation

## Overview

NEXUS-OS provides a powerful REST API for job search automation, alerts management, and application generation.

**Base URL**: `https://your-app.railway.app/api/v1`

## Authentication

All API requests require an API key in the header:

```bash
X-API-Key: nxs_your_api_key_here
```

### Generate API Key

```bash
POST /api/v1/generate-key
Headers:
  Authorization: Bearer your_jwt_token

Response:
{
  "success": true,
  "api_key": "nxs_abc123...",
  "docs": "https://docs.nexus-os.com/api"
}
```

## Endpoints

### 1. Search Jobs

Search for job offers across 23 sites.

```bash
POST /api/v1/jobs/search
Headers:
  X-API-Key: nxs_your_key
  Content-Type: application/json

Body:
{
  "keywords": "Data Engineer",
  "location": "Paris",
  "limit": 10
}

Response:
{
  "success": true,
  "count": 10,
  "jobs": [
    {
      "title": "Data Engineer",
      "company": "Airbus",
      "location": "Paris",
      "link": "https://...",
      "source": "Airbus Careers",
      "relevance_score": 85
    }
  ]
}
```

### 2. Manage Alerts

#### List Alerts
```bash
GET /api/v1/alerts
Headers:
  X-API-Key: nxs_your_key

Response:
{
  "alerts": [
    {
      "id": 1,
      "keywords": "Data Engineer Remote",
      "location": "France",
      "frequency": "daily",
      "active": true
    }
  ]
}
```

#### Create Alert
```bash
POST /api/v1/alerts
Headers:
  X-API-Key: nxs_your_key
  Content-Type: application/json

Body:
{
  "keywords": "Full Stack Developer",
  "location": "Lyon",
  "frequency": "daily"
}

Response:
{
  "success": true,
  "alert_id": 42
}
```

### 3. Get Statistics

```bash
GET /api/v1/stats
Headers:
  X-API-Key: nxs_your_key

Response:
{
  "total_searches": 150,
  "total_offers": 3420,
  "avg_relevance": 72.5
}
```

## Rate Limits

- **Free tier**: 100 requests/hour
- **Pro tier**: 1000 requests/hour
- **Enterprise**: Unlimited

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized (invalid API key) |
| 429 | Rate Limit Exceeded |
| 500 | Internal Server Error |

## Examples

### Python
```python
import requests

API_KEY = "nxs_your_key"
BASE_URL = "https://your-app.railway.app/api/v1"

headers = {"X-API-Key": API_KEY}

# Search jobs
response = requests.post(
    f"{BASE_URL}/jobs/search",
    headers=headers,
    json={"keywords": "Data Engineer", "location": "Paris", "limit": 10}
)

jobs = response.json()["jobs"]
print(f"Found {len(jobs)} jobs")
```

### JavaScript
```javascript
const API_KEY = "nxs_your_key";
const BASE_URL = "https://your-app.railway.app/api/v1";

fetch(`${BASE_URL}/jobs/search`, {
  method: 'POST',
  headers: {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    keywords: 'Data Engineer',
    location: 'Paris',
    limit: 10
  })
})
.then(res => res.json())
.then(data => console.log(`Found ${data.count} jobs`));
```

### cURL
```bash
curl -X POST https://your-app.railway.app/api/v1/jobs/search \
  -H "X-API-Key: nxs_your_key" \
  -H "Content-Type: application/json" \
  -d '{"keywords":"Data Engineer","location":"Paris","limit":10}'
```

## Webhooks

Configure webhooks to receive real-time notifications:

```bash
POST /api/v1/webhooks
Body:
{
  "url": "https://your-app.com/webhook",
  "events": ["new_job_match", "alert_triggered"]
}
```

## Use Cases

1. **Job Aggregator**: Build your own job board
2. **Slack Bot**: Alert your team about new jobs
3. **Mobile App**: Create a job search mobile app
4. **Analytics**: Track job market trends
5. **Auto-Apply**: Automate application process

## Support

- 📧 Email: api@nexus-os.com
- 💬 Discord: https://discord.gg/nexus-os
- 📚 Docs: https://docs.nexus-os.com
