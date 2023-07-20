# AIPRChecker

This Github action can check pull requests to find security issues (vulnerabilities, backdoors, malicious code, secrets leaks...) and code opmitization issues (code smells, bad practices...) and let you know in a comment in the pull request.

## How to use it

Create a Github Action like the following:

```yaml
name: AIPRChecker - Check for security issues and code smells
on: [pull_request, pull_request_target]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Run AIPRChecker
        uses: AI-Gents/AIPRChecker@main
        with:
          api-key: ${{ secrets.OPENAI_API_KEY }}
          model: 'gpt-4'
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

You need to give **write access to the GITHUB_TOKEN** secret to the action: Go to `Settings` > `Actions` > `General` in the `Workflow permissions` section check `Read and write permissions`.