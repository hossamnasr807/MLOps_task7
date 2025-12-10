graph TD
    %% Nodes
    Start((Start))
    Sup[("👮 Supervisor<br>(Router)"))]
    Res[("🔎 Researcher<br>(Agent)")]
    Wri[("✍️ Writer<br>(Agent)")]
    End((End))

    %% Edge Connections
    Start --> Sup
    
    %% Supervisor Decision Logic
    Sup -- "No Data?" --> Res
    Sup -- "Has Data?" --> Wri
    Sup -- "Has Report?" --> End

    %% Returns to Supervisor
    Res --> Sup
    Wri --> Sup

    %% Styling
    style Sup fill:#f9f,stroke:#333,stroke-width:2px
    style Res fill:#bbf,stroke:#333
    style Wri fill:#bfb,stroke:#333