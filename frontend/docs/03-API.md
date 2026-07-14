# API Reference & Function Documentation

Complete reference of all public methods and functions in the Join application, including parameters, return types, and usage examples.

## Table of Contents

1. [Service Overview](#service-overview)
2. [AuthService](#authservice)
3. [FirebaseServices](#firebaseservices)
4. [UserUiService](#useruiservice)
5. [Type Definitions](#type-definitions)
6. [Usage Examples](#usage-examples)

---

## Service Overview

| Service | Location | Responsibility |
|---------|----------|-----------------|
| AuthService | `firebase-services/auth-services.ts` | User authentication |
| FirebaseServices | `firebase-services/firebase-services.ts` | Firestore CRUD |
| UserUiService | `services/user-ui.service.ts` | UI utilities |

---

## AuthService

Manages user authentication including login, signup, logout, and guest access.

**File**: `src/app/firebase-services/auth-services.ts`

### Methods

#### `login(email: string, password: string): Promise<void>`

Login existing user with email and password.

**Parameters**:
- `email` (string): User email address
- `password` (string): User password

**Returns**: Promise<void>

**Throws**:
- `auth/invalid-email`: Invalid email format
- `auth/user-not-found`: User doesn't exist
- `auth/wrong-password`: Incorrect password
- `auth/too-many-requests`: Too many failed attempts

**Example**:
```typescript
async handleLogin() {
  try {
    await this.auth.login('user@example.com', 'password123')
    // User logged in, navigate to /summary
  } catch (error) {
    // Show error message
  }
}
```

---

#### `signup(name: string, email: string, password: string): Promise<void>`

Register new user account.

**Parameters**:
- `name` (string): User's full name (required)
- `email` (string): Email address (must be valid)
- `password` (string): Password (min 6 characters)

**Returns**: Promise<void>

**Process**:
1. Creates auth user with email/password
2. Creates contact document in Firestore
3. Assigns color to user
4. Sets `isUser: true` flag

**Throws**:
- `auth/email-already-in-use`: Email registered
- `auth/weak-password`: Password too short
- `auth/invalid-email`: Invalid email format

**Example**:
```typescript
async handleSignup() {
  try {
    await this.auth.signup('John Doe', 'john@example.com', 'secure123')
    // New account created
  } catch (error) {
    if (error.code === 'auth/email-already-in-use') {
      // Show "email already exists" message
    }
  }
}
```

---

#### `loginGuest(): Promise<void>`

Login as anonymous guest user.

**Parameters**: None

**Returns**: Promise<void>

**Features**:
- No email/password required
- Full read-only access to app
- Cannot edit or create content
- Session ends on logout

**Example**:
```typescript
async handleGuestLogin() {
  try {
    await this.auth.loginGuest()
    // Guest logged in, navigate to /summary
  } catch (error) {
    // Handle guest login error
  }
}
```

---

#### `logout(): Promise<void>`

Logout current user and clear session.

**Parameters**: None

**Returns**: Promise<void>

**Behavior**:
- Signs out from Firebase
- Clears local auth state
- Navigates to login page
- If guest: deletes anonymous account

**Example**:
```typescript
async handleLogout() {
  try {
    await this.auth.logout()
    // Logged out, returned to login page
  } catch (error) {
    // Handle logout error
  }
}
```

---

#### `getCurrentUser(): User | null`

Get currently authenticated user.

**Parameters**: None

**Returns**: `User | null` (Firebase User object or null)

**Properties Returned**:
```typescript
{
  uid: string            // Unique user ID
  email: string | null   // User email
  displayName: string    // User name
  isAnonymous: boolean   // Is guest user
  metadata: {
    creationTime: string
    lastSignInTime: string
  }
}
```

**Example**:
```typescript
const user = this.auth.getCurrentUser()
if (user?.isAnonymous) {
  // Show "guest" label
}
```

---

#### `isAuthenticated(): Observable<boolean>`

Observable stream of authentication state.

**Parameters**: None

**Returns**: `Observable<boolean>`

**Emits**: `true` if user logged in, `false` if logged out

**Example**:
```typescript
this.auth.isAuthenticated()
  .pipe(takeUntilDestroyed(this.destroyRef))
  .subscribe(isAuth => {
    if (isAuth) {
      // Show main app
    } else {
      // Show login page
    }
  })
```

---

## FirebaseServices

Manages all Firestore database operations including CRUD for tasks, contacts, and subtasks.

**File**: `src/app/firebase-services/firebase-services.ts`

### Task Methods

#### `addTask(task: Task): Promise<string>`

Create new task in Firestore.

**Parameters**:
- `task` (Task): Task object with required fields

**Required Fields**:
```typescript
{
  title: string,           // Task title
  description: string,     // Description
  type: TaskType,          // 1=UserStory, 2=TechnicalTask
  status: TaskStatus,      // todo, in_progress, await_feedback, done
  date: Timestamp,         // Due date
  priority: number         // 1=urgent, 2=medium, 3=low
}
```

**Returns**: Promise<string> (new task ID)

**Example**:
```typescript
const newTask: Task = {
  title: 'Design Homepage',
  description: 'Create mockups',
  type: 1,
  status: 'todo',
  date: Timestamp.now(),
  priority: 1
}

const taskId = await this.firebase.addTask(newTask)
console.log('Created task:', taskId)
```

---

#### `updateTask(id: string, task: Partial<Task>): Promise<void>`

Update existing task.

**Parameters**:
- `id` (string): Task document ID
- `task` (Partial<Task>): Fields to update (only send changed fields)

**Example**:
```typescript
// Update only status
await this.firebase.updateTask('task123', {
  status: 'in_progress'
})

// Update multiple fields
await this.firebase.updateTask('task123', {
  title: 'New Title',
  priority: 2
})
```

---

#### `deleteTask(id: string): Promise<void>`

Delete task and all related data.

**Parameters**:
- `id` (string): Task document ID

**Deletes**:
- Task document
- All subtasks
- All task assignments

**Example**:
```typescript
try {
  await this.firebase.deleteTask('task123')
  // Task deleted
} catch (error) {
  // Handle error
}
```

---

#### `subTasks(): Observable<Task[]>`

Subscribe to all tasks in real-time.

**Parameters**: None

**Returns**: `Observable<Task[]>` (emits on any change)

**Updates**: Automatically when tasks change in Firestore

**Example**:
```typescript
tasks$ = this.firebase.subTasks()

// In template
*ngFor="let task of tasks$ | async"
```

---

#### `subSingleTask(id: string): Observable<Task>`

Subscribe to single task in real-time.

**Parameters**:
- `id` (string): Task document ID

**Returns**: `Observable<Task>`

**Example**:
```typescript
taskDetail$ = this.firebase.subSingleTask('task123')

taskDetail$
  .pipe(takeUntilDestroyed(this.destroyRef))
  .subscribe(task => {
    console.log('Task updated:', task.title)
  })
```

---

### Subtask Methods

#### `addSubtask(taskId: string, subtask: Subtask): Promise<string>`

Add subtask to task.

**Parameters**:
- `taskId` (string): Parent task ID
- `subtask` (Subtask): Subtask object

**Subtask Structure**:
```typescript
{
  title: string,     // Subtask title
  done: boolean      // Completion status
}
```

**Returns**: Promise<string> (new subtask ID)

**Example**:
```typescript
const subtask: Subtask = {
  title: 'Create wireframe',
  done: false
}

const subtaskId = await this.firebase.addSubtask('task123', subtask)
```

---

#### `updateSubtask(taskId: string, subtaskId: string, subtask: Partial<Subtask>): Promise<void>`

Update subtask.

**Parameters**:
- `taskId` (string): Parent task ID
- `subtaskId` (string): Subtask ID
- `subtask` (Partial<Subtask>): Fields to update

**Example**:
```typescript
// Mark as complete
await this.firebase.updateSubtask('task123', 'sub456', {
  done: true
})
```

---

#### `deleteSubtask(taskId: string, subtaskId: string): Promise<void>`

Delete subtask.

**Parameters**:
- `taskId` (string): Parent task ID
- `subtaskId` (string): Subtask ID

**Example**:
```typescript
await this.firebase.deleteSubtask('task123', 'sub456')
```

---

#### `subSubtasks(taskId: string): Observable<Subtask[]>`

Subscribe to task's subtasks.

**Parameters**:
- `taskId` (string): Parent task ID

**Returns**: `Observable<Subtask[]>`

**Example**:
```typescript
subtasks$ = this.firebase.subSubtasks('task123')

*ngFor="let subtask of subtasks$ | async"
```

---

### Contact Methods

#### `addContact(contact: Contact): Promise<string>`

Create new contact.

**Parameters**:
- `contact` (Contact): Contact object

**Contact Structure**:
```typescript
{
  name: string,      // Contact name
  email: string,     // Email address
  phone: string,     // Phone number
  color: string,     // Hex color (#RRGGBB)
  isUser: boolean    // Is registered user
}
```

**Returns**: Promise<string> (new contact ID)

**Example**:
```typescript
const contact: Contact = {
  name: 'Alice Smith',
  email: 'alice@example.com',
  phone: '+1234567890',
  color: '#FF5733',
  isUser: false
}

const contactId = await this.firebase.addContact(contact)
```

---

#### `updateContact(id: string, contact: Partial<Contact>): Promise<void>`

Update contact information.

**Parameters**:
- `id` (string): Contact document ID
- `contact` (Partial<Contact>): Fields to update

**Example**:
```typescript
await this.firebase.updateContact('contact123', {
  phone: '+9876543210',
  email: 'newemail@example.com'
})
```

---

#### `deleteContact(id: string): Promise<void>`

Delete contact.

**Parameters**:
- `id` (string): Contact document ID

**Note**: Removes contact from all task assignments

**Example**:
```typescript
await this.firebase.deleteContact('contact123')
```

---

#### `subContactsList(): Observable<Contact[]>`

Subscribe to all contacts.

**Parameters**: None

**Returns**: `Observable<Contact[]>`

**Example**:
```typescript
contacts$ = this.firebase.subContactsList()

contacts$
  .pipe(takeUntilDestroyed(this.destroyRef))
  .subscribe(contacts => {
    this.allContacts = contacts
  })
```

---

#### `subSingleContact(id: string): Observable<Contact>`

Subscribe to single contact.

**Parameters**:
- `id` (string): Contact document ID

**Returns**: `Observable<Contact>`

**Example**:
```typescript
contact$ = this.firebase.subSingleContact('contact123')
```

---

### Task Assignment Methods

#### `assignTaskToContact(taskId: string, contactId: string): Promise<void>`

Assign task to contact.

**Parameters**:
- `taskId` (string): Task ID
- `contactId` (string): Contact ID

**Example**:
```typescript
await this.firebase.assignTaskToContact('task123', 'contact456')
```

---

#### `removeTaskAssignment(taskId: string, assignId: string): Promise<void>`

Remove contact from task.

**Parameters**:
- `taskId` (string): Task ID
- `assignId` (string): Assignment ID

**Example**:
```typescript
await this.firebase.removeTaskAssignment('task123', 'assign789')
```

---

#### `subTaskAssigns(taskId: string): Observable<TaskAssign[]>`

Subscribe to task assignments.

**Parameters**:
- `taskId` (string): Task ID

**Returns**: `Observable<TaskAssign[]>`

**TaskAssign Structure**:
```typescript
{
  id?: string,       // Assignment ID
  contactId: string  // Contact reference
}
```

**Example**:
```typescript
assigns$ = this.firebase.subTaskAssigns('task123')

assigns$
  .pipe(
    switchMap(assigns =>
      forkJoin(assigns.map(a => 
        this.firebase.subSingleContact(a.contactId)
      ))
    )
  )
  .subscribe(contacts => {
    this.assignedContacts = contacts
  })
```

---

### Utility Methods

#### `changeUserColor(newColorNum: number): Promise<void>`

Change user's profile color.

**Parameters**:
- `newColorNum` (number): Color index (0-15)

**Available Colors**: Array of hex colors

**Example**:
```typescript
// Change to color index 5
await this.firebase.changeUserColor(5)
```

---

#### `getCurrentUserData(): Observable<Contact>`

Get current logged-in user's contact data.

**Parameters**: None

**Returns**: `Observable<Contact>`

**Example**:
```typescript
currentUserData$ = this.firebase.getCurrentUserData()

currentUserData$
  .pipe(takeUntilDestroyed(this.destroyRef))
  .subscribe(userData => {
    console.log('User color:', userData.color)
  })
```

---

## UserUiService

Utility functions for UI operations and formatting.

**File**: `src/app/services/user-ui.service.ts`

### Methods

#### `getInitials(name: string): string`

Get user initials from full name.

**Parameters**:
- `name` (string): Full name

**Returns**: `string` (2-3 characters)

**Examples**:
```typescript
getInitials('John Doe')        // Returns 'JD'
getInitials('Alice Smith')     // Returns 'AS'
getInitials('Mary Jane Watson') // Returns 'MJW'
```

---

#### `formatDate(date: Timestamp): string`

Format Firebase Timestamp to readable date.

**Parameters**:
- `date` (Timestamp): Firebase Timestamp object

**Returns**: `string` (formatted date)

**Format**: `MMM dd, yyyy` (e.g., "Jan 15, 2026")

**Example**:
```typescript
const formatted = this.userUi.formatDate(task.date)
// Output: "Jan 15, 2026"
```

---

#### `getDaysUntilDue(dueDate: Timestamp): number`

Calculate days remaining until due date.

**Parameters**:
- `dueDate` (Timestamp): Task due date

**Returns**: `number` (days remaining)

**Notes**:
- Negative if overdue
- 0 if due today
- Positive if future date

**Example**:
```typescript
const daysLeft = this.userUi.getDaysUntilDue(task.date)
if (daysLeft < 0) {
  // Task is overdue
} else if (daysLeft <= 3) {
  // Task due soon
}
```

---

#### `isTaskUrgent(task: Task): boolean`

Check if task is urgent (due within 3 days).

**Parameters**:
- `task` (Task): Task object

**Returns**: `boolean`

**Logic**:
- Returns true if due within 3 days
- Considers overdue tasks as urgent

**Example**:
```typescript
const urgent = this.userUi.isTaskUrgent(task)
if (urgent) {
  // Highlight in red
}
```

---

#### `getTaskTypeLabel(type: TaskType): string`

Convert task type enum to readable label.

**Parameters**:
- `type` (TaskType): Task type (1 or 2)

**Returns**: `string`

**Values**:
- 1 → "User Story"
- 2 → "Technical Task"

**Example**:
```typescript
const label = this.userUi.getTaskTypeLabel(1)
// Output: "User Story"
```

---

#### `getPriorityLabel(priority: number): string`

Convert priority number to readable label.

**Parameters**:
- `priority` (number): Priority (1, 2, or 3)

**Returns**: `string`

**Values**:
- 1 → "Urgent"
- 2 → "Medium"
- 3 → "Low"

**Example**:
```typescript
const label = this.userUi.getPriorityLabel(2)
// Output: "Medium"
```

---

#### `getStatusLabel(status: TaskStatus): string`

Convert task status to readable label.

**Parameters**:
- `status` (TaskStatus): Status string

**Returns**: `string`

**Values**:
- "todo" → "To Do"
- "in_progress" → "In Progress"
- "await_feedback" → "Await Feedback"
- "done" → "Done"

**Example**:
```typescript
const label = this.userUi.getStatusLabel('in_progress')
// Output: "In Progress"
```

---

## Type Definitions

### Task Interface

```typescript
interface Task {
  id?: string
  title: string
  description: string
  type: TaskType           // 1=UserStory, 2=TechnicalTask
  status: TaskStatus       // todo|in_progress|await_feedback|done
  date: Timestamp
  priority: number         // 1=urgent, 2=medium, 3=low
}
```

### Subtask Interface

```typescript
interface Subtask {
  id?: string
  title: string
  done: boolean
}
```

### Contact Interface

```typescript
interface Contact {
  id?: string
  name: string
  email: string
  phone: string
  color: string            // Hex color #RRGGBB
  isUser: boolean
}
```

### TaskAssign Interface

```typescript
interface TaskAssign {
  id?: string
  contactId: string
}
```

### TaskType Enum

```typescript
type TaskType = 1 | 2     // 1=UserStory, 2=TechnicalTask
```

### TaskStatus Enum

```typescript
type TaskStatus = 
  | 'todo'
  | 'in_progress'
  | 'await_feedback'
  | 'done'
```

---

## Usage Examples

### Complete Task Creation Flow

```typescript
// In AddTask component
async createTask() {
  // 1. Create task
  const taskData: Task = {
    title: this.form.value.title,
    description: this.form.value.description,
    type: this.form.value.type,
    status: 'todo',
    date: this.form.value.date,
    priority: this.form.value.priority
  }

  const taskId = await this.firebase.addTask(taskData)

  // 2. Add subtasks
  for (const subtaskTitle of this.form.value.subtasks) {
    await this.firebase.addSubtask(taskId, {
      title: subtaskTitle,
      done: false
    })
  }

  // 3. Assign contacts
  for (const contact of this.form.value.assignedContacts) {
    await this.firebase.assignTaskToContact(taskId, contact.id!)
  }

  // 4. Navigate back
  this.router.navigate(['/board'])
}
```

### Task Status Update

```typescript
// In Board component
async moveTaskToColumn(taskId: string, newStatus: TaskStatus) {
  await this.firebase.updateTask(taskId, {
    status: newStatus
  })
  // Observable updates automatically
}
```

### Contact Assignment

```typescript
// In Task editing
async assignContact(taskId: string, contactId: string) {
  await this.firebase.assignTaskToContact(taskId, contactId)

  // Get updated assignments
  const assigns = await firstValueFrom(
    this.firebase.subTaskAssigns(taskId)
  )
}
```

---

**Related Documentation**:
- [Components Guide](./04-COMPONENTS.md) - Component implementations
- [Database Schema](./05-DATABASE.md) - Data structure details
- [Architecture](./02-ARCHITECTURE.md) - System design

---

**Last Updated**: January 15, 2026  
**Version**: 1.0
