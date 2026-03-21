# Splunk MCP Server - Mermaid Architecture Diagrams

This document contains interactive Mermaid diagrams that can be viewed in GitHub, VS Code (with Mermaid extension), or online at https://mermaid.live/

## 1. System Architecture Overview

```mermaid
graph TB
    subgraph "IBM ICA Agentic Framework"
        ICA_ORCH[IBM Concert Orchestration]
        ICA_REG[Agent Registry]
        ICA_SCHED[Task Scheduler]
        ICA_WF[Workflow Engine]
        
        ICA_ORCH --> ICA_REG
        ICA_ORCH --> ICA_SCHED
        ICA_ORCH --> ICA_WF
        
        COLLAB_BUS[Multi-Agent Collaboration Bus]
        
        SEC_AGENT[Security Agent]
        ANAL_AGENT[Analytics Agent]
        INC_AGENT[Incident Response Agent]
        
        ICA_ORCH --> COLLAB_BUS
        COLLAB_BUS --> SEC_AGENT
        COLLAB_BUS --> ANAL_AGENT
        COLLAB_BUS --> INC_AGENT
        
        SPLUNK_MCP_AGENT[Splunk MCP Agent<br/>Integration Point]
        
        SEC_AGENT --> SPLUNK_MCP_AGENT
        ANAL_AGENT --> SPLUNK_MCP_AGENT
        INC_AGENT --> SPLUNK_MCP_AGENT
    end
    
    subgraph "Client Layer"
        CLAUDE[Claude Desktop<br/>stdio mode]
        HTTP[HTTP Clients<br/>curl, etc]
        MCP_CLIENT[MCP Clients<br/>custom]
    end
    
    subgraph "Transport Layer"
        STDIO[stdio Protocol]
        SSE[SSE Protocol<br/>HTTP/Server-Sent Events]
    end
    
    subgraph "MCP Server Core"
        FASTMCP[FastMCP Framework]
        ROUTER[Tool Registry & Router]
        FASTMCP --> ROUTER
    end
    
    subgraph "Tool Layer"
        SEARCH[search_splunk]
        LIST_IDX[list_splunk_indexes]
        GET_APPS[get_splunk_apps]
        SAVED_SEARCH[get_saved_searches]
        RUN_SAVED[run_saved_search]
        GET_INFO[get_splunk_info]
    end
    
    subgraph "Integration Layer"
        SDK[Splunk SDK<br/>splunklib.client]
        CONN[Connection Manager]
        SDK --> CONN
    end
    
    subgraph "Splunk Instance"
        API[Management API<br/>Port 8089]
        SEARCH_ENG[Search Engine<br/>SPL Processing]
        INDEXES[Indexes<br/>Data Store]
        APPS[Apps & Add-ons]
        
        API --> SEARCH_ENG
        SEARCH_ENG --> INDEXES
        API --> APPS
    end
    
    %% Connections
    SPLUNK_MCP_AGENT -.MCP Protocol.-> FASTMCP
    CLAUDE --> STDIO
    HTTP --> SSE
    MCP_CLIENT --> SSE
    
    STDIO --> FASTMCP
    SSE --> FASTMCP
    
    ROUTER --> SEARCH
    ROUTER --> LIST_IDX
    ROUTER --> GET_APPS
    ROUTER --> SAVED_SEARCH
    ROUTER --> RUN_SAVED
    ROUTER --> GET_INFO
    
    SEARCH --> SDK
    LIST_IDX --> SDK
    GET_APPS --> SDK
    SAVED_SEARCH --> SDK
    RUN_SAVED --> SDK
    GET_INFO --> SDK
    
    CONN -.REST API.-> API
    
    style ICA_ORCH fill:#e1f5ff
    style COLLAB_BUS fill:#fff3e0
    style SPLUNK_MCP_AGENT fill:#c8e6c9
    style FASTMCP fill:#f3e5f5
    style SDK fill:#ffe0b2
    style API fill:#ffccbc
```

## 2. IBM ICA Agent Workflows

### Security Agent Workflow

```mermaid
sequenceDiagram
    participant SA as Security Agent
    participant ICA as ICA Orchestrator
    participant MCP as Splunk MCP Server
    participant Splunk as Splunk Instance
    
    Note over SA: 1. Threat Detection
    SA->>MCP: search_splunk()<br/>Query: failed_login
    MCP->>Splunk: Execute SPL Query
    Splunk-->>MCP: Results: 150 failed logins
    MCP-->>SA: Anomaly Detected
    
    Note over SA: 2. Investigation
    SA->>ICA: Request Correlation
    ICA->>SA: Approved
    SA->>MCP: search_splunk()<br/>Query: source_ip=suspicious
    MCP->>Splunk: Execute SPL Query
    Splunk-->>MCP: Results: Multiple attacks
    MCP-->>SA: Threat Confirmed
    
    Note over SA: 3. Automated Response
    SA->>MCP: run_saved_search()<br/>Name: Block_IP_Playbook
    MCP->>Splunk: Execute Saved Search
    Splunk-->>MCP: Playbook Executed
    MCP-->>SA: IP Blocked
    SA->>ICA: Incident Resolved
```

