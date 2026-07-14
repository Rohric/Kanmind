# Troubleshooting Guide

Solutions for common issues and problems encountered while developing, deploying, or using the Join application.

## Table of Contents

1. [Development Issues](#development-issues)
2. [Firebase Issues](#firebase-issues)
3. [Authentication Problems](#authentication-problems)
4. [Data & Database Issues](#data--database-issues)
5. [Performance Issues](#performance-issues)
6. [Deployment Issues](#deployment-issues)
7. [Browser/Client Issues](#browserclient-issues)
8. [Getting Help](#getting-help)

---

## Development Issues

### Issue: Module Not Found Errors

**Error**: `Cannot find module '@angular/...'`

**Causes**:
- Dependencies not installed
- Incorrect import path
- TypeScript configuration issue

**Solutions**:

```bash
# 1. Clean install dependencies
rm -rf node_modules package-lock.json
npm install

# 2. Verify import paths are correct
import { Component } from '@angular/core'  // ✓ Correct
import { Component } from 'angular/core'   // ✗ Wrong

# 3. Check tsconfig.json paths are correct
```

---

### Issue: Port Already in Use

**Error**: `Port 4200 is already in use`

**Causes**:
- Another dev server still running
- Another application using port 4200

**Solutions**:

```bash
# Option 1: Find and kill process
# Windows PowerShell
Get-Process -Id (Get-NetTCPConnection -LocalPort 4200).OwningProcess | Stop-Process -Force

# Option 2: Use different port
ng serve --port 4300

# Option 3: Close other applications
# Check what's using port 4200
netstat -ano | findstr :4200
taskkill /PID <process-id> /F
```

---

### Issue: TypeScript Compilation Errors

**Error**: `Type 'X' is not assignable to type 'Y'`

**Causes**:
- Type mismatch
- Missing type definitions
- Wrong interface

**Solutions**:

```typescript
// Wrong
const task: Task = {
  title: 'Test'
  // Missing required fields
}

// Correct
const task: Task = {
  title: 'Test',
  description: '',
  type: 1,
  status: 'todo',
  date: Timestamp.now(),
  priority: 1
}

// Check type with hover in VS Code
// Use strict null checks
"strictNullChecks": true in tsconfig.json
```

---

### Issue: Hot Reload Not Working

**Error**: Changes don't automatically refresh in browser

**Causes**:
- Development server stopped
- File watcher not working
- Browser cache

**Solutions**:

```bash
# 1. Restart dev server
ng serve

# 2. Clear browser cache
# Ctrl+Shift+Delete (or Cmd+Shift+Delete on Mac)

# 3. Hard refresh
# Ctrl+F5 (or Cmd+Shift+R on Mac)

# 4. Check file is saved
# Ensure file is saved before making changes
```

---

## Firebase Issues

### Issue: Firebase Not Initialized

**Error**: `FirebaseError: Firebase: No Firebase App '[DEFAULT]' has been created`

**Causes**:
- Firebase configuration missing
- Firebase not initialized before use
- Wrong import

**Solutions**:

```typescript
// Wrong - Firebase not initialized
export class MyComponent {
  constructor(private db: Firestore) {}
}

// Correct - Provider configured
export const appConfig: ApplicationConfig = {
  providers: [
    provideFirebaseApp(() => initializeApp(firebaseConfig))
  ]
}

// In component - now safe to inject
constructor(private db: Firestore) {}
```

---

### Issue: Invalid Firebase Configuration

**Error**: `Unable to parse the provided Firebase configuration`

**Causes**:
- Wrong credentials
- Extra spaces or quotes
- Missing fields

**Solutions**:

```typescript
// Wrong - Extra quotes
const config = {
  projectId: '"my-project"',  // ✗
  apiKey: 'key with spaces'   // ✗
}

// Correct - Clean values
const config = {
  projectId: 'my-project',     // ✓
  apiKey: 'abc123def456ghi'    // ✓
}

// Get correct credentials from:
// Firebase Console → Project Settings → Config
```

---

### Issue: Firestore Connection Timeout

**Error**: `Timeout while fetching data from Firestore`

**Causes**:
- Network connectivity issue
- Firebase project not responding
- Quota exceeded

**Solutions**:

```typescript
// Add retry logic
import { retry } from 'rxjs/operators'

getTasks() {
  return this.subTasks().pipe(
    retry({
      count: 3,
      delay: 1000
    })
  )
}

// Check Firebase status
// Firebase Console → Status
// Check network in DevTools (F12)

// Increase timeout in app config
```

---

## Authentication Problems

### Issue: Login Always Fails

**Error**: `auth/invalid-credential` or `auth/user-not-found`

**Causes**:
- Wrong password
- Email not registered
- Account deleted
- Too many failed attempts

**Solutions**:

```typescript
// Check error code
try {
  await auth.login(email, password)
} catch (error: any) {
  switch (error.code) {
    case 'auth/user-not-found':
      // User doesn't exist - suggest signup
      break
    case 'auth/wrong-password':
      // Show "incorrect password" message
      break
    case 'auth/too-many-requests':
      // Account temporarily locked
      break
  }
}

// Test credentials in Firebase Console
// Firebase Console → Authentication → Users
```

---

### Issue: Signup Fails with Email Already in Use

**Error**: `auth/email-already-in-use`

**Causes**:
- Email registered in another account
- User logged out but email still exists

**Solutions**:

```typescript
// Handle in UI
try {
  await auth.signup(name, email, password)
} catch (error: any) {
  if (error.code === 'auth/email-already-in-use') {
    // Suggest login instead
    showMessage('Email already registered. Try logging in.')
  }
}

// Reset account if needed
// Firebase Console → Authentication → More options → Delete user
```

---

### Issue: Guest Login Not Working

**Error**: `Can't sign in anonymously`

**Causes**:
- Anonymous auth not enabled
- Quotas exceeded

**Solutions**:

```typescript
// Enable in Firebase Console
// Authentication → Sign-in method → Anonymous
// Toggle "Enable"

// Check if quota exceeded
// Firebase Console → Quotas
// Upgrade plan if needed

// In code - ensure provider exists
provideAuth(() => {
  const auth = getAuth()
  return auth
})
```

---

### Issue: User Logged In But Data Not Loading

**Error**: Tasks/contacts not appearing despite login success

**Causes**:
- Security rules blocking reads
- User ID not matching
- Data doesn't exist

**Solutions**:

```typescript
// Check security rules
// Firebase Console → Firestore → Rules

// Verify auth state is correct
this.auth.isAuthenticated()
  .subscribe(isAuth => console.log('Authenticated:', isAuth))

// Check data exists
// Firebase Console → Firestore → Collections
// Browse documents directly

// Ensure request.auth is set
allow read: if request.auth != null
```

---

## Data & Database Issues

### Issue: Data Not Saving to Firestore

**Error**: No error, but data doesn't appear in database

**Causes**:
- Security rules blocking write
- Function returns before write completes
- Incorrect collection/document path

**Solutions**:

```typescript
// Wait for write to complete
const taskId = await this.firebase.addTask(task)
// Now task is saved

// Check security rules allow writes
// Firebase Console → Firestore → Rules
allow write: if request.auth != null

// Verify path is correct
addDoc(collection(firestore, 'tasks'), task)  // ✓
addDoc(collection(firestore, 'task'), task)   // ✗ Wrong collection

// Test in Firebase Console
// Firestore → Try it out
```

---

### Issue: Stale Data (Not Real-time Updated)

**Error**: Changes on other device don't appear

**Causes**:
- Not subscribed to real-time updates
- Subscription not active
- Unsubscribed accidentally

**Solutions**:

```typescript
// Wrong - Data loaded once, not subscribed
let tasks = await getDocs(collection(db, 'tasks'))

// Correct - Real-time subscription
this.tasks$ = collectionData(
  collection(this.firestore, 'tasks'),
  { idField: 'id' }
)

// Use takeUntilDestroyed() to prevent memory leaks
this.tasks$
  .pipe(takeUntilDestroyed(this.destroyRef))
  .subscribe(tasks => this.tasks = tasks)

// Check if subscription is active
// In DevTools → Look for Firestore listeners
```

---

### Issue: Data Deleted Unexpectedly

**Error**: Documents missing from database

**Causes**:
- Accidental delete
- Security rule allows unauthorized delete
- Cascade delete triggered

**Solutions**:

```typescript
// Check security rules
// Only allow authorized deletes
allow delete: if request.auth.uid == userId

// Review deletion logic
// Look for cascading deletes
// Example: Deleting task also deletes assignments

// Restore from backup
// Firebase Console → Firestore → Backups
// Select backup → Restore

// Version control
// Keep important data in version control
```

---

## Performance Issues

### Issue: Slow Loading/High Latency

**Symptoms**: App takes long time to load or respond

**Causes**:
- Large data transfers
- Slow network
- Too many Firestore reads
- Unoptimized queries

**Solutions**:

```typescript
// Optimize queries - fetch less data
// ✗ Bad: Load all 10,000 tasks
const allTasks = collectionData(collection(db, 'tasks'))

// ✓ Good: Load only user's recent tasks
const userTasks = collectionData(
  query(
    collection(db, 'tasks'),
    where('status', '!=', 'done'),
    limit(50)
  )
)

// Pagination for large datasets
// Load 20 items at a time
const first = query(
  collection(db, 'tasks'),
  limit(20)
)

// Use lazy loading for routes
// Code splitting reduces initial bundle

// Monitor performance
// Firebase Console → Performance
// Check for slow reads/writes
```

---

### Issue: High Firestore Costs

**Symptoms**: Unexpected billing charges

**Causes**:
- Too many read/write operations
- Unnecessary data transfers
- Inefficient queries

**Solutions**:

```typescript
// Reduce reads: Use client-side filtering
// ✗ Bad: Read all, filter client-side
const allTasks = await getAllTasks()
const filtered = allTasks.filter(t => t.status === 'done')

// ✓ Good: Filter server-side
const filtered = query(
  collection(db, 'tasks'),
  where('status', '==', 'done')
)

// Batch operations
// Use batch writes to combine operations
const batch = writeBatch(db)
batch.set(doc1, data1)
batch.set(doc2, data2)
await batch.commit()

// Set TTL on temp data
// Automatically delete old data

// Monitor usage
// Firebase Console → Usage
// Set up billing alerts
```

---

## Deployment Issues

### Issue: Blank White Screen After Deployment

**Error**: Deploy succeeds but app shows blank page

**Causes**:
- Build failed but deploy succeeded
- Wrong output directory
- Firebase configuration incorrect
- Security rules blocking everything

**Solutions**:

```bash
# 1. Check build output
npm run build
# Should create dist/join/ directory

# 2. Verify dist/index.html exists
# Check file explorer → dist/join/index.html

# 3. Check Firebase configuration
# Ensure credentials are correct in deployed version

# 4. Check console errors
# Browser DevTools → Console tab
# Look for red error messages

# 5. Test locally first
npm start
# Ensure works before deploying

# 6. Check security rules
# Firebase Console → Firestore → Rules
# Might be blocking all reads

allow read, write: if request.auth != null
```

---

### Issue: Routes Return 404 After Deployment

**Error**: `/board`, `/contacts` etc. return 404

**Causes**:
- SPA routing not configured
- Server doesn't redirect to index.html

**Solutions**:

```json
// firebase.json
{
  "hosting": {
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  }
}

// Then redeploy
// firebase deploy --only hosting
```

---

### Issue: Firebase Deploy Fails

**Error**: `Error: Deploy token expired` or similar

**Causes**:
- Authentication expired
- Wrong project
- Insufficient permissions

**Solutions**:

```bash
# 1. Re-authenticate
firebase logout
firebase login

# 2. Verify correct project
firebase projects:list
firebase use <project-id>

# 3. Check .firebaserc file
# Ensure "default" project is set correctly

# 4. Check permissions
# Firebase Console → Project settings → Members
# Verify user has Editor or Deployer role

# 5. Try using specific target
firebase deploy --only hosting

# 6. Increase timeout for large deployments
firebase deploy --debug
```

---

## Browser/Client Issues

### Issue: App Crashes on Certain Pages

**Error**: White screen or error in console

**Causes**:
- Data not loaded when component renders
- Race condition with async operations
- Memory leak

**Solutions**:

```typescript
// Safe async handling
tasks$ = this.firebase.subTasks().pipe(
  catchError(error => {
    console.error('Error loading tasks:', error)
    return of([])  // Return empty array on error
  })
)

// Use optional chaining
task?.title  // Safe if task is null

// In template - use async pipe
*ngFor="let task of tasks$ | async"  // Auto-subscribes/unsubscribes

// Check memory for leaks
// DevTools → Performance → Memory
// Look for growing memory over time

// Prevent memory leaks
takeUntilDestroyed(this.destroyRef)
```

---

### Issue: Drag-and-Drop Not Working

**Error**: Can't drag tasks between columns

**Causes**:
- CDK drag-drop not imported
- cdkDropList not properly configured
- Data not updating

**Solutions**:

```typescript
// Ensure imports
import { DragDropModule } from '@angular/cdk/drag-drop'

// Configure drop zones
<div cdkDropList #todoList="cdkDropList">
  <!-- Tasks here -->
</div>

// Handle drop event
(cdkDropListDropped)="onDrop($event)"

onDrop(event: CdkDragDrop<Task[]>) {
  // Update task status
  // Update UI
}

// Test in DevTools
// Might be CSS z-index issue
```

---

### Issue: Form Validation Not Working

**Error**: Invalid form submits or won't validate

**Causes**:
- FormGroup not properly set up
- Validators not applied
- Form not marked as touched

**Solutions**:

```typescript
// Setup reactive form properly
taskForm = new FormGroup({
  title: new FormControl('', [Validators.required]),
  priority: new FormControl(1, [Validators.required])
})

// Check form state
isValid = this.taskForm.valid      // Is form valid?
isDirty = this.taskForm.dirty      // Has user changed it?
isTouched = this.taskForm.touched  // Has user focused field?

// Show error only if touched
<div *ngIf="taskForm.get('title')?.invalid && taskForm.get('title')?.touched">
  Title is required
</div>

// Mark all as touched to show all errors
this.taskForm.markAllAsTouched()
```

---

## Getting Help

### Resources

1. **Official Documentation**
   - [Angular Docs](https://angular.io/docs)
   - [Firebase Docs](https://firebase.google.com/docs)
   - [TypeScript Docs](https://www.typescriptlang.org/docs/)

2. **Community Help**
   - Stack Overflow: Tag with `angular`, `firebase`
   - Angular Discord: https://discord.gg/angular
   - Firebase Community: https://firebase.google.com/community

3. **Project Documentation**
   - [Setup Guide](./01-SETUP.md)
   - [API Reference](./03-API.md)
   - [Architecture](./02-ARCHITECTURE.md)

### Debug Checklist

Before asking for help:

- [ ] Checked browser console for errors (F12)
- [ ] Cleared browser cache (Ctrl+Shift+Delete)
- [ ] Restarted dev server
- [ ] Reinstalled dependencies (`npm ci`)
- [ ] Verified Firebase configuration
- [ ] Checked security rules allow operation
- [ ] Tested in incognito/private window
- [ ] Searched existing issues/documentation
- [ ] Created minimal reproduction case

### Reporting Issues

When reporting a bug, include:

```
**Version**: Angular 20.3.0, Firebase 11.10.0
**Environment**: Development/Production, Chrome/Firefox
**Steps to reproduce**:
1. ...
2. ...
3. ...

**Expected behavior**:
...

**Actual behavior**:
...

**Error messages**:
[Paste console errors]

**Screenshots**:
[If applicable]

**Additional context**:
...
```

---

**Related Documentation**:
- [Setup Guide](./01-SETUP.md) - Initial configuration
- [API Reference](./03-API.md) - Available functions
- [Database Schema](./05-DATABASE.md) - Data structure

---

**Last Updated**: January 15, 2026  
**Version**: 1.0
