import json
import random
import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, g, jsonify, render_template, request

app = Flask(__name__)
DATABASE = Path(__file__).parent / "mechano.db"

WORD_POOL = [
    # Common English words
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "I",
    "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
    "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
    "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
    "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
    "when", "make", "can", "like", "time", "no", "just", "him", "know", "take",
    "people", "into", "year", "your", "good", "some", "could", "them", "see",
    "other", "than", "then", "now", "look", "only", "come", "its", "over",
    "think", "also", "back", "after", "use", "two", "how", "our", "work",
    "first", "well", "way", "even", "new", "want", "because", "any", "these",
    "give", "day", "most", "us", "great", "between", "need", "large", "often",
    "hand", "high", "place", "hold", "free", "real", "life", "each", "night",
    "write", "become", "here", "show", "house", "both", "head", "long", "door",
    "thing", "own", "still", "learn", "should", "world", "system", "while",
    "program", "point", "school", "number", "never", "begin", "state", "city",
    "under", "start", "might", "story", "every", "move", "always", "young",
    "close", "public", "keep", "follow", "change", "bring", "watch", "spell",
    "animal", "letter", "mother", "answer", "found", "study",
    "plant", "cover", "food", "earth", "eye", "light", "thought",
    "together", "group", "important", "children", "side", "feet", "car",
    "mile", "walk", "white", "sea", "hard", "open", "difficult",
    "left", "example", "paper", "music", "power", "computer", "development",
    # More common English words
    "again", "away", "before", "below", "between", "came", "does", "down",
    "during", "end", "far", "find", "form", "help", "home", "kind",
    "last", "line", "live", "many", "mean", "men", "much", "must",
    "name", "next", "off", "old", "once", "order", "own", "part",
    "play", "put", "read", "right", "run", "same", "set", "small",
    "such", "sure", "tell", "three", "through", "turn", "very", "water",
    "where", "word", "yet", "along", "already", "another", "around", "ask",
    "away", "began", "best", "better", "big", "body", "book", "boy",
    "brought", "call", "case", "certain", "clear", "dark", "deep", "done",
    "door", "draw", "early", "enough", "ever", "face", "fact", "fall",
    "family", "feel", "few", "field", "fire", "five", "four", "front",
    "full", "game", "gave", "girl", "going", "gone", "got", "green",
    "ground", "grow", "half", "happen", "heard", "heart", "horse", "hot",
    "hundred", "idea", "inside", "iron", "island", "itself", "king", "knew",
    "land", "later", "leave", "less", "letter", "list", "listen", "lost",
    "low", "map", "mark", "matter", "mind", "miss", "money", "morning",
    "near", "nothing", "notice", "often", "once", "pair", "paper", "pass",
    "past", "pattern", "person", "picture", "piece", "plan", "product",
    "problem", "quite", "rain", "reach", "ready", "rest", "river", "road",
    "rock", "room", "round", "rule", "run", "second", "seen", "sentence",
    "serve", "several", "short", "since", "sing", "sit", "six", "sleep",
    "slowly", "snow", "sometimes", "song", "soon", "space", "stand", "step",
    "stop", "strong", "sun", "table", "talk", "ten", "test", "today",
    "top", "toward", "town", "travel", "true", "try", "upon", "voice",
    "war", "warm", "watch", "whether", "wind", "winter", "wish", "woman",
    "wonder", "wood", "wrote", "year", "young", "able", "above", "across",
    "age", "almost", "alone", "among", "appear", "area", "became", "bed",
    "behind", "believe", "beside", "black", "blue", "boat", "bottom",
    "break", "bright", "bring", "busy", "build", "built", "care", "carry",
    "center", "check", "child", "church", "circle", "cold", "common",
    "complete", "contain", "control", "cool", "corner", "count", "country",
    "course", "cross", "cry", "cup", "cut", "dance", "danger", "dead",
    "decide", "describe", "design", "develop", "die", "direct", "dog",
    "dress", "drink", "drive", "drop", "dry", "during", "east", "eat",
    "edge", "effect", "eight", "else", "engine", "equal", "event",
    "experience", "explain", "express", "fair", "famous", "fast", "father",
    "favor", "fight", "figure", "fill", "final", "fine", "finish", "fish",
    "flat", "floor", "flower", "fly", "force", "forest", "forget", "forward",
    "fresh", "friend", "fruit", "garden", "gather", "general", "gentle",
    "glad", "glass", "gold", "gray", "grew", "guess", "guide", "hair",
    "happy", "hat", "heavy", "hill", "history", "hole", "hope", "huge",
    "human", "hunt", "hurry", "ice", "imagine", "inch", "include",
    "increase", "indicate", "industry", "interest", "join", "jump",
    "kept", "kitchen", "lake", "language", "laugh", "law", "lay", "lead",
    "leg", "length", "level", "lie", "lift", "likely", "line", "liquid",
    "log", "lot", "loud", "love", "machine", "main", "major", "market",
    "mass", "material", "measure", "meat", "meet", "member", "metal",
    "middle", "milk", "million", "minute", "modern", "moment", "month",
    "moon", "mountain", "mouth", "multiply", "nation", "natural", "necessary",
    "neighbor", "noise", "north", "nose", "note", "noun", "observe", "occur",
    "ocean", "office", "oil", "opposite", "original", "outside", "page",
    "paint", "paragraph", "parent", "particular", "path", "pay", "perhaps",
    "period", "phrase", "plain", "planet", "please", "plural", "poem",
    "poor", "position", "possible", "post", "pound", "practice", "prepare",
    "present", "press", "pretty", "print", "probable", "produce", "promise",
    "proper", "protect", "prove", "provide", "pull", "push", "quarter",
    "question", "quiet", "race", "raise", "range", "rapid", "rather",
    "receive", "record", "red", "region", "remember", "repeat", "reply",
    "report", "represent", "require", "result", "rich", "ride", "ring",
    "rise", "roll", "rope", "row", "safe", "said", "salt", "sand",
    "sat", "save", "scale", "science", "score", "season", "seat", "section",
    "seed", "seem", "select", "sell", "send", "sense", "separate", "settle",
    "seven", "shape", "share", "sharp", "ship", "shoe", "shop", "shoulder",
    "sight", "sign", "silent", "silver", "similar", "simple", "single",
    "sister", "size", "skill", "skin", "slip", "smell", "smile", "soft",
    "soil", "soldier", "solution", "solve", "sort", "sound", "south",
    "special", "speed", "spend", "spoke", "spot", "spread", "spring",
    "square", "stage", "star", "station", "stay", "steam", "steel", "stick",
    "stone", "stood", "store", "straight", "strange", "street", "stretch",
    "student", "subject", "substance", "success", "sudden", "sugar", "suggest",
    "summer", "supply", "support", "surprise", "sweet", "swim", "symbol",
    "tail", "tall", "teach", "team", "teeth", "temperature", "thick", "thin",
    "tiny", "tire", "together", "tone", "tool", "touch", "track", "trade",
    "train", "triangle", "trip", "trouble", "truck", "trust", "tube", "type",
    "unit", "until", "usual", "valley", "verb", "visit", "wait", "wall",
    "wash", "wave", "wear", "weather", "week", "weight", "went", "west",
    "wheel", "whose", "wide", "wife", "wild", "win", "window", "wing",
    "wire", "women", "won", "written", "wrong", "yard", "yellow",
    # Programming and tech terms
    "function", "variable", "method", "class", "object", "string", "array",
    "index", "value", "return", "import", "module", "package", "server",
    "client", "request", "response", "database", "query", "table", "column",
    "deploy", "build", "debug", "error", "stack", "queue", "graph", "node",
    "tree", "branch", "merge", "commit", "push", "pull", "clone", "fetch",
    "docker", "config", "route", "cache", "proxy", "token", "parse", "render",
    "async", "await", "yield", "lambda", "tuple", "schema", "pipeline",
    "batch", "stream", "buffer", "socket", "thread", "process", "kernel",
    "binary", "boolean", "byte", "callback", "compile", "constant", "cursor",
    "data", "decode", "encode", "encrypt", "endpoint", "enum", "exception",
    "execute", "export", "factory", "filter", "flag", "float", "framework",
    "gateway", "handler", "hash", "header", "heap", "hook", "instance",
    "integer", "interface", "iterate", "json", "key", "library", "link",
    "loader", "local", "loop", "macro", "manifest", "memory", "middleware",
    "migrate", "mock", "mutex", "namespace", "network", "null", "offset",
    "operator", "optimize", "output", "overflow", "parameter", "parser",
    "patch", "payload", "permission", "pointer", "poll", "pool", "port",
    "prefix", "private", "profile", "promise", "protocol", "public",
    "publish", "record", "redirect", "refactor", "reference", "register",
    "release", "remote", "replica", "resolve", "resource", "retry", "revert",
    "runtime", "sandbox", "scope", "script", "serialize", "session", "setter",
    "signal", "snapshot", "source", "spawn", "static", "status", "store",
    "struct", "subscribe", "suffix", "syntax", "target", "template",
    "terminal", "timeout", "timestamp", "trace", "trigger", "truncate",
    "update", "upload", "upstream", "validate", "version", "virtual",
    "volume", "webhook", "worker", "wrapper", "abort", "abstract", "access",
    "adapter", "alias", "allocate", "annotation", "argument", "assert",
    "assign", "attribute", "backend", "benchmark", "binding", "bitwise",
    "block", "bootstrap", "breakpoint", "broadcast", "bucket", "bundle",
    "cache", "channel", "checkpoint", "chunk", "cipher", "cluster",
    "codec", "collection", "compiler", "component", "compose", "compress",
    "concat", "concurrent", "condition", "configure", "connect", "console",
    "consumer", "context", "contract", "convert", "coroutine", "counter",
    "coverage", "credential", "daemon", "deadlock", "debugger", "declare",
    "default", "delegate", "dependency", "deserialize", "destructor",
    "dispatch", "domain", "driver", "duplex", "dynamic", "element",
    "embed", "emit", "emulator", "environment", "evaluate", "event",
    "extend", "extract", "failover", "fallback", "firmware", "fixture",
    "format", "fragment", "function", "garbage", "generic", "global",
    "gradient", "handle", "hardcode", "hostname", "hybrid", "hydrate",
    "idempotent", "immutable", "implement", "increment", "index",
    "inherit", "initialize", "inject", "inline", "input", "inspect",
    "integrate", "intercept", "interpolate", "interrupt", "invoke",
    "isolate", "iterator", "kernel", "keystore", "latency", "launch",
    "layout", "lazy", "lifecycle", "literal", "localhost", "logging",
    "lookup", "linter", "marshal", "method", "metric", "microservice",
    "minify", "module", "monitor", "mount", "multicast", "mutable",
    "native", "negotiate", "notify", "observable", "opaque", "orchestrate",
    "override", "package", "parallel", "partition", "persist", "pixel",
    "platform", "plugin", "polyfill", "populate", "pragma", "predicate",
    "preload", "primitive", "priority", "procedure", "producer", "program",
    "propagate", "property", "prototype", "provision", "proxy", "purge",
    "query", "queue", "random", "reactive", "readonly", "rebase", "rebuild",
    "recursion", "reduce", "regex", "relay", "render", "repository",
    "request", "response", "restore", "rollback", "router", "runtime",
    "scalar", "schedule", "segment", "semaphore", "sentinel", "sequence",
    "shard", "shell", "shim", "singleton", "slice", "socket", "sort",
    "splice", "stack", "staging", "state", "strategy", "stringify", "subnet",
    "subscribe", "suspend", "swap", "switch", "symlink", "sync", "table",
    "tenant", "test", "thread", "throttle", "token", "topology", "trait",
    "transaction", "transform", "traverse", "type", "union", "unique",
    "unlock", "unmount", "unpack", "upstream", "utility", "validate",
    "variable", "vector", "vendor", "viewport", "virtual", "volume",
    "watchdog", "websocket", "widget", "wildcard", "workflow", "workspace",
    "yield", "zero", "zip",
]

