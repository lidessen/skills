# Code Search Patterns Reference

Comprehensive techniques for navigating and understanding codebases through strategic search patterns.

## Table of Contents
- [Search by Code Element](#search-by-code-element)
- [Language-Specific Patterns](#language-specific-patterns)
- [Tracing Code Flow](#tracing-code-flow)
- [Finding Dependencies](#finding-dependencies)
- [Test-Driven Discovery](#test-driven-discovery)
- [Configuration Discovery](#configuration-discovery)
- [Error and Validation Search](#error-and-validation-search)

## Search by Code Element

### Finding Type Definitions

Type definitions reveal data structures and contracts.

**TypeScript/JavaScript**:
```bash
# Interfaces
grep -r "interface\s\+UserProfile" src/

# Type aliases
grep -r "type\s\+UserProfile" src/

# Classes
grep -r "class\s\+UserProfile" src/

# Enums
grep -r "enum\s\+UserStatus" src/
```

**Python**:
```bash
# Classes
grep -r "^class UserProfile" src/

# Type hints with dataclass
grep -r "@dataclass" src/ -A 5

# TypedDict
grep -r "class.*TypedDict" src/
```

**Go**:
```bash
# Struct definitions
grep -r "type.*struct" .

# Interfaces
grep -r "type.*interface" .

# Specific type
grep -r "type UserProfile struct" .
```

**Java**:
```bash
# Classes
grep -r "public class UserProfile" src/

# Interfaces
grep -r "public interface" src/

# Records (Java 14+)
grep -r "public record" src/
```

### Finding Function/Method Definitions

**TypeScript/JavaScript**:
```bash
# Function declarations
grep -r "function getUserProfile" src/

# Arrow functions (exported)
grep -r "export const getUserProfile" src/

# Class methods
grep -r "getUserProfile\s*(" src/ | grep -v "^\s*//"

# Async functions
grep -r "async.*getUserProfile" src/
```

**Python**:
```bash
# Function definitions
grep -r "^def get_user_profile" src/

# Class methods
grep -r "^\s\+def get_user_profile" src/

# Async functions
grep -r "async def get_user_profile" src/
```

**Go**:
```bash
# Function definitions
grep -r "^func GetUserProfile" .

# Methods (with receiver)
grep -r "^func (.*) GetUserProfile" .
```

**Java**:
```bash
# Method definitions
grep -r "public.*getUserProfile\s*(" src/

# With return type
grep -r "public UserProfile getUserProfile" src/
```

### Finding Constants and Configuration

```bash
# Constants
grep -r "const\s\+MAX_RETRY" src/
grep -r "final.*MAX_RETRY" src/  # Java
grep -r "MAX_RETRY\s*=" src/      # Python

# Environment variables
grep -r "process\.env\." src/           # Node.js
grep -r "os\.getenv\|os\.environ" src/  # Python
grep -r "System\.getenv" src/           # Java

# Config objects
grep -r "config\.\|CONFIG\." src/
```

### Finding API Routes/Endpoints

**Express.js**:
```bash
# Route definitions
grep -r "router\.\(get\|post\|put\|delete\|patch\)" src/
grep -r "app\.\(get\|post\|put\|delete\)" src/

# Specific endpoint
grep -r "\.get\s*\(\s*['\"]\/users" src/
```

**FastAPI/Flask**:
```bash
# Route decorators
grep -r "@app\.\(get\|post\|put\|delete\)" src/
grep -r "@router\.\(get\|post\|put\|delete\)" src/

# Specific route
grep -r "@.*\.get\(.*\/users" src/
```

**Spring Boot**:
```bash
# Request mappings
grep -r "@GetMapping\|@PostMapping\|@PutMapping" src/
grep -r "@RequestMapping" src/

# Specific endpoint
grep -r "@GetMapping.*\"/users\"" src/
```

### Finding Database Queries

**SQL queries**:
```bash
# Direct SQL strings
grep -r "SELECT.*FROM.*users" src/

# Query builders
grep -r "\.select\(.*users\|\.from\(.*users" src/

# ORM queries
grep -r "User\.find\|User\.query" src/
```

**Database models**:
```bash
# Mongoose (MongoDB)
grep -r "mongoose\.model\|new Schema" src/

# Sequelize
grep -r "sequelize\.define\|DataTypes\." src/

# TypeORM
grep -r "@Entity\|@Column" src/

# SQLAlchemy
grep -r "class.*Base\|Column\(" src/
```

## Language-Specific Patterns

### TypeScript/JavaScript

**Finding imports/exports**:
```bash
# ES6 imports
grep -r "import.*from.*['\"].*user" src/

# Require statements
grep -r "require\(['\"].*user" src/

# Exports
grep -r "export.*User\|export default" src/

# Re-exports
grep -r "export.*from" src/
```

**Finding React components**:
```bash
# Function components
grep -r "function.*Component\|const.*Component.*=" src/ --include="*.tsx" --include="*.jsx"

# Hooks usage
grep -r "useState\|useEffect\|useContext" src/

# Props interfaces
grep -r "interface.*Props" src/ --include="*.tsx"
```

**Finding decorators** (if using):
```bash
grep -r "@Component\|@Injectable\|@Entity" src/
```

### Python

**Finding class inheritance**:
```bash
# Classes inheriting from specific base
grep -r "class.*\(.*BaseModel\)" src/

# Multiple inheritance
grep -r "class.*\(.*,.*\)" src/
```

**Finding decorators**:
```bash
# Common decorators
grep -r "@property\|@staticmethod\|@classmethod" src/

# Custom decorators
grep -r "@login_required\|@cache" src/
```

**Finding async code**:
```bash
# Async functions
grep -r "async def\|await " src/

# Async context managers
grep -r "async with" src/
```

### Go

**Finding interfaces and implementations**:
```bash
# Interface definitions
grep -r "type.*interface {" .

# Struct methods (potential interface implementation)
grep -r "func (.*\*.*) .*(" .
```

**Finding goroutines**:
```bash
# Go routine launches
grep -r "go func\|go .*\(" .

# Channels
grep -r "make(chan\|<-.*chan\|chan.*<-" .
```

### Java

**Finding annotations**:
```bash
# Spring annotations
grep -r "@Service\|@Repository\|@Controller\|@Component" src/

# JPA annotations
grep -r "@Entity\|@Table\|@Column" src/

# Testing annotations
grep -r "@Test\|@Before\|@After" src/
```

**Finding inheritance**:
```bash
# Class extension
grep -r "class.*extends" src/

# Interface implementation
grep -r "class.*implements" src/
```

## Tracing Code Flow

### Entry Point to Implementation

**Step 1: Find entry point**
```bash
# HTTP endpoints
grep -r "router\.\|@.*Mapping\|@app\." src/

# Main function
grep -r "function main\|def main\|func main\|public static void main" .

# Event handlers
grep -r "addEventListener\|on\(.*,\|@EventListener" src/
```

**Step 2: Trace function calls**
```bash
# Find where function is called
grep -r "getUserProfile\(" src/

# Find function definition
grep -r "function getUserProfile\|const getUserProfile\|def get_user_profile" src/
```

**Step 3: Follow imports**
```bash
# Find where module is imported
grep -r "from.*userService\|import.*userService" src/
```

**Step 4: Map data flow**
```bash
# Track variable transformations
# Read the implementation file to see how data flows
```

### Reverse Tracing (From Implementation to Usage)

**Step 1: Find function definition**
```bash
grep -r "function calculateTotal" src/
```

**Step 2: Find all usages**
```bash
grep -r "calculateTotal\(" src/ | grep -v "function calculateTotal"
```

**Step 3: Identify calling contexts**
```bash
# Read files that call the function to understand usage contexts
```

## Finding Dependencies

### Direct Dependencies

**Package dependencies**:
```bash
# Node.js
cat package.json | grep -A 20 "dependencies"

# Python
cat requirements.txt
cat pyproject.toml

# Go
cat go.mod

# Java
cat pom.xml | grep -A 5 "<dependencies>"
```

### Import Dependencies

**Find all imports from a module**:
```bash
# TypeScript/JavaScript
grep -r "from ['\"].*module-name" src/

# Python
grep -r "from module_name import\|import module_name" src/

# Go
grep -r "\"module-name" .

# Java
grep -r "import.*module\.name" src/
```

### Finding Internal Dependencies

**Module dependency graph**:
```bash
# Find all files importing from specific module
grep -rl "from.*['\"]@/services/user" src/

# Find what a module imports
grep "^import\|^from" src/services/user.ts
```

### Finding Circular Dependencies

```bash
# Find imports between two modules
grep -r "from.*moduleA" src/moduleB/
grep -r "from.*moduleB" src/moduleA/
```

## Test-Driven Discovery

Tests reveal expected behavior and usage patterns.

### Finding Test Files

```bash
# By naming convention
Glob: "**/*.test.{ts,js,py}"
Glob: "**/*.spec.{ts,js}"
Glob: "**/test_*.py"

# By directory
Glob: "tests/**/*"
Glob: "__tests__/**/*"
```

### Finding Tests for Specific Feature

```bash
# Test file for module
find . -name "*user*test*" -o -name "*user*spec*"

# Test cases mentioning feature
grep -r "describe.*user\|test.*user\|it.*user" tests/

# Python tests
grep -r "def test_.*user\|class Test.*User" tests/
```

### Understanding Behavior from Tests

**Look for**:
1. Test setup - What's being initialized
2. Test input - What parameters are used
3. Assertions - What's the expected behavior
4. Edge cases - Error conditions tested

```bash
# Find test assertions
grep -r "expect\|assert" tests/user.test.ts

# Find error tests
grep -r "toThrow\|raises\|assertRaises" tests/
```

## Configuration Discovery

### Finding Config Files

```bash
# Common config locations
ls config/*.{js,json,yaml,yml}
ls *.config.{js,ts}
ls .*.{json,yaml,yml}

# Environment configs
ls .env*
ls config/*.env*
```

### Finding Config Usage

```bash
# Import/require of config
grep -r "import.*config\|require.*config" src/

# Config object access
grep -r "config\.\|CONFIG\.\|settings\." src/

# Environment variable usage
grep -r "process\.env\.\|os\.getenv\|System\.getenv" src/
```

### Schema Discovery

```bash
# JSON Schema
find . -name "*schema.json" -o -name "schema.json"

# GraphQL Schema
find . -name "schema.graphql" -o -name "*.graphql"

# Protocol Buffers
find . -name "*.proto"

# OpenAPI/Swagger
find . -name "openapi.yaml" -o -name "swagger.*"
```

## Error and Validation Search

### Finding Error Definitions

```bash
# Error classes
grep -r "class.*Error extends\|class.*Exception" src/

# Error constants
grep -r "ERROR_\|ERR_" src/ --include="*.ts" --include="*.js"

# Error enums
grep -r "enum.*Error" src/
```

### Finding Error Throwing

```bash
# Throw statements
grep -r "throw new\|throw " src/

# Specific error type
grep -r "throw new ValidationError\|throw ValidationError" src/

# Python raise
grep -r "raise.*Error\|raise " src/
```

### Finding Error Handling

```bash
# Try-catch blocks
grep -r "try\s*{" src/ -A 10

# Catch specific errors
grep -r "catch.*Error\|except.*Error" src/

# Error callbacks
grep -r "\.catch\(.*=>\|\.on\(['\"]error" src/
```

### Finding Validation Logic

```bash
# Validation functions
grep -r "function.*validate\|validate.*function" src/

# Validation libraries
grep -r "from.*validator\|import.*validation" src/

# Schema validation
grep -r "\.validate\(.*schema\|schema\.validate" src/

# Type guards (TypeScript)
grep -r "function is.*\(.*:.*is " src/
```

## Advanced Search Techniques

### Using Glob for Pattern Matching

```bash
# All TypeScript files in feature directories
Glob: "src/features/**/*.ts"

# All test files
Glob: "**/*.{test,spec}.{ts,js,py}"

# All config files
Glob: "**/*.config.{js,ts,json}"

# Specific component types
Glob: "src/components/**/*.component.tsx"
```

### Combining Grep Patterns

```bash
# Find class definitions with inheritance
grep -rE "class \w+ extends|class \w+ implements" src/

# Find async arrow functions
grep -rE "const \w+ = async \(.*\) =>" src/

# Find exported types
grep -rE "export (type|interface|class)" src/
```

### Context-Aware Search

```bash
# Show function with 10 lines after (to see implementation start)
grep -r "function processPayment" src/ -A 10

# Show class with context
grep -r "class UserService" src/ -A 30

# Show imports and first function
grep -r "^import\|^function\|^export function" src/file.ts
```

### Multi-Step Search Chains

**Example: Find all API routes and their handlers**

```bash
# Step 1: Find route definitions
grep -r "router\.get" src/routes/ -n

# Step 2: For each route, find the handler
# From: router.get('/users/:id', getUserHandler)
grep -r "function getUserHandler\|const getUserHandler" src/

# Step 3: Find handler implementation details
# Read the handler file to understand logic
```

## Search Workflow Examples

### Example 1: Understanding a Feature End-to-End

**Goal**: Understand how "user registration" works

```bash
# 1. Find API endpoint
grep -r "router.*post.*register\|@.*Post.*register" src/

# 2. Find handler function
grep -r "function.*register\|const.*register.*=.*async" src/

# 3. Find service layer
grep -r "class.*UserService\|export.*userService" src/

# 4. Find data model
grep -r "interface User\|type User\|class User" src/

# 5. Find database operations
grep -r "\.create\|\.insert.*user" src/

# 6. Find validation
grep -r "validate.*user\|user.*schema" src/

# 7. Find tests
grep -r "describe.*register\|test.*register" tests/
```

### Example 2: Finding All Usages of a Utility

**Goal**: Find everywhere `formatDate` is used

```bash
# 1. Find definition
grep -r "function formatDate\|const formatDate\|def format_date" src/

# 2. Find all imports
grep -r "import.*formatDate\|from.*format_date" src/

# 3. Find all direct calls
grep -r "formatDate\(" src/ | grep -v "function formatDate"

# 4. Check if it's re-exported
grep -r "export.*formatDate.*from" src/
```

### Example 3: Tracing Data Transformation

**Goal**: Track how user data is transformed from request to database

```bash
# 1. Find request handler
grep -r "router.post.*users" src/

# 2. Find DTO/input type
grep -r "interface.*UserInput\|CreateUserDto" src/

# 3. Find transformation functions
grep -r "transform.*user\|map.*user\|toEntity" src/

# 4. Find entity/model type
grep -r "class User.*Entity\|interface UserEntity" src/

# 5. Find database save operation
grep -r "\.save\(.*user\|\.insert.*user" src/

# Read each file in sequence to understand transformation
```

## Tips for Effective Code Search

### Do's
- ✓ Start with type definitions (interfaces, schemas)
- ✓ Check tests for usage examples
- ✓ Follow imports to trace dependencies
- ✓ Use appropriate context lines (-A, -B, -C flags)
- ✓ Read entire files for critical code paths
- ✓ Look for naming patterns and conventions
- ✓ Search both definition and usage
- ✓ Use language-specific search patterns

### Don'ts
- ✗ Search only by keyword without understanding patterns
- ✗ Ignore test files
- ✗ Skip type definitions
- ✗ Search without file type filters (too much noise)
- ✗ Stop at first match without verifying
- ✗ Ignore code comments
- ✗ Forget to check config files
- ✗ Miss re-exports and aliases

## Common Patterns by Language

### TypeScript/JavaScript Common Locations
- Types: `src/types/`, `src/models/`, `*.types.ts`
- API: `src/routes/`, `src/controllers/`, `src/api/`
- Business logic: `src/services/`, `src/lib/`
- Utils: `src/utils/`, `src/helpers/`
- Config: `src/config/`, `config/`

### Python Common Locations
- Models: `models/`, `src/models/`
- Views/Routes: `views/`, `routes/`, `api/`
- Business logic: `services/`, `lib/`
- Utils: `utils/`, `helpers/`
- Config: `config/`, `settings.py`

### Go Common Locations
- Main: `main.go`, `cmd/`
- Handlers: `handlers/`, `http/`
- Services: `services/`, `pkg/`
- Models: `models/`, `entity/`
- Config: `config/`, `internal/config/`

### Java Common Locations
- Models: `src/main/java/.../model/`, `entity/`
- Controllers: `src/main/java/.../controller/`
- Services: `src/main/java/.../service/`
- Config: `src/main/resources/`, `application.properties`
