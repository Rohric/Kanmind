# Setup & Installation Guide

Complete guide for installing and configuring the Join project for development and production environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Steps](#installation-steps)
3. [Firebase Configuration](#firebase-configuration)
4. [Environment Setup](#environment-setup)
5. [Development Server](#development-server)
6. [Build for Production](#build-for-production)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Ensure you have the following installed:

### Required

- **Node.js**: v18+ (LTS recommended)
  - [Download](https://nodejs.org/)
  - Verify: `node --version`

- **npm**: v9+ (comes with Node.js)
  - Verify: `npm --version`

- **Git**: For version control
  - [Download](https://git-scm.com/)
  - Verify: `git --version`

### Optional

- **Angular CLI**: v20.3.8+
  ```bash
  npm install -g @angular/cli@20
  ```

- **VS Code**: Recommended editor
  - [Download](https://code.visualstudio.com/)

### Accounts

- **Firebase Account**: Free tier available
  - [Create Account](https://firebase.google.com/)

---

## Installation Steps

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd join
```

### Step 2: Install Dependencies

```bash
# Using npm
npm install

# Or using yarn
yarn install
```

This installs all dependencies listed in `package.json`:
- Angular framework and libraries
- Firebase SDK
- Material Design components
- Development tools

**Installation time**: 2-5 minutes (depends on internet speed)

### Step 3: Configure Firebase

#### 3a. Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **Create a new project**
3. Enter project name: `Join` (or your choice)
4. Enable Google Analytics (optional)
5. Click **Create project**

#### 3b. Get Firebase Credentials

1. In Firebase Console, click **Settings** ⚙️
2. Go to **Project settings**
3. Find your Web app configuration
4. Copy these values:
   ```
   projectId
   appId
   storageBucket
   apiKey
   authDomain
   messagingSenderId
   ```

#### 3c. Update Project Configuration

Edit `src/app/app.config.ts`:

```typescript
export const appConfig: ApplicationConfig = {
  providers: [
    provideFirebaseApp(() =>
      initializeApp({
        projectId: 'your-project-id',      // ← Replace
        appId: 'your-app-id',              // ← Replace
        storageBucket: 'your-bucket',      // ← Replace
        apiKey: 'your-api-key',            // ← Replace
        authDomain: 'your-auth-domain',    // ← Replace
        messagingSenderId: 'your-sender-id', // ← Replace
      })
    ),
    // ... rest of configuration
  ],
};
```

### Step 4: Setup Firestore Database

1. In Firebase Console, go to **Firestore Database**
2. Click **Create database**
3. Choose region (us-central1 recommended)
4. Start in **Test mode** (for development)
5. Click **Create**

### Step 5: Enable Authentication

1. In Firebase Console, go to **Authentication**
2. Click **Get started**
3. Enable **Email/Password**:
   - Click **Email/Password** provider
   - Toggle **Enable**
   - Click **Save**

---

## Firebase Configuration

### Database Collections Setup

Create these collections in Firestore:

#### 1. `contacts/` Collection
```
Path: /contacts/
Document fields:
  - name: string
  - email: string
  - phone: string
  - color: string (hex color)
  - isUser: boolean (true if registered user)
```

#### 2. `tasks/` Collection
```
Path: /tasks/
Document fields:
  - title: string
  - description: string
  - type: string (UserStory | TechnicalTask)
  - status: string (todo | in_progress | await_feedback | done)
  - date: timestamp (due date)
  - priority: number (1=urgent, 2=medium, 3=low)
  
Subcollections:
  - subtasks/
  - assigns/
```

#### 3. `appSettings/` Collection
```
Path: /appSettings/contacts/
Document fields:
  - lastUserColor: number (0-15)
```

### Security Rules (Development)

For **development only**, use these rules:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Authenticated users can read/write their data
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

**⚠️ WARNING**: These rules are permissive. Update for production!

---

## Environment Setup

### Development Environment

Create `.env.development` (optional but recommended):

```
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_AUTH_DOMAIN=your-auth-domain.firebaseapp.com
FIREBASE_API_KEY=your-api-key
NODE_ENV=development
```

### Production Environment

Create `.env.production`:

```
FIREBASE_PROJECT_ID=production-project-id
FIREBASE_AUTH_DOMAIN=production-auth-domain.firebaseapp.com
FIREBASE_API_KEY=production-api-key
NODE_ENV=production
```

---

## Development Server

### Start Development Server

```bash
npm start
# or
ng serve
```

**Output**:
```
✔ Compiled successfully.
Local:   http://localhost:4200/
```

### Access Application

Open browser and navigate to:
```
http://localhost:4200/
```

### Features

- **Hot reload**: Changes are reflected instantly
- **Source maps**: Debugging in browser DevTools
- **TypeScript checking**: Real-time error detection

### Development Flow

1. Make code changes
2. Server automatically recompiles
3. Browser refreshes automatically
4. Test changes in browser

### Stop Server

Press `Ctrl + C` in terminal

---

## Build for Production

### Production Build

```bash
npm run build
# or
ng build
```

**Output**: Built files in `dist/join/` directory

### Build Configuration

Angular optimizes production builds with:
- **AOT Compilation**: Ahead-of-Time compilation
- **Tree-shaking**: Removes unused code
- **Minification**: Reduces file sizes
- **Source maps**: For debugging (optional)

### Build Output

```
dist/join/
├── index.html
├── main.[hash].js      # Main application bundle
├── styles.[hash].css   # Global styles
└── assets/             # Images, fonts, etc.
```

### File Sizes

Typical production build:
- JavaScript: 200-300 KB (gzipped)
- CSS: 50-100 KB (gzipped)
- Total: ~300-400 KB

---

## Troubleshooting

### Node/npm Issues

**Error**: `npm: command not found`
```bash
# Solution: Install Node.js from https://nodejs.org/
node --version  # Verify installation
```

**Error**: `npm ERR! code ERESOLVE`
```bash
# Solution: Clear cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Firebase Configuration Issues

**Error**: `Firebase: No Firebase App '[DEFAULT]' has been created`
```
Solution:
1. Verify credentials in src/app/app.config.ts
2. Check Firebase Console for project ID
3. Ensure Firestore database is created
```

**Error**: `Unable to parse the provided Firebase configuration`
```
Solution:
1. Copy credentials correctly (no extra spaces/quotes)
2. Verify all fields are present
3. Check for typos in field names
```

### Port Already in Use

**Error**: `Port 4200 is already in use`
```bash
# Solution: Use different port
ng serve --port 4300
```

### Build Errors

**Error**: `Cannot find module '@angular/...'`
```bash
# Solution: Reinstall dependencies
npm ci  # Clean install
npm run build
```

**Error**: `TypeScript compilation failed`
```bash
# Check for syntax errors in .ts files
# Verify all imports are correct
# Check tsconfig.json settings
```

### Authentication Issues

**Error**: `Auth permission denied`
```
Solution:
1. Update Firebase security rules
2. Verify user is authenticated
3. Check collection permissions
```

---

## Next Steps

After successful setup:

1. **Review Architecture**: See [02-ARCHITECTURE.md](./02-ARCHITECTURE.md)
2. **Explore Components**: See [04-COMPONENTS.md](./04-COMPONENTS.md)
3. **Understand API**: See [03-API.md](./03-API.md)
4. **Start Developing**: Create first task in the app
5. **Read Contributing**: See [../CONTRIBUTING.md](../CONTRIBUTING.md)

---

## Support

- **Issues**: Check [08-TROUBLESHOOTING.md](./08-TROUBLESHOOTING.md)
- **Questions**: Review [03-API.md](./03-API.md)
- **Examples**: See [examples/](./examples/) folder

---

**Last Updated**: January 15, 2026  
**Version**: 1.0
