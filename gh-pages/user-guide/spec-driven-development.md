---
layout: guide
title: Spec-Driven Development
---

# Spec-Driven Development

PrompTrek provides a complete spec-driven development workflow, inspired by GitHub's Spec-Kit methodology. This feature enables systematic software development through structured documentation artifacts - from project constitution to implementation feedback.

## Overview

Spec-driven development uses AI-assisted commands to create structured documentation artifacts that guide your software development process. PrompTrek implements eight specialized commands that work together to take you from project values to production code:

1. **Constitution** - Define project values and working agreements
2. **Specify** - Create structured problem specifications
3. **Plan** - Generate technical implementation plans
4. **Tasks** - Break plans into actionable checklists
5. **Implement** - Generate production-ready code
6. **Analyze** - Review consistency across artifacts
7. **History** - Track changes and evolution
8. **Feedback** - Provide structured PR reviews

All spec artifacts are stored in `promptrek/specs/` (committed to git for team sharing), except for the constitution which lives at `promptrek/constitution.md`.

## The Complete Workflow

### Step 1: Establish Project Constitution

The constitution defines your team's shared values, anti-patterns, and working agreements. This foundational document guides all subsequent development work.

**Command**: `/promptrek.spec.constitution`

**Arguments**: Optional context or scope

**What it creates**: `promptrek/constitution.md` (not tracked in specs registry)

**Example usage**:
```
/promptrek.spec.constitution
```

**Example output**:
```markdown
# Project Constitution

## Values
- Code quality over speed
- Comprehensive testing and documentation
- Clear communication and code reviews
- Iterative improvement and learning

## Anti-Patterns
- Skipping tests to meet deadlines
- Implementing without understanding requirements
- Copy-pasting code without comprehension
- Ignoring technical debt

## Working Agreements
- All code changes require peer review
- Test coverage must be maintained above 80%
- Documentation updated with code changes
- Weekly architecture review meetings
```

### Step 2: Create Feature Specification

Define what you're building with a structured specification that clarifies the problem, goals, non-goals, and assumptions.

**Command**: `/promptrek.spec.specify`

**Arguments**: `{{ topic }}` - Required. The feature or module name (e.g., "auth-flow", "payment-integration")

**What it creates**: `promptrek/specs/<topic>.spec.md` + registry entry

**Example usage**:
```
/promptrek.spec.specify user-authentication
```

**Example output**:
```markdown
# User Authentication

## Title
OAuth 2.0 Authentication Flow

## Problem
Users need a secure way to authenticate with the application using third-party identity providers (Google, GitHub) without exposing credentials to our system.

## Goals
- Implement OAuth 2.0 authorization code flow
- Support Google and GitHub as identity providers
- Secure token storage and refresh mechanisms
- Smooth user experience during authentication
- Comprehensive audit logging

## Non-Goals
- Custom password-based authentication
- Social media integrations beyond auth
- Multi-factor authentication (future phase)
- Enterprise SSO/SAML (future consideration)

## Assumptions
- OAuth 2.0 libraries available for our stack
- Third-party provider APIs are stable
- Users have accounts with supported providers
- SSL/TLS certificates properly configured
```

**Registry entry** (in `promptrek/specs.yaml`):
```yaml
specs:
  - id: user-authentication
    title: "OAuth 2.0 Authentication Flow"
    path: promptrek/specs/user-authentication.spec.md
    source_command: /promptrek.spec.specify
    summary: "Secure third-party OAuth authentication"
    created: "2025-11-07T10:30:00"
```

### Step 3: Generate Implementation Plan

Create a detailed technical plan covering approach, technology stack, and implementation milestones.

**Command**: `/promptrek.spec.plan`

**Arguments**: `{{ topic }}` - Required. The feature name to plan (should match a spec)

**What it creates**: `promptrek/specs/<topic>.plan.md` + registry entry

**Example usage**:
```
/promptrek.spec.plan user-authentication
```

