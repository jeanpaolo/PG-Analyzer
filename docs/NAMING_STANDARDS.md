# Naming Standards Analysis

The PostgreSQL Performance Analyzer includes comprehensive naming standards analysis to help maintain consistent and professional database naming conventions.

## Overview

The naming standards analyzer evaluates database objects against industry best practices and identifies:

- **Naming pattern consistency** (snake_case, camelCase, PascalCase)
- **Reserved word violations**
- **Naming convention compliance**
- **Index and constraint naming patterns**
- **Problematic naming issues**

## Features

### 1. Table Naming Analysis

Evaluates table names for:

- **Case conventions**: snake_case, camelCase, PascalCase, or mixed
- **Consistency score**: Percentage of tables following the dominant pattern
- **Reserved words**: Tables using PostgreSQL reserved words
- **Length issues**: Names too short (< 3 chars) or too long (> 63 chars)
- **Invalid patterns**: Names starting with numbers

**Example Output:**
```
Total Tables: 6
Dominant Pattern: snake_case
Consistency Score: 100.0%

Naming Pattern Distribution:
- snake_case: 6
- camelCase: 0
- PascalCase: 0
- mixed_case: 0
```

### 2. Column Naming Analysis

Analyzes column names for:

- **Naming patterns**: Case convention usage
- **Reserved words**: Columns using reserved words
- **Common prefixes**: Identifies frequently used prefixes (e.g., `is_`, `has_`, `user_`)
- **Common suffixes**: Identifies frequently used suffixes (e.g., `_id`, `_date`, `_count`)
- **Length violations**: Names exceeding PostgreSQL limits

**Common Patterns Detected:**
- `id` suffix for primary keys
- `_at` suffix for timestamps
- `is_` prefix for boolean flags
- `_count` suffix for counters

### 3. Index Naming Analysis

Evaluates index naming conventions:

- **Standard prefixes**: `idx_`, `pk_`, `fk_`, `uk_`
- **Table name inclusion**: Whether index names include the table name
- **Pattern consistency**: Adherence to naming standards
- **Primary key patterns**: `_pkey` suffix detection

**Recommended Patterns:**
- Primary keys: `pk_tablename` or `tablename_pkey`
- Foreign keys: `fk_tablename_columnname`
- Indexes: `idx_tablename_columnname`
- Unique constraints: `uk_tablename_columnname`

### 4. Constraint Naming Analysis

Checks constraint naming conventions:

- **Type-specific prefixes**: `pk_`, `fk_`, `uk_`, `ck_`
- **Naming consistency**: Adherence to expected patterns
- **Constraint types**: PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK

### 5. Schema Naming Analysis

Evaluates schema names for:

- **Case conventions**: Lowercase or snake_case preferred
- **Naming clarity**: Descriptive and meaningful names
- **Pattern consistency**: Uniform naming across schemas

## AI-Enhanced Analysis

The naming standards analysis is integrated with AI recommendations. The enhanced AI prompts now include:

### Detailed Naming Analysis Requests

1. **Table Naming Conventions**
   - Evaluate snake_case, PascalCase, camelCase usage
   - Identify inconsistencies across schemas
   - Check plural vs singular naming
   - Verify abbreviation clarity

2. **Column Naming Standards**
   - Assess naming consistency and clarity
   - Check for reserved words
   - Evaluate prefix/suffix patterns

3. **Index Naming Patterns**
   - Review naming conventions (e.g., `idx_tablename_columnname`)
   - Verify table name inclusion
   - Check for standard prefixes

4. **Specific Recommendations**
   - Violations with examples
   - Suggested corrections
   - Priority levels (High/Medium/Low)

## Best Practices

### Recommended Naming Conventions

#### Tables
```sql
-- Good: snake_case, descriptive, plural
CREATE TABLE customer_orders (...);
CREATE TABLE product_reviews (...);

-- Avoid: Mixed case, unclear
CREATE TABLE CustomerOrder (...);
CREATE TABLE tbl_orders (...);
```