LESSONS = [
    {
        "level": 1,
        "level_name": "Home Row",
        "lessons": [
            {
                "id": "1.1",
                "title": "Left Hand Home Keys",
                "description": "Build muscle memory for a s d f",
                "keys": ["a", "s", "d", "f"],
                "text": "ff dd ss aa fd sa df as ff dd ss aa fad sad add dad ff sa dd as df fad sad dad add",
                "pass_accuracy": 90,
            },
            {
                "id": "1.2",
                "title": "Right Hand Home Keys",
                "description": "Build muscle memory for j k l ;",
                "keys": ["j", "k", "l", ";"],
                "text": "jj kk ll ;; jk lk j; kl jj kk ll ;; jk kl j; lk jl k; jk lk j; kl jl k; jj kk",
                "pass_accuracy": 90,
            },
            {
                "id": "1.3",
                "title": "Full Home Row",
                "description": "Combine both hands on the home row",
                "keys": ["a", "s", "d", "f", "j", "k", "l", ";"],
                "text": "as df jk l; fd sa lk j; ask all fall lads salad flask dad add jks alf sdk sad fall",
                "pass_accuracy": 90,
            },
            {
                "id": "1.4",
                "title": "Home Row Words",
                "description": "Type real words using home row keys",
                "keys": ["a", "s", "d", "f", "j", "k", "l"],
                "text": "all add ask dad fad lad sad fall flask salad dad ask lads all add fad sad flask salad",
                "pass_accuracy": 90,
            },
        ],
    },
    {
        "level": 2,
        "level_name": "Top Row",
        "lessons": [
            {
                "id": "2.1",
                "title": "Left Top Row",
                "description": "Reach up for q w e r t",
                "keys": ["q", "w", "e", "r", "t"],
                "text": "we wetrew tree were ter rew wet tree we ter rew were wet tree we rew ter wet were",
                "pass_accuracy": 90,
            },
            {
                "id": "2.2",
                "title": "Right Top Row",
                "description": "Reach up for y u i o p",
                "keys": ["y", "u", "i", "o", "p"],
                "text": "you your yip poi you poi up you pup poi your yup yip up poi you your pup yip yup",
                "pass_accuracy": 90,
            },
            {
                "id": "2.3",
                "title": "Top and Home Row Combined",
                "description": "Mix top row with home row keys",
                "keys": ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
                "text": "quest typed route query write type your port output quest route typed query write port",
                "pass_accuracy": 90,
            },
            {
                "id": "2.4",
                "title": "Top Row Words",
                "description": "Real words focusing on the top row",
                "keys": ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
                "text": "power write tower poetry require quote equity routed triple equity tower quite proper poetry",
                "pass_accuracy": 90,
            },
        ],
    },
    {
        "level": 3,
        "level_name": "Bottom Row",
        "lessons": [
            {
                "id": "3.1",
                "title": "Left Bottom Row",
                "description": "Reach down for z x c v b",
                "keys": ["z", "x", "c", "v", "b"],
                "text": "cab bvc zxc vex box cab vex zxc bvc box cab vex box zxc bvc cab vex box zxc bvc cab",
                "pass_accuracy": 90,
            },
            {
                "id": "3.2",
                "title": "Right Bottom Row",
                "description": "Reach down for n m , .",
                "keys": ["n", "m", ",", "."],
                "text": "man. men, nm, mn. man. men, nm, mn. man. men, nm, mn. name. mine, man. men, name.",
                "pass_accuracy": 90,
            },
            {
                "id": "3.3",
                "title": "Full Alphabet Drill",
                "description": "Use all three rows together",
                "keys": [],
                "text": "the quick brown fox jumps over the lazy dog pack my box with five dozen liquor jugs",
                "pass_accuracy": 90,
            },
            {
                "id": "3.4",
                "title": "Bottom Row Words",
                "description": "Real words focusing on bottom row keys",
                "keys": ["z", "x", "c", "v", "b", "n", "m"],
                "text": "vim env bin mix zone box nav mob vex zinc van comic bonanza cave bench enzyme cabin",
                "pass_accuracy": 90,
            },
        ],
    },
    {
        "level": 4,
        "level_name": "Numbers and Shift",
        "lessons": [
            {
                "id": "4.1",
                "title": "Numbers 1 through 5",
                "description": "Left hand number row",
                "keys": ["1", "2", "3", "4", "5"],
                "text": "11 22 33 44 55 12 23 34 45 51 123 234 345 451 512 135 241 352 543 215 321 432 145",
                "pass_accuracy": 90,
            },
            {
                "id": "4.2",
                "title": "Numbers 6 through 0",
                "description": "Right hand number row",
                "keys": ["6", "7", "8", "9", "0"],
                "text": "66 77 88 99 00 67 78 89 90 60 678 789 890 906 607 796 890 670 980 760 897 608 709",
                "pass_accuracy": 90,
            },
            {
                "id": "4.3",
                "title": "Numbers in Context",
                "description": "Ports, IPs, and common dev numbers",
                "keys": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
                "text": "port 5432 port 8080 port 3306 port 6379 port 443 port 27017 version 3.12 node 18.0",
                "pass_accuracy": 90,
            },
            {
                "id": "4.4",
                "title": "Capital Letters",
                "description": "Practice holding Shift for capitals",
                "keys": ["Shift"],
                "text": "Python Flask Docker Linux SQL API JSON YAML CSV Kafka Spark Airflow BigQuery AWS GCP",
                "pass_accuracy": 90,
            },
        ],
    },
    {
        "level": 5,
        "level_name": "Programming Symbols",
        "lessons": [
            {
                "id": "5.1",
                "title": "Brackets and Braces",
                "description": "Master ( ) [ ] { } for code",
                "keys": ["(", ")", "[", "]", "{", "}"],
                "text": "() [] {} (x) [0] {key} (a, b) [i] {name: val} ([]) ({}) [()] {[]} (data) [index]",
                "pass_accuracy": 85,
            },
            {
                "id": "5.2",
                "title": "Operators",
                "description": "Common programming operators",
                "keys": ["=", "+", "-", "*", "/", "<", ">", "|", "&"],
                "text": "x = 1 a + b x - y a * b x / y a == b x != y a <= b x >= y a && b x || y a += 1",
                "pass_accuracy": 85,
            },
            {
                "id": "5.3",
                "title": "Special Characters",
                "description": "Underscores, quotes, colons and more",
                "keys": ["_", "-", ".", ":", ";", "'", '"', "`", "~"],
                "text": "my_var data-set file.py key: val; 'text' \"string\" `cmd` ~/home path.to.key a_b-c.d",
                "pass_accuracy": 85,
            },
            {
                "id": "5.4",
                "title": "Shift Symbols",
                "description": "! @ # $ % ^ & characters",
                "keys": ["!", "@", "#", "$", "%", "^", "&"],
                "text": "! error @user #tag $var 100% x^2 a & b !important @param #comment $PATH 50% y^n",
                "pass_accuracy": 85,
            },
        ],
    },
    {
        "level": 6,
        "level_name": "Common Code Patterns",
        "lessons": [
            {
                "id": "6.1",
                "title": "Python Patterns",
                "description": "def, class, import, and common syntax",
                "keys": [],
                "text": "def main(): import os from pathlib import Path class Config: self.name = name return data if __name__ == '__main__': for item in items: print(f'{key}: {val}')",
                "pass_accuracy": 85,
            },
            {
                "id": "6.2",
                "title": "SQL Queries",
                "description": "SELECT, INSERT, JOIN and more",
                "keys": [],
                "text": "SELECT id, name FROM users WHERE active = 1 ORDER BY created_at DESC LIMIT 10; INSERT INTO logs (event, ts) VALUES ('click', NOW()); LEFT JOIN orders ON users.id = orders.user_id;",
                "pass_accuracy": 85,
            },
            {
                "id": "6.3",
                "title": "Shell Commands",
                "description": "docker, git, and terminal commands",
                "keys": [],
                "text": "docker run -d -p 8080:80 nginx git checkout -b feature/auth git add . && git commit -m 'init' ls -la | grep .py cd ~/projects && source venv/bin/activate",
                "pass_accuracy": 85,
            },
            {
                "id": "6.4",
                "title": "Config and YAML",
                "description": "YAML, JSON, and config file patterns",
                "keys": [],
                "text": "version: '3.8' services: db: image: postgres:15 environment: - POSTGRES_DB=app {\"name\": \"config\", \"debug\": true, \"port\": 5555} host: 0.0.0.0",
                "pass_accuracy": 85,
            },
        ],
    },
    {
        "level": 7,
        "level_name": "Speed Building",
        "lessons": [
            {
                "id": "7.1",
                "title": "Most Common Words",
                "description": "The 50 most typed English words",
                "keys": [],
                "text": "the be to of and a in that have I it for not on with he as you do at this but his by from they we say her she or an will my one all would there their what so up out if about who get which go me",
                "pass_accuracy": 90,
            },
            {
                "id": "7.2",
                "title": "Programming Keywords",
                "description": "Keywords you type every day",
                "keys": [],
                "text": "import return function class object string array index value def self None True False lambda yield async await try except finally raise with as from pass break continue elif else for while in not or and is",
                "pass_accuracy": 90,
            },
            {
                "id": "7.3",
                "title": "Data Engineering Terms",
                "description": "Terms from your daily work",
                "keys": [],
                "text": "pipeline schema transform ingest partition batch stream buffer checkpoint warehouse lakehouse medallion bronze silver gold orchestration lineage catalog metadata quality governance observability dbt airflow spark kafka bigquery snowflake redshift fivetran",
                "pass_accuracy": 90,
            },
            {
                "id": "7.4",
                "title": "CamelCase and snake_case",
                "description": "Naming conventions used in code",
                "keys": [],
                "text": "getData getUserById processPayment sendEmail validateInput parse_config load_data run_pipeline build_schema create_table drop_index fetch_results merge_branch deploy_service",
                "pass_accuracy": 90,
            },
        ],
    },
    {
        "level": 8,
        "level_name": "Real-World Drills",
        "lessons": [
            {
                "id": "8.1",
                "title": "Python Function",
                "description": "Type a complete Python function",
                "keys": [],
                "text": "def extract_data(source: str, limit: int = 100) -> list[dict]: conn = get_connection(source) rows = conn.execute(f'SELECT * FROM raw LIMIT {limit}') return [dict(row) for row in rows]",
                "pass_accuracy": 85,
            },
            {
                "id": "8.2",
                "title": "SQL Pipeline Query",
                "description": "A real data pipeline query",
                "keys": [],
                "text": "WITH daily AS (SELECT date_trunc('day', created_at) AS dt, COUNT(*) AS events FROM raw_events WHERE created_at >= CURRENT_DATE - INTERVAL '7 days' GROUP BY 1) SELECT dt, events, AVG(events) OVER (ORDER BY dt ROWS 2 PRECEDING) AS moving_avg FROM daily;",
                "pass_accuracy": 85,
            },
            {
                "id": "8.3",
                "title": "Docker Compose",
                "description": "Type a docker-compose service definition",
                "keys": [],
                "text": "services: api: build: ./api ports: - '8080:8080' environment: - DATABASE_URL=postgresql://user:pass@db:5432/app depends_on: - db db: image: postgres:16 volumes: - pgdata:/var/lib/postgresql/data",
                "pass_accuracy": 85,
            },
            {
                "id": "8.4",
                "title": "Git Workflow",
                "description": "A full git feature branch workflow",
                "keys": [],
                "text": "git fetch origin && git checkout -b feature/add-metrics origin/main pip install -r requirements.txt pytest tests/ -v git add src/ tests/ git commit -m 'feat: add pipeline metrics endpoint' git push -u origin feature/add-metrics gh pr create --title 'Add metrics' --body 'Adds /metrics endpoint'",
                "pass_accuracy": 85,
            },
        ],
    },
]