### Analytics Agent Workflow

```mermaid
sequenceDiagram
    participant AA as Analytics Agent
    participant MCP as Splunk MCP Server
    participant Splunk as Splunk Instance
    
    Note over AA: Performance Monitoring
    AA->>MCP: get_splunk_info()
    MCP->>Splunk: Get Server Info
    Splunk-->>MCP: Server Status
    MCP-->>AA: Health: OK
    
    Note over AA: Trend Analysis
    AA->>MCP: search_splunk()<br/>Query: timechart count
    MCP->>Splunk: Execute SPL Query
    Splunk-->>MCP: Time Series Data
    MCP-->>AA: Trend Data
    AA->>AA: Analyze Patterns
    
    Note over AA: Capacity Planning
    AA->>MCP: list_splunk_indexes()
    MCP->>Splunk: Get Index Info
    Splunk-->>MCP: Index Sizes & Counts
    MCP-->>AA: Capacity Metrics
    AA->>AA: Predict Growth
```

### Incident Response Agent Workflow

```mermaid
sequenceDiagram
    participant IRA as Incident Response Agent
    participant ICA as ICA Orchestrator
    participant MCP as Splunk MCP Server
    participant Splunk as Splunk Instance
    
    Note over IRA: Alert Triage
    IRA->>MCP: get_saved_searches()
    MCP->>Splunk: List Saved Searches
    Splunk-->>MCP: Alert Definitions
    MCP-->>IRA: Active Alerts
    
    Note over IRA: Context Gathering
    IRA->>MCP: search_splunk()<br/>Query: alert_criteria
    MCP->>Splunk: Execute SPL Query
    Splunk-->>MCP: Incident Timeline
    MCP-->>IRA: Context Data
    
    Note over IRA: Automated Response
    IRA->>ICA: Request Approval
    ICA-->>IRA: Approved
    IRA->>MCP: run_saved_search()<br/>Name: Incident_Playbook
    MCP->>Splunk: Execute Playbook
    Splunk-->>MCP: Remediation Complete
    MCP-->>IRA: Incident Resolved
```

## 3. Multi-Agent Collaboration

```mermaid
graph TB
    subgraph "Time: T0 - Detection"
        ALERT[Alert Triggered]
    end
    
    subgraph "ICA Orchestration"
        ORCH[ICA Orchestrator]
        COLLAB[Collaboration Bus]
    end
    
    subgraph "Coordinated Response"
        SA[Security Agent<br/>Threat Hunt]
        AA[Analytics Agent<br/>Correlate Data]
        IRA[Incident Agent<br/>Remediate]
        CA[Compliance Agent<br/>Audit Log]
    end
    
    subgraph "Splunk MCP Server"
        MCP[MCP Server<br/>Concurrent Requests]
    end
    
    subgraph "Splunk Instance"
        SPLUNK[Splunk<br/>Parallel Execution]
    end
    
    ALERT --> ORCH
    ORCH --> COLLAB
    
    COLLAB --> SA
    COLLAB --> AA
    COLLAB --> IRA
    COLLAB --> CA
    
    SA -.search_splunk.-> MCP
    AA -.search_splunk.-> MCP
    IRA -.run_saved_search.-> MCP
    CA -.search_splunk.-> MCP
    
    MCP --> SPLUNK
    
    SPLUNK -.Results.-> MCP
    MCP -.Data.-> SA
    MCP -.Data.-> AA
    MCP -.Data.-> IRA
    MCP -.Data.-> CA
    
    SA --> COLLAB
    AA --> COLLAB
    IRA --> COLLAB
    CA --> COLLAB
    
    COLLAB --> ORCH
    
    style ALERT fill:#ffcdd2
    style ORCH fill:#e1f5ff
    style COLLAB fill:#fff3e0
    style MCP fill:#c8e6c9
    style SPLUNK fill:#ffccbc
```

## 4. Data Flow - Search Query

