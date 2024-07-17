# Second Opinion 🩺 (AI Code Review)

A Github Action which reviews your code.

This action is designed to run on pull request actions, specifically ones which change the code in the PR (open & synchronize).
This action will take the latest changes and send them to a chat gpt model asking it to review the changes.
The response is posted as a comment on the PR.

In order to run this you will need an Open AI key, or details for an Azure Open AI Deployment.
It is recommended to store your API key as a secret in Github to avoid it being exposed to others 
https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions


The action wayneplural/second-opinion@8
is used as follows and has the following options:

```yaml
  - name: Generate A Second Opinion
    uses: wayneplural/second-opinion@v13
    with:
      openai-api-key: '<YOUR API KEY>' # Required - This can be either an Open AI key or Azure Open AI key if using Azure
      ai-model: '<API MODEL>' # Required - The GPT model to use or the deployment model if using an Azure deployment
      azure-openai-api-endpoint: '<AZURE OPEN AI ENDPOINT>' # Only required for Azure Open AI deployments
      azure-api-version: '<AZURE OPEN AI VERSION>' # Only required for Azure Open AI deployemnts
      custom-prompt: '<CUSTOM REVIEW PROMPT>' # Optional - a custom prompt to provide as the review prompt.
```

Before using the action you should use the checkout action to checkout your repo you will need to use a "fetch-depth" of at least 2 to get the last two commits:

```yaml
  uses: actions/checkout@v4
  with:
    fetch-depth: 2
```

You will also need to provide pull request write permission and contents read permission to the job to allow the job to post a comment on your PR, and to checkout the repo.

```yaml
jobs:
  second-opinion:
    permissions:
      pull-requests: write
      contents: read
    runs-on: ubuntu-latest
```


### Example Usage

#### Open AI

```yaml
name: Second Opinion - AI Code Review
run-name: Second Opinion - Diagnosing code 🩺
on: 
  pull_request:
    types: [opened, synchronize]

jobs:
  second-opinion:
    permissions:
      pull-requests: write
      contents: read
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4
        with:
          fetch-depth: 2

      - name: Generate A Second Opinion
        uses: wayneplural/second-opinion@v13
        with:
          openai-api-key: ${{ secrets.AZURE_OPENAI_API_KEY }}
          ai-model: "gpt-3.5-turbo"
      
```

#### Azure Open AI

```yaml
name: Second Opinion - AI Code Review
run-name: Second Opinion - Diagnosing code 🩺
on: 
  pull_request:
    types: [opened, synchronize]

jobs:
  second-opinion:
    permissions:
      pull-requests: write
      contents: read
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4
        with:
          fetch-depth: 2

      - name: Generate A Second Opinion
        uses: wayneplural/second-opinion@v13
        with:
          azure-openai-api-endpoint: "https://openaiplural.openai.azure.com/"
          azure-api-version: "2024-05-01-preview"
          openai-api-key: ${{ secrets.OPENAI_API_KEY }}
          ai-model: "second-opinion"
```