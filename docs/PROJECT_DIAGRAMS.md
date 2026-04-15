# Project Diagrams

## Mermaid

```mermaid
flowchart TB
    subgraph Frontend["Frontend / Next.js"]
        Home["/"]
        Merchant["/merchant"]
        Admin["/admin"]
        APIClient["frontend/lib/api.ts"]
    end

    subgraph Backend["Backend / FastAPI"]
        Main["backend/app/main.py"]
        Router["backend/app/api/v1/router.py"]
        ContentRoute["content routes"]
        AssetRoute["asset routes"]
        ReviewRoute["review routes"]
        ReportRoute["report routes"]
        JobRoute["job routes"]
        PublishRoute["publish routes"]
        AuditRoute["audit routes"]
        ObsRoute["observability routes"]
    end

    subgraph Domain["Services / Graph / Domain"]
        ContentSvc["ContentService"]
        AssetSvc["AssetService"]
        ReviewSvc["ReviewService"]
        ReportSvc["ReportService"]
        JobSvc["JobService"]
        PublishSvc["PublishService"]
        PublishResultSvc["PublishResultService"]
        AuditSvc["AuditService"]
        ObsSvc["ObservabilityService"]
        ContentGraph["LangGraph: content"]
        ReviewGraph["LangGraph: review"]
        StatusRules["status_rules.py"]
    end

    subgraph Storage["Current Runtime Storage"]
        MemoryRepo["MemoryRepository"]
        AuditLogs["audit_logs"]
        RequestLogs["request_logs"]
        PublishResults["publish_results"]
    end

    subgraph FutureInfra["Infra Scaffold"]
        Settings["core/settings.py"]
        SQLA["SQLAlchemy models / db session"]
        Celery["Celery worker"]
        Redis["Redis"]
        Postgres["PostgreSQL"]
        Docker["infra/docker-compose.yml"]
    end

    Home --> APIClient
    Merchant --> APIClient
    Admin --> APIClient

    APIClient --> Main
    Main --> Router
    Router --> ContentRoute
    Router --> AssetRoute
    Router --> ReviewRoute
    Router --> ReportRoute
    Router --> JobRoute
    Router --> PublishRoute
    Router --> AuditRoute
    Router --> ObsRoute

    ContentRoute --> ContentSvc
    AssetRoute --> AssetSvc
    ReviewRoute --> ReviewSvc
    ReportRoute --> ReportSvc
    JobRoute --> JobSvc
    PublishRoute --> PublishResultSvc
    AuditRoute --> AuditSvc
    ObsRoute --> ObsSvc

    ContentSvc --> ContentGraph
    ReviewSvc --> ReviewGraph
    ContentSvc --> PublishSvc
    ContentSvc --> StatusRules
    ReviewSvc --> StatusRules
    PublishSvc --> StatusRules

    ContentSvc --> MemoryRepo
    AssetSvc --> MemoryRepo
    ReviewSvc --> MemoryRepo
    ReportSvc --> MemoryRepo
    JobSvc --> MemoryRepo
    PublishSvc --> MemoryRepo
    PublishResultSvc --> PublishResults
    AuditSvc --> AuditLogs
    ObsSvc --> RequestLogs

    Settings --> Main
    Settings --> SQLA
    Settings --> Celery
    SQLA --> Postgres
    Celery --> Redis
    Docker --> Postgres
    Docker --> Redis
    Docker --> Celery
```

## Graphviz DOT