```mermaid
flowchart LR
    USER[User/Agent<br/>Request]
    
    subgraph "Request"
        REQ[Search Query<br/>index=main error<br/>earliest=-1h]
    end
    
    subgraph "MCP Server"
        MCP[MCP Server<br/>Receive Request]
        TOOL[search_splunk<br/>Tool Handler]
    end
    
    subgraph "Splunk Integration"
        SDK[Splunk SDK<br/>Create Job]
        API[REST API<br/>POST /search/jobs]
    end
    
    subgraph "Splunk Processing"
        ENGINE[Search Engine<br/>Parse SPL]
        EXEC[Execute Query<br/>Scan Indexes]
        DATA[Fetch Data<br/>Apply Filters]
    end
    
    subgraph "Response"
        FORMAT[Format Results<br/>JSON]
        RETURN[Return to User<br/>100 events]
    end
    
    USER --> REQ
    REQ --> MCP
    MCP --> TOOL
    TOOL --> SDK
    SDK --> API
    API --> ENGINE
    ENGINE --> EXEC
    EXEC --> DATA
    DATA --> FORMAT
    FORMAT --> RETURN
    RETURN --> USER
    
    style USER fill:#e3f2fd
    style MCP fill:#f3e5f5
    style SDK fill:#fff3e0
    style ENGINE fill:#ffccbc
    style RETURN fill:#c8e6c9
```

## 5. Deployment Architecture

### Cloud Deployment (Render.com)

```mermaid
graph TB
    subgraph "Clients"
        AGENTS[ICA Agents]
        USERS[Users]
        APPS[Applications]
    end
    
    INTERNET[Internet<br/>HTTPS]
    
    subgraph "Render.com Platform"
        CDN[CDN/SSL<br/>Auto-Certificates]
        
        subgraph "Container"
            MCP[MCP Server<br/>Python App]
            ENV[Environment<br/>Variables]
            HEALTH[Health Check<br/>/sse endpoint]
            
            MCP --- ENV
            MCP --- HEALTH
        end
        
        LOGS[Logs &<br/>Monitoring]
        AUTO[Auto-Deploy<br/>from Git]
    end
    
    subgraph "Splunk"
        CLOUD[Splunk Cloud<br/>or Enterprise]
        API[Management API<br/>Port 8089]
        
        CLOUD --- API
    end
    
    AGENTS --> INTERNET
    USERS --> INTERNET
    APPS --> INTERNET
    
    INTERNET --> CDN
    CDN --> MCP
    
    MCP -.REST API.-> API
    
    MCP --> LOGS
    AUTO -.Deploy.-> MCP
    
    style CDN fill:#e1f5ff
    style MCP fill:#c8e6c9
    style ENV fill:#fff3e0
    style CLOUD fill:#ffccbc
```

### Local Development

```mermaid
graph LR
    subgraph "Developer Machine"
        IDE[VS Code<br/>Development]
        LOCAL[MCP Server<br/>localhost:8000]
        ENV_FILE[.env File<br/>Credentials]
        
        IDE --> LOCAL
        LOCAL --- ENV_FILE
    end
    
    subgraph "Splunk Instance"
        SPLUNK[Splunk Enterprise<br/>On-Premise]
        PORT[Port 8089<br/>Management API]
        
        SPLUNK --- PORT
    end
    
    LOCAL -.HTTPS/HTTP.-> PORT
    
    style IDE fill:#e3f2fd
    style LOCAL fill:#c8e6c9
    style SPLUNK fill:#ffccbc
```

## 6. Tool Architecture

```mermaid
graph TB
    subgraph "MCP Tools"
        SEARCH[search_splunk<br/>Execute SPL Queries]
        LIST[list_splunk_indexes<br/>Get Index Info]
        APPS[get_splunk_apps<br/>List Applications]
        SAVED[get_saved_searches<br/>List Saved Searches]
        RUN[run_saved_search<br/>Execute by Name]
        INFO[get_splunk_info<br/>Server Information]
    end
    
    subgraph "Common Functions"
        CONN[get_splunk_service<br/>Connection Factory]
        ERROR[Error Handling<br/>Try/Catch]
        FORMAT[Response Formatting<br/>JSON Structure]
    end
    
    subgraph "Splunk SDK"
        CLIENT[splunklib.client<br/>Service Connection]
        JOBS[jobs.create<br/>Search Jobs]
        RESULTS[results.JSONResultsReader<br/>Parse Results]
    end
    
    SEARCH --> CONN
    LIST --> CONN
    APPS --> CONN
    SAVED --> CONN
    RUN --> CONN
    INFO --> CONN
    
    CONN --> CLIENT
    
    SEARCH --> JOBS
    RUN --> JOBS
    
    JOBS --> RESULTS
    
    SEARCH --> ERROR
    LIST --> ERROR
    APPS --> ERROR
    SAVED --> ERROR
    RUN --> ERROR
    INFO --> ERROR
    
    ERROR --> FORMAT
    
    style SEARCH fill:#e3f2fd
    style CONN fill:#fff3e0
    style CLIENT fill:#ffccbc
    style FORMAT fill:#c8e6c9
```

