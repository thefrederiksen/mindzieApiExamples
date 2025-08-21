# mindzie-api Examples

This directory contains example scripts demonstrating how to use the mindzie-api package.

## Installation

First, install the mindzie-api package:

```bash
# From PyPI (once published)
pip install mindzie-api

# Or install from local development
cd ..
pip install -e .
```

## Examples

### 1. hello_world.py - Simplest Example (No Auth Required)

The absolute minimum code to verify the package is working. No authentication required!

```bash
python hello_world.py
```

This example:
- Creates a client connection to the dev server
- Calls an unauthenticated ping endpoint
- Verifies the package is installed and working

**No API credentials needed for this example!**

### 2. hello_world_authenticated.py - Simple Authenticated Example

The simplest authenticated API call. Shows you exactly what credentials are needed.

```bash
# First, set your credentials:
set MINDZIE_TENANT_ID="your-tenant-id-here"
set MINDZIE_API_KEY="your-api-key-here"

# Then run:
python hello_world_authenticated.py
```

**Required Credentials:**
- **MINDZIE_TENANT_ID**: Your tenant identifier (GUID format)
- **MINDZIE_API_KEY**: Your API authentication key

If you run without credentials, the script shows detailed instructions on:
- Where to find these values in mindzieStudio
- How to set environment variables
- What format the values should be

### 3. basic_usage.py - Basic Authenticated Usage

A more comprehensive example showing authenticated API calls.

```bash
# Set your credentials first
set MINDZIE_TENANT_ID="your-tenant-id"
set MINDZIE_API_KEY="your-api-key"

python basic_usage.py
```

This example:
- Uses real authentication
- Lists projects
- Retrieves datasets
- Shows error handling

## Testing After pip Install

To test the package after installing from PyPI:

1. **Create a new virtual environment** (outside this project):
   ```bash
   cd %TEMP%
   python -m venv test_mindzie
   test_mindzie\Scripts\activate
   ```

2. **Install the package**:
   ```bash
   pip install mindzie-api
   ```

3. **Run the hello world test**:
   ```bash
   python -c "from mindzie_api import MindzieAPIClient; client = MindzieAPIClient('https://dev.mindziestudio.com', 'test', api_key='test'); print('Success! Package is working')"
   ```

4. **Or copy and run hello_world.py**:
   ```bash
   # Copy the hello_world.py file to your test directory
   python hello_world.py
   ```

## Troubleshooting

If examples don't work:

1. **Check package installation**:
   ```bash
   pip show mindzie-api
   python -c "import mindzie_api; print(mindzie_api.__version__)"
   ```

2. **Check network connectivity**:
   ```bash
   curl https://dev.mindziestudio.com/api/test/test/ping/unauthorized-ping
   ```

3. **For authenticated examples**, verify credentials:
   ```bash
   echo %MINDZIE_TENANT_ID%
   echo %MINDZIE_API_KEY%
   ```

## Additional Examples

### Projects
The `projects/` directory contains comprehensive examples for working with projects:
- `list_projects.py` - List and explore projects
- `get_project_details.py` - Get detailed project information
- `search_projects.py` - Search and filter projects
- `project_statistics.py` - Generate project analytics

### Actions
The `actions/` directory contains examples for working with action execution:

**Basic Examples:**
- `test_action_connectivity.py` - Test action endpoint connectivity
- `execute_action.py` - Execute actions and get results
- `list_actions.py` - Action discovery and guidance
- `get_action_executions.py` - Retrieve action execution history
- `get_last_execution.py` - Get the most recent execution
- `get_execution_details.py` - Detailed execution analysis
- `download_execution_package.py` - Download execution results
- `monitor_action_execution.py` - Real-time execution monitoring

**Advanced Examples:**
- `action_execution_workflow.py` - Complete execute → monitor → analyze → download workflow
- `compare_executions.py` - Compare multiple executions for performance analysis
- `action_statistics.py` - Comprehensive execution analytics and reporting

## More Examples Coming Soon

- Data upload example
- Dashboard creation example  
- Async operations example
- Error handling patterns
- Pagination example

---

For full documentation, visit: https://docs.mindzie.com/api/python