```dot
digraph HarnessFramework {
  rankdir=LR;
  node [shape=box, style=rounded];

  subgraph cluster_frontend {
    label="Frontend / Next.js";
    Home [label="/"];
    Merchant [label="/merchant"];
    Admin [label="/admin"];
    APIClient [label="frontend/lib/api.ts"];
  }

  subgraph cluster_backend {
    label="Backend / FastAPI";
    Main [label="backend/app/main.py"];
    Router [label="api/v1/router.py"];
    ContentRoute [label="content routes"];
    AssetRoute [label="asset routes"];
    ReviewRoute [label="review routes"];
    ReportRoute [label="report routes"];
    JobRoute [label="job routes"];
    PublishRoute [label="publish routes"];
    AuditRoute [label="audit routes"];
    ObsRoute [label="observability routes"];
  }

  subgraph cluster_domain {
    label="Services / Domain";
    ContentSvc [label="ContentService"];
    AssetSvc [label="AssetService"];
    ReviewSvc [label="ReviewService"];
    ReportSvc [label="ReportService"];
    JobSvc [label="JobService"];
    PublishSvc [label="PublishService"];
    PublishResultSvc [label="PublishResultService"];
    AuditSvc [label="AuditService"];
    ObsSvc [label="ObservabilityService"];
    ContentGraph [label="LangGraph content"];
    ReviewGraph [label="LangGraph review"];
    StatusRules [label="status_rules.py"];
  }

  subgraph cluster_storage {
    label="Current Storage";
    MemoryRepo [label="MemoryRepository"];
    PublishResults [label="publish_results"];
    AuditLogs [label="audit_logs"];
    RequestLogs [label="request_logs"];
  }

  subgraph cluster_future {
    label="Infra Scaffold";
    Settings [label="core/settings.py"];
    SQLA [label="SQLAlchemy / db session"];
    Celery [label="Celery worker"];
    Redis [label="Redis"];
    Postgres [label="PostgreSQL"];
  }

  Home -> APIClient;
  Merchant -> APIClient;
  Admin -> APIClient;

  APIClient -> Main;
  Main -> Router;
  Router -> ContentRoute;
  Router -> AssetRoute;
  Router -> ReviewRoute;
  Router -> ReportRoute;
  Router -> JobRoute;
  Router -> PublishRoute;
  Router -> AuditRoute;
  Router -> ObsRoute;

  ContentRoute -> ContentSvc;
  AssetRoute -> AssetSvc;
  ReviewRoute -> ReviewSvc;
  ReportRoute -> ReportSvc;
  JobRoute -> JobSvc;
  PublishRoute -> PublishResultSvc;
  AuditRoute -> AuditSvc;
  ObsRoute -> ObsSvc;

  ContentSvc -> ContentGraph;
  ReviewSvc -> ReviewGraph;
  ContentSvc -> PublishSvc;
  ContentSvc -> StatusRules;
  ReviewSvc -> StatusRules;
  PublishSvc -> StatusRules;

  ContentSvc -> MemoryRepo;
  AssetSvc -> MemoryRepo;
  ReviewSvc -> MemoryRepo;
  ReportSvc -> MemoryRepo;
  JobSvc -> MemoryRepo;
  PublishSvc -> MemoryRepo;
  PublishResultSvc -> PublishResults;
  AuditSvc -> AuditLogs;
  ObsSvc -> RequestLogs;

  Settings -> Main;
  Settings -> SQLA;
  Settings -> Celery;
  SQLA -> Postgres;
  Celery -> Redis;
}
```

## System Sequence

```mermaid
sequenceDiagram
    autonumber
    actor Merchant as Merchant UI
    participant Frontend as Next.js Frontend
    participant API as FastAPI API
    participant ContentSvc as ContentService
    participant ContentGraph as LangGraph Content Graph
    participant Repo as MemoryRepository
    participant Audit as AuditService

    Merchant->>Frontend: Fill form + upload asset metadata
    Frontend->>API: POST /assets/upload-init
    API->>Repo: Save source asset
    API->>Audit: Record asset.upload_init
    API-->>Frontend: asset_id

    Merchant->>Frontend: Submit content request
    Frontend->>API: POST /contents/generate
    API->>ContentSvc: generate()
    ContentSvc->>ContentGraph: run_content_graph()
    ContentGraph-->>ContentSvc: title/body/hashtags
    ContentSvc->>Repo: Save content + job
    ContentSvc->>Audit: Record content.generate
    API-->>Frontend: draft response
```

