# mindzie Project Controller Examples 🚀

**Zero-Configuration Python Samples** - All scripts now run out-of-the-box with just your API credentials!

This folder contains comprehensive example scripts that demonstrate the Project Controller functionality of the mindzie API. Every script is designed to work immediately without requiring specific project IDs or complex setup.

## 🎯 Quick Start (Zero Configuration)

1. **Set your credentials** (choose one method):
   ```bash
   # Method 1: Environment variables
   export MINDZIE_TENANT_ID="your-tenant-id"
   export MINDZIE_API_KEY="your-api-key"
   
   # Method 2: Create .env file in examples/ directory
   echo 'MINDZIE_TENANT_ID=your-tenant-id' > ../.env
   echo 'MINDZIE_API_KEY=your-api-key' >> ../.env
   ```

2. **Run any script immediately**:
   ```bash
   python get_project_details.py     # Auto-discovers and shows first project
   python compare_projects.py        # Auto-compares 2-3 projects
   python search_projects.py         # Shows all projects
   python project_statistics.py      # Analyzes all tenant projects
   ```

That's it! All scripts work out-of-the-box with intelligent defaults.

## 🤖 Smart Auto-Discovery

All scripts now feature **smart project discovery** with helpful messages:

```bash
$ python get_project_details.py
[INFO] Finding project, please wait...
[SUCCESS] Using project: 'AI Studio Development' (auto-selected)
          ID: 4315075c-b4d9-48c2-9520-cda63f04da7a
[TIP] To use a different project, run: python get_project_details.py <project_id>
```

```bash
$ python compare_projects.py
[INFO] Finding 3 projects for comparison, please wait...
[SUCCESS] Using projects: 'AI Studio', 'Insurance Claims', 'Python Demo' (auto-selected)
[TIP] To use a different project, run: python compare_projects.py --project-ids <id1> <id2>

====================================================================================================
PROJECT COMPARISON
====================================================================================================
Metric                  | AI Studio Development  | Insurance Claims        | Python Demo            
----------------------------------------------------------------------------------------------------
Most Datasets:    Python Demo (15 datasets)
Most Dashboards:  AI Studio Development (58 dashboards)
```

## 📋 Available Scripts

### 🔧 1. api_utils.py
**Utility functions and credential tester**

```bash
python api_utils.py                    # Test credentials and show available functions
```

**What it shows when run directly:**
- Explains what the utility file does
- Tests your API credentials
- Lists available projects
- Shows how to import utility functions

### 🌐 2. test_project_connectivity.py
**Test API connectivity and authentication** ✅ *Works out-of-the-box*

```bash
python test_project_connectivity.py   # No arguments needed!
```

- Tests both authenticated and unauthenticated ping endpoints
- Measures response times
- Verifies authentication is working correctly
- Perfect for debugging connection issues

### 📊 3. get_project_details.py
**Get comprehensive details for a project** 🤖 *Auto-discovery enabled*

```bash
# Zero-config: Auto-selects first project
python get_project_details.py

# Specific project: Use any project ID
python get_project_details.py 4315075c-b4d9-48c2-9520-cda63f04da7a
```

- **Auto-discovery**: Finds and uses your first available project
- Displays full project information including metadata, timestamps, and statistics
- Shows all available project fields with smart formatting
- Validates project ID format and handles errors gracefully

### 📈 4. get_project_summary.py
**Get summary statistics for a project** 🤖 *Auto-discovery enabled*

```bash
# Zero-config: Auto-selects first project
python get_project_summary.py

# Specific project: Use any project ID  
python get_project_summary.py bc7f6a6d-552d-44bf-b9f7-310adf733dc0
```

- **Auto-discovery**: Automatically picks your first available project
- Attempts to get project summary from dedicated endpoint
- Falls back to basic project info if summary not available
- Calculates insights like dashboard/dataset ratios

### 🔍 5. search_projects.py
**Search and filter projects** ✅ *Works out-of-the-box*

```bash
# Zero-config: Show all projects
python search_projects.py

# With filters: Search and filter as needed
python search_projects.py --name demo                    # Name contains "demo"
python search_projects.py --active                       # Only active projects
python search_projects.py --min-datasets 10              # At least 10 datasets
python search_projects.py --name ai --active --min-datasets 5  # Combined filters
```

**Available filters:**
- `--name <text>` - Filter by project name (case-insensitive partial match)
- `--active` / `--inactive` - Filter by project status
- `--min-datasets <n>` - Show projects with at least N datasets
- `--max-results <n>` - Limit number of results (default: 50)

### 📊 6. project_statistics.py
**Generate comprehensive tenant statistics** ✅ *Works out-of-the-box*

```bash
# Zero-config: Analyze all projects
python project_statistics.py

# With options: Get detailed analysis and export
python project_statistics.py --detailed                  # Detailed breakdowns
python project_statistics.py --export stats.csv         # Export to CSV
python project_statistics.py --detailed --export full_stats.csv  # Both
```

**Features:**
- **Tenant overview**: Total projects, active/inactive counts, activity rates
- **Content statistics**: Datasets, dashboards, notebooks, users across all projects
- **Health metrics**: Projects with data vs empty projects
- **Distribution analysis**: How content is distributed across projects
- **Top performers**: Projects ranked by datasets and dashboards
- **Timeline analysis**: Project creation patterns over time

