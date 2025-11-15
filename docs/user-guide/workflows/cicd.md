# CI/CD Integration

Integrate PrompTrek into your continuous integration and deployment pipelines.

## Overview

PrompTrek can be integrated into CI/CD pipelines to:

- Validate prompt files on pull requests
- Generate editor files during deployment
- Enforce prompt file standards
- Automate multi-environment configurations

## GitHub Actions

### Validate on PR

```yaml
# .github/workflows/validate-prompts.yml
name: Validate PrompTrek Files

on:
  pull_request:
    paths:
      - '**.promptrek.yaml'
  push:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v2

      - name: Install PrompTrek
        run: uv pip install promptrek

      - name: Validate files
        run: |
          for file in *.promptrek.yaml; do
            promptrek validate "$file"
          done
```

### Generate on Deploy

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install PrompTrek
        run: uv pip install promptrek

      - name: Generate prompts
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          OPENAI_KEY: ${{ secrets.OPENAI_KEY }}
        run: |
          promptrek generate --all \
            -V ENVIRONMENT=production \
            -V GITHUB_TOKEN="$GITHUB_TOKEN" \
            -V OPENAI_API_KEY="$OPENAI_KEY"

      - name: Deploy files
        run: |
          # Deploy generated files
          # ...
```

## GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - validate
  - deploy

validate-prompts:
  stage: validate
  image: python:3.11
  before_script:
    - pip install promptrek
  script:
    - promptrek validate project.promptrek.yaml
  only:
    changes:
      - "**.promptrek.yaml"

deploy:
  stage: deploy
  script:
    - promptrek generate --all -V ENVIRONMENT=production
    - # Deploy files...
  only:
    - main
```

## Jenkins

```groovy
// Jenkinsfile
pipeline {
    agent any

    stages {
        stage('Validate') {
            steps {
                sh 'pip install promptrek'
                sh 'promptrek validate project.promptrek.yaml'
            }
        }

        stage('Generate') {
            when {
                branch 'main'
            }
            steps {
                withCredentials([
                    string(credentialsId: 'github-token', variable: 'GITHUB_TOKEN')
                ]) {
                    sh '''
                        promptrek generate --all \
                          -V ENVIRONMENT=production \
                          -V GITHUB_TOKEN=$GITHUB_TOKEN
                    '''
                }
            }
        }
    }
}
```

## Best Practices

!!! tip "Validate on PR"
    Always validate prompt files in pull requests:
    ```yaml
    on: [pull_request]
    run: promptrek validate *.promptrek.yaml
    ```

!!! tip "Use Secrets for Tokens"
    Never hardcode secrets:
    ```yaml
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    ```

!!! warning "Don't Commit Generated Files"
    Generate files in CI, don't commit them:
    ```yaml
    - run: promptrek generate --all
    - run: deploy-generated-files.sh
    # Don't: git add .claude/ && git commit
    ```

## See Also

- [Variables](../configuration/variables.md)
- [Validate Command](../../cli/commands/validate.md)
- [Generate Command](../../cli/commands/generate.md)
