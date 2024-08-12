# Receipt Processing with Multi-Agents

This project leverages CrewAI to design multiple agents for processing a receipt.

### Key Learnings

- Multi-agent processing can be slow.
- Non-deterministic results may lead to agent errors.
- Forecasting costs is challenging due to the unpredictable number of LLM queries made by each agent.

![screenshot](screenshot.png)

## Setup and Go

### Environment Setup

1. Create a virtual environment:
   ```shell
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Set your OpenAI API key:
   ```shell
   export OPENAI_API_KEY=<your-api-key>
   ```

3. Install the required packages:
   ```shell
   pip install -r requirements.txt
   ```

### Running a Test

To run a test, execute the following command:
```shell
python main.py ./example/1000-receipt.jpg
```
