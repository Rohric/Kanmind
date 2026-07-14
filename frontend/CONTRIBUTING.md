# Contributing to Join

Guidelines for contributing to the Join project, including development workflow, code standards, and pull request process.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Code Style Guide](#code-style-guide)
5. [Commit Messages](#commit-messages)
6. [Pull Requests](#pull-requests)
7. [Testing Requirements](#testing-requirements)
8. [Documentation](#documentation)

---

## Code of Conduct

### Expected Behavior

- **Respectful**: Treat everyone with respect and professionalism
- **Inclusive**: Welcome diverse perspectives and backgrounds
- **Constructive**: Provide helpful feedback and suggestions
- **Collaborative**: Work together toward common goals

### Unacceptable Behavior

- Harassment, discrimination, or offensive language
- Insulting or demeaning comments
- Spam or low-effort contributions
- Deliberate disruption of discussions

---

## Getting Started

### Prerequisites

- Node.js v18+ (LTS)
- npm v9+ or yarn
- Git
- Firebase account
- VS Code (recommended)

### Setup Development Environment

```bash
# 1. Fork the repository
# Click Fork on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/join.git
cd join

# 3. Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/join.git

# 4. Install dependencies
npm install

# 5. Create feature branch
git checkout -b feature/your-feature-name

# 6. Start dev server
npm start
```

---

## Development Workflow

### Branch Naming Convention

```
feature/feature-name              # New features
bugfix/bug-description            # Bug fixes
docs/documentation-topic          # Documentation
refactor/refactor-description     # Code refactoring
test/test-description             # Test additions
chore/maintenance-task            # Maintenance
```

**Examples**:
```
feature/kanban-drag-drop          ✓ Good
bugfix/auth-timeout-error         ✓ Good
docs/api-reference-update         ✓ Good

new-feature                        ✗ Too vague
fixbug                            ✗ Unclear
update                            ✗ Not descriptive
```

### Commit Workflow

```bash
# 1. Make changes to files
# Edit src/app/board/board.ts

# 2. Stage changes
git add src/app/board/board.ts
# or stage all
git add .

# 3. Commit with descriptive message
git commit -m "feat: add task drag-drop functionality"

# 4. Keep branch up-to-date
git fetch upstream
git rebase upstream/main

# 5. Push to your fork
git push origin feature/your-feature-name
```

---

## Code Style Guide

### TypeScript Standards

#### File Structure

```typescript
// 1. Imports (grouped and sorted)
import { Component, Input, Output } from '@angular/core'
import { CommonModule } from '@angular/common'
import { FormsModule } from '@angular/forms'

// 2. Component decorator
@Component({
  selector: 'app-task-preview',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './task-preview.html',
  styleUrls: ['./task-preview.scss']
})

// 3. Export class
export class TaskPreviewComponent {
  // ...
}
```

#### Naming Conventions

```typescript
// Classes: PascalCase
export class TaskBoard { }
export class UserService { }

// Functions: camelCase
function calculateTotal() { }
const formatDate = () => { }

// Constants: UPPER_SNAKE_CASE
const MAX_TASKS = 100
const DEFAULT_PRIORITY = 2

// Private: underscore prefix (or private keyword)
private _internalState: any
private internalState: any

// Boolean: is/has prefix
isValid: boolean
hasError: boolean
canDelete: boolean

// Observables: $ suffix
tasks$: Observable<Task[]>
user$: Observable<User>
```

#### Type Annotations

```typescript
// Always use types/interfaces
interface Task {
  id: string
  title: string
  priority: number
}

// Avoid any type
let data: any              // ✗ Bad
let data: Task             // ✓ Good

// Use explicit return types
function process(): Task[] {  // ✓ Good
  return []
}

function process() {          // ✗ Bad (return type inferred)
  return []
}
```

#### Method Organization

```typescript
export class TaskService {
  // 1. Static properties
  static readonly DEFAULT_PRIORITY = 1

  // 2. Properties
  tasks: Task[] = []

  // 3. Signals
  selectedId = signal<string | null>(null)

  // 4. Constructor
  constructor(private firebase: FirebaseServices) {}

  // 5. Lifecycle hooks
  ngOnInit() {}

  // 6. Public methods
  addTask(task: Task): Promise<void> { }

  // 7. Private methods
  private validate(task: Task): boolean { }
}
```

### Component Standards

#### Template (HTML)

```html
<!-- 1. Keep lines under 80 characters -->
<div class="task-container">
  <!-- 2. Use meaningful class names -->
  <div class="task-header">
    <!-- 3. Use proper Angular binding syntax -->
    <h2>{{ task.title }}</h2>
    
    <!-- 4. Use *ngIf instead of CSS display:none -->
    <button *ngIf="canEdit" (click)="edit()">Edit</button>
    
    <!-- 5. Always use trackBy with *ngFor -->
    <app-subtask
      *ngFor="let subtask of subtasks; trackBy: trackBySubtaskId"
      [subtask]="subtask">
    </app-subtask>
  </div>
</div>
```

#### Styling (SCSS)

```scss
// 1. Use BEM methodology
.task {
  &__header {
    display: flex;
  }
  
  &__title {
    font-weight: 600;
  }
}

// 2. Keep selectors specific but not too deep
.task__title { }        // ✓ Good
.container > div > p { } // ✗ Too specific

// 3. Use variables for consistency
$primary-color: #3f51b5;
$spacing-unit: 8px;

// 4. Responsive design
@media (max-width: 768px) {
  .task {
    flex-direction: column;
  }
}

// 5. Use nested selectors
.task {
  &:hover {
    background: lighten($primary-color, 5%);
  }
}
```

---

## Commit Messages

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type

```
feat:     New feature
fix:      Bug fix
docs:     Documentation
style:    Formatting, missing semicolons, etc.
refactor: Code refactoring
test:     Adding or updating tests
chore:    Maintenance, dependencies
```

### Examples

**Good**:
```
feat(board): add drag-drop between columns

Implement CDK drag-drop to allow moving tasks between status columns.
Includes validation and real-time database updates.

Closes #123
```

**Good**:
```
fix(auth): resolve login timeout issue

The login request was timing out after 5 seconds.
Increased timeout to 30 seconds and added retry logic.

Fixes #456
```

**Bad**:
```
fixed stuff
Updated files
working version
```

### Guidelines

- Use imperative mood: "add" not "added"
- Limit subject to 50 characters
- Capitalize first letter
- No period at end of subject
- Wrap body at 72 characters
- Separate subject and body with blank line

---

## Pull Requests

### Creating a Pull Request

```bash
# 1. Push your branch
git push origin feature/your-feature

# 2. Go to GitHub
# Click "Compare & pull request"

# 3. Fill in template
# See below for template details
```

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Documentation update
- [ ] Refactoring

## Related Issue
Closes #123

## Testing Done
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

Describe manual testing:
1. ...
2. ...

## Screenshots (if applicable)
[Paste screenshots]

## Checklist
- [ ] Code follows style guide
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added/updated
```

### Review Process

**What reviewers look for**:
- Code quality and style adherence
- Functionality correctness
- Test coverage
- Documentation completeness
- Performance implications
- Security concerns

**Your responsibilities**:
- Respond to all feedback
- Make requested changes promptly
- Don't force merge (wait for approval)
- Keep PR focused and manageable

**Timeline**:
- Response to feedback: 48 hours
- Review completion: 3-5 business days

---

## Testing Requirements

### Unit Tests Required

- Service methods (100% coverage)
- Component logic (80% coverage)
- Utility functions (100% coverage)
- Critical paths (100% coverage)

### Test File Requirements

```bash
# Create test file alongside component
src/app/board/board.ts
src/app/board/board.spec.ts

# Naming convention
*.spec.ts     # Unit tests
*.e2e.ts      # E2E tests (if applicable)
```

### Running Tests

```bash
# Run all tests
npm test -- --watch=false

# Run specific test file
npm test -- --include='**/board.spec.ts'

# Generate coverage report
npm test -- --code-coverage

# Minimum coverage: 80%
```

---

## Documentation

### Code Comments

```typescript
// Use comments for "why", not "what"
// ✗ Bad
const total = sum + tax;  // Add tax to sum

// ✓ Good
// Apply sales tax for CA residents only
if (state === 'CA') {
  const total = sum + (sum * 0.0625);
}
```

### JSDoc for Public Methods

```typescript
/**
 * Creates a new task in Firestore
 * 
 * @param task - The task data to save
 * @returns Promise that resolves with the new task ID
 * @throws FirebaseError if write fails
 * 
 * @example
 * const taskId = await addTask({
 *   title: 'New Task',
 *   priority: 1
 * })
 */
async addTask(task: Task): Promise<string> {
  // ...
}
```

### Update Documentation When

- Adding new features
- Changing API
- Fixing bugs (if affects usage)
- Adding configuration options
- Updating dependencies

### Documentation Files

- **README.md**: Project overview
- **docs/**: Feature documentation
- **Code comments**: Implementation details
- **CHANGELOG.md**: Version history

---

## PR Checklist

Before submitting a PR, ensure:

- [ ] Branch is created from `main`
- [ ] Branch name follows convention
- [ ] Code follows style guide
- [ ] All tests pass: `npm test`
- [ ] Code coverage adequate: `npm test -- --code-coverage`
- [ ] No console errors/warnings
- [ ] Commit messages are descriptive
- [ ] PR description is clear
- [ ] Related issues referenced
- [ ] No merge conflicts
- [ ] Documentation updated
- [ ] Screenshots/demos included (if UI change)

---

## Questions?

- Check existing [Issues](../../issues)
- Review [Discussions](../../discussions)
- Read [Documentation](../docs/)
- Contact maintainers

---

**Thank you for contributing to Join!** 🎉

---

**Last Updated**: January 15, 2026  
**Version**: 1.0
