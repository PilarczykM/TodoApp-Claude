# Project guidance

## Tech Stack
- Language: Python 3.12+
- Framework: No
- Database: No

## Project Structure
- `domain/`: Core business logic
- `application/`: Use cases and services  
- `infrastructure/`: External concerns
- `interfaces/`: Controllers and adapters

<project-guidelines>
  <commands>
    <command name="make test" purpose="testing">Run all unit tests with pytest</command>
    <command name="make cov" purpose="coverage">Run test coverage analysis</command>
    <command name="make lint" purpose="linting">Show linting issues (e.g., flake8, ruff)</command>
    <command name="make format" purpose="formatting">Autofix formatting/lint issues (e.g. ruff)</command>
    <command name="make typecheck" purpose="type-checking">Run static type checking (e.g., mypy)</command>
  </commands>

  <code-style>
    <principle>TDD: Write tests before implementation</principle>
    <principle>Clean Code: Write code that is readable and maintainable</principle>
    <principle>KISS: Prefer simplicity over unnecessary complexity</principle>
    <principle>YAGNI: Don’t implement features until they are actually needed</principle>
    <principle>NEVER USE RELATIVE IMPORTS</principle>
    <architecture>Domain-Driven Design (DDD)</architecture>
    <modules>
      <module>domain</module>
      <module>application</module>
      <module>infrastructure</module>
      <module>interfaces</module>
    </modules>
    <modeling>Use Pydantic v2 for models and value objects</modeling>
  </code-style>

  <testing>
    <framework>pytest</framework>
    <organization>Class-based test organization</organization>
    <file-structure>Split large test files by domain</file-structure>
  </testing>

  <workflow>
    <step>Run <code>make format</code> to autofix code style issues</step>
    <step>Run <code>make lint</code> to check for lint violations</step>
    <step>Run <code>make typecheck</code> to perform static type analysis</step>
    <step>Run <code>make test</code> to execute all tests and verify correctness</step>
    <step>Run <code>make cov</code> to execute tests coverage and verify that we are not below 90%</step>
    <step>Do all of the above before committing any code</step>
    <step>Commit frequently to keep changes atomic and traceable</step>
    <quality-target>Maintain test coverage above 85%</quality-target>
  </workflow>

  <restrictions>
    <restriction>Do not commit directly to main branch</restriction>
    <restriction>Do not commit without checking code quality</restriction>
    <restriction>Do not use relative imports</restriction>
  </restrictions>
</project-guidelines>
