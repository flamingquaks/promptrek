# Node.js API Example

This example demonstrates how to configure PrompTrek for a Node.js REST API project using TypeScript, Express, and modern backend practices.

## Overview

**Use Case:** Production-ready Node.js REST API with TypeScript, Express, PostgreSQL, and JWT authentication

**What You'll Learn:**
- Configuring PrompTrek for backend projects
- Setting up API-specific guidelines
- Security and validation best practices
- Database and authentication patterns

## Complete Configuration

```yaml
# yaml-language-server: $schema=https://promptrek.ai/schema/v3.1.0.json
schema_version: "3.1.0"
metadata:
  title: Node.js REST API
  description: AI coding assistant configuration for Node.js REST API projects
  version: 1.0.0
  author: PrompTrek
  tags:
    - nodejs
    - typescript
    - api
    - backend

content: |
  # Node.js REST API Development Guide

  ## Project Overview
  This is a Node.js REST API built with TypeScript and modern best practices.

  **Tech Stack:**
  - Node.js 20+ with TypeScript
  - Express.js for routing
  - PostgreSQL with Prisma ORM
  - JWT for authentication
  - Zod for validation

  ## Code Style Guidelines

  ### API Structure
  - Use RESTful conventions (GET, POST, PUT, DELETE)
  - Return consistent response formats
  - Use proper HTTP status codes
  - Implement versioning (e.g., /api/v1/)

  ### TypeScript Best Practices
  - Enable strict mode
  - Define request/response types
  - Use interfaces for data models
  - Avoid `any` - use `unknown` or proper types

  ### File Organization
  ```
  src/
    routes/         # API route handlers
    controllers/    # Business logic
    services/       # External service integrations
    models/         # Database models
    middleware/     # Express middleware
    utils/          # Utility functions
    types/          # TypeScript type definitions
  ```

  ## Route Handler Example

  ```typescript
  // routes/users.ts
  import { Router } from 'express';
  import { createUser, getUser } from '../controllers/users';
  import { authenticate } from '../middleware/auth';
  import { validateRequest } from '../middleware/validation';
  import { createUserSchema } from '../schemas/user';

  const router = Router();

  router.post(
    '/users',
    authenticate,
    validateRequest(createUserSchema),
    createUser
  );

  router.get('/users/:id', authenticate, getUser);

  export default router;
  ```

  ## Controller Example

  ```typescript
  // controllers/users.ts
  import { Request, Response } from 'express';
  import { UserService } from '../services/user';
  import { CreateUserInput } from '../types/user';

  export async function createUser(req: Request, res: Response) {
    try {
      const input: CreateUserInput = req.body;
      const user = await UserService.create(input);

      res.status(201).json({
        success: true,
        data: user,
      });
    } catch (error) {
      res.status(400).json({
        success: false,
        error: error.message,
      });
    }
  }
  ```

  ## Validation Example

  ```typescript
  // schemas/user.ts
  import { z } from 'zod';

  export const createUserSchema = z.object({
    body: z.object({
      email: z.string().email(),
      name: z.string().min(2).max(100),
      password: z.string().min(8),
    }),
  });

  export type CreateUserInput = z.infer<typeof createUserSchema>['body'];
  ```

  ## Error Handling
  - Use centralized error handling middleware
  - Return consistent error response format
  - Log errors with appropriate severity levels
  - Never expose sensitive information in error messages

  ## Security
  - Validate all user inputs with Zod
  - Use parameterized queries to prevent SQL injection
  - Implement rate limiting for API endpoints
  - Use CORS properly for frontend access
  - Hash passwords with bcrypt (min 10 rounds)
  - Use JWT tokens with short expiration times

  ## Testing
  - Use Jest for unit and integration tests
  - Use Supertest for API endpoint testing
  - Mock external dependencies
  - Test error scenarios and edge cases
  - Aim for >80% code coverage

  ## Performance
  - Use connection pooling for database
  - Implement caching where appropriate (Redis)
  - Add database indexes for frequently queried fields
  - Use pagination for list endpoints
  - Monitor response times and optimize slow queries

variables:
  DATABASE_URL: postgresql://localhost:5432/mydb
  JWT_SECRET: your-secret-key
  PORT: "3000"
```

## Configuration Breakdown

### API Guidelines

The configuration focuses on backend-specific concerns:

