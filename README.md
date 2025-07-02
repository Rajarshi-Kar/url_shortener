# BitLink — Serverless URL Shortener

- Live: https://bitlink.uk
- Domain Managed by: Cloudflare DNS
- Frontend Hosted on: AWS S3 + CloudFront (with HTTPS via ACM)
- Version Controlled on: GitHub

BitLink is a lightweight, cloud-native URL shortener that supports user authentication, analytics, and link management — all under a custom domain, and fully deployed without any traditional server.


What started as a simple redirector evolved into a full-featured, production-grade system with real-time logging, QR generation, and user-specific link history. The project is designed to be resilient, cost-efficient, and highly maintainable, relying on managed services wherever possible.


## Features

- Custom short URLs like bitlink.uk/abc123
- Google sign-in via Firebase Authentication
- Link history unique to each authenticated user
- Total click count per shortlink
- Per-click metadata tracking (IP, timestamp, user-agent)





## Tech Stack
**Client**: HTML, JavaScript (inlined), Firebase Authentication

**Serverless Backend**: AWS Lambda, API Gateway, DynamoDB, CloudFront

**Hosting & Storage**: AWS S3 (static site hosting), GitHub Pages (previously), Cloudflare DNS

**Analytics & Data**: DynamoDB (ShortLinks, ClickMetadata tables)
## Directory Structure
bitlink/

├── index.html          
├── analytics.html      
├── dashboard.html    

No external JS or CSS files are used. All logic is embedded inside 

## Installation & Setup

Since this project is fully serverless and deployed on the cloud, there's no local server to run. However, for development or customization, here’s how to set up and run it locally:

1. Clone the Repository:
```http
git clone https://github.com/rajarshi-kar/bitlink-url-shortener.git
cd bitlink-url-shortener
```

2. Frontend:
- No frameworks or CSS libraries are used.
- Open index.html, analytics.html, or dashboard.html in any browser to preview.
- All JavaScript is inline inside the HTML files.

3. Deployment:
- Frontend hosted via AWS S3 + CloudFront under the custom domain https://bitlink.uk

- DNS managed through Cloudflare

- Backend deployed using the AWS Console (Lambda + API Gateway)

There might be issues running this locally with the Firebase Firestore authentication, as specified domains need to be added to it's permission list.

## Usage Instructions

To use the system once deployed:

#### 1. Shorten a URL:

- Navigate to the homepage and paste your original URL.

- Click "Shorten" to receive a custom short URL.

#### 2. Track Analytics:

- Click the "Analytics" link to see total clicks.

- Click through to the "Dashboard" to view timestamped click metadata.

#### 3. Login with Google (Optional):

- Firebase Authentication is integrated for user-specific history.

- Once logged in, you’ll be able to see links you’ve shortened.

#### 4. API Use:

- Refer to the API Reference section to integrate the service into external apps.

#### 5. QR Code Generation:

- Each short URL is also linked to a downloadable QR code on the dashboard.

No additional configurations are required beyond deployment — everything runs on the cloud.
## Demo

BitLink is currently live and production-ready at https://bitlink.uk
Video demo- https://youtu.be/MlPTm2RG0CU


## API Reference

#### Get all clicks for a short code



```http
  GET /clicks/{short_id}
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `short_id` | `string` | The unique short link ID |

#### Get click metadata for a short code

```http
GET/metadata/{short_id}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `short_id`      | `string` | The unique short link ID |

#### Shorten a URL



```http
POST /shorten
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `Body with URL`      | `string` | Long URL is passed

#### Shorten an URL
```http
GET /{short_code}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `short_code`      | `string` | Redirects to original link |





## Deployment

BitLink is deployed entirely using AWS-managed services, stitched together without any traditional compute or manual server provisioning:

- Frontend: Hosted on Amazon S3 with CloudFront as the CDN. S3 ensures high availability with minimal latency, and CloudFront adds low-latency edge delivery.

- Custom Domain: Managed via Cloudflare DNS, which allows easy redirection and secure domain configuration.

- Backend: AWS Lambda for request handling. API Gateway for defining and exposing HTTP endpoints. DynamoDB stores both short links and click metadata.

The architecture is designed for durability, speed, and near-zero ops overhead.


## Optimizations

Zero JavaScript frameworks: To reduce load time, the frontend uses raw HTML with <script> tags for JavaScript. This keeps the app extremely lightweight.

No CSS frameworks: Plain HTML used for layout; ensures minimal bundle size.

No backend server: Fully event-driven Lambda execution. Infrequent requests incur zero cost.

CloudFront + S3: Ensures cache-efficient content delivery across the globe.

Separate click metadata table: Improves querying efficiency and reduces overhead on the main link table.


## Usage/Examples

- Paste a long URL and click "Shorten".

- You’ll receive a BitLink like: go.bitlink.uk/abc123

- You can view analytics by visiting analytics.

- Every visit to the short link records IP, User-Agent, Timestamp

- If logged in with Google (via Firebase Auth), shortened links are also tracked under that user's UID.


## Conclusion

This system is a fully deployed, serverless URL shortening service backed by a custom domain and a scalable cloud-native stack. Built with modular AWS components, it handles URL shortening, redirection, and metadata tracking efficiently with zero traditional servers involved. From routing to analytics, every part runs as a managed service—making the infrastructure lightweight, maintainable, and production-ready.
