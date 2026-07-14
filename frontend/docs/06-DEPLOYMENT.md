# Deployment & Production Guide

Complete guide for building, deploying, and running the Join application in production environments.

## Table of Contents

1. [Production Build](#production-build)
2. [Deployment Options](#deployment-options)
3. [Firebase Deployment](#firebase-deployment)
4. [Performance Optimization](#performance-optimization)
5. [Security Configuration](#security-configuration)
6. [Monitoring & Logging](#monitoring--logging)
7. [Rollback Procedures](#rollback-procedures)
8. [Troubleshooting](#troubleshooting)

---

## Production Build

### Building for Production

```bash
# Build optimized production bundle
npm run build
# or
ng build

# Output directory
dist/join/
```

### Build Process

```
1. Compilation
   - TypeScript → JavaScript
   - AOT (Ahead-of-Time) compilation
   - Tree-shaking (remove unused code)

2. Bundling
   - Combines multiple modules
   - Creates main, vendor, polyfills bundles
   - Generates source maps (optional)

3. Optimization
   - Minification (reduce file size)
   - CSS minification
   - Asset optimization

4. Output
   - index.html (entry point)
   - main.[hash].js (application code)
   - styles.[hash].css (global styles)
   - assets/ (images, fonts, etc.)
```

### Build Configuration

**File**: `angular.json`

```json
{
  "configurations": {
    "production": {
      "outputHashing": "all",
      "aot": true,
      "optimization": true,
      "sourceMap": false,
      "vendorChunk": false
    }
  }
}
```

### Build Output Analysis

```bash
# Analyze bundle size
npm run build -- --stats-json
# Creates dist/stats.json

# View bundle with webpack-bundle-analyzer
npm install -g webpack-bundle-analyzer
webpack-bundle-analyzer dist/stats.json
```

### Typical Sizes

| Bundle | Size (gzipped) | Size (uncompressed) |
|--------|--|--|
| main.js | 200-300 KB | 800-1200 KB |
| styles.css | 50-100 KB | 200-300 KB |
| vendor.js | 500-700 KB | 1.5-2.2 MB |
| Total | ~800 KB | ~3-4 MB |

---

## Deployment Options

### Option 1: Firebase Hosting (Recommended)

**Advantages**:
- Integrated with Firebase backend
- Global CDN
- SSL/HTTPS included
- Fast deployment
- Automatic scalability

**Setup**:
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Initialize Firebase in project
firebase init hosting

# Deploy
firebase deploy --only hosting
```

### Option 2: Netlify

**Advantages**:
- Simple deployment from Git
- Automatic builds on push
- Environment variables management
- Preview deployments

**Setup**:
```bash
# Connect repository to Netlify
# In Netlify UI:
# Build command: npm run build
# Publish directory: dist/join
```

### Option 3: Vercel

**Advantages**:
- Edge network
- Automatic deployments
- Environment management
- Analytics included

**Setup**:
```bash
# Deploy to Vercel
npm install -g vercel
vercel
```

### Option 4: Docker

**Advantages**:
- Container-based deployment
- Run anywhere
- Consistent environments
- Scaling options

**Dockerfile**:
```dockerfile
# Build stage
FROM node:18 AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Serve stage
FROM nginx:latest
COPY --from=build /app/dist/join /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## Firebase Deployment

### Step 1: Configure Firebase Project

```bash
# Initialize Firebase
firebase init

# Select:
# - Database: Firestore
# - Hosting: Yes
# - Functions: No (for now)
# - Emulator: Yes (optional)
```

### Step 2: Update Firebase Configuration

**File**: `src/app/app.config.ts`

Ensure production credentials:

```typescript
export const appConfig: ApplicationConfig = {
  providers: [
    provideFirebaseApp(() =>
      initializeApp({
        projectId: 'production-project-id',
        appId: 'production-app-id',
        storageBucket: 'production-bucket',
        apiKey: 'production-api-key',
        authDomain: 'production-auth-domain',
        messagingSenderId: 'production-sender-id'
      })
    ),
    // ...
  ]
}
```

### Step 3: Set Security Rules

**File**: `firestore.rules`

```firestore
rules_version = '2';

service cloud.firestore {
  match /databases/{database}/documents {
    
    // Require authentication for all reads/writes
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
    
    // Contacts: Users can manage their own
    match /contacts/{userId} {
      allow read: if request.auth != null;
      allow create: if request.auth.uid == userId;
      allow update, delete: if request.auth.uid == userId;
    }
    
    // Tasks: Authenticated users can manage
    match /tasks/{taskId} {
      allow read: if request.auth != null;
      allow create: if request.auth != null;
      allow update, delete: if request.auth != null;
      
      // Subcollections
      match /subtasks/{subtaskId} {
        allow read, write: if request.auth != null;
      }
      
      match /assigns/{assignId} {
        allow read, write: if request.auth != null;
      }
    }
    
    // App settings: Read only
    match /appSettings/{document=**} {
      allow read: if request.auth != null;
      allow write: if false;
    }
  }
}
```

### Step 4: Deploy

```bash
# Build application
npm run build

# Deploy to Firebase
firebase deploy

# Deploy specific targets
firebase deploy --only hosting
firebase deploy --only firestore:rules
firebase deploy --only firestore:indexes

# View deployment
firebase open hosting:site
```

### Step 5: Verify Deployment

```bash
# Check deployment status
firebase hosting:channels:list

# Test deployed site
# Open: https://your-project-name.web.app

# View logs
firebase functions:log
```

---

## Performance Optimization

### 1. Content Delivery Network (CDN)

Firebase Hosting includes global CDN:
- 6+ global Points of Presence (PoPs)
- Automatic gzip compression
- Cache headers optimization
- SSL/TLS certificate included

### 2. Caching Strategy

**Cache Configuration** (`firebase.json`):

```json
{
  "hosting": {
    "headers": [
      {
        "source": "**/*.@(css|js)",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "max-age=31536000"
          }
        ]
      },
      {
        "source": "index.html",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "max-age=3600"
          }
        ]
      }
    ]
  }
}
```

### 3. Code Splitting

Enable route-based code splitting:

```typescript
// routes/app.routes.ts
const routes: Routes = [
  {
    path: 'summary',
    loadComponent: () => import('./summary.ts')
      .then(m => m.SummaryComponent)
  },
  {
    path: 'board',
    loadComponent: () => import('./board.ts')
      .then(m => m.BoardComponent)
  }
  // ... other routes
]
```

### 4. Image Optimization

**WebP format**:
```html
<!-- Serve modern format with fallback -->
<picture>
  <source type="image/webp" srcset="image.webp">
  <img src="image.png" alt="Description">
</picture>
```

### 5. Performance Metrics

**Track Core Web Vitals**:

```typescript
// In main.ts
if (typeof window !== 'undefined') {
  import('web-vitals').then(vitals => {
    vitals.getCLS(metric => console.log('CLS:', metric))
    vitals.getFID(metric => console.log('FID:', metric))
    vitals.getFCP(metric => console.log('FCP:', metric))
    vitals.getLCP(metric => console.log('LCP:', metric))
  })
}
```

---

## Security Configuration

### 1. HTTPS/SSL

Firebase Hosting automatically provides:
- Free SSL/TLS certificate
- HTTPS on all domains
- HTTP → HTTPS redirect
- HSTS (HTTP Strict Transport Security)

### 2. Content Security Policy

**Add to `index.html`**:

```html
<meta http-equiv="Content-Security-Policy" 
  content="
    default-src 'self';
    script-src 'self' 'nonce-{value}' https://apis.google.com;
    style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
    img-src 'self' data: https:;
    font-src 'self' https://fonts.gstatic.com;
    connect-src 'self' https://*.firebase.com;
  ">
```

### 3. Environment Variables

**Firebase Configuration**:
```bash
# .firebaserc (add to .gitignore)
{
  "projects": {
    "production": "join-production"
  },
  "targets": {}
}
```

### 4. Authentication Security

**Enforce strong passwords**:

```typescript
// In signup validation
const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/

if (!passwordRegex.test(password)) {
  throw new Error('Password must be 8+ chars with uppercase, lowercase, number, special char')
}
```

### 5. CORS Configuration

**Firebase allows**:
- Same-origin requests (default)
- Specified domains
- Custom CORS rules

---

## Monitoring & Logging

### 1. Firebase Analytics

Enable in `app.config.ts`:

```typescript
import { provideAnalytics, getAnalytics } from '@angular/fire/analytics'

export const appConfig: ApplicationConfig = {
  providers: [
    // ...
    provideAnalytics(() => getAnalytics())
  ]
}
```

### 2. Error Tracking

**Google Cloud Error Reporting**:

```typescript
// In error handlers
try {
  // code
} catch (error) {
  console.error('Error:', error)
  // Automatically reported to Cloud Error Reporting
}
```

### 3. Performance Monitoring

**Google Cloud Trace**:

```typescript
// Automatic with Firebase SDK
// No additional setup needed
// View in Firebase Console → Performance
```

### 4. Custom Logging

```typescript
// In service
export class LogService {
  log(message: string, data?: any) {
    const timestamp = new Date().toISOString()
    console.log(`[${timestamp}] ${message}`, data)
    
    // Send to backend if needed
    this.firebase.logEvent(message, data)
  }
}
```

---

## Rollback Procedures

### Quick Rollback

```bash
# View deployment history
firebase hosting:channels:list

# Rollback to previous version
firebase hosting:channels:deploy [channel-name]

# Or manually:
# 1. Go to Firebase Console
# 2. Select Hosting
# 3. Click Release history
# 4. Select previous version
# 5. Click Rollback
```

### Database Rollback

```bash
# Restore from backup
# Firebase Console → Firestore → Backups
# Select backup → Restore
```

---

## Troubleshooting

### Common Issues

**Issue**: Blank page after deployment

```
Solution:
1. Check browser console for errors
2. Verify Firebase credentials
3. Check security rules allow reads
4. Clear browser cache (Ctrl+Shift+Del)
5. Check dist/index.html exists
```

**Issue**: Routes not working (404 errors)

```
Solution:
Add to firebase.json:
{
  "rewrites": [
    {
      "source": "**",
      "destination": "/index.html"
    }
  ]
}
```

**Issue**: Firebase connection fails

```
Solution:
1. Verify Firebase credentials in app.config.ts
2. Check Firestore is enabled
3. Verify security rules allow your app
4. Check API keys in Firebase Console
```

**Issue**: Slow loading times

```
Solution:
1. Enable gzip compression
2. Implement code splitting
3. Optimize images
4. Use CDN (enabled by default)
5. Check bundle size: npm run build -- --stats-json
```

---

**Related Documentation**:
- [Setup Guide](./01-SETUP.md) - Initial setup
- [Architecture](./02-ARCHITECTURE.md) - System design
- [Database](./05-DATABASE.md) - Database setup

---

**Last Updated**: January 15, 2026  
**Version**: 1.0