**Example output**:
```markdown
# User Authentication - Implementation Plan

## Approach
We'll implement a standard OAuth 2.0 authorization code flow with PKCE (Proof Key for Code Exchange) for enhanced security. The system will use a backend service to handle token exchange and validation, keeping sensitive credentials server-side.

### Architecture Overview
- Frontend: React components for login/redirect handling
- Backend: Express.js middleware for OAuth flow
- Storage: JWT tokens in httpOnly cookies
- Session: Redis for server-side session management

## Stack

### Frontend
- React 18+ with TypeScript
- React Router for redirect handling
- Axios for API calls
- @auth0/auth0-react for OAuth client logic

### Backend
- Node.js 18+ with Express
- Passport.js with OAuth strategies
- jsonwebtoken for JWT handling
- Redis for session storage
- PostgreSQL for user data

### Third-Party Services
- Google OAuth 2.0 API
- GitHub OAuth Apps API
- Redis Cloud for session store

## Milestones

### Phase 1: Core OAuth Infrastructure (Week 1-2)
- Set up OAuth client credentials for Google and GitHub
- Implement backend OAuth middleware with Passport.js
- Create JWT token generation and validation
- Set up Redis session store
- Database schema for user accounts

### Phase 2: Frontend Integration (Week 2-3)
- Login component with provider selection
- OAuth redirect and callback handling
- Token storage and automatic refresh
- Protected route wrapper components
- Loading states and error handling

### Phase 3: Security & Edge Cases (Week 3-4)
- PKCE implementation for mobile security
- CSRF token protection
- Rate limiting on auth endpoints
- Logout and session invalidation
- Comprehensive error messages

### Phase 4: Testing & Documentation (Week 4)
- Unit tests for all authentication flows
- Integration tests with mock OAuth providers
- End-to-end tests for complete user journeys
- API documentation for auth endpoints
- User documentation for supported providers
```

### Step 4: Break Down into Tasks

Convert the implementation plan into a concrete checklist of development tasks.

**Command**: `/promptrek.spec.tasks`

**Arguments**: `{{ topic }}` - Required. The feature name (should have a corresponding plan)

**What it creates**: `promptrek/specs/<topic>.tasks.md` + registry entry

**Example usage**:
```
/promptrek.spec.tasks user-authentication
```

**Example output**:
```markdown
# User Authentication - Implementation Tasks

## Phase 1: Core OAuth Infrastructure

- [ ] Register OAuth applications with Google Cloud Console
- [ ] Register OAuth application with GitHub
- [ ] Create environment configuration for OAuth credentials
- [ ] Install and configure Passport.js with OAuth strategies
- [ ] Implement Google OAuth strategy
- [ ] Implement GitHub OAuth strategy
- [ ] Create JWT token generation utility
- [ ] Create JWT token validation middleware
- [ ] Set up Redis connection and session store
- [ ] Create database migration for users table
- [ ] Implement user creation/update logic on OAuth callback

## Phase 2: Frontend Integration

- [ ] Create Login component with provider buttons
- [ ] Implement OAuth redirect to provider
- [ ] Create callback route handler
- [ ] Implement token storage in httpOnly cookies
- [ ] Create useAuth custom hook for auth state
- [ ] Implement automatic token refresh logic
- [ ] Create ProtectedRoute wrapper component
- [ ] Add loading spinner during auth flow
- [ ] Implement error boundary for auth failures
- [ ] Create logout functionality

## Phase 3: Security & Edge Cases

- [ ] Implement PKCE code challenge generation
- [ ] Add PKCE code verifier validation
- [ ] Generate and validate CSRF tokens
- [ ] Add rate limiting to /auth endpoints
- [ ] Implement session cleanup on logout
- [ ] Handle expired OAuth tokens gracefully
- [ ] Add user-friendly error messages
- [ ] Implement account linking for existing users

## Phase 4: Testing & Documentation

- [ ] Write unit tests for OAuth strategies
- [ ] Write unit tests for JWT utilities
- [ ] Create integration tests with mock OAuth servers
- [ ] Write E2E tests for Google OAuth flow
- [ ] Write E2E tests for GitHub OAuth flow
- [ ] Test token refresh mechanism
- [ ] Document OAuth callback URLs in README
- [ ] Create API documentation for auth endpoints
- [ ] Write user guide for authentication
```

