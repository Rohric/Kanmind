# Component Documentation

Detailed documentation for all Angular components in the Join application, including their responsibilities, inputs, outputs, and usage.

## Table of Contents

1. [Component Overview](#component-overview)
2. [Core Components](#core-components)
3. [Feature Components](#feature-components)
4. [Shared Components](#shared-components)
5. [Component Patterns](#component-patterns)
6. [Best Practices](#best-practices)

---

## Component Overview

| Component | Type | Route | Purpose |
|-----------|------|-------|---------|
| App | Root | N/A | Root component, routing |
| Login | Page | `/login` | Authentication page |
| MainPage | Layout | `/` | Protected main layout |
| Header | Shared | N/A | Top navigation |
| Navbar | Shared | N/A | Side navigation |
| Summary | Page | `/summary` | Dashboard with stats |
| Board | Page | `/board` | Kanban task board |
| AddTask | Page | `/add-task` | Task creation form |
| Contacts | Page | `/contacts` | Contact management |
| Helper | Page | `/helper` | Help documentation |
| LegalNotice | Page | `/legal-notice` | Legal information |
| PrivacyPolicy | Page | `/privacy-policy` | Privacy policy |

---

## Core Components

### App Component

Root component that initializes the application and manages routing.

**File**: `src/app/app.ts`

**Selector**: `<app-root></app-root>`

**Template Structure**:
```html
<router-outlet></router-outlet>
```

**Responsibilities**:
- Initialize Firebase configuration
- Set up application providers
- Display Login or MainPage based on auth state
- Handle global error states

**Key Methods**:
```typescript
// Component initialization
ngOnInit(): void
// Initialize auth state checks

// Properties
isLoggedIn$: Observable<boolean>
// Stream of authentication state
```

**Usage**:
```typescript
// In main.ts
bootstrapApplication(App, appConfig)
```

---

### Login Component

Handles user authentication with login, signup, and guest access options.

**File**: `src/app/login/login.ts`

**Selector**: `<app-login></app-login>`

**Route**: `/login`

**Features**:
- Email/password login
- User registration/signup
- Guest access
- Form validation
- Error messages
- Loading states

**Key Methods**:
```typescript
// Handle login form submission
login(email: string, password: string): Promise<void>

// Handle signup form submission
signup(name: string, email: string, password: string): Promise<void>

// Handle guest login
loginGuest(): Promise<void>

// Toggle between login and signup forms
toggleForm(): void

// Validate form inputs
validateForm(): boolean
```

**Template Sections**:
- Email input
- Password input
- Name input (signup only)
- Confirm password (signup only)
- Login button
- Signup toggle
- Guest login button
- Error message display

**Styling**: `login.scss`
- Responsive design (mobile-first)
- Material Design styling
- Form animations

**Example**:
```html
<div class="login-container">
  <form (ngSubmit)="login(email, password)">
    <mat-form-field>
      <input matInput placeholder="Email" [(ngModel)]="email">
    </mat-form-field>
    <button mat-raised-button>Login</button>
  </form>
</div>
```

---

### MainPage Component

Main application layout container for authenticated users.

**File**: `src/app/login/main-page/main-page.ts`

**Selector**: `<app-main-page></app-main-page>`

**Route**: `/`

**Structure**:
```
MainPage
├── Header
├── Navbar
└── Router Outlet (child routes)
    ├── Summary
    ├── Board
    ├── AddTask
    ├── Contacts
    ├── Helper
    ├── LegalNotice
    └── PrivacyPolicy
```

**Responsibilities**:
- Layout container for protected routes
- User authentication check
- Navigation management
- Responsive layout handling

**Key Methods**:
```typescript
// Check if user is authenticated
checkAuthState(): void

// Handle window resize for responsive layout
onWindowResize(): void

// Toggle mobile navbar visibility
toggleMobileNavbar(): void
```

**Properties**:
```typescript
isMobileView: signal<boolean>
// Current view is mobile

activeRoute: signal<string>
// Currently active route
```

**Layout**:
- Desktop: Sidebar navbar + content
- Mobile: Toggle navbar + full-width content
- Responsive breakpoints at 768px

---

## Feature Components

### Board Component (Kanban Board)

Main task board with kanban columns and drag-drop functionality.

**File**: `src/app/login/main-page/board/board.ts`

**Selector**: `<app-board></app-board>`

**Route**: `/board`

**Features**:
- 4 kanban columns (todo, in_progress, await_feedback, done)
- Drag-and-drop tasks between columns
- Task search/filter
- Task preview (click on card)
- Add task dialog
- Real-time updates

**Columns**:
```
[Todo] → [In Progress] → [Await Feedback] → [Done]
```

**Key Methods**:
```typescript
// Load all tasks
loadTasks(): void

// Handle drag-drop event
onTaskDropped(taskId: string, newStatus: string): void

// Open add task dialog
openAddTaskDialog(): void

// Filter tasks by search term
filterTasks(searchTerm: string): void

// Open task detail/edit dialog
openTaskPreview(task: Task): void
```

**Properties**:
```typescript
tasks$ = this.firebase.subTasks()
// Observable of all tasks

searchTerm = signal<string>('')
// Current search filter

draggedTask = signal<Task | null>(null)
// Currently dragged task
```

**Columns Component**:
Each column is built with:
```html
<div class="column">
  <h3>Column Title</h3>
  <div cdkDropList [cdkDropListData]="columnTasks">
    <app-task-preview 
      *ngFor="let task of columnTasks; trackBy: trackByTaskId"
      [task]="task"
      (click)="openTaskPreview(task)">
    </app-task-preview>
  </div>
</div>
```

**Styling**: `board.scss`
- Responsive grid layout
- Column styling
- Drag-drop visual feedback
- Mobile: Single column scrollable view

---

### TaskPreview Component

Individual task card displayed in kanban board.

**File**: `src/app/login/main-page/board/task-preview/task-preview.ts`

**Selector**: `<app-task-preview></app-task-preview>`

**Inputs**:
```typescript
@Input() task: Task
// Task data to display

@Input() isSelected: boolean = false
// Visual selection state
```

**Outputs**:
```typescript
@Output() taskClicked = new EventEmitter<Task>()
// Emitted when card is clicked

@Output() deleteClicked = new EventEmitter<string>()
// Emitted when delete is clicked (taskId)
```

**Features**:
- Displays task title and priority
- Shows assigned contacts with avatar colors
- Displays due date
- Task type indicator
- Click to edit/preview
- Delete button (hover)

**Display Format**:
```
┌─────────────────────────┐
│ 🔴 High Priority        │
│ Design UI Mockups       │
│                         │
│ 👤 John 👤 Jane        │
│ Due: Jan 15, 2026      │
└─────────────────────────┘
```

**Key Methods**:
```typescript
// Get contact avatar color
getContactColor(contact: Contact): string

// Format due date
formatDueDate(date: Timestamp): string

// Handle card click
onCardClick(): void
```

---

### AddTask Component

Full-page task creation form.

**File**: `src/app/login/main-page/add-task/add-task.ts`

**Selector**: `<app-add-task></app-add-task>`

**Route**: `/add-task`

**Form Fields**:
- **Title** (required): Task title
- **Description**: Detailed description
- **Date**: Due date picker
- **Type**: UserStory or TechnicalTask
- **Priority**: Urgent (1), Medium (2), Low (3)
- **Contacts**: Assign to contacts
- **Subtasks**: Add multiple subtasks

**Key Methods**:
```typescript
// Submit form and create task
createTask(): Promise<void>

// Add empty subtask input
addSubtaskInput(): void

// Remove subtask from list
removeSubtask(index: number): void

// Validate form before submission
validateForm(): boolean

// Reset form to initial state
resetForm(): void
```

**Form Validation**:
```typescript
validators: {
  title: [required, minLength(3), maxLength(100)],
  description: [maxLength(1000)],
  date: [required],
  type: [required],
  priority: [required]
}
```

**Example**:
```typescript
// Form data structure
interface AddTaskForm {
  title: string
  description: string
  date: Timestamp
  type: TaskType
  priority: number
  assignedContacts: Contact[]
  subtasks: string[]
}
```

**Styling**: `add-task.scss`
- Form layout with spacing
- Input field styling
- Subtask section
- Submit button styling

---

### Contacts Component

Contact management with list and detail views.

**File**: `src/app/login/main-page/contacts/contacts.ts`

**Selector**: `<app-contacts></app-contacts>`

**Route**: `/contacts`

**Features**:
- List all contacts
- Add new contact
- View contact details
- Edit contact
- Delete contact
- Search/filter

**Subcomponents**:

#### ListContact
- Displays contact list
- Shows email and phone
- Add new contact button
- Click to view details

#### SingleContact
- Shows full contact details
- Edit form (inline or dialog)
- Delete confirmation
- Back to list button

**Key Methods**:
```typescript
// Load all contacts
loadContacts(): void

// Add new contact
addContact(contact: Contact): Promise<void>

// Update existing contact
updateContact(id: string, contact: Contact): Promise<void>

// Delete contact
deleteContact(id: string): Promise<void>

// Select contact to view
selectContact(id: string): void
```

**Properties**:
```typescript
contacts$ = this.firebase.subContactsList()
// Observable of all contacts

selectedContactId = signal<string | null>(null)
// Currently selected contact

editMode = signal<boolean>(false)
// Is in edit mode
```

**Contact Fields**:
```typescript
interface Contact {
  id?: string
  name: string
  email: string
  phone: string
  color: string
  isUser: boolean
}
```

---

### Summary Component (Dashboard)

Overview dashboard with task statistics.

**File**: `src/app/login/main-page/summary/summary.ts`

**Selector**: `<app-summary></app-summary>`

**Route**: `/summary`

**Displays**:
- Total tasks count
- Tasks by status (pie chart)
- Tasks by priority
- Upcoming due dates
- Assigned to me count
- Team members list

**Key Methods**:
```typescript
// Calculate task statistics
calculateStats(): TaskStats

// Get tasks due within X days
getUpcomingTasks(days: number): Task[]

// Get tasks by status
getTasksByStatus(status: TaskStatus): Task[]

// Format statistics for display
formatStats(stats: TaskStats): void
```

**Statistics Calculated**:
```typescript
interface TaskStats {
  totalTasks: number
  todoCount: number
  inProgressCount: number
  awaitFeedbackCount: number
  doneCount: number
  urgentCount: number
  mediumCount: number
  lowCount: number
}
```

**Styling**: `summary.scss` + `summary-media.scss`
- Statistics card layout
- Responsive grid
- Chart styling
- Mobile optimizations

---

## Shared Components

### Header Component

Top navigation bar with user menu.

**File**: `src/app/shared/header/header.ts`

**Selector**: `<app-header></app-header>`

**Features**:
- Application logo/title
- User profile menu
- Logout button
- Mobile menu toggle button

**Key Methods**:
```typescript
// Handle logout
logout(): void

// Toggle user menu
toggleUserMenu(): void

// Get current user name
getUserName(): string

// Get user initials for avatar
getUserInitials(): string
```

**Properties**:
```typescript
currentUser$ = this.auth.currentUser$
// Current user information

isMenuOpen = signal<boolean>(false)
// User menu open state
```

---

### Navbar Component

Side navigation menu.

**File**: `src/app/shared/navbar/navbar.ts`

**Selector**: `<app-navbar></app-navbar>`

**Navigation Links**:
- Dashboard (Summary)
- Board (Kanban)
- Add Task
- Contacts
- Helper
- Privacy Policy
- Legal Notice

**Key Methods**:
```typescript
// Handle navigation link click
navigateTo(route: string): void

// Check if route is active
isRouteActive(route: string): boolean

// Toggle mobile navbar
toggleMobileNav(): void

// Handle logout
logout(): void
```

**Properties**:
```typescript
currentRoute = signal<string>('')
// Currently active route

isMobileOpen = signal<boolean>(false)
// Mobile navbar open state
```

**Responsive Behavior**:
- Desktop: Always visible sidebar
- Mobile: Toggle button shows/hides
- Closes on route navigation

---

### Dialog Component

Generic modal dialog for confirmations and user input.

**File**: `src/app/shared/dialog/dialog.ts`

**Selector**: `<app-dialog></app-dialog>`

**Inputs**:
```typescript
@Input() title: string = ''
@Input() message: string = ''
@Input() confirmText: string = 'OK'
@Input() cancelText: string = 'Cancel'
@Input() type: 'confirm' | 'alert' | 'input' = 'alert'
```

**Outputs**:
```typescript
@Output() confirm = new EventEmitter<string>()
@Output() cancel = new EventEmitter<void>()
```

**Usage Examples**:

```typescript
// Delete confirmation
openDialog({
  title: 'Delete Task?',
  message: 'This cannot be undone',
  type: 'confirm'
})
.pipe(takeUntilDestroyed(this.destroyRef))
.subscribe(confirmed => {
  if (confirmed) this.deleteTask(taskId)
})

// User input
openDialog({
  title: 'Enter Task Title',
  type: 'input'
})
.subscribe(input => this.createTask(input))
```

---

### FilterTaskPipe

Custom pipe for filtering tasks by search term.

**File**: `src/app/shared/pipes/filter-Task-pipe.ts`

**Name**: `filterTask`

**Usage**:
```html
<app-task-preview 
  *ngFor="let task of tasks | filterTask:searchTerm">
</app-task-preview>
```

**Implementation**:
```typescript
@Pipe({
  name: 'filterTask',
  pure: true,
  standalone: true
})
export class FilterTaskPipe implements PipeTransform {
  transform(tasks: Task[], searchTerm: string): Task[] {
    // Filters tasks by title and description
    // Case-insensitive matching
  }
}
```

---

## Component Patterns

### Smart Component Pattern

```typescript
@Component({
  selector: 'app-board',
  standalone: true,
  imports: [CommonModule, DragDropModule, TaskPreviewComponent]
})
export class BoardComponent implements OnInit {
  private firebase = inject(FirebaseServices)
  private router = inject(Router)

  tasks$ = this.firebase.subTasks()

  ngOnInit(): void {
    // Load data on init
  }
}
```

### Input/Output Pattern

```typescript
@Component({
  selector: 'app-task-preview'
})
export class TaskPreviewComponent {
  @Input() task!: Task
  @Output() taskClicked = new EventEmitter<Task>()

  onCardClick() {
    this.taskClicked.emit(this.task)
  }
}
```

### Reactive Pattern

```typescript
export class ContactsComponent {
  contacts$ = this.firebase.subContactsList()

  selectedId = signal<string | null>(null)
  readonly selectedContact$ = computed(() =>
    this.firebase.subSingleContact(this.selectedId())
  )
}
```

---

## Best Practices

### 1. Component Naming
- Use descriptive names
- Suffix with "Component"
- Match file name
- Example: `TaskPreviewComponent` in `task-preview.ts`

### 2. Standalone Components
- All components are standalone
- Import dependencies explicitly
- Improves tree-shaking
- Better code splitting

### 3. Change Detection
- Use `OnPush` strategy
- Update via Signals
- Minimal dependency checks
- Better performance

### 4. Unsubscription
- Use `takeUntilDestroyed()`
- Prevents memory leaks
- Automatic cleanup
- Simpler than manual unsubscribe

### 5. Template Best Practices
- Use `trackBy` with *ngFor
- Use `async` pipe
- Avoid logic in templates
- Reactive forms over template-driven

---

**Related Documentation**:
- [API Reference](./03-API.md) - Service methods
- [Architecture](./02-ARCHITECTURE.md) - Component hierarchy
- [Database](./05-DATABASE.md) - Data models

---

**Last Updated**: January 15, 2026  
**Version**: 1.0
