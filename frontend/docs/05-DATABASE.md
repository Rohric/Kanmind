# Database Schema & Design

Complete documentation of Firestore database structure, collections, fields, relationships, and indexing requirements.

## Table of Contents

1. [Database Overview](#database-overview)
2. [Collections](#collections)
3. [Data Models](#data-models)
4. [Relationships](#relationships)
5. [Indexes](#indexes)
6. [Best Practices](#best-practices)
7. [Migration Guide](#migration-guide)

---

## Database Overview

### Architecture

```
Firestore Database
│
├── contacts/          (Collection)
├── tasks/             (Collection)
│   ├── subtasks/      (Subcollection per task)
│   └── assigns/       (Subcollection per task)
└── appSettings/       (Collection)
```

### Key Statistics

| Metric | Value |
|--------|-------|
| **Collections** | 4 main collections |
| **Document Limit** | Unlimited per collection |
| **Field Limit** | Unlimited per document |
| **Subcollection Depth** | 2 levels |
| **Region** | us-central1 (recommended) |
| **Billing** | Pay-per-read, write, delete |

---

## Collections

### 1. contacts/

Stores contact information for both users and team members.

**Path**: `/contacts/{documentId}`

**Document Structure**:

```json
{
  "id": "user123",                    // Document ID
  "name": "John Doe",                 // Contact name (required)
  "email": "john@example.com",        // Email address (required)
  "phone": "+1-555-0123",             // Phone number (optional)
  "color": "#FF5733",                 // Hex color code (required)
  "isUser": true                      // Is registered user (required)
}
```

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | N/A | Document ID (auto-generated) |
| name | string | ✓ | Contact full name |
| email | string | ✓ | Email address |
| phone | string | ✗ | Phone number |
| color | string | ✓ | Hex color (#RRGGBB) |
| isUser | boolean | ✓ | True if registered user |

**Indexes**: None required (simple lookup only)

**Access Pattern**: 
- Read all contacts
- Filter by `isUser: true` to get users only
- Direct document lookup by ID

**Examples**:

```typescript
// Create contact
{
  name: "Alice Smith",
  email: "alice@example.com",
  phone: "+1-555-0456",
  color: "#33FF57",
  isUser: true
}

// Team member (not registered user)
{
  name: "Bob Jones",
  email: "bob@example.com",
  phone: "+1-555-0789",
  color: "#3357FF",
  isUser: false
}
```

---

### 2. tasks/

Stores all task information.

**Path**: `/tasks/{documentId}`

**Document Structure**:

```json
{
  "id": "task456",                    // Document ID
  "title": "Design UI Mockups",       // Task title (required)
  "description": "Create mockups...", // Task description (required)
  "type": 1,                          // Task type: 1=UserStory, 2=TechnicalTask
  "status": "in_progress",            // Status (required)
  "date": Timestamp,                  // Due date (required)
  "priority": 1,                      // Priority: 1=urgent, 2=medium, 3=low
  "createdAt": Timestamp,             // Creation timestamp
  "updatedAt": Timestamp              // Last update timestamp
}
```

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | N/A | Document ID |
| title | string | ✓ | Task title (1-100 chars) |
| description | string | ✓ | Task description (0-1000 chars) |
| type | number | ✓ | 1=UserStory, 2=TechnicalTask |
| status | string | ✓ | todo, in_progress, await_feedback, done |
| date | Timestamp | ✓ | Due date |
| priority | number | ✓ | 1=urgent, 2=medium, 3=low |
| createdAt | Timestamp | ✗ | Auto-timestamp on create |
| updatedAt | Timestamp | ✗ | Auto-timestamp on update |

**Status Values**:
```
"todo"            → In To Do column
"in_progress"     → In Progress column
"await_feedback"  → Awaiting feedback
"done"            → Completed
```

**Subcollections**:
- `subtasks/` - Child tasks
- `assigns/` - Contact assignments

**Example**:

```json
{
  "title": "Design Homepage",
  "description": "Create responsive design for home page",
  "type": 1,
  "status": "in_progress",
  "date": Timestamp.fromDate(new Date('2026-02-15')),
  "priority": 1,
  "createdAt": Timestamp.now(),
  "updatedAt": Timestamp.now()
}
```

---

### 3. tasks/{taskId}/subtasks/

Stores subtasks for each task.

**Path**: `/tasks/{taskId}/subtasks/{documentId}`

**Document Structure**:

```json
{
  "id": "sub123",                     // Document ID
  "title": "Create wireframe",        // Subtask title (required)
  "done": false,                      // Completion status (required)
  "createdAt": Timestamp              // Creation timestamp
}
```

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | N/A | Document ID |
| title | string | ✓ | Subtask title (1-200 chars) |
| done | boolean | ✓ | Completion status |
| createdAt | Timestamp | ✗ | Auto-timestamp on create |

**Features**:
- Subcollection (nested under task)
- Can have 0 to many subtasks per task
- Simple toggle for completion
- Inherits parent task context

**Example**:

```json
{
  "title": "Create wireframe sketches",
  "done": false,
  "createdAt": Timestamp.now()
}
```

---

### 4. tasks/{taskId}/assigns/

Stores contact assignments for each task.

**Path**: `/tasks/{taskId}/assigns/{documentId}`

**Document Structure**:

```json
{
  "id": "assign456",                  // Document ID
  "contactId": "contact789",          // Reference to contact
  "assignedAt": Timestamp             // Assignment timestamp
}
```

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | N/A | Document ID |
| contactId | string | ✓ | Reference to contacts/{id} |
| assignedAt | Timestamp | ✗ | Auto-timestamp on assign |

**Features**:
- Subcollection (nested under task)
- Stores contact references (not denormalized)
- Multiple contacts can be assigned
- Soft-delete friendly (just remove assignment)

**Example**:

```json
{
  "contactId": "user123",
  "assignedAt": Timestamp.now()
}
```

---

### 5. appSettings/

Stores application-level settings.

**Path**: `/appSettings/{documentId}`

**Document Structure** (contacts settings):

```json
{
  "id": "contacts",                   // Document ID
  "lastUserColor": 5                  // Last assigned color index (0-15)
}
```

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | N/A | Document ID |
| lastUserColor | number | ✓ | Color index (0-15) |

**Purpose**: Track app state (currently just color rotation)

**Example**:

```json
{
  "lastUserColor": 7
}
```

---

## Data Models

### Task Model

```typescript
interface Task {
  id?: string
  title: string              // Required, 1-100 chars
  description: string        // Required, 0-1000 chars
  type: TaskType             // 1=UserStory, 2=TechnicalTask
  status: TaskStatus         // todo, in_progress, await_feedback, done
  date: Timestamp            // Due date
  priority: number           // 1=urgent, 2=medium, 3=low
  createdAt?: Timestamp      // Auto-set
  updatedAt?: Timestamp      // Auto-set
}
```

### BoardTask Model (Extended)

```typescript
interface BoardTask extends Task {
  subtasks: Subtask[]        // Embedded subtasks
  assigns: Contact[]         // Expanded contact assignments
  daysUntilDue: number       // Calculated field
  isUrgent: boolean          // Calculated field
}
```

### Subtask Model

```typescript
interface Subtask {
  id?: string
  title: string              // Required, 1-200 chars
  done: boolean              // Required
  createdAt?: Timestamp      // Auto-set
}
```

### Contact Model

```typescript
interface Contact {
  id?: string
  name: string               // Required
  email: string              // Required
  phone: string              // Optional
  color: string              // Required (hex color)
  isUser: boolean            // Required
}
```

### Task Assignment Model

```typescript
interface TaskAssign {
  id?: string
  contactId: string          // Reference to Contact document
  assignedAt?: Timestamp     // Auto-set
}
```

---

## Relationships

### Entity Relationship Diagram

```
Contact (1)
    │
    ├──────── (Many) Task Assignments
    │             └─ in Task.assigns
    │
    └──────── References in multiple tasks

Task (1)
    │
    ├──────── (Many) Subtasks
    │             └─ in Task.subtasks
    │
    └──────── (Many) Assignments
                  └─ in Task.assigns
                      └─ references Contact

AppSettings (1)
    └──────── (Many) Settings documents
```

### Denormalization Strategy

**Denormalized Data** (stored in document):
- Contact basic info (name, email, color)
- Task metadata (title, date, priority)
- Subtask details (title, done status)

**Normalized Data** (stored as reference):
- Task assignments use `contactId` reference
- Assignments are in subcollection (not duplicated)

**Benefits**:
- Reduce reads (get assignment + denormalized contact in one query)
- Maintain data integrity (single source of truth)
- Flexible querying (can filter on references)

### Reference Integrity

When deleting a contact:
1. Delete contact document
2. Remove from all task assignments

When deleting a task:
1. Delete task document
2. Automatically delete subtasks (subcollection)
3. Automatically delete assignments (subcollection)

---

## Indexes

### Composite Indexes

Currently, no composite indexes required due to simple query patterns:

```
- Single field queries (no index needed)
- Subcollection queries (indexed automatically)
- No complex filters on timestamps
```

### Future Indexes (if needed)

If adding advanced queries:

```
// For filtering tasks by status and priority
GET /tasks
  WHERE status == 'in_progress'
  AND priority == 1
  ORDER BY date ASC

// Requires composite index: (status, priority, date)

// For filtering tasks by user
GET /tasks
  WHERE (user in ["user1", "user2"])
  ORDER BY date DESC

// Requires composite index: (user, date)
```

### View Indexes

Firestore automatically creates indexes for:
- All single-field queries
- All subcollection queries
- Automatic pagination indexes

---

## Best Practices

### 1. Document ID Strategy

**Current Approach**: Firestore auto-generates IDs

```typescript
// Auto-generated (recommended)
addDoc(collection(db, 'tasks'), taskData)
// Generates: "aBcDeF1234..."

// Custom ID (use cases only)
setDoc(doc(db, 'tasks', 'custom-id'), taskData)
```

**Advantages**:
- Distributed writes (no hotspots)
- Collision-free
- Sortable by timestamp

---

### 2. Timestamp Fields

**Always use Firestore Timestamp**:

```typescript
// Correct
date: Timestamp.fromDate(new Date())

// Wrong
date: new Date()
date: Date.now()
```

**Benefits**:
- Server-side timestamp
- Consistency across clients
- Proper sorting

---

### 3. Subcollection Limits

**Guidelines**:
- Keep subcollections < 100,000 documents per parent
- Current limits: ~100 subtasks/task, ~50 assignments/task (safe)
- Monitor growth for performance

---

### 4. Query Optimization

**Best practices**:

```typescript
// ✓ Good: Direct document
docData(doc(db, 'tasks', 'task123'))

// ✓ Good: Collection with simple filter
query(collection(db, 'tasks'), 
  where('status', '==', 'done'))

// ✗ Avoid: Multiple filters (requires index)
query(collection(db, 'tasks'),
  where('status', '==', 'done'),
  where('priority', '==', 1),
  where('date', '<', today))
```

---

### 5. Data Validation

**Required field validation** (before Firestore):

```typescript
// Type-safe with TypeScript
const task: Task = {
  title: '',        // Error: required
  description: '',
  // ...
}

// Runtime validation
validateTask(task) {
  if (!task.title) throw new Error('Title required')
  if (task.title.length > 100) throw new Error('Title too long')
}
```

---

### 6. Backup & Recovery

**Automatic backups**:
- Firestore keeps 7-day automatic backup
- Enable point-in-time recovery (paid feature)

**Manual export**:
```bash
gcloud firestore export gs://my-backup/backup-2026-01
```

---

## Migration Guide

### Initialization Checklist

**Step 1: Create Collections**
```
- contacts/
- tasks/
- appSettings/
```

**Step 2: Create Sample Documents**
```
// contacts/user1
{name, email, phone, color, isUser}

// tasks/task1
{title, description, type, status, date, priority}

// tasks/task1/subtasks/sub1
{title, done}

// tasks/task1/assigns/assign1
{contactId}

// appSettings/contacts
{lastUserColor}
```

**Step 3: Create Indexes**
- No composite indexes needed initially
- Add as queries become complex

**Step 4: Set Security Rules**
- Start with test mode (development)
- Implement proper rules for production

---

### Data Import

**Import from CSV** (if migrating from another system):

```typescript
async importTasksFromCSV(csvFile: File) {
  const rows = parseCSV(csvFile)
  const batch = writeBatch(db)

  for (const row of rows) {
    const taskRef = doc(collection(db, 'tasks'))
    batch.set(taskRef, {
      title: row.title,
      description: row.description,
      type: parseInt(row.type),
      status: row.status,
      date: Timestamp.fromDate(new Date(row.date)),
      priority: parseInt(row.priority)
    })
  }

  await batch.commit()
}
```

---

**Related Documentation**:
- [API Reference](./03-API.md) - Firebase methods
- [Architecture](./02-ARCHITECTURE.md) - Data flow
- [Troubleshooting](./08-TROUBLESHOOTING.md) - Common issues

---

**Last Updated**: January 15, 2026  
**Version**: 1.0