### Step 5: Implement Features

Generate production-ready code based on your task list and plan.

**Command**: `/promptrek.spec.implement`

**Arguments**: `{{ topic }}` - Required. The specific task or module to implement

**Output Format**: `code` (code blocks only)

**Example usage**:
```
/promptrek.spec.implement JWT token generation utility
```

**Example output**:
```typescript
/**
 * JWT Token Generation and Validation Utilities
 *
 * Handles creation, verification, and refresh of JSON Web Tokens
 * for user authentication.
 */

import jwt from 'jsonwebtoken';
import { promisify } from 'util';

const signAsync = promisify(jwt.sign);
const verifyAsync = promisify(jwt.verify);

interface TokenPayload {
  userId: string;
  email: string;
  provider: 'google' | 'github';
}

interface RefreshTokenPayload {
  userId: string;
  tokenVersion: number;
}

const ACCESS_TOKEN_SECRET = process.env.ACCESS_TOKEN_SECRET!;
const REFRESH_TOKEN_SECRET = process.env.REFRESH_TOKEN_SECRET!;
const ACCESS_TOKEN_EXPIRY = '15m';
const REFRESH_TOKEN_EXPIRY = '7d';

/**
 * Generate access token for authenticated user
 *
 * @param payload User data to encode in token
 * @returns Signed JWT access token
 */
export async function generateAccessToken(
  payload: TokenPayload
): Promise<string> {
  return await signAsync(payload, ACCESS_TOKEN_SECRET, {
    expiresIn: ACCESS_TOKEN_EXPIRY,
    issuer: 'your-app-name',
    audience: 'your-app-api',
  });
}

/**
 * Generate refresh token for token rotation
 *
 * @param payload User ID and token version
 * @returns Signed JWT refresh token
 */
export async function generateRefreshToken(
  payload: RefreshTokenPayload
): Promise<string> {
  return await signAsync(payload, REFRESH_TOKEN_SECRET, {
    expiresIn: REFRESH_TOKEN_EXPIRY,
    issuer: 'your-app-name',
  });
}

/**
 * Verify and decode access token
 *
 * @param token JWT access token to verify
 * @returns Decoded token payload
 * @throws Error if token is invalid or expired
 */
export async function verifyAccessToken(
  token: string
): Promise<TokenPayload> {
  try {
    const decoded = await verifyAsync(token, ACCESS_TOKEN_SECRET, {
      issuer: 'your-app-name',
      audience: 'your-app-api',
    });
    return decoded as TokenPayload;
  } catch (error) {
    if (error instanceof jwt.TokenExpiredError) {
      throw new Error('Access token expired');
    }
    if (error instanceof jwt.JsonWebTokenError) {
      throw new Error('Invalid access token');
    }
    throw error;
  }
}

/**
 * Verify and decode refresh token
 *
 * @param token JWT refresh token to verify
 * @returns Decoded token payload
 * @throws Error if token is invalid or expired
 */
export async function verifyRefreshToken(
  token: string
): Promise<RefreshTokenPayload> {
  try {
    const decoded = await verifyAsync(token, REFRESH_TOKEN_SECRET, {
      issuer: 'your-app-name',
    });
    return decoded as RefreshTokenPayload;
  } catch (error) {
    if (error instanceof jwt.TokenExpiredError) {
      throw new Error('Refresh token expired');
    }
    if (error instanceof jwt.JsonWebTokenError) {
      throw new Error('Invalid refresh token');
    }
    throw error;
  }
}
```

### Step 6: Analyze Consistency

Review your spec artifacts for consistency, completeness, and potential issues.

**Command**: `/promptrek.spec.analyze`

**Arguments**: `{{ topic }}` - Optional. Specific spec chain to analyze (analyzes all if omitted)

**Example usage**:
```
/promptrek.spec.analyze user-authentication
```