1. **RESTful Design** - Proper HTTP methods and status codes
2. **Type Safety** - TypeScript for all components
3. **Validation** - Input validation with Zod
4. **Security** - Authentication, authorization, and data protection
5. **Error Handling** - Consistent error responses
6. **Performance** - Database optimization and caching

### Variables for Environment

```yaml
variables:
  DATABASE_URL: postgresql://localhost:5432/mydb
  JWT_SECRET: your-secret-key
  PORT: "3000"
```

**Best Practice:** Use environment variables for:
- Database connection strings
- API keys and secrets
- Port numbers
- Feature flags

**Override for different environments:**

```bash
# Development
promptrek generate api-config.promptrek.yaml --editor cursor \
  -V DATABASE_URL=postgresql://localhost:5432/dev_db

# Production
promptrek generate api-config.promptrek.yaml --editor cursor \
  -V DATABASE_URL=postgresql://prod-db:5432/prod_db \
  -V JWT_SECRET=super-secret-production-key
```

## Usage Instructions

### Step 1: Create Configuration

Save the complete configuration to `api-project.promptrek.yaml`.

### Step 2: Validate

```bash
promptrek validate api-project.promptrek.yaml
```

### Step 3: Generate

```bash
# For all editors
promptrek generate api-project.promptrek.yaml --all

# For specific editor
promptrek generate api-project.promptrek.yaml --editor claude
```

### Step 4: Customize

Adapt to your specific API:

```yaml
content: |
  # My E-Commerce API

  ## Project Context
  This API powers an e-commerce platform with:
  - Product catalog management
  - Shopping cart functionality
  - Order processing
  - Payment integration (Stripe)
  - Inventory tracking

  ## Special Requirements
  - PCI compliance for payment handling
  - GDPR compliance for EU customers
  - Rate limiting: 100 requests/minute per user
  - Response time SLA: 95% under 200ms
```

## Generated Files

### GitHub Copilot

**File:** `.github/copilot-instructions.md`

Contains all API guidelines formatted for Copilot's context.

### Claude Code

**Files:**
- `.claude/CLAUDE.md` - Main guidelines
- `.mcp.json` - MCP server configurations (if plugins configured)

### Cursor

**Files:**
- `.cursor/rules/index.mdc` - Main rules with metadata
- `AGENTS.md` - Project overview

## Advanced: With MCP Servers

Add database and API integrations:

```yaml
schema_version: "3.1.0"
metadata:
  title: Node.js REST API with Tools

content: |
  # API Development Guide
  ...

# Database access via MCP
mcp_servers:
  - name: postgres
    command: npx
    args: ["-y", "@modelcontextprotocol/server-postgres"]
    env:
      POSTGRES_CONNECTION_STRING: "{{{ DATABASE_URL }}}"
    description: PostgreSQL database access
    trust_metadata:
      trusted: true
      trust_level: partial
      requires_approval: true

  # GitHub for CI/CD and issues
  - name: github
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_TOKEN: "{{{ GITHUB_TOKEN }}}"
    description: GitHub API integration

variables:
  DATABASE_URL: postgresql://localhost:5432/mydb
  GITHUB_TOKEN: ghp_your_token
```

**Generate MCP files:**

```bash
promptrek plugins generate api-project.promptrek.yaml --editor claude
```

## Advanced: With Custom Commands

Add API-specific slash commands:

```yaml
# Custom commands for API development
commands:
  - name: create-endpoint
    description: Generate a new REST endpoint
    prompt: |
      Create a new REST endpoint with:
      - Route handler in routes/
      - Controller in controllers/
      - Service layer in services/
      - Zod validation schema
      - Unit tests
      - Integration tests
      Include proper error handling and TypeScript types.

  - name: add-auth
    description: Add authentication to endpoint
    prompt: |
      Add JWT authentication to the endpoint:
      - Import authenticate middleware
      - Add role-based authorization if needed
      - Update types for authenticated requests
      - Add tests for auth scenarios

  - name: optimize-query
    description: Optimize database query
    prompt: |
      Analyze and optimize the database query:
      - Check for N+1 query problems
      - Suggest appropriate indexes
      - Consider using select() to limit fields
      - Add pagination if needed
      - Suggest caching opportunities
```

**Use in editor:**

```
/create-endpoint users/profile
/add-auth admin-only
/optimize-query getUserWithOrders
```

## Real-World Example: Authentication Endpoints