## Content Flow

```mermaid
flowchart LR
    A[Merchant Form Input] --> B[frontend/lib/api.ts]
    B --> C[POST /api/v1/contents/generate]
    C --> D[ContentService.generate]
    D --> E[Asset Ownership Validation]
    E --> F[LangGraph Content Graph]
    F --> G[Draft Content Fields]
    G --> H[Save content in repository]
    H --> I[Create content_generate job]
    I --> J[Write audit log]
    J --> K[Return draft response]
```

## Publish And Variant Flow

```mermaid
flowchart TB
    A[Admin UI] --> B[POST /contents/{id}/publish]
    B --> C[ContentService.publish]
    C --> D[PublishService.publish_content]
    D --> E{Approved Content?}
    E -- No --> X[409 CONTENT_NOT_APPROVED]
    E -- Yes --> F{apply_image_variant?}
    F -- No --> H[Create publish job]
    F -- Yes --> G[Nano Banana Stub Adapter]
    G --> G1[Create variant assets]
    G1 --> G2[Create image_variant_generate job]
    G2 --> H[Create publish job]
    H --> I{Platform == blog?}
    I -- Yes --> J[blog_publish_adapter.publish_post]
    I -- No --> K[internal_stub result]
    J --> L[Save publish_result]
    K --> L[Save publish_result]
    L --> M[Update content status scheduled]
    M --> N[Write audit log]
    N --> O[Return publish response]
```

## Review Approval Flow

```mermaid
sequenceDiagram
    autonumber
    participant Webhook as Review Webhook
    participant API as FastAPI API
    participant ReviewSvc as ReviewService
    participant ReviewGraph as LangGraph Review Graph
    participant Repo as MemoryRepository
    participant Admin as Admin UI
    participant Audit as AuditService

    Webhook->>API: POST /webhooks/reviews
    API->>ReviewSvc: ingest()
    ReviewSvc->>ReviewGraph: run_review_graph()
    ReviewGraph-->>ReviewSvc: sensitivity + reply_draft + escalated
    ReviewSvc->>Repo: Save review + job
    ReviewSvc->>Audit: Record review.ingest_webhook
    API-->>Admin: review_id available

    Admin->>API: POST /reviews/{id}/approve-reply
    API->>ReviewSvc: approve_reply()
    ReviewSvc->>Repo: Update review status approved
    ReviewSvc->>Audit: Record review.approve_reply
    API-->>Admin: approved reply response
```

## Audit And Observability Flow

```mermaid
flowchart LR
    A[Incoming HTTP Request] --> B[FastAPI Middleware]
    B --> C[Assign request_id]
    C --> D[Call route handler]
    D --> E[Service action]
    E --> F{Sensitive action?}
    F -- Yes --> G[AuditService.record]
    F -- No --> H[Skip audit write]
    G --> I[audit_logs store]
    H --> J[Build response]
    I --> J
    J --> K[request_logs store]
    K --> L[Add X-Request-Id header]
    L --> M[Admin observability UI]
```

## Worker And Infra Flow

```dot
digraph RuntimeFlow {
  rankdir=TB;
  node [shape=box, style=rounded];

  Frontend [label="Next.js frontend"];
  API [label="FastAPI app"];
  Settings [label="Settings / .env"];
  Repo [label="Current: MemoryRepository"];
  DB [label="Future: PostgreSQL + SQLAlchemy"];
  Worker [label="Celery worker"];
  Broker [label="Redis broker/result backend"];
  Docker [label="docker-compose"];

  Frontend -> API;
  Settings -> API;
  Settings -> Worker;
  API -> Repo;
  API -> Worker [label="future async jobs"];
  Worker -> Broker;
  Worker -> DB;
  API -> DB [label="future persistence"];
  Docker -> API;
  Docker -> Worker;
  Docker -> Broker;
  Docker -> DB;
}
```