**Example output**:
```markdown
# Consistency Analysis: User Authentication

## Issues Identified

### Missing Pieces
- **Plan**: No mention of password reset flow (spec implies OAuth-only, but users may still need email-based recovery)
- **Tasks**: Missing task for error logging implementation (mentioned in plan but not in checklist)
- **Plan**: Database schema details not specified (what fields in users table?)

### Contradictions
- **Spec vs Plan**: Spec says "no custom password authentication" but plan includes PostgreSQL for "user data" without clarifying if email/password is stored
- **Plan vs Tasks**: Plan mentions "comprehensive error messages" in Phase 3, but tasks don't include error message creation

### Unclear Terms
- **Plan**: "PKCE implementation for mobile security" - are we building a mobile app? Not mentioned in spec
- **Tasks**: "Account linking for existing users" - what does this mean? Not defined in spec or plan

## Suggested Fixes

### Spec Document (`user-authentication.spec.md`)
- Add explicit note about user data storage model (email, profile data from OAuth)
- Clarify if mobile app is in scope or future consideration
- Define what "account linking" means in context

### Plan Document (`user-authentication.plan.md`)
- Add database schema section with explicit table structure
- Remove mobile/PKCE reference or add mobile app to scope
- Add error logging to Architecture Overview

### Tasks Document (`user-authentication.tasks.md`)
- Add task: "Design and implement error logging strategy"
- Add task: "Define database schema for users table"
- Add task: "Create error message constants file"
- Clarify "account linking" task with specific acceptance criteria
```

### Step 7: Track History

Summarize the evolution and changes across your spec documents.

**Command**: `/promptrek.spec.history`

**Arguments**: `{{ topic }}` - Optional. Limit summary to specific spec

**Example usage**:
```
/promptrek.spec.history user-authentication
```

**Example output**:
```markdown
# Spec History: User Authentication

## 2025-11-07 - Initial Specification Created
- **Files**: `user-authentication.spec.md`
- **Changes**: Created initial OAuth 2.0 authentication specification
- **Summary**: Defined problem, goals, non-goals, and assumptions for third-party auth integration

## 2025-11-08 - Implementation Plan Added
- **Files**: `user-authentication.plan.md`
- **Changes**: Added technical implementation plan with 4-phase approach
- **Summary**: Detailed architecture using React, Express, Passport.js, Redis, and PostgreSQL

## 2025-11-08 - Task Breakdown Created
- **Files**: `user-authentication.tasks.md`
- **Changes**: Converted plan into 35+ actionable development tasks
- **Summary**: Organized tasks across 4 phases matching plan milestones

## 2025-11-09 - Spec Updated After Analysis
- **Files**: `user-authentication.spec.md`
- **Changes**:
  - Added clarification about user data storage model
  - Added assumption about email storage for notifications
  - Updated non-goals to explicitly exclude mobile apps (current phase)
- **Summary**: Addressed consistency issues identified in analysis

## 2025-11-09 - Plan Updated for Database Schema
- **Files**: `user-authentication.plan.md`
- **Changes**:
  - Added explicit database schema section
  - Removed PKCE/mobile references
  - Added error logging to architecture
- **Summary**: Aligned plan with spec scope and filled in missing details

## 2025-11-10 - Tasks Updated
- **Files**: `user-authentication.tasks.md`
- **Changes**:
  - Added 3 new tasks for error logging, schema design, and error messages
  - Clarified "account linking" task with acceptance criteria
  - Reordered Phase 1 tasks for logical dependency flow
- **Summary**: Incorporated analysis feedback into task list
```

### Step 8: Provide PR Feedback

Generate structured feedback for code reviews or spec diffs.

**Command**: `/promptrek.spec.feedback`

**Arguments**: `{{ topic }}` - Required. File or diff description

**Example usage**:
```
/promptrek.spec.feedback JWT token implementation PR
```

