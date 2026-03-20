PASSAGES = [
    {
        "title": "The Zen of Python",
        "text": "Beautiful is better than ugly. Explicit is better than implicit. Simple is better than complex. Complex is better than complicated. Flat is better than nested. Sparse is better than dense. Readability counts. Special cases aren't special enough to break the rules. Although practicality beats purity. Errors should never pass silently. Unless explicitly silenced. In the face of ambiguity, refuse the temptation to guess.",
    },
    {
        "title": "Git Basics",
        "text": "Git is a distributed version control system that tracks changes in any set of computer files. It is usually used for coordinating work among programmers who are collaboratively developing source code during software development. Git was originally authored by Linus Torvalds in 2005 for development of the Linux kernel.",
    },
    {
        "title": "Data Pipelines",
        "text": "A data pipeline is a series of data processing steps. If the data is not currently loaded into the data platform, then it is ingested at the beginning of the pipeline. Then there are a series of steps in which each step delivers an output that is the input to the next step. This continues until the pipeline is complete.",
    },
    {
        "title": "Docker Containers",
        "text": "Docker is an open platform for developing, shipping, and running applications. Docker enables you to separate your applications from your infrastructure so you can deliver software quickly. With Docker, you can manage your infrastructure in the same ways you manage your applications.",
    },
    {
        "title": "SQL Fundamentals",
        "text": "Structured Query Language is a domain specific language used in programming and designed for managing data held in a relational database management system. It is particularly useful in handling structured data, where there are relations between different entities and variables of the data.",
    },
    {
        "title": "Cloud Computing",
        "text": "Cloud computing is the on demand availability of computer system resources, especially data storage and computing power, without direct active management by the user. Large clouds often have functions distributed over multiple locations, each of which is a data center. Cloud computing relies on sharing of resources to achieve coherence and typically uses a pay as you go model.",
    },
    {
        "title": "API Design",
        "text": "A good API should be easy to learn, easy to use, and hard to misuse. It should be sufficiently powerful to satisfy the requirements of the application. An API should provide a clear mapping to the underlying data model and support efficient access patterns. Well designed APIs evolve gracefully and are well documented.",
    },
    {
        "title": "Linux Terminal",
        "text": "The command line interface is a powerful tool for interacting with your computer. It allows you to navigate the file system, manipulate files, install software, and automate tasks. Learning terminal commands increases your productivity and gives you greater control over your development environment.",
    },
    {
        "title": "Open Source Software",
        "text": "Open source software is software with source code that anyone can inspect, modify, and enhance. When a program is open source, its source code is freely available to users. This allows developers around the world to contribute to projects, fix bugs, and add features. The open source movement has fundamentally changed how software is built and distributed.",
    },
    {
        "title": "Machine Learning Basics",
        "text": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. The process begins with observations or data, such as examples or direct experience, in order to look for patterns in data and make better decisions in the future. The primary aim is to allow computers to learn automatically.",
    },
    {
        "title": "Agile Development",
        "text": "Agile software development is an approach to building software through incremental delivery, team collaboration, continual planning, and continual learning. It encourages rapid and flexible response to change. Rather than building everything at once, agile teams deliver work in small but consumable increments, gathering feedback from users along the way.",
    },
    {
        "title": "Database Normalization",
        "text": "Database normalization is the process of structuring a relational database to reduce data redundancy and improve data integrity. It involves dividing large tables into smaller ones and defining relationships between them. The normal forms provide guidelines to ensure that each table has a single purpose and that every piece of data is stored exactly once.",
    },
    {
        "title": "REST Architecture",
        "text": "Representational State Transfer is an architectural style for designing networked applications. It relies on a stateless, client-server communication protocol, almost always HTTP. REST provides a set of constraints that, when applied as a whole, emphasizes scalability of component interactions, generality of interfaces, and independent deployment of components.",
    },
    {
        "title": "Cybersecurity Fundamentals",
        "text": "Cybersecurity is the practice of protecting systems, networks, and programs from digital attacks. These attacks are usually aimed at accessing, changing, or destroying sensitive information, extorting money from users, or interrupting normal business processes. Implementing effective cybersecurity measures is particularly challenging today because there are more devices than people.",
    },
    {
        "title": "Version Control",
        "text": "Version control is a system that records changes to a file or set of files over time so that you can recall specific versions later. It allows you to revert selected files back to a previous state, compare changes over time, see who last modified something, and more. Using a version control system generally means that if you mess things up, you can easily recover.",
    },
    {
        "title": "Networking Protocols",
        "text": "The internet is built on layers of protocols that handle different aspects of communication. TCP ensures reliable data delivery by breaking messages into packets and reassembling them at the destination. HTTP sits on top of TCP and defines how web browsers and servers exchange information. DNS translates human readable domain names into IP addresses that computers use to identify each other.",
    },
    {
        "title": "Functional Programming",
        "text": "Functional programming is a paradigm that treats computation as the evaluation of mathematical functions and avoids changing state and mutable data. Functions are first class citizens, meaning they can be passed as arguments, returned from other functions, and assigned to variables. Pure functions always produce the same output for the same input and have no side effects.",
    },
    {
        "title": "Testing Strategies",
        "text": "Software testing is the process of evaluating and verifying that a product or application does what it is supposed to do. Good testing practices prevent bugs, reduce development costs, and improve performance. Unit tests verify individual components in isolation. Integration tests check that different parts of the system work together. End to end tests validate the entire application flow.",
    },
    {
        "title": "Microservices Architecture",
        "text": "Microservices are an architectural approach where an application is structured as a collection of small, independent services. Each service runs in its own process and communicates through lightweight mechanisms, often HTTP APIs. Services are built around business capabilities and independently deployable. This architecture enables organizations to scale specific parts of their system without scaling everything.",
    },
    {
        "title": "Data Structures",
        "text": "Data structures are specialized formats for organizing, processing, retrieving, and storing data. They provide a means to manage large amounts of data efficiently for uses such as large databases and internet indexing services. Common data structures include arrays, linked lists, stacks, queues, hash tables, trees, and graphs. Choosing the right data structure is crucial for writing efficient algorithms.",
    },
    {
        "title": "DevOps Culture",
        "text": "DevOps is a set of practices that combines software development and IT operations. It aims to shorten the systems development lifecycle and provide continuous delivery with high software quality. DevOps is complementary to agile software development because several DevOps aspects came from the agile methodology. Automation, monitoring, and collaboration are key principles of the DevOps approach.",
    },
    {
        "title": "Kubernetes Overview",
        "text": "Kubernetes is an open source container orchestration platform that automates the deployment, scaling, and management of containerized applications. It groups containers into logical units for easy management and discovery. Kubernetes builds upon fifteen years of experience running production workloads at Google, combined with best of breed ideas and practices from the community.",
    },
    {
        "title": "The Art of Debugging",
        "text": "Debugging is the process of finding and resolving bugs or defects in software. The most effective debugging strategy is to reproduce the problem consistently. Once reproducible, you can use tools like debuggers, log statements, and stack traces to narrow down the root cause. The best programmers are not those who write bug free code, but those who can find and fix bugs quickly.",
    },
    {
        "title": "Code Reviews",
        "text": "Code review is a software quality assurance activity in which one or more people check a program by viewing and reading parts of its source code. The primary purpose is to find mistakes overlooked during initial development. Code reviews also promote knowledge sharing, maintain coding standards, and improve overall code quality. A good review catches logic errors, edge cases, and potential security issues.",
    },
    {
        "title": "Technical Debt",
        "text": "Technical debt is a concept in software development that reflects the implied cost of additional rework caused by choosing an easy or limited solution now instead of a better approach that would take longer. Like monetary debt, technical debt is not necessarily a bad thing, and sometimes it is required to move projects forward. The key is to manage it deliberately and pay it down over time.",
    },
    {
        "title": "Observability",
        "text": "Observability is the ability to measure the internal states of a system by examining its outputs. In software, this means understanding what is happening inside your applications through three pillars: logs, metrics, and traces. Logs record discrete events. Metrics track numeric measurements over time. Traces follow a request as it flows through distributed services. Together they provide a complete picture of system health.",
    },
    {
        "title": "WebAssembly",
        "text": "WebAssembly is a binary instruction format designed as a portable compilation target for programming languages. It enables high performance applications to run in web browsers at near native speed. Languages like C, C++, and Rust can be compiled to WebAssembly, allowing developers to bring computationally intensive workloads to the browser without relying solely on JavaScript.",
    },
    {
        "title": "Cryptography",
        "text": "Cryptography is the practice of securing communication and data through the use of mathematical algorithms. Symmetric encryption uses the same key for both encryption and decryption, while asymmetric encryption relies on a public and private key pair. Hash functions produce fixed length outputs from arbitrary input, providing data integrity verification without revealing the original content.",
    },
    {
        "title": "Distributed Systems",
        "text": "A distributed system is a collection of independent computers that appears to its users as a single coherent system. These systems face unique challenges such as network partitions, variable latency, and the impossibility of achieving perfect consensus in asynchronous networks. The CAP theorem states that a distributed system can only guarantee two of three properties at any time: consistency, availability, and partition tolerance.",
    },
    {
        "title": "Type Systems in Programming",
        "text": "A type system is a set of rules that assigns a property called a type to every term in a program. Static type systems catch errors at compile time, while dynamic type systems defer type checking to runtime. Strongly typed languages prevent implicit type conversions that could lead to subtle bugs. Modern type systems support generics, algebraic data types, and type inference to balance safety with expressiveness.",
    },
    {
        "title": "Concurrency and Parallelism",
        "text": "Concurrency is the ability of a program to manage multiple tasks by interleaving their execution, while parallelism is the simultaneous execution of tasks across multiple processors. Common concurrency primitives include threads, locks, and channels. Race conditions occur when multiple threads access shared data without proper synchronization, leading to unpredictable behavior that is notoriously difficult to reproduce and debug.",
    },
]