PASSAGES = [
    {
        "title": "The Zen of Python",
        "text": "Beautiful is better than ugly. Explicit is better than implicit. Simple is better than complex. Complex is better than complicated. Flat is better than nested. Sparse is better than dense. Readability counts. Special cases aren't special enough to break the rules. Although practicality beats purity. Errors should never pass silently. Unless explicitly silenced. In the face of ambiguity, refuse the temptation to guess."
    },
    {
        "title": "Git Basics",
        "text": "Git is a distributed version control system that tracks changes in any set of computer files. It is usually used for coordinating work among programmers who are collaboratively developing source code during software development. Git was originally authored by Linus Torvalds in 2005 for development of the Linux kernel."
    },
    {
        "title": "Data Pipelines",
        "text": "A data pipeline is a series of data processing steps. If the data is not currently loaded into the data platform, then it is ingested at the beginning of the pipeline. Then there are a series of steps in which each step delivers an output that is the input to the next step. This continues until the pipeline is complete."
    },
    {
        "title": "Docker Containers",
        "text": "Docker is an open platform for developing, shipping, and running applications. Docker enables you to separate your applications from your infrastructure so you can deliver software quickly. With Docker, you can manage your infrastructure in the same ways you manage your applications."
    },
    {
        "title": "SQL Fundamentals",
        "text": "Structured Query Language is a domain specific language used in programming and designed for managing data held in a relational database management system. It is particularly useful in handling structured data, where there are relations between different entities and variables of the data."
    },
    {
        "title": "Cloud Computing",
        "text": "Cloud computing is the on demand availability of computer system resources, especially data storage and computing power, without direct active management by the user. Large clouds often have functions distributed over multiple locations, each of which is a data center. Cloud computing relies on sharing of resources to achieve coherence and typically uses a pay as you go model."
    },
    {
        "title": "API Design",
        "text": "A good API should be easy to learn, easy to use, and hard to misuse. It should be sufficiently powerful to satisfy the requirements of the application. An API should provide a clear mapping to the underlying data model and support efficient access patterns. Well designed APIs evolve gracefully and are well documented."
    },
    {
        "title": "Linux Terminal",
        "text": "The command line interface is a powerful tool for interacting with your computer. It allows you to navigate the file system, manipulate files, install software, and automate tasks. Learning terminal commands increases your productivity and gives you greater control over your development environment."
    },
    {
        "title": "Open Source Software",
        "text": "Open source software is software with source code that anyone can inspect, modify, and enhance. When a program is open source, its source code is freely available to users. This allows developers around the world to contribute to projects, fix bugs, and add features. The open source movement has fundamentally changed how software is built and distributed."
    },
    {
        "title": "Machine Learning Basics",
        "text": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. The process begins with observations or data, such as examples or direct experience, in order to look for patterns in data and make better decisions in the future. The primary aim is to allow computers to learn automatically."
    },
    {
        "title": "Agile Development",
        "text": "Agile software development is an approach to building software through incremental delivery, team collaboration, continual planning, and continual learning. It encourages rapid and flexible response to change. Rather than building everything at once, agile teams deliver work in small but consumable increments, gathering feedback from users along the way."
    },
    {
        "title": "Database Normalization",
        "text": "Database normalization is the process of structuring a relational database to reduce data redundancy and improve data integrity. It involves dividing large tables into smaller ones and defining relationships between them. The normal forms provide guidelines to ensure that each table has a single purpose and that every piece of data is stored exactly once."
    },
    {
        "title": "REST Architecture",
        "text": "Representational State Transfer is an architectural style for designing networked applications. It relies on a stateless, client-server communication protocol, almost always HTTP. REST provides a set of constraints that, when applied as a whole, emphasizes scalability of component interactions, generality of interfaces, and independent deployment of components."
    },
    {
        "title": "Cybersecurity Fundamentals",
        "text": "Cybersecurity is the practice of protecting systems, networks, and programs from digital attacks. These attacks are usually aimed at accessing, changing, or destroying sensitive information, extorting money from users, or interrupting normal business processes. Implementing effective cybersecurity measures is particularly challenging today because there are more devices than people."
    },
    {
        "title": "Version Control",
        "text": "Version control is a system that records changes to a file or set of files over time so that you can recall specific versions later. It allows you to revert selected files back to a previous state, compare changes over time, see who last modified something, and more. Using a version control system generally means that if you mess things up, you can easily recover."
    },
    {
        "title": "Networking Protocols",
        "text": "The internet is built on layers of protocols that handle different aspects of communication. TCP ensures reliable data delivery by breaking messages into packets and reassembling them at the destination. HTTP sits on top of TCP and defines how web browsers and servers exchange information. DNS translates human readable domain names into IP addresses that computers use to identify each other."
    },
    {
        "title": "Functional Programming",
        "text": "Functional programming is a paradigm that treats computation as the evaluation of mathematical functions and avoids changing state and mutable data. Functions are first class citizens, meaning they can be passed as arguments, returned from other functions, and assigned to variables. Pure functions always produce the same output for the same input and have no side effects."
    },
    {
        "title": "Testing Strategies",
        "text": "Software testing is the process of evaluating and verifying that a product or application does what it is supposed to do. Good testing practices prevent bugs, reduce development costs, and improve performance. Unit tests verify individual components in isolation. Integration tests check that different parts of the system work together. End to end tests validate the entire application flow."
    },
    {
        "title": "Microservices Architecture",
        "text": "Microservices are an architectural approach where an application is structured as a collection of small, independent services. Each service runs in its own process and communicates through lightweight mechanisms, often HTTP APIs. Services are built around business capabilities and independently deployable. This architecture enables organizations to scale specific parts of their system without scaling everything."
    },
    {
        "title": "Data Structures",
        "text": "Data structures are specialized formats for organizing, processing, retrieving, and storing data. They provide a means to manage large amounts of data efficiently for uses such as large databases and internet indexing services. Common data structures include arrays, linked lists, stacks, queues, hash tables, trees, and graphs. Choosing the right data structure is crucial for writing efficient algorithms."
    },
    {
        "title": "DevOps Culture",
        "text": "DevOps is a set of practices that combines software development and IT operations. It aims to shorten the systems development lifecycle and provide continuous delivery with high software quality. DevOps is complementary to agile software development because several DevOps aspects came from the agile methodology. Automation, monitoring, and collaboration are key principles of the DevOps approach."
    },
    {
        "title": "Kubernetes Overview",
        "text": "Kubernetes is an open source container orchestration platform that automates the deployment, scaling, and management of containerized applications. It groups containers into logical units for easy management and discovery. Kubernetes builds upon fifteen years of experience running production workloads at Google, combined with best of breed ideas and practices from the community."
    },
    {
        "title": "The Art of Debugging",
        "text": "Debugging is the process of finding and resolving bugs or defects in software. The most effective debugging strategy is to reproduce the problem consistently. Once reproducible, you can use tools like debuggers, log statements, and stack traces to narrow down the root cause. The best programmers are not those who write bug free code, but those who can find and fix bugs quickly."
    },
    {
        "title": "Code Reviews",
        "text": "Code review is a software quality assurance activity in which one or more people check a program by viewing and reading parts of its source code. The primary purpose is to find mistakes overlooked during initial development. Code reviews also promote knowledge sharing, maintain coding standards, and improve overall code quality. A good review catches logic errors, edge cases, and potential security issues."
    },
    {
        "title": "Technical Debt",
        "text": "Technical debt is a concept in software development that reflects the implied cost of additional rework caused by choosing an easy or limited solution now instead of a better approach that would take longer. Like monetary debt, technical debt is not necessarily a bad thing, and sometimes it is required to move projects forward. The key is to manage it deliberately and pay it down over time."
    },
    {
        "title": "Observability",
        "text": "Observability is the ability to measure the internal states of a system by examining its outputs. In software, this means understanding what is happening inside your applications through three pillars: logs, metrics, and traces. Logs record discrete events. Metrics track numeric measurements over time. Traces follow a request as it flows through distributed services. Together they provide a complete picture of system health."
    },
]


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wpm REAL NOT NULL,
            accuracy REAL NOT NULL,
            errors INTEGER NOT NULL,
            total_chars INTEGER NOT NULL,
            correct_chars INTEGER NOT NULL,
            streak INTEGER NOT NULL DEFAULT 0,
            duration INTEGER NOT NULL,
            mode TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS char_errors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expected_char TEXT NOT NULL,
            typed_char TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS lesson_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson_id TEXT NOT NULL,
            wpm REAL NOT NULL,
            accuracy REAL NOT NULL,
            errors INTEGER NOT NULL,
            total_chars INTEGER NOT NULL,
            correct_chars INTEGER NOT NULL,
            passed INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()
    db.close()