## 7. Security Architecture

```mermaid
graph TB
    subgraph "Security Layers"
        subgraph "Transport Security"
            TLS[HTTPS/TLS<br/>Encrypted Transport]
            STDIO[Secure stdio<br/>Local Channel]
        end
        
        subgraph "Authentication"
            CREDS[Splunk Credentials<br/>Username/Password]
            TOKEN[Token-Based Auth<br/>Future Enhancement]
        end
        
        subgraph "Authorization"
            RBAC[Splunk RBAC<br/>Role-Based Access]
            INDEX_PERM[Index Permissions<br/>Data Access Control]
        end
        
        subgraph "Data Protection"
            ENV_VARS[Environment Variables<br/>Secure Storage]
            NO_LOG[No Credential Logging<br/>Security Policy]
        end
    end
    
    subgraph "MCP Server"
        SERVER[MCP Server<br/>Application]
    end
    
    subgraph "Splunk"
        SPLUNK_API[Splunk API<br/>Secure Endpoint]
    end
    
    TLS --> SERVER
    STDIO --> SERVER
    
    SERVER --> CREDS
    SERVER --> TOKEN
    
    CREDS --> SPLUNK_API
    TOKEN -.Future.-> SPLUNK_API
    
    SPLUNK_API --> RBAC
    RBAC --> INDEX_PERM
    
    SERVER --- ENV_VARS
    SERVER --- NO_LOG
    
    style TLS fill:#c8e6c9
    style RBAC fill:#fff3e0
    style ENV_VARS fill:#e1f5ff
    style SPLUNK_API fill:#ffccbc
```

## 8. Integration Patterns

```mermaid
graph TB
    subgraph "Pattern 1: Direct Integration"
        AGENT1[ICA Agent]
        MCP1[MCP Server]
        SPLUNK1[Splunk]
        
        AGENT1 -->|MCP Protocol| MCP1
        MCP1 -->|REST API| SPLUNK1
    end
    
    subgraph "Pattern 2: Orchestrated Multi-Agent"
        ORCH[ICA Orchestrator]
        
        SA2[Security Agent]
        AA2[Analytics Agent]
        IA2[Incident Agent]
        
        MCP2[MCP Server<br/>Shared Resource]
        SPLUNK2[Splunk]
        
        ORCH --> SA2
        ORCH --> AA2
        ORCH --> IA2
        
        SA2 --> MCP2
        AA2 --> MCP2
        IA2 --> MCP2
        
        MCP2 --> SPLUNK2
    end
    
    subgraph "Pattern 3: Event-Driven"
        SPLUNK3[Splunk Events]
        MCP3[MCP Server<br/>Event Listener]
        BUS[ICA Event Bus]
        
        AGENTS3[Multiple Agents<br/>Subscribers]
        
        SPLUNK3 -->|Alerts| MCP3
        MCP3 -->|Publish| BUS
        BUS -->|Notify| AGENTS3
    end
    
    style ORCH fill:#e1f5ff
    style MCP2 fill:#c8e6c9
    style BUS fill:#fff3e0
```

## How to View These Diagrams

### Option 1: GitHub (Automatic Rendering)
- Push this file to GitHub
- GitHub automatically renders Mermaid diagrams

### Option 2: VS Code
1. Install "Markdown Preview Mermaid Support" extension
2. Open this file
3. Press `Cmd+Shift+V` (Mac) or `Ctrl+Shift+V` (Windows/Linux)

### Option 3: Mermaid Live Editor
1. Visit https://mermaid.live/
2. Copy any diagram code
3. Paste and view/edit interactively
4. Export as PNG or SVG

### Option 4: Export to Images
```bash
# Install mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Convert to PNG
mmdc -i MERMAID_DIAGRAMS.md -o mermaid_output.png
```

## Diagram Features

- ✅ **Interactive**: Clickable and zoomable
- ✅ **Scalable**: Vector-based, crisp at any size
- ✅ **Editable**: Easy to modify and update
- ✅ **Version Control**: Text-based, perfect for Git
- ✅ **Multiple Formats**: Can export to PNG, SVG, PDF
- ✅ **Responsive**: Adapts to different screen sizes
- ✅ **Professional**: Clean, modern appearance

These Mermaid diagrams provide a comprehensive visual representation of the Splunk MCP Server architecture integrated with IBM ICA Agentic Framework!