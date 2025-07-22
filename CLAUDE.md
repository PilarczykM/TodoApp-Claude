# Project guidance  

<project-guidelines>
  <commands>
    <command name="make test" purpose="testing">Run all unit tests with pytest</command>
    <command name="make lint" purpose="linting">Show linting issues (e.g., flake8, ruff)</command>
    <command name="make format" purpose="formatting">Autofix formatting/lint issues (e.g. ruff)</command>
    <command name="make typecheck" purpose="type-checking">Run static type checking (e.g., mypy)</command>
  </commands>

  <code-style>
    <principle>TDD: Write tests before implementation</principle>
    <principle>Clean Code: Write code that is readable and maintainable</principle>
    <principle>KISS: Prefer simplicity over unnecessary complexity</principle>
    <principle>YAGNI: Don’t implement features until they are actually needed</principle>
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
    <step>Do all of the above before committing any code</step>
    <step>Commit frequently to keep changes atomic and traceable</step>
    <quality-target>Maintain test coverage above 90%</quality-target>
  </workflow>
</project-guidelines>