def _get_lesson_by_id(lesson_id):
    for level in LESSONS:
        for lesson in level["lessons"]:
            if lesson["id"] == lesson_id:
                return lesson
    return None


def _get_all_lesson_ids():
    ids = []
    for level in LESSONS:
        for lesson in level["lessons"]:
            ids.append(lesson["id"])
    return ids


# --- Routes ---

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/words", methods=["GET"])
def get_words():
    count = request.args.get("count", 200, type=int)
    words = [random.choice(WORD_POOL) for _ in range(count)]
    return jsonify({"words": " ".join(words)})


@app.route("/api/passages", methods=["GET"])
def get_passages():
    return jsonify({"passages": PASSAGES})


@app.route("/api/passage", methods=["GET"])
def get_passage():
    idx = request.args.get("index", None, type=int)
    if idx is not None and 0 <= idx < len(PASSAGES):
        return jsonify(PASSAGES[idx])
    return jsonify(random.choice(PASSAGES))


@app.route("/api/results", methods=["POST"])
def save_result():
    data = request.get_json()
    db = get_db()
    db.execute(
        """INSERT INTO results (wpm, accuracy, errors, total_chars, correct_chars, streak, duration, mode)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            data["wpm"],
            data["accuracy"],
            data["errors"],
            data["total_chars"],
            data["correct_chars"],
            data["streak"],
            data["duration"],
            data["mode"],
        ),
    )
    db.commit()
    return jsonify({"status": "ok"})


@app.route("/api/results", methods=["GET"])
def get_results():
    db = get_db()
    limit = request.args.get("limit", 50, type=int)
    rows = db.execute(
        "SELECT * FROM results ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    results = [dict(row) for row in rows]
    return jsonify({"results": results})


@app.route("/api/stats", methods=["GET"])
def get_stats():
    db = get_db()
    row = db.execute("""
        SELECT
            COUNT(*) as total_tests,
            COALESCE(AVG(wpm), 0) as avg_wpm,
            COALESCE(MAX(wpm), 0) as best_wpm,
            COALESCE(AVG(accuracy), 0) as avg_accuracy,
            COALESCE(MAX(streak), 0) as best_streak,
            COALESCE(SUM(total_chars), 0) as total_chars_typed
        FROM results
    """).fetchone()
    stats = dict(row)

    recent = db.execute(
        "SELECT wpm, accuracy, streak, created_at FROM results ORDER BY created_at DESC LIMIT 30"
    ).fetchall()
    stats["history"] = [dict(r) for r in recent]

    return jsonify(stats)


@app.route("/api/lessons", methods=["GET"])
def get_lessons():
    db = get_db()
    # Get all passed lesson IDs
    rows = db.execute(
        "SELECT DISTINCT lesson_id FROM lesson_progress WHERE passed = 1"
    ).fetchall()
    completed = {row["lesson_id"] for row in rows}

    # Get best stats per lesson
    best_rows = db.execute("""
        SELECT lesson_id, MAX(wpm) as best_wpm, MAX(accuracy) as best_accuracy
        FROM lesson_progress GROUP BY lesson_id
    """).fetchall()
    best_stats = {row["lesson_id"]: dict(row) for row in best_rows}

    all_ids = _get_all_lesson_ids()
    result = []
    for level in LESSONS:
        level_data = {
            "level": level["level"],
            "level_name": level["level_name"],
            "lessons": [],
        }
        for lesson in level["lessons"]:
            lid = lesson["id"]
            idx = all_ids.index(lid)
            # Available if first lesson or previous lesson completed
            if idx == 0:
                status = "completed" if lid in completed else "available"
            elif all_ids[idx - 1] in completed:
                status = "completed" if lid in completed else "available"
            else:
                status = "locked"

            entry = {
                "id": lid,
                "title": lesson["title"],
                "description": lesson["description"],
                "keys": lesson["keys"],
                "pass_accuracy": lesson["pass_accuracy"],
                "status": status,
            }
            if lid in best_stats:
                entry["best_wpm"] = best_stats[lid]["best_wpm"]
                entry["best_accuracy"] = best_stats[lid]["best_accuracy"]
            level_data["lessons"].append(entry)
        result.append(level_data)

    return jsonify({"levels": result})


@app.route("/api/lesson/<lesson_id>", methods=["GET"])
def get_lesson(lesson_id):
    lesson = _get_lesson_by_id(lesson_id)
    if not lesson:
        return jsonify({"error": "not found"}), 404
    return jsonify(lesson)


@app.route("/api/lesson/<lesson_id>/result", methods=["POST"])
def save_lesson_result(lesson_id):
    lesson = _get_lesson_by_id(lesson_id)
    if not lesson:
        return jsonify({"error": "not found"}), 404
    data = request.get_json()
    passed = 1 if data["accuracy"] >= lesson["pass_accuracy"] else 0
    db = get_db()
    db.execute(
        """INSERT INTO lesson_progress (lesson_id, wpm, accuracy, errors, total_chars, correct_chars, passed)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (lesson_id, data["wpm"], data["accuracy"], data["errors"],
         data["total_chars"], data["correct_chars"], passed),
    )
    db.commit()
    return jsonify({"status": "ok", "passed": bool(passed)})


