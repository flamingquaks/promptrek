---
layout: default
title: Home
---

<style>
/* Fix horizontal overflow on entire page */
html, body {
  overflow-x: hidden !important;
  width: 100% !important;
  max-width: 100vw !important;
  margin: 0 !important;
  padding: 0 !important;
}
body.home-page {
  overflow-x: hidden !important;
}
.home-page .wrapper {
  max-width: 100% !important;
  padding: 0 !important;
  margin: 0 !important;
  overflow-x: hidden !important;
}
/* Allow header wrapper to show dropdown menu */
.home-page .site-header .wrapper {
  overflow: visible !important;
}
.home-page .page-content {
  padding: 0 !important;
}

/* Force button fixes with maximum specificity */
.cta-final-section .btn-cta.primary {
  background: white !important;
  color: #0f172a !important;
  border: 2px solid white !important;
}
.cta-final-section .btn-cta.secondary {
  background: transparent !important;
  color: white !important;
  border: 2px solid white !important;
}

/* Fix benefits section - full width, no wrapper constraints */
.benefits-section {
  width: 100% !important;
  max-width: 100% !important;
  margin: 0 !important;
  padding: 4rem 0 !important;
  box-sizing: border-box !important;
}
.benefits-section .container {
  max-width: 1200px !important;
  margin: 0 auto !important;
  padding: 0 2rem !important;
  width: 100% !important;
  box-sizing: border-box !important;
}
.benefits-grid {
  display: grid !important;
  grid-template-columns: repeat(3, 1fr) !important;
  gap: 2rem !important;
  width: 100% !important;
  margin: 0 !important;
}

/* Fix CTA section - full width, no wrapper constraints */
.cta-final-section {
  width: 100% !important;
  max-width: 100% !important;
  margin: 0 !important;
  padding: 4rem 0 !important;
  box-sizing: border-box !important;
}

@media (max-width: 1024px) {
  .benefits-grid {
    grid-template-columns: 1fr !important;
  }
}
</style>