**Example output**:
```markdown
# PR Feedback: JWT Token Implementation

## Summary
The JWT token implementation provides a solid foundation for authentication with proper TypeScript types, error handling, and async/await patterns. Security considerations are well-addressed with separate access and refresh tokens.

## Suggestions

### High Priority
- **Security**: Hard-coded token secrets should be validated at startup
  - Add runtime check: `if (!ACCESS_TOKEN_SECRET) throw new Error('ACCESS_TOKEN_SECRET not configured')`
  - Prevents silent failures in production

- **Error Handling**: Token verification errors should be more specific
  - Currently throws generic "Invalid token" for all JWT errors
  - Differentiate between expired, malformed, and invalid signature
  - Helps with debugging and user experience

### Medium Priority
- **Type Safety**: Consider making environment variables type-safe
  - Use a config validation library like `envalid` or `zod`
  - Ensures all required env vars are present and valid at startup

- **Testing**: Add unit tests for edge cases
  - Test with malformed tokens
  - Test with tokens signed with wrong secret
  - Test with tokens from wrong issuer
  - Verify token expiry is enforced

### Low Priority
- **Documentation**: Add JSDoc examples for each function
  - Show sample usage in comments
  - Makes API clearer for other developers

- **Code Organization**: Consider extracting constants to config file
  - `ACCESS_TOKEN_EXPIRY`, `REFRESH_TOKEN_EXPIRY`, etc.
  - Makes configuration changes easier
  - Could allow different expiry times per environment

## Priority Ranking
1. **High**: Security validation and error differentiation (must have)
2. **Medium**: Type-safe config and comprehensive tests (should have)
3. **Low**: Enhanced documentation and config extraction (nice to have)

## Approval Recommendation
✅ **Approve with requested changes**

The implementation is solid but needs the high-priority security validations before merging. Medium and low priority items can be follow-up tasks.
```

## Argument Template Syntax

All spec commands support argument templates using the `{{ topic }}` syntax. This allows you to pass dynamic values to the AI prompts.

### Basic Usage

When you invoke a command with arguments, the `{{ topic }}` placeholder in the prompt is replaced with your provided value:

```
/promptrek.spec.specify payment-gateway
```

The AI receives:
```
You are writing a structured software specification for the feature "payment-gateway".
```

### Optional Arguments

Some commands have optional `{{ topic }}` arguments (like `analyze` and `history`):

```
/promptrek.spec.analyze             # Analyzes all specs
/promptrek.spec.analyze auth-flow   # Analyzes only auth-flow specs
```

## File Storage and Organization

### Spec Documents Location

All spec artifacts are stored in `promptrek/specs/` and committed to git for team collaboration:

```
promptrek/
├── specs/
│   ├── user-authentication.spec.md      # Specification
│   ├── user-authentication.plan.md      # Implementation plan
│   ├── user-authentication.tasks.md     # Task breakdown
│   ├── payment-gateway.spec.md
│   ├── payment-gateway.plan.md
│   └── ...
├── specs.yaml                            # Registry of all specs
└── constitution.md                       # Project constitution (not in registry)
```

### The Specs Registry

The `promptrek/specs.yaml` file maintains a registry of all spec documents (excluding the constitution):

```yaml
specs:
  - id: user-authentication
    title: "OAuth 2.0 Authentication Flow"
    path: promptrek/specs/user-authentication.spec.md
    source_command: /promptrek.spec.specify
    summary: "Secure third-party OAuth authentication"
    created: "2025-11-07T10:30:00Z"

  - id: user-authentication-plan
    title: "OAuth 2.0 Authentication Flow - Plan"
    path: promptrek/specs/user-authentication.plan.md
    source_command: /promptrek.spec.plan
    summary: "Technical implementation plan"
    created: "2025-11-08T09:15:00Z"
```

The registry provides:
- Quick lookup of all spec artifacts
- Metadata about each document
- Traceability of which command created each file
- Timestamps for change tracking

### Constitution Document

The constitution is special and stored at `promptrek/constitution.md` (not in the specs registry). It represents project-wide values that transcend individual features.

## CLI Integration

### Spec Management Commands

PrompTrek provides CLI commands for managing your specs:

```bash
# List all specs in the registry
promptrek list-specs

# Export a spec to markdown
promptrek spec export user-authentication
```

### Command Injection

Spec commands are automatically injected into your AI editor when you run:

```bash
promptrek generate project.promptrek.yaml --editor claude
```

