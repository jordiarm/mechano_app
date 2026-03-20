CODE_SNIPPETS = [
    {
        "title": "Python — List Comprehension",
        "language": "python",
        "text": "results = [item.strip().lower() for item in raw_data if item and len(item) > 3]",
    },
    {
        "title": "Python — Dictionary Merge",
        "language": "python",
        "text": "config = {**defaults, **overrides, 'debug': True, 'port': int(os.environ.get('PORT', 8080))}",
    },
    {
        "title": "Python — Context Manager",
        "language": "python",
        "text": "with open(path, 'r', encoding='utf-8') as f: data = json.load(f); print(f'Loaded {len(data)} items')",
    },
    {
        "title": "Python — Lambda Sort",
        "language": "python",
        "text": "users.sort(key=lambda u: (u['role'] != 'admin', -u['score'], u['name'].lower()))",
    },
    {
        "title": "Python — Decorator",
        "language": "python",
        "text": "def retry(max_attempts=3): def decorator(func): @wraps(func) def wrapper(*args, **kwargs): pass return wrapper return decorator",
    },
    {
        "title": "Python — Exception Handling",
        "language": "python",
        "text": "try: result = conn.execute(query, params).fetchone() except (sqlite3.OperationalError, sqlite3.IntegrityError) as e: logger.error(f'DB error: {e}')",
    },
    {
        "title": "JavaScript — Array Methods",
        "language": "javascript",
        "text": "const active = users.filter(u => u.status === 'active').map(u => ({...u, label: `${u.name} <${u.email}>`}));",
    },
    {
        "title": "JavaScript — Destructuring",
        "language": "javascript",
        "text": "const {data: {users = [], total}, status} = await fetch('/api/users?limit=50').then(r => r.json());",
    },
    {
        "title": "JavaScript — Promise Chain",
        "language": "javascript",
        "text": "fetch(url, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)}).then(r => r.json());",
    },
    {
        "title": "JavaScript — Template Literal",
        "language": "javascript",
        "text": 'const html = `<div class="${cls}" data-id="${item.id}">${escapeHtml(item.name)}</div>`;',
    },
    {
        "title": "JavaScript — Event Listener",
        "language": "javascript",
        "text": "document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && modal.classList.contains('active')) modal.remove(); });",
    },
    {
        "title": "SQL — Window Function",
        "language": "sql",
        "text": "SELECT id, name, salary, RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rank FROM employees WHERE active = 1;",
    },
    {
        "title": "SQL — CTE with Aggregation",
        "language": "sql",
        "text": "WITH daily AS (SELECT date_trunc('day', ts) AS dt, COUNT(*) AS cnt FROM events GROUP BY 1) SELECT dt, cnt, AVG(cnt) OVER (ORDER BY dt ROWS 6 PRECEDING) AS avg_7d FROM daily;",
    },
    {
        "title": "SQL — Subquery Join",
        "language": "sql",
        "text": "SELECT u.name, o.total FROM users u JOIN (SELECT user_id, SUM(amount) AS total FROM orders WHERE status != 'cancelled' GROUP BY user_id) o ON u.id = o.user_id;",
    },
    {
        "title": "Shell — Pipeline",
        "language": "shell",
        "text": "cat access.log | grep 'POST /api' | awk '{print $1}' | sort | uniq -c | sort -rn | head -20",
    },
    {
        "title": "Shell — Docker Build",
        "language": "shell",
        "text": "docker build -t myapp:$(git rev-parse --short HEAD) . && docker push registry.io/myapp:$(git rev-parse --short HEAD)",
    },
    {
        "title": "Shell — Find and Replace",
        "language": "shell",
        "text": "find . -name '*.py' -exec grep -l 'old_func' {} \\; | xargs sed -i 's/old_func/new_func/g'",
    },
    {
        "title": "TypeScript — Generic Function",
        "language": "typescript",
        "text": "function groupBy<T, K extends string>(items: T[], key: (item: T) => K): Record<K, T[]> { return {} as Record<K, T[]>; }",
    },
    {
        "title": "CSS — Grid Layout",
        "language": "css",
        "text": ".dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; padding: 24px; }",
    },
    {
        "title": "HTML — Form Input",
        "language": "html",
        "text": '<input type="email" name="user_email" placeholder="you@example.com" required autocomplete="off" class="form-input" />',
    },
    {
        "title": "Go — Error Handling",
        "language": "go",
        "text": 'data, err := json.Marshal(payload); if err != nil { return fmt.Errorf("marshal failed: %w", err) }',
    },
    {
        "title": "Rust — Match Expression",
        "language": "rust",
        "text": "match response.status() { 200..=299 => Ok(response.json().await?), 404 => Err(Error::NotFound), _ => Err(Error::Server(response.status())), }",
    },
    {
        "title": "YAML — CI Pipeline",
        "language": "yaml",
        "text": "steps: - name: test run: pytest -v --tb=short - name: build run: docker build -t ${{ github.sha }} . env: REGISTRY: ghcr.io",
    },
    {
        "title": "JSON — Config Object",
        "language": "json",
        "text": '{"database": {"host": "localhost", "port": 5432, "name": "app_db", "pool": {"min": 2, "max": 10, "timeout": 30}}}',
    },
    {
        "title": "Regex — URL Validation",
        "language": "regex",
        "text": "^https?:\\/\\/(www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b([-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$",
    },
]