```yaml
content: |
  # Authentication API Guidelines

  ## Authentication Endpoints

  ### POST /api/v1/auth/register
  ```typescript
  interface RegisterRequest {
    email: string;      // Valid email format
    password: string;   // Min 8 chars, 1 uppercase, 1 number
    name: string;       // 2-100 characters
  }

  interface RegisterResponse {
    success: true;
    data: {
      user: {
        id: string;
        email: string;
        name: string;
      };
      token: string;    // JWT token
    };
  }
  ```

  ### POST /api/v1/auth/login
  ```typescript
  interface LoginRequest {
    email: string;
    password: string;
  }

  interface LoginResponse {
    success: true;
    data: {
      user: User;
      token: string;
      refreshToken: string;
    };
  }
  ```

  ### Implementation Requirements
  - Hash passwords with bcrypt (12 rounds)
  - JWT tokens expire in 15 minutes
  - Refresh tokens expire in 7 days
  - Implement rate limiting: 5 attempts per 15 minutes
  - Log all authentication attempts
  - Return generic error messages (don't reveal if email exists)
```

## Testing Configuration

Add test-specific guidelines:

```yaml
documents:
  - name: testing
    content: |
      # API Testing Guidelines

      ## Unit Tests
      - Test each function in isolation
      - Mock external dependencies
      - Test error conditions

      ## Integration Tests
      ```typescript
      describe('POST /api/v1/users', () => {
        it('creates user with valid data', async () => {
          const response = await request(app)
            .post('/api/v1/users')
            .send({
              email: 'test@example.com',
              name: 'Test User',
              password: 'SecurePass123',
            })
            .expect(201);

          expect(response.body.success).toBe(true);
          expect(response.body.data.user.email).toBe('test@example.com');
        });

        it('returns 400 for invalid email', async () => {
          await request(app)
            .post('/api/v1/users')
            .send({
              email: 'invalid-email',
              name: 'Test',
              password: 'password',
            })
            .expect(400);
        });
      });
      ```
    file_globs: "**/*.{test,spec}.ts"
    always_apply: false
```

## Best Practices

### Security Checklist

- [ ] All inputs validated with Zod
- [ ] Passwords hashed with bcrypt (min 10 rounds)
- [ ] JWT tokens with short expiration
- [ ] Rate limiting on all public endpoints
- [ ] CORS configured properly
- [ ] Helmet.js for security headers
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention
- [ ] CSRF protection for state-changing operations

### API Design Checklist

- [ ] RESTful resource naming
- [ ] Proper HTTP methods
- [ ] Correct status codes
- [ ] Consistent response format
- [ ] API versioning
- [ ] Pagination for lists
- [ ] Filtering and sorting
- [ ] Error messages with error codes
- [ ] Request/response logging

### Performance Checklist

- [ ] Database connection pooling
- [ ] Indexes on frequently queried fields
- [ ] Caching for expensive operations
- [ ] Pagination for large datasets
- [ ] Compression (gzip)
- [ ] Response time monitoring
- [ ] Query optimization
- [ ] Async operations where appropriate

## Troubleshooting

### Database Connection Issues

**Problem:** Can't connect to database

**Solution:**
```bash
# Test connection string
promptrek generate api-config.promptrek.yaml --editor cursor \
  -V DATABASE_URL=postgresql://user:pass@localhost:5432/testdb

# Verify in generated files
cat .cursor/rules/index.mdc | grep DATABASE_URL
```

### JWT Secret Not Working

**Problem:** JWT tokens invalid

**Solution:** Ensure JWT_SECRET is set and not empty:

```yaml
variables:
  JWT_SECRET: "at-least-32-characters-long-secret-key"
```

## Related Examples

- **[React TypeScript](react-typescript.md)** - Frontend to consume this API
- **[NX Monorepo](../advanced/monorepo.md)** - Full-stack project structure
- **[MCP Servers](../plugins/mcp-servers.md)** - Database integration

## Additional Resources

- [Express.js Guide](https://expressjs.com/en/guide/routing.html)
- [Prisma Documentation](https://www.prisma.io/docs)
- [Zod Validation](https://zod.dev/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [REST API Design](https://restfulapi.net/)

---

**Next Steps:**
1. Adapt configuration for your API
2. Add MCP servers for database access
3. Create custom commands for common tasks
4. Generate files and test with your editor