#### Columns
```sql
-- Good: snake_case, descriptive
customer_id INTEGER
created_at TIMESTAMP
is_active BOOLEAN
email_address VARCHAR(255)

-- Avoid: Unclear, reserved words
id INTEGER  -- Too generic
user TEXT   -- Reserved word
```

#### Indexes
```sql
-- Good: Prefix + table + column
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);

-- Avoid: No pattern
CREATE INDEX customer_email_index ON customers(email);
```

#### Constraints
```sql
-- Good: Type prefix + table + column
ALTER TABLE customers ADD CONSTRAINT pk_customers PRIMARY KEY (id);
ALTER TABLE orders ADD CONSTRAINT fk_orders_customer_id 
    FOREIGN KEY (customer_id) REFERENCES customers(id);

-- Avoid: Auto-generated names
ALTER TABLE customers ADD PRIMARY KEY (id);  -- Creates random name
```

### PostgreSQL Naming Standards

1. **Use lowercase**: PostgreSQL is case-insensitive but converts to lowercase
2. **Use snake_case**: Preferred over camelCase or PascalCase
3. **Be descriptive**: Avoid abbreviations unless widely understood
4. **Avoid reserved words**: Don't use SQL keywords as names
5. **Keep it short**: Under 63 characters (PostgreSQL limit)
6. **Be consistent**: Follow the same pattern throughout the database
7. **Use prefixes**: For constraints and indexes (pk_, fk_, idx_, uk_)
8. **Singular vs Plural**: Choose one and stick to it (plural is more common)

## Using the Naming Analyzer

### Command Line

```bash
# Run full analysis including naming standards
pg-perf-analyzer analyze \
  --host localhost \
  --database mydb \
  --user myuser \
  --output report.md
```

The naming analysis is automatically included in all reports.

### Programmatic Usage

```python
from pg_perf_analyzer.analyzers import NamingAnalyzer
from pg_perf_analyzer.utils import DatabaseConnection

db_config = {
    'host': 'localhost',
    'database': 'mydb',
    'user': 'myuser',
    'password': 'mypass'
}

with DatabaseConnection(db_config) as db:
    analyzer = NamingAnalyzer(db)
    results = analyzer.analyze()
    
    # Access specific results
    table_naming = results['table_naming']
    print(f"Consistency: {table_naming['consistency_score']}%")
    print(f"Dominant pattern: {table_naming['dominant_pattern']}")
    
    # Check for issues
    if table_naming['reserved_words']:
        print("Reserved word violations found!")
        for violation in table_naming['reserved_words']:
            print(f"  - {violation['table']}: {violation['issue']}")
```

## Report Output

### Naming Standards Section

The report includes a dedicated "Naming Standards Analysis" section with:

1. **Table Naming Conventions**
   - Total tables
   - Dominant pattern
   - Consistency score
   - Pattern distribution
   - Reserved word violations

2. **Index Naming Conventions**
   - Total indexes
   - Prefix usage statistics
   - Naming issues count

3. **Naming Standards Summary**
   - Total naming issues
   - Reserved word violations
   - Overall recommendation

### AI Recommendations

When AI analysis is enabled, you'll receive:

- Specific naming violations with examples
- Suggested corrections for non-compliant objects
- Priority levels for fixes
- SQL scripts for renaming (when applicable)

## Common Issues and Solutions

### Issue: Mixed Naming Patterns

**Problem:** Database has mix of snake_case and camelCase
```
customers (snake_case)
productReviews (camelCase)
Order_Items (mixed)
```

**Solution:** Standardize to snake_case
```sql
ALTER TABLE productReviews RENAME TO product_reviews;
ALTER TABLE Order_Items RENAME TO order_items;
```

### Issue: Reserved Word Usage

**Problem:** Table or column uses reserved word
```sql
CREATE TABLE user (...);  -- 'user' is reserved
```

**Solution:** Rename or quote
```sql
-- Option 1: Rename (recommended)
ALTER TABLE user RENAME TO users;

-- Option 2: Quote (not recommended)
CREATE TABLE "user" (...);
```

### Issue: Inconsistent Index Naming

**Problem:** Indexes lack standard prefixes
```sql
customer_email_index
orders_idx
customer_id_fk
```

