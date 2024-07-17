# 1.0.0
- Migration to pydantic v2

# 1.0.1
- Change Map type to dict (key, value)

# 1.0.2
- Stringify mutation input strings
- Add __typename to payload
- create test folder as a module

# 1.1.0
- Support inline and extracted variables for mutation and query
- Stringify fix

# 1.1.1
- Fix missing inputs for mutation and query render in extracted format
- ENUM keys always uppercase

# 1.2.0
- Allow to populate by name

# 1.2.1
- Fix rendering issue when payload is bool

# 1.2.1
- Security updates
- Disable pyright check for reportCallIssue
- Disable pyright check for reportIncompatibleVariableOverride