@app.route("/api/char-errors", methods=["POST"])
def save_char_errors():
    data = request.get_json()
    errors = data.get("errors", [])
    if not errors:
        return jsonify({"status": "ok"})
    db = get_db()
    for err in errors:
        db.execute(
            "INSERT INTO char_errors (expected_char, typed_char) VALUES (?, ?)",
            (err["expected"], err["typed"]),
        )
    db.commit()
    return jsonify({"status": "ok"})


@app.route("/api/weak-keys", methods=["GET"])
def get_weak_keys():
    db = get_db()
    rows = db.execute("""
        SELECT expected_char, COUNT(*) as miss_count
        FROM char_errors
        WHERE expected_char BETWEEN 'a' AND 'z'
           OR expected_char BETWEEN 'A' AND 'Z'
        GROUP BY LOWER(expected_char)
        ORDER BY miss_count DESC
        LIMIT 10
    """).fetchall()
    keys = [{"char": row["expected_char"].lower(), "count": row["miss_count"]} for row in rows]
    return jsonify({"weak_keys": keys})


@app.route("/api/weak-keys/practice", methods=["GET"])
def get_weak_keys_practice():
    """Generate practice words that focus on the user's weakest keys."""
    db = get_db()
    rows = db.execute("""
        SELECT LOWER(expected_char) as ch, COUNT(*) as miss_count
        FROM char_errors
        WHERE expected_char BETWEEN 'a' AND 'z'
           OR expected_char BETWEEN 'A' AND 'Z'
        GROUP BY LOWER(expected_char)
        ORDER BY miss_count DESC
        LIMIT 6
    """).fetchall()

    if not rows:
        return jsonify({"text": "", "weak_keys": [], "has_data": False})

    weak_chars = {row["ch"] for row in rows}
    weak_list = [{"char": row["ch"], "count": row["miss_count"]} for row in rows]

    # Score each word in WORD_POOL by how many weak chars it contains
    scored = []
    for word in WORD_POOL:
        score = sum(1 for c in word.lower() if c in weak_chars)
        if score > 0:
            scored.append((score, word))
    scored.sort(key=lambda x: -x[0])

    # Take the top words, with some randomness
    top_words = [w for _, w in scored[:60]]
    if len(top_words) < 20:
        # Fallback: generate letter combos if not enough matching words
        for ch in weak_chars:
            top_words.extend([ch * 3, ch + "a", "a" + ch, ch + "e", "e" + ch])

    count = min(50, max(30, len(top_words)))
    selected = [random.choice(top_words) for _ in range(count)]
    return jsonify({
        "text": " ".join(selected),
        "weak_keys": weak_list,
        "has_data": True,
    })


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5555)
