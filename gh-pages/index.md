---
layout: default
title: Home
---

<section class="intro-section">
  <div class="container">
    <div class="intro-content">
      <h2 class="section-title">One Prompt Configuration.<br>Every AI Editor.</h2>
      <p class="intro-description">Stop recreating prompts for different AI coding assistants. PrompTrek lets you write comprehensive coding guidelines once and automatically generates the perfect configuration for GitHub Copilot, Cursor, Continue, and more.</p>
    </div>
  </div>
</section>

<section class="problem-solution-section">
  <div class="container">
    <div class="problem-solution-grid">
      <div class="problem-card">
        <div class="card-icon">🎯</div>
        <h3>The Problem</h3>
        <p>AI coding assistants use different prompt formats and configuration methods. Teams waste time maintaining separate configurations, recreating prompts when switching tools, and struggling with consistency across different editors.</p>
        <ul class="problem-list">
          <li>Maintain separate configurations for each AI editor</li>
          <li>Recreate prompts when switching tools</li>
          <li>Struggle with team consistency</li>
          <li>Face migration headaches with new AI tools</li>
        </ul>
      </div>

      <div class="solution-card">
        <div class="card-icon">🚀</div>
        <h3>The Solution</h3>
        <p>PrompTrek provides a universal format for creating comprehensive coding prompts once, then automatically generates editor-specific configurations for your entire team.</p>
        <ul class="solution-list">
          <li>Universal format for all prompt configurations</li>
          <li>Multi-editor support with one-click generation</li>
          <li>Team consistency across different editor preferences</li>
          <li>Easy migration between AI coding tools</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="editors-section">
  <div class="container">
    <h2 class="section-title">Supported AI Editors</h2>
    <p class="section-description">Generate perfect configurations for all major AI coding assistants</p>

    <div class="editors-grid">
      <div class="editor-card">
        <div class="editor-icon">
          <img src="https://github.githubassets.com/images/modules/site/copilot/copilot.png" alt="GitHub Copilot" width="32" height="32" onerror="this.style.display='none'; this.nextElementSibling.style.display='inline';">
          <span style="display:none;">🐙</span>
        </div>
        <h4>GitHub Copilot</h4>
        <p>Repository-wide and path-specific instructions</p>
        <span class="status-badge supported">Fully Supported</span>
      </div>

      <div class="editor-card">
        <div class="editor-icon">
          <img src="https://cursor.com/brand/icon.svg" alt="Cursor" width="32" height="32" onerror="this.style.display='none'; this.nextElementSibling.style.display='inline';">
          <span style="display:none;">🎯</span>
        </div>
        <h4>Cursor</h4>
        <p>Modern 2025 rules with Always/Auto Attached types and project overview</p>
        <span class="status-badge supported">Fully Supported</span>
      </div>

      <div class="editor-card">
        <div class="editor-icon">
          <img src="https://avatars.githubusercontent.com/u/125663687?s=200&v=4" alt="Continue" width="32" height="32" onerror="this.style.display='none'; this.nextElementSibling.style.display='inline';">
          <span style="display:none;">⚡</span>
        </div>
        <h4>Continue</h4>
        <p>Complete YAML configuration system</p>
        <span class="status-badge supported">Fully Supported</span>
      </div>

      <div class="editor-card">
        <div class="editor-icon">
          <img src="assets/q-logo.svg" alt="Amazon Q" width="32" height="32" onerror="this.style.display='none'; this.nextElementSibling.style.display='inline';">
          <span style="display:none;">☁️</span>
        </div>
        <h4>Amazon Q</h4>
        <p>Comment-based assistance templates</p>
        <span class="status-badge supported">Fully Supported</span>
      </div>

      <div class="editor-card">
        <div class="editor-icon">
          <img src="https://resources.jetbrains.com/storage/products/company/brand/logos/jb_beam.png" alt="JetBrains AI" width="32" height="32" onerror="this.style.display='none'; this.nextElementSibling.style.display='inline';">
          <span style="display:none;">🧠</span>
        </div>
        <h4>JetBrains AI</h4>
        <p>IDE-integrated prompts</p>
        <span class="status-badge supported">Fully Supported</span>
      </div>

      <div class="editor-card">
        <div class="editor-icon">
          <img src="https://kiro.dev/favicon.ico" alt="Kiro" width="32" height="32" onerror="this.style.display='none'; this.nextElementSibling.style.display='inline';">
          <span style="display:none;">🤖</span>
        </div>
        <h4>Kiro</h4>
        <p>AI-powered steering, specs, hooks, and prompts</p>
        <span class="status-badge supported">Fully Supported</span>
      </div>

      <div class="editor-card">
        <div class="editor-icon">
          <img src="assets/cline-logo.svg" alt="Cline" width="32" height="32" onerror="this.style.display='none'; this.nextElementSibling.style.display='inline';">
          <span style="display:none;">📝</span>
        </div>
        <h4>Cline</h4>
        <p>Markdown-based rules</p>
        <span class="status-badge supported">Fully Supported</span>
      </div>
    </div>
  </div>
</section>