This creates command files in `.claude/commands/`:
- `promptrek.spec.constitution.md`
- `promptrek.spec.specify.md`
- `promptrek.spec.plan.md`
- `promptrek.spec.tasks.md`
- `promptrek.spec.implement.md`
- `promptrek.spec.analyze.md`
- `promptrek.spec.history.md`
- `promptrek.spec.feedback.md`

## Command Reference

| Command | Purpose | Arguments | Output Location | Registry |
|---------|---------|-----------|-----------------|----------|
| `/promptrek.spec.constitution` | Define project values | Optional context | `promptrek/constitution.md` | Not tracked |
| `/promptrek.spec.specify` | Create specification | `{{ topic }}` (required) | `promptrek/specs/<topic>.spec.md` | ✓ |
| `/promptrek.spec.plan` | Generate implementation plan | `{{ topic }}` (required) | `promptrek/specs/<topic>.plan.md` | ✓ |
| `/promptrek.spec.tasks` | Break down into tasks | `{{ topic }}` (required) | `promptrek/specs/<topic>.tasks.md` | ✓ |
| `/promptrek.spec.implement` | Generate production code | `{{ topic }}` (required) | Code blocks only | - |
| `/promptrek.spec.analyze` | Review consistency | `{{ topic }}` (optional) | Analysis output | - |
| `/promptrek.spec.history` | Track changes | `{{ topic }}` (optional) | History summary | - |
| `/promptrek.spec.feedback` | PR review feedback | `{{ topic }}` (required) | Feedback report | - |

## Best Practices

### 1. Start with Constitution

Always establish your project constitution before creating specs. This ensures consistency in values and approach across all features.

### 2. Follow the Natural Flow

The commands are designed to follow a logical progression:
1. Constitution (once per project)
2. Specify (per feature)
3. Plan (per feature)
4. Tasks (per feature)
5. Implement (per task)
6. Analyze (as needed)
7. History (periodically)
8. Feedback (during reviews)

### 3. Use Consistent Naming

Use the same `{{ topic }}` value across related commands:
```
/promptrek.spec.specify user-auth
/promptrek.spec.plan user-auth
/promptrek.spec.tasks user-auth
```

This creates a coherent set of artifacts that are easy to track.

### 4. Analyze Regularly

Run `/promptrek.spec.analyze` after completing each phase to catch inconsistencies early. It's easier to fix alignment issues before implementation begins.

### 5. Update History After Major Changes

When you modify specs, plans, or tasks, use `/promptrek.spec.history` to document what changed and why. This creates an audit trail for future reference.

### 6. Commit Everything

All files in `promptrek/specs/` and the `constitution.md` should be committed to version control. This enables:
- Team collaboration on specs
- Historical tracking of decisions
- Onboarding documentation for new team members

### 7. Review Before Implementation

Before running `/promptrek.spec.implement`, ensure your spec, plan, and tasks are aligned. Use `/promptrek.spec.analyze` to verify consistency.

## Editor Support

The spec-driven development commands are available in all PrompTrek-supported editors:

- ✅ **Claude Code** - Full support with slash commands
- ✅ **GitHub Copilot** - Commands via instruction files
- ✅ **Cursor** - Commands in `.cursor/rules/`
- ✅ **Continue** - Commands in `.continue/prompts/`
- ✅ **Windsurf** - Commands in `.windsurf/rules/`
- ✅ **Kiro** - Commands in steering documents
- ✅ **Cline** - Commands in `.clinerules/`
- ✅ **Amazon Q** - Commands in `.amazonq/prompts/`
- ✅ **JetBrains AI** - Commands in `.assistant/rules/`

Simply generate for your editor and the commands will be available in your AI assistant.

## Migration from .promptrek/specs/ (For Users Upgrading from v0.5.x or Earlier)

**If you have existing specs in `.promptrek/specs/` from PrompTrek v0.5.x or earlier**, you need to migrate them to `promptrek/specs/`:

```bash
# Create new directory
mkdir -p promptrek/specs

# Move spec files
mv .promptrek/specs/*.md promptrek/specs/

# Move registry
mv .promptrek/specs.yaml promptrek/specs.yaml

# Regenerate editor files
promptrek generate project.promptrek.yaml --all
```

The new location ensures your specs are:
- ✅ Committed to git (team-shared, not gitignored)
- ✅ Visible to all team members
- ✅ Part of your project's documentation
- ✅ Tracked through version control

## Examples and Templates

### Example: Complete Feature Workflow

Here's a complete example of developing a notification system:

```bash
# 1. Start with constitution (if not already done)
/promptrek.spec.constitution

# 2. Create specification
/promptrek.spec.specify notification-system

# 3. Generate implementation plan
/promptrek.spec.plan notification-system

# 4. Break down into tasks
/promptrek.spec.tasks notification-system

# 5. Check consistency before coding
/promptrek.spec.analyze notification-system

# 6. Implement individual components
/promptrek.spec.implement email notification service
/promptrek.spec.implement push notification handler
/promptrek.spec.implement notification preferences UI

# 7. Track changes
/promptrek.spec.history notification-system

# 8. Review implementation
/promptrek.spec.feedback notification system PR #42
```

### Template: Basic Spec Structure

When creating a spec, follow this structure:

```markdown
# [Feature Name]

## Title
Clear, concise title (1 line)

## Problem
What problem does this solve? (2-3 paragraphs)

## Goals
- Specific, measurable outcome 1
- Specific, measurable outcome 2
- ...

## Non-Goals
- Explicitly out of scope item 1
- Explicitly out of scope item 2
- ...

## Assumptions
- Precondition or requirement 1
- Precondition or requirement 2
- ...
```

### Template: Implementation Plan Structure

Plans should follow this format:

```markdown
# [Feature Name] - Implementation Plan

## Approach
High-level strategy and architecture overview (2-3 paragraphs)

### Architecture Overview
- Component 1: Purpose and responsibilities
- Component 2: Purpose and responsibilities

## Stack

### Frontend
- Technology 1: Use case
- Technology 2: Use case

### Backend
- Technology 1: Use case
- Technology 2: Use case

### Infrastructure/Services
- Service 1: Use case
- Service 2: Use case

## Milestones

### Phase 1: [Name] (Timeline)
- Deliverable 1
- Deliverable 2

### Phase 2: [Name] (Timeline)
- Deliverable 1
- Deliverable 2
```

## Troubleshooting

### Commands Not Appearing in Editor

**Problem**: Spec commands don't show up in your AI editor

**Solution**: Regenerate editor configurations:
```bash
promptrek generate project.promptrek.yaml --editor <your-editor>
```

### Registry Out of Sync

**Problem**: `specs.yaml` doesn't reflect actual files

**Solution**: Use the sync command:
```bash
promptrek specs sync
```

### Constitution vs Spec Confusion

**Problem**: Unsure whether to use constitution or spec for project-wide guidelines

**Guideline**:
- **Constitution**: Timeless values, anti-patterns, working agreements (rarely changes)
- **Spec**: Feature-specific requirements and implementation details (changes per feature)

## Related Features

### Variable Substitution

Combine spec commands with PrompTrek's variable system for dynamic content:

```yaml
# project.promptrek.yaml
schema_version: "3.1.0"
content: |
  Use specs from promptrek/specs/ directory.
  Current sprint: {{{ SPRINT_NUMBER }}}

variables:
  SPRINT_NUMBER:
    type: command
    value: cat .current-sprint
```

### Multi-Document Support

Create separate instruction files for different spec workflows:

```yaml
# project.promptrek.yaml
schema_version: "3.1.0"
documents:
  - path: spec-workflow.md
    content: |
      Follow the spec-driven workflow:
      1. Constitution
      2. Specify
      3. Plan
      4. Tasks
      5. Implement

  - path: review-workflow.md
    content: |
      For PR reviews:
      1. Run /promptrek.spec.analyze
      2. Run /promptrek.spec.feedback
      3. Update specs if needed
```

---

Ready to start building with specs? Try creating your first constitution and specification! 🚀