<section class="intro-section">
  <div class="container">
    <div class="intro-content">
      <h2 class="section-title">One Configuration.<br>Every AI Editor.<br>Prompts, Plugins & Beyond.</h2>
      <p class="intro-description">Define your complete AI editor setup once - prompts, MCP servers, custom commands, autonomous agents, and event hooks - then let PrompTrek take it on a journey across every platform. Stop recreating configurations for GitHub Copilot, Cursor, Continue, Claude Code, and more.</p>
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
          <li>Universal format for all prompt, MCP, agent, & hook configurations</li>
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
    <h2 class="section-title">9 Supported AI Editors (So far...)</h2>
    <p class="section-description">Generate perfect configurations for all major AI coding assistants from one universal format</p>

    <div class="editors-grid">
      <a href="https://github.com/features/copilot" target="_blank" rel="noopener noreferrer" class="editor-card">
        <div class="editor-icon">
          <img src="https://github.githubassets.com/images/modules/site/copilot/copilot.png" alt="GitHub Copilot" width="64" height="64" onerror="this.style.display='none'; this.nextElementSibling.style.display='inline';">
          <span style="display:none; font-size: 64px;">🐙</span>
        </div>
        <h3>GitHub Copilot</h3>
      </a>

      <a href="https://www.cursor.com" target="_blank" rel="noopener noreferrer" class="editor-card">
        <div class="editor-icon">
          <img src="assets/cursor.png" alt="Cursor" width="64" height="64" onerror="this.style.display='none'; this.nextElementSibling.style.display='inline';">
          <span style="display:none; font-size: 64px;">🎯</span>
        </div>
        <h3>Cursor</h3>
      </a>

      <a href="https://www.continue.dev" target="_blank" rel="noopener noreferrer" class="editor-card">
        <div class="editor-icon">
          <img src="https://cdn.prod.website-files.com/663e06c56841363663ffbbcf/664c918ec47bacdd3acdc167_favicon%408x.png" alt="Continue" width="64" height="64" onerror="this.style.display='none'; this.nextElementSibling.style.display='inline';">
          <span style="display:none; font-size: 64px;">⚡</span>
        </div>
        <h3>Continue</h3>
      </a>

      <a href="https://kiro.dev" target="_blank" rel="noopener noreferrer" class="editor-card">
        <div class="editor-icon">
          <img src="https://kiro.dev/favicon.ico" alt="Kiro" width="64" height="64" onerror="this.style.display='none'; this.nextElementSibling.style.display='inline';">
          <span style="display:none; font-size: 64px;">🤖</span>
        </div>
        <h3>Kiro</h3>
      </a>

      <a href="https://github.com/cline/cline" target="_blank" rel="noopener noreferrer" class="editor-card">
        <div class="editor-icon">
          <img src="assets/cline-logo.svg" alt="Cline" width="64" height="64" onerror="this.style.display='none'; this.nextElementSibling.style.display='inline';">
          <span style="display:none; font-size: 64px;">📝</span>
        </div>
        <h3>Cline</h3>
      </a>

      <a href="https://docs.claude.com/en/docs/claude-code" target="_blank" rel="noopener noreferrer" class="editor-card">
        <div class="editor-icon">
          <img src="assets/claude-code.svg" alt="Claude Code" width="64" height="64" onerror="this.style.display='none'; this.nextElementSibling.style.display='inline';">
          <span style="display:none; font-size: 64px;">📝</span>
        </div>
        <h3>Claude Code</h3>
      </a>

      <a href="https://codeium.com/windsurf" target="_blank" rel="noopener noreferrer" class="editor-card">
        <div class="editor-icon">
          <img src="assets/windsurf.svg" alt="Windsurf" width="64" height="64" onerror="this.style.display='none'; this.nextElementSibling.style.display='inline';">
          <span style="display:none; font-size: 64px;">📝</span>
        </div>
        <h3>Windsurf</h3>
      </a>

      <a href="https://aws.amazon.com/q/developer/" target="_blank" rel="noopener noreferrer" class="editor-card">
        <div class="editor-icon">
          <img src="assets/q-logo.svg" alt="Amazon Q" width="64" height="64" onerror="this.style.display='none'; this.nextElementSibling.style.display='inline';">
          <span style="display:none; font-size: 64px;">☁️</span>
        </div>
        <h3>Amazon Q</h3>
      </a>

      <a href="https://www.jetbrains.com/ai/" target="_blank" rel="noopener noreferrer" class="editor-card">
        <div class="editor-icon">
          <img src="https://resources.jetbrains.com/storage/products/company/brand/logos/jb_beam.png" alt="JetBrains AI" width="64" height="64" onerror="this.style.display='none'; this.nextElementSibling.style.display='inline';">
          <span style="display:none; font-size: 64px;">🧠</span>
        </div>
        <h3>JetBrains AI</h3>
      </a>
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
            <code>promptrek</code>
          </div>
          <p><strong>New!</strong> Interactive wizard guides you through setup, or use:<br><code>promptrek init --setup-hooks</code> for traditional CLI</p>
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
        <h3>Universal Configuration (Schema v3.1.0)</h3>
        <p>Write your prompt once in PrompTrek format:</p>
        <div class="code-example">
{% raw %}<pre><code>schema_version: "3.1.0"
metadata:
  title: "Full-Stack Development Assistant"
  description: "Production-ready coding standards"
  tags: [fullstack, typescript, react]

content: |
  # Full-Stack Development Assistant

  Last updated: {{{ CURRENT_DATE }}} at {{{ CURRENT_TIME }}}
  Current Branch: {{{ GIT_BRANCH }}}

  ## General Guidelines
  - Write clean, maintainable code with proper error handling
  - Use TypeScript with strict mode for all new code
  - Follow SOLID principles and design patterns
  - Include comprehensive JSDoc comments
  - Contact {{{ TEAM_NAME }}} for code review assistance

  ## Frontend Development
  - Use React functional components with hooks
  - Implement proper loading states and error boundaries
  - Follow accessibility best practices (WCAG 2.1)
  - Write unit tests with Jest and React Testing Library

  ## Backend Development
  - Use RESTful API design with proper HTTP status codes
  - Implement input validation and sanitization
  - Add proper logging and monitoring
  - Write integration tests for all endpoints

