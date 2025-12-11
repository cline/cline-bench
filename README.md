# cline-bench early access

Real-world coding benchmarks derived from [actual Cline user sessions](https://cline.bot/blog/cline-bench-initiative). Tasks are challenging, verified, and represent genuine engineering problems solved in production.

## Prerequisites

- **Python 3.13**
- **uv** (Python package manager)
- **Docker** (for local testing)
- **Daytona API key** (for cloud execution)
- **LLM Provider API key** (Anthropic, OpenRouter, OpenAI, or OpenAI-compatible)

## Directory Structure

```
cline-bench/
├── README.md           # This file
└── tasks/              # Benchmark tasks
    ├── 01k6kr5hbv8za80v8vnze3at8h-every-plugin-api-migration/
    ├── 01k6n26zm27ffa7qqbcx0prrnw-police-sync-segfault/
    ├── 01k6rkmyfgbwpvf7h81gh4pdgd-intercept-axios-error-handling/
    ├── 01k6zz0nyj31znwsevx4sn6zb2-telegram-plugin-refactor/
    ├── 01k7a12sd1nk15j08e6x0x7v9e-discord-trivia-approval-keyerror/
    ├── 01k7x8zyeg4nzx6ehdb0fg5gfx-terraform-azurerm-deployment-stacks/
    └── etc.
```

Each task contains:
- `instruction.md` - Task description (agent input)
- `task.toml` - Harbor configuration (timeouts, resources)
- `environment/Dockerfile` - Container with broken initial state
- `solution/solve.sh` - Oracle's ground truth solution
- `tests/` - Pytest verification suite

## Installation

```bash
# 1. Create Python 3.13 virtual environment
uv venv --python 3.13
source .venv/bin/activate

# 2. Install Harbor
uv tool install harbor

# 3. Verify installation
python --version  # Should show 3.13.x
which harbor      # Should show harbor binary location
```

## Running Benchmarks

### Environment Variables

Cline CLI supports multiple LLM providers via environment variables:

```bash
# Required: Cloud execution
export DAYTONA_API_KEY=dtn_your-key-here

# Required: API key for your provider
export API_KEY=your-api-key-here

# Optional: For openai provider only (custom OpenAI-compatible endpoints)
export BASE_URL=https://your-endpoint.com/v1
```

**Model Name Format:** `provider:model-id`

The provider is specified as a prefix in the model name using `:` separator.

**Examples:**

```bash
# Option 1: Anthropic Direct
export API_KEY=sk-ant-xxx
harbor run ... -m anthropic:claude-sonnet-4-20250514

# Option 2: OpenRouter
export API_KEY=sk-or-v1-xxx
harbor run ... -m openrouter:anthropic/claude-sonnet-4-5:1m

# Option 3: OpenAI Native
export API_KEY=sk-proj-xxx
harbor run ... -m openai-native:gpt-4o

# Option 4: OpenAI (custom OpenAI-compatible endpoints: local LLMs, Ollama, vLLM)
export API_KEY=your-key
export BASE_URL=http://localhost:8000/v1
harbor run ... -m openai:your-model-id
```

### Local Execution (Docker)

```bash
# Activate venv
source .venv/bin/activate

# Run single task with Oracle (ground truth)
harbor run -p tasks/01k7a12sd1nk15j08e6x0x7v9e-discord-trivia-approval-keyerror \
           -a oracle \
           --env docker

# Run with Cline CLI using Anthropic direct
export API_KEY=sk-ant-your-key
harbor run -p tasks/01k7a12sd1nk15j08e6x0x7v9e-discord-trivia-approval-keyerror \
           -a cline-cli \
           -m anthropic:claude-sonnet-4-20250514 \
           --env docker

# Run with Cline CLI using OpenRouter
export API_KEY=sk-or-v1-your-key
harbor run -p tasks/01k7a12sd1nk15j08e6x0x7v9e-discord-trivia-approval-keyerror \
           -a cline-cli \
           -m openrouter:anthropic/claude-sonnet-4-5:1m \
           --env docker

# Run all tasks
export API_KEY=sk-ant-your-key
harbor run -p tasks \
           -a cline-cli \
           -m anthropic:claude-sonnet-4-5:1m \
           --env docker
```

### Cloud Execution (Daytona)

```bash
# Activate venv
source .venv/bin/activate

# Set environment variables
export DAYTONA_API_KEY=dtn_your-key
export API_KEY=sk-ant-your-key

# Run single task with Anthropic direct
harbor run -p tasks/01k7a12sd1nk15j08e6x0x7v9e-discord-trivia-approval-keyerror \
           -a cline-cli \
           -m anthropic:claude-sonnet-4-20250514 \
           --env daytona \
           --force-build

# Run single task with OpenRouter
export API_KEY=sk-or-v1-your-key
harbor run -p tasks/01k7a12sd1nk15j08e6x0x7v9e-discord-trivia-approval-keyerror \
           -a cline-cli \
           -m openrouter:anthropic/claude-sonnet-4-5:1m \
           --env daytona \
           --force-build

# Run all tasks on Daytona (batch execution)
export API_KEY=sk-ant-your-key
harbor run -p tasks \
           -a cline-cli \
           -m anthropic:claude-sonnet-4-5:1m \
           --env daytona \
           -n 200 \
           -k 1 \
           --max-retries 2 \
           --force-build
```

**Note:** Daytona has known issues with concurrent sandbox creation. If you encounter "Session is closed" errors during batch runs, run tasks sequentially or reduce concurrency.

### Additional Provider Examples

**Using OpenAI-compatible endpoints (local LLMs, Ollama, vLLM):**
```bash
source .venv/bin/activate
export DAYTONA_API_KEY=dtn_your-key
export API_KEY=your-key
export BASE_URL=http://localhost:8000/v1

harbor run -p tasks/01k7a12sd1nk15j08e6x0x7v9e-discord-trivia-approval-keyerror \
           -a cline-cli \
           -m openai:your-model-name \
           --env daytona \
           --force-build
```

**Comparing multiple models:**
```bash
# Test Sonnet 4.5 via Anthropic direct
export API_KEY=sk-ant-your-key
harbor run -p tasks -a cline-cli -m anthropic:claude-sonnet-4-5:1m --env daytona -n 200 -k 1 --max-retries 2 --force-build

# Test Sonnet 4 via OpenRouter
export API_KEY=sk-or-v1-your-key
harbor run -p tasks -a cline-cli -m openrouter:anthropic/claude-sonnet-4-20250514 --env daytona -n 200 -k 1 --max-retries 2 --force-build

# Test GPT-4 via OpenRouter
export API_KEY=sk-or-v1-your-key
harbor run -p tasks -a cline-cli -m openrouter:openai/gpt-4 --env daytona -n 200 -k 1 --max-retries 2 --force-build
```

## Interpreting Results

Results are written to `jobs/` directory:

```
jobs/
└── 2025-11-11__15-30-00/           # Job timestamp
    ├── config.json                 # Job configuration
    ├── result.json                 # Aggregate results
    └── <task-id>__<hash>/          # Trial directory
        ├── config.json             # Trial configuration
        ├── result.json             # Trial result (reward, timing, costs)
        ├── agent/                  # Agent execution logs
        │   ├── cline.txt           # Full conversation log
        │   ├── setup/              # Installation logs
        │   └── command-*/          # Shell command logs
        └── verifier/               # Test results
            ├── reward.txt          # 1 (pass) or 0 (fail)
            ├── test-stdout.txt     # Pytest output
            └── test-stderr.txt     # Pytest warnings
```

### Quick result check

```bash
# Find latest job
LATEST=$(ls -td jobs/2025-*/ | head -1)

# Check reward
cat ${LATEST}/*/verifier/reward.txt

# View test results
cat ${LATEST}/*/verifier/test-stdout.txt | grep -E "PASSED|FAILED"

# View agent conversation
tail -50 ${LATEST}/*/agent/cline.txt
```

## Scoring

Binary pass/fail:
- **reward = 1.0** - All tests pass
- **reward = 0.0** - Any test fails

This mirrors real-world standards: code either works or it doesn't.

## Resource Limits

Daytona Tier 3:
- Max memory per sandbox: 8GB
- All tasks validated to work within 8GB
- Complex tasks (Qt WASM, Android) take 20-30 minutes

## Common Issues

### Venv not activated

**Symptom:** `harbor: command not found` or wrong harbor version

**Fix:**
```bash
source .venv/bin/activate
which harbor  # Verify: should show .venv/bin/harbor
```

### Wrong Python version

**Symptom:** Installation errors or compatibility issues

**Fix:**
```bash
rm -rf .venv
uv venv --python 3.13
source .venv/bin/activate
uv tool install harbor
```

## Architecture

cline-bench uses [Harbor](https://harborframework.com), the official successor to Terminal-Bench:

- **Agent-agnostic** - Pre-integrated support for 10+ coding agents
- **Cloud-native** - Daytona, Modal, E2B integration
- **Flexible** - Docker compose for local, cloud for scale
- **Battle-tested** - Production-ready framework from Laude Institute

Harbor repository: https://github.com/laude-institute/harbor

## Citation

If you use cline-bench in your research:

```
@misc{cline-bench2025,
  title={cline-bench: Real-World Coding Benchmarks from Production Agent Sessions},
  author={[Your name/org]},
  year={2025},
  howpublished={\url{https://github.com/[your-repo]}}
}
```

## Support

For issues:
- Harbor framework: https://github.com/laude-institute/harbor/issues
- cline-bench tasks: https://github.com/cline/cline or reach out to [@pashmerepat](https://x.com/pashmerepat) on X

## Understanding Results

Harbor writes all execution data to the `jobs/` directory:

```
jobs/
└── 2025-11-11__10-47-23/           # Job timestamp
    ├── config.json                 # Job configuration
    ├── result.json                 # Aggregate results
    └── 01k7a12s...disco__fhSEuhr/  # Trial directory (task-id + hash)
        ├── config.json             # Trial config
        ├── result.json             # Trial result (reward, timing, costs)
        ├── agent/
        │   ├── cline.txt           # Full Cline conversation log
        │   ├── install.sh          # Generated installation script
        │   ├── setup/              # Agent installation phase
        │   │   ├── stdout.txt      # Installation output
        │   │   ├── stderr.txt      # Installation errors
        │   │   └── return-code.txt # Exit code (0 = success)
        │   ├── command-0/          # First command (config setup)
        │   │   ├── command.txt     # Command that ran
        │   │   └── return-code.txt
        │   └── command-1/          # Second command (cline execution)
        │       ├── command.txt
        │       ├── stdout.txt      # Same as cline.txt (tee'd)
        │       └── return-code.txt
        └── verifier/               # Test execution
            ├── reward.txt          # 1 (pass) or 0 (fail)
            ├── test-stdout.txt     # pytest output
            └── test-stderr.txt     # pytest warnings
```

### Quick Commands

```bash
# Find latest job
LATEST=$(ls -td jobs/2025-*/ | head -1)
echo "Latest: $LATEST"

# Check reward (1 = pass, 0 = fail)
cat ${LATEST}/*/verifier/reward.txt

# View test results
cat ${LATEST}/*/verifier/test-stdout.txt | tail -20

# Count passed/failed tests
grep -c "PASSED" ${LATEST}/*/verifier/test-stdout.txt
grep -c "FAILED" ${LATEST}/*/verifier/test-stdout.txt

# View Cline's last actions
tail -50 ${LATEST}/*/agent/cline.txt

# Check if agent installed successfully
cat ${LATEST}/*/agent/setup/return-code.txt  # Should be 0
```

### Example: Successful Run

```bash
$ cat jobs/2025-11-11__10-47-23/01k7a12s...disco__fhSEuhr/verifier/reward.txt
1

$ cat jobs/2025-11-11__10-47-23/01k7a12s...disco__fhSEuhr/verifier/test-stdout.txt | tail -3
PASSED test_approval_session_fix.py::test_approval_session_creation
PASSED test_approval_session_fix.py::test_trivia_approval_function
========================= 2 passed, 1 warning in 5.70s =========================
```

## Running Locally with Docker

Testing locally without running on Daytona cloud:

```bash
# Activate venv
source .venv/bin/activate

# Run Oracle (ground truth) to validate task
harbor run -p tasks/01k7a12sd1nk15j08e6x0x7v9e-discord-trivia-approval-keyerror \
           -a oracle \
           --env docker

# Run Cline CLI locally
export API_KEY=sk-ant-your-key
harbor run -p tasks/01k7a12sd1nk15j08e6x0x7v9e-discord-trivia-approval-keyerror \
           -a cline-cli \
           -m anthropic:claude-sonnet-4-5:1m \
           --env docker

# Run all tasks locally (sequential)
export API_KEY=sk-ant-your-key
harbor run -p tasks -a cline-cli -m anthropic:claude-sonnet-4-5:1m --env docker
```

**Local vs Cloud:**
- **Docker (local):** Slower, uses your machine resources, free
- **Daytona (cloud):** Faster, parallel execution, costs money

**Recommendation:** Test single tasks with Docker first, then scale to Daytona for batch evaluation.

### Modifying Cline's Agentic Loop

To modify Cline's behavior (system prompt, tools, API shapes like Responses API), you need to:

1. Create a PR to `cline/cline`
2. Set environment variable when running cline-cli in harbor with: export CUSTOM_CLINE_BUILD=<link-to-pr-here>


**Recommendation:** This process is more involved for early access. Wait for the GA release where this will be streamlined.
