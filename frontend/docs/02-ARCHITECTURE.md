# System Architecture & Design

Complete overview of Join's system design, component hierarchy, data flow, and technology decisions.

## Table of Contents

1. [High-Level Overview](#high-level-overview)
2. [Component Hierarchy](#component-hierarchy)
3. [Firestore Database Schema](#firestore-database-schema)
4. [Data Flow Architecture](#data-flow-architecture)
5. [Service Layer](#service-layer)
6. [Authentication Flow](#authentication-flow)
7. [Real-time Data Synchronization](#real-time-data-synchronization)
8. [Design Patterns](#design-patterns)

---

## High-Level Overview

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│              Browser / Web Client                   │
│         (Angular 20 + TypeScript)                   │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────────┐    ┌──────────────────┐
│   Components     │    │    Services      │
│   Layer          │    │    Layer         │
│                  │    │                  │
│  - Board         │    │ - AuthService    │
│  - Login         │    │ - FirebaseServ   │
│  - Contacts      │    │ - UserUiService  │
│  - Summary       │    │                  │
└────────┬─────────┘    └──────┬───────────┘
         │                      │
         │       ┌──────────────┘
         │       │
         ▼       ▼
    ┌──────────────────────────┐
    │   Firebase SDK           │
    │  (AngularFire)           │
    └────────┬────────┬────────┘
             │        │
        ┌────▼────┐  ┌▼─────────────┐
        │          │  │              │
        ▼          ▼  ▼              ▼
    ┌─────────┐  ┌──────────┐  ┌──────────┐
    │   Auth  │  │Firestore │  │ Storage  │
    │         │  │          │  │          │
    └─────────┘  └──────────┘  └──────────┘
```

---

## Component Hierarchy

### Full Component Tree

```
App (Root)
│
├── Login (Authentication Page)
│   ├── Login Form
│   ├── Signup Form
│   └── Guest Login Button
│
└── MainPage (Authenticated Layout)
    ├── Header (Shared)
    │   ├── User Menu
    │   ├── Logout Button
    │   └── Mobile Toggle
    │
    ├── Navbar (Shared)
    │   ├── Navigation Links
    │   │   ├── Summary
    │   │   ├── Board
    │   │   ├── Contacts
    │   │   ├── Add Task
    │   │   ├── Helper
    │   │   ├── Privacy Policy
    │   │   └── Legal Notice
    │   └── Auth Status
    │
    └── Router Outlet
        ├── Summary (Dashboard)
        │   └── Statistics Display
        │
        ├── Board (Kanban)
        │   ├── Todo Column
        │   ├── In Progress Column
        │   ├── Await Feedback Column
        │   ├── Done Column
        │   ├── TaskPreview (Card)
        │   │   └── DialogShowEditTask (Modal)
        │   └── DialogAddTask (Modal)
        │
        ├── AddTask (Form Page)
        │   ├── Title Input
        │   ├── Description Input
        │   ├── Date Picker
        │   ├── Type Selector
        │   ├── Priority Selector
        │   ├── Contact Selector
        │   └── Subtask Manager
        │
        ├── Contacts (Contact Management)
        │   ├── ListContact (List View)
        │   │   ├── Contact List
        │   │   └── DialogAddNewContact (Modal)
        │   └── SingleContact (Detail View)
        │       └── DialogEditContact (Modal)
        │
        ├── Helper
        ├── Legal Notice
        └── Privacy Policy

Legend:
  - Components at same level are sibling routes
  - Indentation shows component nesting
  - (Modal) = Dialog component overlay
```

### Component Responsibilities

| Component | Responsibility | Features |
|-----------|-----------------|----------|
| **App** | Root component, routing outlet | N/A |
| **Login** | Authentication | Login, Signup, Guest access |
| **MainPage** | Layout container | Header, Navbar, Child routes |
| **Header** | Top navigation | User menu, Logout, Mobile toggle |
| **Navbar** | Side navigation | Navigation links, Routing |
| **Board** | Kanban board | Columns, Drag-drop, Search |
| **TaskPreview** | Task card | Display task info, Edit/Delete |
| **AddTask** | Task creation form | Full form, Validation |
| **Contacts** | Contact management | List, Details, CRUD |
| **Summary** | Dashboard | Statistics, Overview |

---

## Firestore Database Schema

### Collections Structure

```
Firestore Database
├── contacts/ (Collection)
│   ├── {userId} (Document)
│   │   ├── name: string
│   │   ├── email: string
│   │   ├── phone: string
│   │   ├── color: string
│   │   └── isUser: boolean
│   └── {contactId} (Document)
│       └── [same fields]
│
├── tasks/ (Collection)
│   └── {taskId} (Document)
│       ├── title: string
│       ├── description: string
│       ├── type: TaskType (1=UserStory, 2=TechnicalTask)
│       ├── status: TaskStatus (todo|in_progress|await_feedback|done)
│       ├── date: Timestamp
│       ├── priority: number (1|2|3)
│       ├── subtasks/ (Subcollection)
│       │   └── {subtaskId} (Document)
│       │       ├── title: string
│       │       └── done: boolean
│       └── assigns/ (Subcollection)
│           └── {assignId} (Document)
│               └── contactId: string
│
└── appSettings/ (Collection)
    └── contacts/ (Document)
        └── lastUserColor: number
```

### Data Relationships

```
Contact (1) ──────── (Many) Task Assignments
            ├────────────────┐
            │                │
            ▼                ▼
      User Profile      Task Assignments
      (name, email)     (in Task.assigns)
      
Task (1) ──────────── (Many) Subtasks
  ├─ Task data        └─ Subcollection
  ├─ Type, Status     ├─ title
  ├─ Priority         └─ done

Task (1) ──────────── (Many) Assignments
  └─ Subcollection
     └─ contactId references
```

### Document Examples

#### Contact Document
```json
{
  "id": "user123",
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "color": "#FF5733",
  "isUser": true
}
```

#### Task Document
```json
{
  "id": "task456",
  "title": "Design UI Mockups",
  "description": "Create mockups for dashboard",
  "type": 1,
  "status": "in_progress",
  "date": Timestamp,
  "priority": 1,
  "subtasks/": [
    {
      "id": "sub1",
      "title": "Create wireframes",
      "done": true
    }
  ],
  "assigns/": [
    {
      "id": "assign1",
      "contactId": "contact123"
    }
  ]
}
```

---

## Data Flow Architecture

### Complete Data Flow Diagram

```
User Action (Click, Input)
        │
        ▼
    Component
    (Board, Login, etc.)
        │
        ├─ Updates Signal/Form State
        │
        ├─ Calls Service Method
        │     (firebase.addTask, auth.login, etc.)
        │
        ▼
    Service Layer
    (FirebaseServices, AuthService)
        │
        ├─ Validates Input
        │
        ├─ Calls Firebase SDK
        │
        ▼
    Firebase Operations
    ├─ Create: addDoc()
    ├─ Read: collectionData(), docData()
    ├─ Update: updateDoc()
    └─ Delete: deleteDoc()
        │
        ▼
    Firestore Database
    (Persists Data)
        │
        ├─ Broadcasts Change
        │  (Observable Stream)
        │
        ▼
    Component Subscribes
    (via Observable)
        │
        ├─ Updates Signal
        ├─ Triggers Re-render
        │
        ▼
    View Updates
    (Angular Change Detection)
        │
        ▼
    User Sees Change
```

### Example: Creating a Task

```
1. User fills form (Board or AddTask)
   └─ Component updates local signals

2. User clicks "Create Task"
   └─ Calls component.addTask()

3. Component calls service
   └─ this.firebase.addTask(taskData)

4. Service validates and calls Firebase
   └─ addDoc(collection(firestore, 'tasks'), taskData)

5. Firebase creates document in Firestore
   └─ Generates unique ID, stores document

6. Observable streams update
   └─ firebase.subTasks() emits new data

7. Board component receives update
   └─ tasks$ observable updates

8. Template renders new task
   └─ *ngFor updates, drag-drop enabled

9. Task appears in "To Do" column
   └─ User sees new task immediately
```

---

## Service Layer

### Service Dependency Graph

```
Components
    │
    ├──> AuthService
    │        │
    │        ├─> Firebase Auth
    │        ├─> FirebaseServices
    │        └─> Router
    │
    ├──> FirebaseServices
    │        │
    │        ├─> Firestore (Collections)
    │        ├─> Firebase Auth (User state)
    │        └─> UserUiService (Color management)
    │
    └──> UserUiService
             │
             ├─> FirebaseServices (Color persistence)
             └─> Utility functions
```

### Service Responsibilities

#### AuthService
- User authentication (login, signup, logout)
- Guest access management
- Session lifecycle
- Auth state observable

#### FirebaseServices
- Firestore CRUD operations
- Real-time data subscriptions
- Task management
- Contact management
- Subtask handling
- Data transformation

#### UserUiService
- UI utilities (initials, date formatting)
- Color management and rotation
- Task urgency calculations
- Component state helpers

---

## Authentication Flow

### User Login Flow

```
1. Login Page
   └─ User enters email/password

2. Submit Form
   └─ auth.login(email, password)

3. Firebase Auth
   └─ Validates credentials with Firebase

4. Success
   ├─ Firebase returns User object
   ├─ Sets justLoggedIn flag
   └─ Navigates to /summary

5. MainPage
   ├─ Checks authState
   ├─ Shows Navbar/Header
   └─ Renders protected routes
```

### User Signup Flow

```
1. Signup Form
   ├─ User enters name, email, password
   └─ Validation (email format, password length, match)

2. Create Auth User
   └─ auth.signup(name, email, password)

3. Firebase Auth
   └─ createUserWithEmailAndPassword()

4. Initialize User
   ├─ Create user contact document
   ├─ Assign color
   └─ Set isUser: true

5. Success
   ├─ Sets justLoggedIn flag
   └─ Navigates to /summary
```

### Guest Login Flow

```
1. Click Guest Login
   └─ auth.loginGuest()

2. Firebase Auth
   └─ signInAnonymously()

3. Anonymous User
   ├─ No contact document
   ├─ Limited features
   └─ Can explore app

4. On Logout
   └─ Delete anonymous user account
```

---

## Real-time Data Synchronization

### Observable Subscriptions

```
Components subscribe to:

1. Contact Updates
   firebase.subContactsList() 
   └─ Emits when any contact changes

2. Task Updates
   firebase.subTasks()
   └─ Emits when any task changes

3. Subtask Updates
   firebase.subSubtasks(taskId)
   └─ Emits when subtasks change

4. Task Assignments
   firebase.subTaskAssigns(taskId)
   └─ Emits when assignments change

5. User Data
   firebase.currentUserData$
   └─ Emits when user changes
```

### Reactive Updates

```
Firestore Database Change
        │
        ▼
Observable Emits New Value
        │
        ▼
All Subscribers Receive Value
        │
        ├─> Board Component
        ├─> Summary Component
        ├─> Contacts Component
        └─> Other Listeners
        │
        ▼
Components Update Signals
        │
        ▼
Templates Re-render (OnPush)
        │
        ▼
User Sees Update Immediately
```

---

## Design Patterns

### 1. Smart & Dumb Components

**Smart (Container)**
- Fetches data via services
- Manages state
- Handles business logic
- Example: Board, Login, AddTask

**Dumb (Presentational)**
- Pure @Input/@Output
- No side effects
- Only renders data
- Example: TaskPreview, Dialog

### 2. Dependency Injection

```typescript
export class BoardComponent {
  private firebase = inject(FirebaseServices);
  private router = inject(Router);
  private userUi = inject(UserUiService);
}
```

### 3. Reactive Streams

```typescript
tasks$ = this.firebase.subTasks().pipe(
  map(tasks => this.enrichTasks(tasks)),
  shareReplay(1)
);
```

### 4. Signal-based State

```typescript
selectedContactId = signal<string | null>(null);

readonly contact$ = computed(() =>
  this.firebase.subSingleContact(this.contactId())
);
```

### 5. Cascade Operations

```typescript
// Delete task deletes:
// - Task document
// - All subtasks
// - All assignments
// (Atomic batch write)
deleteTaskWithChildren(taskId)
```

### 6. Type Safety

```typescript
// Interfaces ensure type safety
interface Task {
  id?: string;
  type: TaskType;
  status: TaskStatus;
  // ...
}

interface BoardTask extends Task {
  assigns: TaskAssign[];
  subtasks: Subtask[];
}
```

---

## Technology Decisions

### Why Angular 20?
- Modern standalone components
- Signals for reactive state
- Excellent TypeScript support
- Material Design integration
- Enterprise-grade framework

### Why Firebase?
- Real-time Firestore
- Built-in authentication
- Scalable backend
- No server infrastructure needed
- Free tier available

### Why RxJS?
- Powerful stream handling
- Compose async operations
- Unsubscribe management
- Wide ecosystem support

### Why Material Design?
- Professional UI components
- Accessibility built-in
- Consistent theming
- Mobile optimized

---

## Performance Considerations

### Optimization Techniques

1. **Lazy Loading**: Routes loaded on-demand
2. **Change Detection**: OnPush strategy for components
3. **TrackBy**: Efficient *ngFor with trackBy
4. **Unsubscribe**: takeUntilDestroyed() prevents memory leaks
5. **Firestore Indexes**: Optimize queries

### Scalability

- Firestore auto-scales
- Real-time synchronization efficient
- Component hierarchy optimized
- No complex state management needed

---

**Next Steps**:
- See [03-API.md](./03-API.md) for detailed function documentation
- See [04-COMPONENTS.md](./04-COMPONENTS.md) for component details
- See [05-DATABASE.md](./05-DATABASE.md) for database setup

---

**Last Updated**: January 15, 2026  
**Version**: 1.0
