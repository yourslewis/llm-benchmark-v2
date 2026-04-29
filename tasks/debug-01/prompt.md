# Task: Diagnose LiteLLM Config Failures

## Background

You are running LiteLLM as a proxy for multiple LLM providers. After a recent config update, three groups of models are failing with different errors. Your task is to diagnose each failure type and provide a working fix.

## Current LiteLLM Config

```yaml
# litellm_config.yaml
model_list:
  # Group A: OpenAI models
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_API_KEY
      api_base: https://api.openai.com/v1
      max_tokens: 4096

  - model_name: gpt-4o-mini
    litellm_params:
      model: openai/gpt-4o-mini
      api_key: os.environ/OPENAI_API_KEY
      api_base: https://api.openai.com/v1
      max_tokens: 4096

  # Group B: Azure OpenAI models
  - model_name: azure-gpt4
    litellm_params:
      model: azure/gpt-4
      api_key: os.environ/AZURE_OPENAI_API_KEY
      api_base: https://contoso.openai.azure.com
      api_version: "2024-02-15-preview"
      max_tokens: 4096

  - model_name: azure-gpt4-mini
    litellm_params:
      model: azure/gpt-4o-mini
      api_key: os.environ/AZURE_OPENAI_API_KEY
      api_base: https://contoso.openai.azure.com
      api_version: "2024-02-15-preview"
      max_tokens: 4096

  # Group C: Anthropic models (via LiteLLM)
  - model_name: claude-opus
    litellm_params:
      model: anthropic/claude-opus-4-20250514
      api_key: os.environ/ANTHROPIC_API_KEY
      max_tokens: 4096

  - model_name: claude-sonnet
    litellm_params:
      model: anthropic/claude-sonnet-4-20250514
      api_key: os.environ/ANTHROPIC_API_KEY
      max_tokens: 4096

  # Group D: Mistral models
  - model_name: mistral-large
    litellm_params:
      model: mistral/mistral-large-latest
      api_key: os.environ/MISTRAL_API_KEY
      max_tokens: 4096

  - model_name: mistral-small
    litellm_params:
      model: mistral/mistral-small-latest
      api_key: os.environ/MISTRAL_API_KEY
      max_tokens: 4096

  # Group E: Groq models
  - model_name: llama-fast
    litellm_params:
      model: groq/llama-3.3-70b-versatile
      api_key: os.environ/GROQ_API_KEY
      max_tokens: 32768

  - model_name: llama-mini
    litellm_params:
      model: groq/llama-3.1-8b-instant
      api_key: os.environ/GROQ_API_KEY
      max_tokens: 32768

litellm_settings:
  drop_params: true
  request_timeout: 30
  retry_policy:
    TimeoutErrorRetries: 3
    RateLimitErrorRetries: 3

router_settings:
  routing_strategy: least-busy
  model_group_alias:
    fast: ["gpt-4o-mini", "claude-sonnet", "llama-fast"]
    smart: ["gpt-4o", "claude-opus", "azure-gpt4"]

general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY
  database_url: os.environ/DATABASE_URL
  store_model_in_db: false
```

## Error Logs

After deploying this config, you see three distinct error types in your LiteLLM logs:

### Error Type 1: Azure models (azure-gpt4, azure-gpt4-mini)
```
Error: APIConnectionError - Azure OpenAI request failed
Details: {"error": {"code": "DeploymentNotFound", "message": "The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again."}}
Status: 404
```

### Error Type 2: Anthropic models (claude-opus, claude-sonnet)
```
Error: BadRequestError - Anthropic API error
Details: {"type": "error", "error": {"type": "invalid_request_error", "message": "model: field required"}}
Status: 400
```

### Error Type 3: Groq models (llama-fast, llama-mini)
```
Error: BadRequestError - Groq API error  
Details: {"error": {"message": "max_tokens exceeds the model context window. Requested: 32768, Context window: 8192", "type": "invalid_request_error"}}
Status: 400
```

## Your Task

### 1. Diagnose Each Error Type

For each of the 3 error types:
- **Root cause:** What exactly is wrong in the config?
- **Why this error:** Explain the technical reason this error is produced

### 2. Provide Fixed Config

Show the corrected YAML snippet for each failing group. Only show the changed lines — no need to repeat the entire config.

### 3. Validation Checklist

After applying fixes, what commands or checks should you run to verify each fix worked?

### 4. Prevention

What config validation or CI check would catch each of these errors before deployment?