<section class="quickstart-section">
  <div class="container">
    <h2 class="section-title">Get Started in Minutes</h2>
    <div class="steps-grid">

      <div class="step-card">
        <div class="step-number">1</div>
        <div class="step-content">
          <h3>Install PrompTrek</h3>
          <div class="code-block">
            <code>pip install promptrek</code>
          </div>
          <p>Get PrompTrek installed and ready to use in seconds</p>
        </div>
      </div>

      <div class="step-card">
        <div class="step-number">2</div>
        <div class="step-content">
          <h3>Create Universal Prompt</h3>
          <div class="code-block">
            <code>promptrek init --output my-project.promptrek.yaml</code>
          </div>
          <p>Initialize your first universal prompt configuration file</p>
        </div>
      </div>

      <div class="step-card">
        <div class="step-number">3</div>
        <div class="step-content">
          <h3>Generate for All Editors</h3>
          <div class="code-block">
            <code>promptrek generate --all</code>
          </div>
          <p>Automatically create configurations for all your AI editors</p>
        </div>
      </div>

    </div>
  </div>
</section>

<section class="example-section">
  <div class="container">
    <h2 class="section-title">See It In Action</h2>
    <div class="example-grid">

      <div class="example-input">
        <h3>Universal Configuration</h3>
        <p>Write your prompt once in PrompTrek format:</p>
        <div class="code-example">
<pre><code>schema_version: "1.0.0"
metadata:
  title: "Full-Stack Development Assistant"
  description: "Production-ready coding standards"

# Optional - generates for all supported editors if not specified
targets: [copilot, cursor, continue, cline]

instructions:
  general:
    - "Write clean, maintainable code with proper error handling"
    - "Use TypeScript with strict mode for all new code"
    - "Follow SOLID principles and design patterns"
    - "Include comprehensive JSDoc comments"

  frontend:
    - "Use React functional components with hooks"
    - "Implement proper loading states and error boundaries"
    - "Follow accessibility best practices (WCAG 2.1)"
    - "Write unit tests with Jest and React Testing Library"

  backend:
    - "Use RESTful API design with proper HTTP status codes"
    - "Implement input validation and sanitization"
    - "Add proper logging and monitoring"
    - "Write integration tests for all endpoints"</code></pre>
        </div>
      </div>

      <div class="example-output">
        <h3>Generated for All Editors</h3>
        <p>PrompTrek automatically creates editor-specific files:</p>
        <div class="generated-files">
          <div class="file-item">
            <span class="file-icon">📄</span>
            <span class="file-name">.github/copilot-instructions.md</span>
          </div>
          <div class="file-item">
            <span class="file-icon">📄</span>
            <span class="file-name">.cursor/rules/index.mdc</span>
          </div>
          <div class="file-item">
            <span class="file-icon">📄</span>
            <span class="file-name">.continue/config.yaml</span>
          </div>
          <div class="file-item">
            <span class="file-icon">📄</span>
            <span class="file-name">.cline_rules.md</span>
          </div>
          <div class="file-item">
            <span class="file-icon">📄</span>
            <span class="file-name">.kiro/steering/product.md</span>
          </div>
        </div>
        <div class="command-example">
          <code>promptrek generate --all</code>
        </div>
      </div>

    </div>
  </div>
</section>

<section class="features-section">
  <div class="container">
    <h2 class="section-title">Powerful Features</h2>

    <div class="features-grid">
      <div class="feature-card-modern">
        <div class="feature-icon">🔄</div>
        <h3>Variable Substitution</h3>
        <p>Use dynamic variables in your prompts that get substituted during generation. Perfect for project-specific configurations.</p>
      </div>

      <div class="feature-card-modern">
        <div class="feature-icon">🎯</div>
        <h3>Conditional Instructions</h3>
        <p>Apply different instructions based on project context or target editor. Smart prompts that adapt to your environment.</p>
      </div>

      <div class="feature-card-modern">
        <div class="feature-icon">📦</div>
        <h3>Import System</h3>
        <p>Organize and reuse prompt components across multiple configurations. Build a library of reusable prompt templates.</p>
      </div>

      <div class="feature-card-modern">
        <div class="feature-icon">🎨</div>
        <h3>Multi-Editor Support</h3>
        <p>Generate prompts for all major AI coding assistants from a single source. Never write the same prompt twice.</p>
      </div>
    </div>
  </div>
</section>

<section class="benefits-section">
  <div class="container">
    <h2 class="section-title">Why Choose PrompTrek?</h2>

    <div class="benefits-grid">
      <div class="benefit-card">
        <div class="benefit-icon">👤</div>
        <h3>For Individual Developers</h3>
        <ul>
          <li>Work seamlessly across different AI editors</li>
          <li>Maintain consistent coding standards</li>
          <li>Easy experimentation with new AI tools</li>
        </ul>
      </div>

      <div class="benefit-card">
        <div class="benefit-icon">👥</div>
        <h3>For Teams</h3>
        <ul>
          <li>Standardized AI assistance across all team members</li>
          <li>Easy onboarding regardless of editor preference</li>
          <li>Consistent code quality and patterns</li>
        </ul>
      </div>

      <div class="benefit-card">
        <div class="benefit-icon">🏢</div>
        <h3>For Organizations</h3>
        <ul>
          <li>Reduce tool lock-in and migration costs</li>
          <li>Standardize AI-assisted development practices</li>
          <li>Scale AI adoption across diverse teams</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="cta-final-section">
  <div class="container">
    <div class="cta-content">
      <h2>Ready to Unify Your AI Coding Experience?</h2>
      <p>Join developers who have streamlined their AI editor workflows with PrompTrek.</p>
      <div class="cta-buttons">
        <a href="quick-start.html" class="btn-cta primary">Get Started Now</a>
        <a href="{{ site.github_url }}" class="btn-cta secondary" target="_blank">View on GitHub</a>
      </div>
    </div>
  </div>
</section>