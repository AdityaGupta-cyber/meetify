
<body>
    <h1>Meetify - SDE Assignment OneAssure</h1>
    <p>Meet the dedicated yet overwhelmed OneAssure Customer Support Team, striving to provide unparalleled service to their clients. Unfortunately, they find themselves hopelessly entangled in a web of scheduling conflicts, missed appointments, and communication breakdowns. Each day, they juggle a myriad of customer inquiries, feedback sessions, and internal meetings, but their current system is proving to be a significant bottleneck.

To mitigate these challenges and restore efficiency, OneAssure decides to build a sophisticated Meeting Scheduling App, Meetify. This new system will streamline the scheduling process, allowing the support team to effortlessly book, manage, and track meetings.</p>
    <h2>Deployed Version -</h2>
      <ol>
        <li><a href="https://hub.docker.com/r/adityagupta075/meetify">Docker Image🐳</a></li>
        <li><a href="https://meetify-ncnr.onrender.com">Web Service 🕸️</a></li>
    </ol>
    <h2>Table of Contents</h2>
    <ol>
        <li><a href="#features">Features</a></li>
        <li><a href="#technologies-used">Technologies Used</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#configuration">Configuration</a></li>
        <li><a href="#running-the-app">Running the App</a></li>
    </ol>
    <h2 id="features">Features</h2>
    <ul>
        <li>APIs for creating users, scheduling meetings, updating user settings, and checking available time slots.</li>
        <li>Notification system for meeting reminders.</li>
        <li>Meeting scheduling with timezone support.</li>
        <li>Cron-based scheduling for recurring notifications.</li>
        <li>User management with Do Not Disturb (DND) settings.</li>
    </ul>
    <h2 id="technologies-used">Technologies Used</h2>
    <ul>
        <li><strong>Flask</strong>: Web framework.</li>
        <li><strong>SQLAlchemy</strong>: ORM for database interactions.</li>
        <li><strong>SQLite</strong>: Database (can be replaced with other databases like PostgreSQL).</li>
        <li><strong>pytz</strong>: World Timezone definitions.</li>
        <li><strong>APScheduler</strong>: Advanced Python Scheduler for scheduling tasks.</li>
        <li><strong>croniter</strong>: For validatiing a cron expression.</li>
        <li><strong>Flask-Migrate</strong>: Handle database migrations for SQLAlchemy models.</li>
    </ul>
    <h2 id="installation">Installation</h2>
    <h3>Prerequisites</h3>
    <ul>
        <li>Python 3.x</li>
        <li>pip (Python package installer)</li>
        <li>Virtual environment</li>
    </ul>
    <h3>Steps</h3>
    <ol>
        <li><strong>Clone the repository:</strong>
            <pre><code>git clone &lt;repository_url&gt;
cd &lt;repository_directory&gt;</code></pre>
        </li>
        <li><strong>Create and activate a virtual environment:</strong>
            <pre><code>python3 -m venv venv
venv/Scripts/activate</code></pre>
        </li>
        <li><strong>Install the required packages:</strong>
            <pre><code>pip install -r requirements.txt</code></pre>
        </li>
        <li><strong>Set up environment variables:</strong>
            <p>Create a <code>.env</code> file in the root directory and add your database URL or any other necessary environment variables:</p>
            <pre><code>DATABASE_URL=sqlite:///site.db</code>
            <code>FLASK_APP=server.py</code>
           <code>FLASK_DEBUG=1</code></pre>
        </li>
    </ol>
    <h2 id="configuration">Configuration</h2>
    <h3>Database Configuration</h3>
    <p>The application uses SQLAlchemy for ORM and Flask-Migrate for handling migrations. By default, it uses an SQLite database. You can change the database by modifying the <code>DATABASE_URL</code> in the <code>.env</code> file.</p>
    <h3>Scheduler Configuration</h3>
    <p>The application uses APScheduler to handle cron-based scheduling for meeting notifications. The scheduler starts automatically when the app runs.</p>
    <h2 id="running-the-app">Running the App</h2>
    <h3>Local Development</h3>
    <ol>
         <li><strong>Run the Flask application:</strong>
            <pre><code>flask run</code></pre>
        </li>
    </ol>
    <h3>Docker</h3>
    <ol>
        <li><strong>Build the Docker image:</strong>
            <pre><code>docker build -t {tagname} -f Dockerfile .</code></pre>
        </li>
        <li><strong>Run the Docker container:</strong>
            <pre><code>docker run -p 5000:5000 -v /app/instance -e DATABASE_URL=sqlite:////app/instance/site.db {tagname}</code></pre>
        </li>
    </ol>
</body>
