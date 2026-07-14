# Testing Guide

Comprehensive guide for writing, running, and maintaining tests in the Join application.

## Table of Contents

1. [Testing Overview](#testing-overview)
2. [Test Setup](#test-setup)
3. [Unit Tests](#unit-tests)
4. [Component Tests](#component-tests)
5. [Service Tests](#service-tests)
6. [Testing Best Practices](#testing-best-practices)
7. [Test Coverage](#test-coverage)
8. [Running Tests](#running-tests)

---

## Testing Overview

### Test Framework Stack

| Tool | Version | Purpose |
|------|---------|---------|
| **Jasmine** | 5.9.0 | Testing framework & assertions |
| **Karma** | 6.4.0 | Test runner |
| **TypeScript** | 5.9.2 | Type-safe tests |
| **Angular Testing Utilities** | 20.3.0 | Component/service testing |

### Test Types

```
Unit Tests (70%)
├─ Service logic
├─ Utility functions
└─ Data transformations

Component Tests (20%)
├─ Template rendering
├─ User interactions
└─ Component lifecycle

Integration Tests (10%)
├─ Firebase operations
├─ Authentication flow
└─ Complex workflows
```

---

## Test Setup

### Configuration Files

**`karma.conf.js`** - Test runner configuration

```javascript
module.exports = function(config) {
  config.set({
    basePath: '',
    frameworks: ['jasmine', '@angular-devkit/build-angular'],
    plugins: [
      require('karma-jasmine'),
      require('karma-chrome-launcher'),
      require('@angular-devkit/build-angular/plugins/karma')
    ],
    client: {
      jasmine: {
        random: false
      },
      clearContext: false
    },
    coverageReporter: {
      dir: require('path').join(__dirname, './coverage/'),
      reports: ['html', 'lcov'],
      fixWebpackSourcePaths: true,
      check: {
        global: {
          statements: 80,
          branches: 75,
          functions: 80,
          lines: 80
        }
      }
    },
    reporters: ['progress', 'coverage'],
    port: 9876,
    colors: true,
    logLevel: config.LOG_INFO,
    autoWatch: true,
    browsers: ['Chrome'],
    singleRun: false,
    restartOnFileChange: true
  })
}
```

**`tsconfig.spec.json`** - TypeScript test configuration

```json
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "outDir": "./out-tsc/spec",
    "types": [
      "jasmine"
    ]
  },
  "include": [
    "src/**/*.spec.ts"
  ]
}
```

### Test File Naming

```
Component:     board.ts      → board.spec.ts
Service:       firebase.ts   → firebase.spec.ts
Utility:       helpers.ts    → helpers.spec.ts
```

---

## Unit Tests

### Basic Test Structure

```typescript
import { TestBed } from '@angular/core/testing'

describe('MyService', () => {
  let service: MyService

  beforeEach(() => {
    TestBed.configureTestingModule({})
    service = TestBed.inject(MyService)
  })

  it('should be created', () => {
    expect(service).toBeTruthy()
  })

  it('should calculate correctly', () => {
    const result = service.calculate(5, 3)
    expect(result).toBe(8)
  })
})
```

### Jasmine Matchers

```typescript
// Equality
expect(value).toBe(expected)           // ===
expect(value).toEqual(expected)        // Deep equality
expect(value).toMatch(/pattern/)       // Regex

// Boolean
expect(value).toBeTruthy()
expect(value).toBeFalsy()

// Null/undefined
expect(value).toBeNull()
expect(value).toBeUndefined()

// Numbers
expect(value).toBeCloseTo(5.5, 1)
expect(value).toBeLessThan(10)
expect(value).toBeGreaterThan(0)

// Arrays/Objects
expect(array).toContain(element)
expect(object).toHaveProperty('key')

// Errors
expect(() => { throw Error() }).toThrowError()

// Not
expect(value).not.toBe(0)
```

---

## Component Tests

### Login Component Test

```typescript
import { ComponentFixture, TestBed } from '@angular/core/testing'
import { LoginComponent } from './login'
import { AuthService } from '../firebase-services/auth-services'
import { Router } from '@angular/router'

describe('LoginComponent', () => {
  let component: LoginComponent
  let fixture: ComponentFixture<LoginComponent>
  let authService: jasmine.SpyObj<AuthService>
  let router: jasmine.SpyObj<Router>

  beforeEach(async () => {
    // Create mock services
    authService = jasmine.createSpyObj('AuthService', [
      'login',
      'signup',
      'loginGuest'
    ])

    router = jasmine.createSpyObj('Router', ['navigate'])

    await TestBed.configureTestingModule({
      imports: [LoginComponent],
      providers: [
        { provide: AuthService, useValue: authService },
        { provide: Router, useValue: router }
      ]
    }).compileComponents()

    fixture = TestBed.createComponent(LoginComponent)
    component = fixture.componentInstance
    fixture.detectChanges()
  })

  it('should create', () => {
    expect(component).toBeTruthy()
  })

  it('should call login on submit', async () => {
    authService.login.and.returnValue(Promise.resolve())
    
    component.email = 'test@example.com'
    component.password = 'password123'
    
    await component.login()
    
    expect(authService.login).toHaveBeenCalledWith(
      'test@example.com',
      'password123'
    )
  })

  it('should toggle between login and signup forms', () => {
    expect(component.isSignup()).toBe(false)
    component.toggleForm()
    expect(component.isSignup()).toBe(true)
  })

  it('should display error message on login failure', async () => {
    const error = new Error('Invalid credentials')
    authService.login.and.returnValue(Promise.reject(error))
    
    component.email = 'test@example.com'
    component.password = 'wrong'
    
    await component.login()
    fixture.detectChanges()
    
    expect(component.errorMessage).toBe('Invalid credentials')
  })
})
```

### Board Component Test

```typescript
import { ComponentFixture, TestBed } from '@angular/core/testing'
import { BoardComponent } from './board'
import { FirebaseServices } from '../../firebase-services/firebase-services'
import { of } from 'rxjs'

describe('BoardComponent', () => {
  let component: BoardComponent
  let fixture: ComponentFixture<BoardComponent>
  let firebaseService: jasmine.SpyObj<FirebaseServices>

  beforeEach(async () => {
    firebaseService = jasmine.createSpyObj('FirebaseServices', [
      'subTasks',
      'updateTask',
      'deleteTask'
    ])

    const mockTasks: Task[] = [
      {
        id: '1',
        title: 'Task 1',
        status: 'todo',
        // ... other fields
      }
    ]

    firebaseService.subTasks.and.returnValue(of(mockTasks))

    await TestBed.configureTestingModule({
      imports: [BoardComponent],
      providers: [
        { provide: FirebaseServices, useValue: firebaseService }
      ]
    }).compileComponents()

    fixture = TestBed.createComponent(BoardComponent)
    component = fixture.componentInstance
    fixture.detectChanges()
  })

  it('should load tasks on init', (done) => {
    fixture.whenStable().then(() => {
      expect(firebaseService.subTasks).toHaveBeenCalled()
      done()
    })
  })

  it('should move task to new status', async () => {
    firebaseService.updateTask.and.returnValue(Promise.resolve())
    
    await component.onTaskDropped('task1', 'in_progress')
    
    expect(firebaseService.updateTask).toHaveBeenCalledWith('task1', {
      status: 'in_progress'
    })
  })

  it('should filter tasks by search term', () => {
    component.searchTerm.set('Task')
    
    const filtered = component.filteredTasks()
    
    expect(filtered.length).toBeGreaterThan(0)
  })
})
```

---

## Service Tests

### AuthService Test

```typescript
import { TestBed } from '@angular/core/testing'
import { AuthService } from './auth-services'
import { Auth, createUserWithEmailAndPassword } from '@angular/fire/auth'
import { FirebaseServices } from './firebase-services'

describe('AuthService', () => {
  let service: AuthService
  let auth: jasmine.SpyObj<Auth>
  let firebaseService: jasmine.SpyObj<FirebaseServices>

  beforeEach(() => {
    auth = jasmine.createSpyObj('Auth', [])
    firebaseService = jasmine.createSpyObj('FirebaseServices', [
      'addContact'
    ])

    TestBed.configureTestingModule({
      providers: [
        AuthService,
        { provide: Auth, useValue: auth },
        { provide: FirebaseServices, useValue: firebaseService }
      ]
    })

    service = TestBed.inject(AuthService)
  })

  it('should be created', () => {
    expect(service).toBeTruthy()
  })

  it('should login user', async () => {
    // Setup mock
    spyOn(auth, 'signInWithEmailAndPassword')
      .and.returnValue(Promise.resolve({
        user: { uid: '123', email: 'test@example.com' }
      } as any))

    // Execute
    await service.login('test@example.com', 'password')

    // Assert
    expect(auth.signInWithEmailAndPassword).toHaveBeenCalled()
  })

  it('should handle signup with contact creation', async () => {
    const userCred = {
      user: { uid: '123', email: 'new@example.com' }
    }

    spyOn(auth, 'createUserWithEmailAndPassword')
      .and.returnValue(Promise.resolve(userCred as any))

    firebaseService.addContact.and.returnValue(Promise.resolve('contactId'))

    await service.signup('John Doe', 'new@example.com', 'password')

    expect(auth.createUserWithEmailAndPassword).toHaveBeenCalled()
    expect(firebaseService.addContact).toHaveBeenCalled()
  })
})
```

### FirebaseServices Test

```typescript
import { TestBed } from '@angular/core/testing'
import { FirebaseServices } from './firebase-services'
import { Firestore } from '@angular/fire/firestore'

describe('FirebaseServices', () => {
  let service: FirebaseServices
  let firestore: jasmine.SpyObj<Firestore>

  beforeEach(() => {
    firestore = jasmine.createSpyObj('Firestore', [])

    TestBed.configureTestingModule({
      providers: [
        FirebaseServices,
        { provide: Firestore, useValue: firestore }
      ]
    })

    service = TestBed.inject(FirebaseServices)
  })

  it('should add task', async () => {
    const mockTask: Task = {
      title: 'New Task',
      description: 'Test',
      type: 1,
      status: 'todo',
      date: {} as any,
      priority: 1
    }

    // Spy on addDoc
    spyOn(service, 'addTask')
      .and.returnValue(Promise.resolve('newTaskId'))

    const result = await service.addTask(mockTask)

    expect(result).toBe('newTaskId')
  })

  it('should update task', async () => {
    spyOn(service, 'updateTask')
      .and.returnValue(Promise.resolve())

    await service.updateTask('task123', { status: 'done' })

    expect(service.updateTask).toHaveBeenCalledWith('task123', {
      status: 'done'
    })
  })

  it('should delete task', async () => {
    spyOn(service, 'deleteTask')
      .and.returnValue(Promise.resolve())

    await service.deleteTask('task123')

    expect(service.deleteTask).toHaveBeenCalledWith('task123')
  })

  it('should get tasks observable', (done) => {
    const mockTasks: Task[] = [
      {
        id: '1',
        title: 'Task 1',
        status: 'todo'
        // ... other fields
      }
    ]

    spyOn(service, 'subTasks')
      .and.returnValue(of(mockTasks))

    service.subTasks()
      .subscribe(tasks => {
        expect(tasks.length).toBe(1)
        expect(tasks[0].title).toBe('Task 1')
        done()
      })
  })
})
```

---

## Testing Best Practices

### 1. Arrange-Act-Assert (AAA)

```typescript
it('should calculate total correctly', () => {
  // Arrange
  const item1 = { price: 10, qty: 2 }
  const item2 = { price: 5, qty: 3 }

  // Act
  const total = calculateTotal([item1, item2])

  // Assert
  expect(total).toBe(35)
})
```

### 2. Use Descriptive Names

```typescript
// ✓ Good
it('should return empty array when no contacts exist', () => {})

// ✗ Bad
it('should return array', () => {})
```

### 3. One Assertion Per Test

```typescript
// ✓ Good
it('should add contact successfully', () => {
  const result = service.addContact(contact)
  expect(result).toBeTruthy()
})

it('should generate unique ID', () => {
  const id = generateId()
  expect(id).toMatch(/^[a-f0-9]+$/)
})

// ✗ Bad (multiple assertions)
it('should add contact', () => {
  const result = service.addContact(contact)
  expect(result).toBeTruthy()
  expect(result.id).toMatch(/^[a-f0-9]+$/)
})
```

### 4. Mock External Dependencies

```typescript
// Use spies for services
spyOn(firebaseService, 'addTask')
  .and.returnValue(Promise.resolve('id123'))

// Use jasmine.createSpyObj for multiple methods
const mockAuth = jasmine.createSpyObj('AuthService', [
  'login',
  'logout',
  'signup'
])
```

### 5. Test Edge Cases

```typescript
it('should handle empty input gracefully', () => {
  expect(() => service.process('')).not.toThrow()
})

it('should handle null values', () => {
  const result = service.format(null)
  expect(result).toBe('N/A')
})

it('should handle large datasets', () => {
  const largeArray = Array(10000).fill(0)
  expect(() => service.process(largeArray)).not.toThrow()
})
```

---

## Test Coverage

### Coverage Thresholds

Set in `karma.conf.js`:

```javascript
check: {
  global: {
    statements: 80,   // 80% of statements covered
    branches: 75,     // 75% of branches covered
    functions: 80,    // 80% of functions covered
    lines: 80         // 80% of lines covered
  }
}
```

### Generating Coverage Report

```bash
npm test -- --code-coverage

# Output: coverage/index.html
# Open in browser to view detailed report
```

### Coverage Report

Typical coverage structure:

```
Services:        90% (critical business logic)
Components:      75% (templates harder to test)
Utilities:       95% (pure functions)
Overall:         85% (target minimum)
```

---

## Running Tests

### Command Line

```bash
# Run all tests once
npm test -- --watch=false

# Run tests in watch mode
npm test

# Run specific test file
npm test -- --include='**/board.spec.ts'

# Run with code coverage
npm test -- --code-coverage

# Run in headless mode (CI)
npm test -- --watch=false --browsers=ChromeHeadless
```

### Debugging Tests

```bash
# Run with detailed output
npm test -- --log-level=debug

# Open Chrome DevTools
npm test
# Tests run in Chrome browser, can use DevTools
```

### CI/CD Integration

**GitHub Actions example** (`.github/workflows/test.yml`):

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: npm ci
      - run: npm test -- --watch=false --code-coverage
      - uses: codecov/codecov-action@v2
```

---

**Related Documentation**:
- [Components Guide](./04-COMPONENTS.md) - Component structure
- [API Reference](./03-API.md) - Service methods
- [Contributing](../CONTRIBUTING.md) - Development standards

---

**Last Updated**: January 15, 2026  
**Version**: 1.0