variables:
  TEAM_NAME: "Engineering Team"
  GIT_BRANCH:
    type: command
    value: git rev-parse --abbrev-ref HEAD</code></pre>{% endraw %}
        </div>
        <p class="schema-note">✨ <strong>Schema v3.1.0 (Latest Stable)</strong>: Markdown-first with clean top-level plugins and refined agent model. No <code>targets</code> field needed - works with ALL editors! MCP servers, commands, agents, and hooks at the top level.<br><br>
        <em>Note: Schema versions (v1.x, v2.x, v3.x) define the configuration file format and are independent of the PrompTrek application version.</em></p>
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
            <span class="file-name">.continue/mcpServers/*.yaml</span>
          </div>
          <div class="file-item">
            <span class="file-icon">📄</span>
            <span class="file-name">.continue/prompts/*.md</span>
          </div>
          <div class="file-item">
            <span class="file-icon">📄</span>
            <span class="file-name">.continue/rules/*.md</span>
          </div>
          <div class="file-item">
            <span class="file-icon">📄</span>
            <span class="file-name">.clinerules/*.md</span>
          </div>
          <div class="file-item">
            <span class="file-icon">📄</span>
            <span class="file-name">.kiro/steering/*.md</span>
          </div>
          <div class="file-item">
            <span class="file-icon">📄</span>
            <span class="file-name">.windsurf/rules/*.md</span>
          </div>
          <div class="file-item">
            <span class="file-icon">📄</span>
            <span class="file-name">.assistant/rules/*.md</span>
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
        <div class="feature-icon">⚡</div>
        <h3>Multi-Step Workflows</h3>
        <p>Define complex, automated workflows with tool requirements and structured steps. Perfect for PR reviews, deployments, and testing pipelines. <a href="user-guide/workflows.html">Learn more →</a></p>
      </div>

      <div class="feature-card-modern">
        <div class="feature-icon">◆</div>
        <h3>Dynamic Variables</h3>
        <p>Built-in variables (version, timestamp, date), command-based variables (git info, system details), and file-based variables. Keep sensitive values in .promptrek/variables.promptrek.yaml (automatically gitignored). <a href="user-guide/advanced-features.html#variable-substitution">Learn more →</a></p>
      </div>

      <div class="feature-card-modern">
        <div class="feature-icon">⟷</div>
        <h3>Import & Sync</h3>
        <p>Import existing editor configurations into PrompTrek format. 9 editors (GitHub Copilot, Cursor, Continue, Kiro, Cline, Windsurf, Claude Code, Amazon Q, JetBrains) support lossless round-trip: generate to editor files, then sync changes back to PrompTrek.</p>
      </div>

      <div class="feature-card-modern">
        <div class="feature-icon">◉</div>
        <h3>Preview Mode</h3>
        <p>Preview generated output before creating files. Test configurations with variable overrides without making changes.</p>
      </div>

      <div class="feature-card-modern">
        <div class="feature-icon">▣</div>
        <h3>Built-in Templates</h3>
        <p>Production-ready templates for common project types (basic, React, API). Initialize new projects instantly with best practices baked in.</p>
      </div>

      <div class="feature-card-modern">
        <div class="feature-icon">◎</div>
        <h3>Multi-Editor Support</h3>
        <p>Generate prompts for 9 major AI coding assistants from a single source (GitHub Copilot, Cursor, Continue, Claude Code, Cline, Windsurf, Kiro, Amazon Q, JetBrains). Never write the same prompt twice.</p>
      </div>

      <div class="feature-card-modern">
        <div class="feature-icon">✓</div>
        <h3>Pre-commit Integration</h3>
        <p>Automatic validation and protection. Pre-commit hooks ensure your .promptrek.yaml files are valid and prevent accidental commits of generated files.</p>
      </div>

      <div class="feature-card-modern">
        <div class="feature-icon">≡</div>
        <h3>JSON Schema Support</h3>
        <p>Published JSON Schemas for schema v2.0, v2.1, v3.0, and v3.1. Get autocompletion, validation, and inline documentation in your editor. <a href="schema/">Learn more →</a></p>
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