### ⚖️ 7. compare_projects.py
**Compare multiple projects side-by-side** 🤖 *Auto-discovery enabled*

```bash
# Zero-config: Auto-compare first 2-3 projects
python compare_projects.py

# Specific projects by ID:
python compare_projects.py --project-ids 4315075c-b4d9-48c2-9520-cda63f04da7a bc7f6a6d-552d-44bf-b9f7-310adf733dc0

# Projects by name (partial matches):
python compare_projects.py --by-name "AI Studio" "Insurance Claims" "Python Demo"

# Mixed approach:
python compare_projects.py --by-name "AI Studio" --by-id bc7f6a6d-552d-44bf-b9f7-310adf733dc0
```

**Features:**
- **Auto-discovery**: Automatically selects 2-3 projects for comparison
- **Side-by-side table**: Clear comparison matrix
- **Key metrics**: Datasets, dashboards, notebooks, users, activity status
- **Smart analysis**: Identifies top performers and provides insights
- **Combined totals**: Aggregated statistics across all compared projects

## ✨ Key Features

### 🤖 Smart Auto-Discovery
- **Zero friction**: All scripts work immediately with just credentials
- **Intelligent selection**: Automatically picks appropriate projects
- **Helpful messages**: Clear feedback on what's happening
- **Easy customization**: Simple tips on how to use specific projects

### 🛡️ Robust Error Handling
- **Credential validation**: Clear messages for missing or invalid credentials
- **Connection testing**: Built-in connectivity verification
- **Graceful fallbacks**: Handles missing data and API variations
- **User-friendly errors**: Helpful error messages instead of cryptic stack traces

### 🔧 Developer-Friendly
- **Consistent interface**: All scripts follow the same patterns
- **Flexible usage**: Works with environment variables or .env files
- **Unicode safe**: Handles special characters in project names
- **Cross-platform**: Works on Windows, macOS, and Linux

## 🚀 Recommended Workflow

### Option 1: Zero-Config Explorer
```bash
# 1. Test your setup
python test_project_connectivity.py

# 2. Get the big picture
python project_statistics.py --detailed

# 3. Explore your first project
python get_project_details.py

# 4. Compare top projects
python compare_projects.py
```

### Option 2: Targeted Analysis
```bash
# 1. Find projects of interest
python search_projects.py --name "production" --active

# 2. Get details for specific projects
python get_project_details.py <project-id-from-search>

# 3. Compare specific projects
python compare_projects.py --project-ids <id1> <id2> <id3>

# 4. Export statistics
python project_statistics.py --detailed --export analysis.csv
```

## 🔗 Example Output

### Auto-Discovery in Action
```bash
$ python compare_projects.py
[INFO] Finding 3 projects for comparison, please wait...
[SUCCESS] Using projects: '_A Case Stage Development', '_Chairs', '_hl7_infusion_sample_2_3' (auto-selected)
[TIP] To use a different project, run: python compare_projects.py --project-ids <id1> <id2>

====================================================================================================
PROJECT COMPARISON
====================================================================================================
Metric                  | _A Case Stage Develo... | _Chairs                 | _hl7_infusion_sample...
----------------------------------------------------------------------------------------------------
Project ID              | b2ec01c6...4ee40dab     | a8807159...59fa922d     | 6bc25182...a9de3227    
Active Status           | Yes                     | Yes                     | Yes                    
Datasets                | 2                       | 2                       | 4                      
Dashboards              | 1                       | 2                       | 10                     
Created                 | 2025-01-23 17:35        | 2024-12-21 02:49        | 2025-03-05 13:26       

====================================================================================================
COMPARISON ANALYSIS
====================================================================================================

Most Datasets:    _hl7_infusion_sample_2_3 (4 datasets)
Most Dashboards:  _hl7_infusion_sample_2_3 (10 dashboards)
Activity: All 3 projects are active
```

## 🛠️ Technical Details

### Authentication
All scripts use Bearer token authentication:
```
Authorization: Bearer {api_key}
```

### API Endpoints Used
- `GET /api/project/unauthorized-ping` - Connectivity test (no auth)
- `GET /api/{tenantId}/project/ping` - Authenticated connectivity test  
- `GET /api/{tenantId}/project` - List all projects
- `GET /api/{tenantId}/project/{projectId}` - Get project details
- `GET /api/{tenantId}/project/{projectId}/summary` - Get project summary

### Error Recovery
- **Network timeouts**: 30-second timeout with clear error messages
- **Invalid credentials**: Specific guidance on credential setup
- **Missing projects**: Helpful suggestions for project creation
- **Unicode issues**: Windows-compatible output without special characters

## 🆘 Troubleshooting

### No Projects Found
```bash
[ERROR] No projects found. Create a project in mindzieStudio first.
        Visit https://dev.mindziestudio.com to create a project.
```
**Solution**: Log into mindzieStudio and create at least one project.

### Authentication Failed
```bash
[ERROR] No credentials found
Set MINDZIE_TENANT_ID and MINDZIE_API_KEY environment variables
```
**Solution**: Set your credentials using environment variables or .env file.

### Only One Project (for comparison)
```bash
[WARNING] Only 1 project found, need 2 for comparison.
          Create more projects in mindzieStudio to enable comparison.
```
**Solution**: Create additional projects to enable comparison features.

---

**🎉 Ready to explore? Just set your credentials and run any script - they all work out-of-the-box!**