**Solution:** Standardize with prefixes
```sql
ALTER INDEX customer_email_index RENAME TO idx_customers_email;
ALTER INDEX orders_idx RENAME TO idx_orders_created_at;
ALTER INDEX customer_id_fk RENAME TO fk_orders_customer_id;
```

### Issue: Unclear Abbreviations

**Problem:** Ambiguous abbreviations
```sql
CREATE TABLE cust_ord (...);  -- What is this?
```

**Solution:** Use full descriptive names
```sql
ALTER TABLE cust_ord RENAME TO customer_orders;
```

## Integration with CI/CD

### Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run naming analysis
pg-perf-analyzer analyze \
  --host localhost \
  --database dev_db \
  --user dev_user \
  --skip-ai \
  --format json \
  --output naming_check.json

# Check for naming issues
ISSUES=$(jq '.naming_analysis.naming_summary.total_naming_issues' naming_check.json)

if [ "$ISSUES" -gt 0 ]; then
    echo "❌ Naming standards violations detected: $ISSUES issues"
    echo "Run: pg-perf-analyzer analyze ... to see details"
    exit 1
fi

echo "✅ Naming standards check passed"
```

### CI Pipeline Check

```yaml
# .github/workflows/naming-standards.yml
name: Naming Standards Check

on: [pull_request]

jobs:
  check-naming:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run naming analysis
        run: |
          pg-perf-analyzer analyze \
            --host ${{ secrets.DB_HOST }} \
            --database ${{ secrets.DB_NAME }} \
            --user ${{ secrets.DB_USER }} \
            --skip-ai \
            --format json \
            --output naming.json
      
      - name: Check for violations
        run: |
          ISSUES=$(jq '.naming_analysis.naming_summary.total_naming_issues' naming.json)
          if [ "$ISSUES" -gt 5 ]; then
            echo "Too many naming violations: $ISSUES"
            exit 1
          fi
```

## Configuration

### Custom Reserved Words

You can extend the reserved words list by modifying `naming_analyzer.py`:

```python
RESERVED_WORDS = {
    # Standard PostgreSQL reserved words
    'user', 'order', 'group', 'table',
    # Add your organization-specific reserved words
    'admin', 'system', 'config',
}
```

### Custom Naming Patterns

Define organization-specific patterns:

```python
def _is_company_standard(self, name: str) -> bool:
    """Check if name follows company naming standard."""
    # Example: Must start with department prefix
    valid_prefixes = ['sales_', 'hr_', 'finance_']
    return any(name.startswith(prefix) for prefix in valid_prefixes)
```

## Metrics and Scoring

### Consistency Score

Calculated as:
```
consistency_score = (count_of_dominant_pattern / total_objects) * 100
```

**Interpretation:**
- **90-100%**: Excellent consistency
- **70-89%**: Good, minor improvements needed
- **50-69%**: Fair, standardization recommended
- **< 50%**: Poor, major refactoring needed

### Naming Quality Score

Future enhancement will include overall quality score based on:
- Pattern consistency (40%)
- Reserved word avoidance (20%)
- Descriptive clarity (20%)
- Length appropriateness (10%)
- Special character usage (10%)

## Future Enhancements

Planned improvements:

1. **Custom naming rules**: Define organization-specific standards
2. **Auto-fix suggestions**: Generate SQL scripts for corrections
3. **Historical tracking**: Compare naming quality over time
4. **Team standards**: Share and enforce team conventions
5. **IDE integration**: Real-time naming feedback
6. **Naming templates**: Pre-defined patterns for common scenarios

## References

- [PostgreSQL Naming Conventions](https://www.postgresql.org/docs/current/sql-syntax-lexical.html)
- [SQL Style Guide](https://www.sqlstyle.guide/)
- [Database Design Best Practices](https://wiki.postgresql.org/wiki/Don%27t_Do_This)

## Support

For questions or issues with naming standards analysis:
- Review the generated report's naming section
- Check the AI recommendations for specific guidance
- Consult the PostgreSQL documentation for reserved words
- Use `--skip-ai` flag for faster analysis during development
