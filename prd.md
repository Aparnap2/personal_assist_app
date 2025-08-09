# Personal AI Assistant (Creator/Consultant MVP) — PRD, Workflow, Design, and Requirements

This PRD captures what buyers expect from personal AI assistants in 2025, and scopes a commercially viable MVP with clear workflows, UX, and technical requirements. It prioritizes measurable outcomes, human-in-the-loop safety, and integrations that drive quick ROI.[1][2][3]

## 1) Product Overview

- Product name: Nexus Personal AI
- Mission: Deliver a done-with-you assistant that produces brand-consistent social posts and organized Notion artifacts, with decisive consultation and human approvals.
- Core value:
  - Action over advice: auto-drafts and schedules content, and organizes notes/tasks in Notion (not just “tips”).[1]
  - Hyper-personalization: adapts to voice and goals via samples and feedback.[1]
  - Trust-first: human-in-the-loop approvals, audit trails, and resilient retries.[4][5][6][3][7]

Primary ICP: Solo consultants/creators active on X and Notion who want consistency, time savings, and engagement lift.[2][1]

Success focus: Time saved, approval rate without edits, engagement lift, weekly active automations.[2][1]

## 2) MVP Scope

Must-have capabilities (V1):
- Voice-calibrated social post drafting and scheduling for X with approval queue and “best time” suggestions.[1]
- Notion CRUD for notes, tasks, and meeting summaries from chat/uploads; templated pages.
- Opinionated consultation with “apply” actions that pipe outputs to X drafts or Notion items.
- Feedback loop: accept/reject, 1–5 rating; learning impacts next drafts/topics.
- Safety: moderation checks; default human approvals; full audit log.[5][6][3][7][4]

Deferrals (V1.1–V1.2):
- Calendar ingestion for proactive prompts.
- Lightweight content calendar and repost suggestions.
- Multi-account support.

Why this MVP: Buyers pick assistants that automate narrow, high-value workflows, integrate with their stack, and show ROI fast (time saved, engagement uplift).[2][1]

## 3) User Flows

### 3.1 First-time onboarding
1) Sign in with Google/LinkedIn/Twitter (Firebase Auth).
2) Connect X and Notion via OAuth.
3) Voice modeling:
   - Paste 10–20 writing samples or link past tweets; choose voice sliders (formal, punchy, contrarian).
4) Goals & themes:
   - Select domains, ICP, CTAs, posting frequency; pick Notion templates (task, note, meeting summary).
5) Quick win:
   - App generates 5 post drafts now; user approves/schedules 1–2; creates a Notion “Content Plan” page with links.

Outcome: User experiences immediate value and sets trust via approvals and auditability.[3][4]

### 3.2 Daily use
- Morning: “2 drafts ready” notification → 1-click approve/schedule → Notion sync updates content plan.
- During day: Ask for topics/positioning; convert to draft post or Notion task in one tap.
- Evening: Weekly analytics card recommends next topics, cadence tweaks, and reposts based on engagement.[1]

### 3.3 Human-in-the-loop approvals
- All outbound actions pause at approval gates; reviewers get summarized context and safe defaults (edit/approve/reject).[6][4][5][3]
- Long-lived state preserved during pauses; retries and recovery are automatic.[3]
- Full audit log for every action.[4][5][3]

## 4) Functional Requirements

Content co-pilot
- Draft X posts in user voice with hashtags and CTA variants; best-time suggestions; schedule queue; engagement capture from X API.[1]
- Quick-edit UX; one-tap A/B variants.

Notion automation
- Create/update pages for meeting notes, tasks, and project briefs; templates with variables; link content to themes/goals.
- Bi-directional status sync for tasks.

Consultation chat
- Short, decisive suggestions (topics, positioning, networking).
- “Apply” buttons to generate drafts/tasks immediately.

Feedback and learning
- Accept/reject, 1–5 usefulness; track edits; engagement outcomes reinforce topic/voice selection over time.[6][3]

Safety & trust
- Moderation for toxicity/privacy; configurable guardrails.
- Default approval mode; per-user policies for auto-post escalation.
- Audit trails with who/what/when, and rollback references.[7][5][4][3]

Performance targets
- Time-to-first-approved-draft: 99.5% uptime; robust retries for API calls and scheduled posts; dead-letter queue.
- Latency: ≤2s perceived response for chat; background jobs async.
- Security: OAuth, token vaulting, least-privilege scopes; audit logging.[5][4]
- Privacy: Clear data control; export/delete; no posting without consent.
- Observability: Task/job logs, approvals, errors, API health dashboards.[5][3]

## 6) Information Architecture

Data entities (examples)
- User, Integration(Twitter/Notion), VoiceProfile, Theme, Draft, Post, Schedule, EngagementMetrics, NotionPage, Task, MeetingSummary, Feedback, AuditEvent.
- Relationships kept in Neo4j to personalize suggestions and map drafts↔performance↔themes for learning.

Storage design
- Firestore: profiles, preferences, queue/status, chat history.
- Realtime DB: live draft/approval status feed.
- graphiti with Neo4j: knowledge graph of user skills, themes, drafts→posts→engagement, preferences for retrieval and learning.
- Object storage (S3/GCS): uploads, attachments.
- Redis: rate limits, short-lived state, job dedupe.

## 7) UX Design and Screens

Design principles
- Clear outcomes over chat verbosity; short advice with “Apply” buttons.
- Make approvals effortless; show confidence and safety badges.
- Always show “what will happen” and “where it goes” (Notion, X).
- Progress and status are visible; every action is traceable.[4][3]

Key screens
- Dashboard: mode toggle; “Drafts awaiting approval”; today’s schedule; last 7-day engagement sparkline; quick actions.
- Draft review: left: variant cards; right: “why this draft” (themes, tone), best-time picker; approve/schedule/edit/reject; confidence and moderation status.
- Consultation: chat + context rail (goals/themes/recent wins); suggestions with Apply-to-X/Notion.
- Notion hub: template selector; recent pages; quick-create; sync status.
- Analytics: engagement by theme/time; approval rate; edit rate; recommendations.

Microcopy
- “Approve and schedule for 10:30am (best-time).”
- “Why suggested: performs well Tue mornings; matches ‘AI strategy’ theme.”
- “Approved drafts increase your reach by 31% on average.”[2]

## 8) System Architecture

Frontend
- React/TypeScript; Firebase Auth; Firestore/Realtime SDKs.
- Web app first; responsive for mobile.

AI backend (Python)
- FastAPI + LangGraph for agent orchestration (consultation path, automation path, approval checkpoints).
- Services: Twitter(X) API, Notion API, OpenAI/Anthropic LLM, Moderation API.
- Neo4j service for retrieval and learning signals; embeddings for voice/theme retrieval.

Orchestration patterns
- Human-in-the-loop pauses with long-lived state; resumable workflows; policy-driven approvals (per action type/sensitivity).[7][6][3][4][5]
- Error handling with checkpointing, retries, and escalations.[3]

Scheduling and jobs
- Post scheduler with idempotent jobs and backoff.
- Engagement collectors run periodically; write to metrics; trigger insights.

Security
- OAuth per integration; token encryption; scope minimization; rotation.
- Role-based approval thresholds (e.g., allow auto-post for “low-risk” templates after N clean approvals).

## 9) Detailed Workflows

A) Draft and schedule a post
- Trigger: user asks for weekly topics or taps “Generate drafts.”
- Retrieve themes/voice → generate 5 variants → run moderation → enqueue approval items.
- User approves 2, schedules at best-time; scheduler posts; engagement collector logs metrics; learning updates topic/voice weights.[4][3][1]

B) Meeting summary to Notion
- User uploads transcript or pastes notes → summarize → create Notion page using template; create 3 tasks with due dates; link to theme and upcoming post ideas.

C) Consultation to automation
- User: “How should I position my offer for architects?” → concise advice + “Draft 3 posts” and “Create Notion brief” buttons → user approves both.

D) Human-in-the-loop policy
- All outbound posts require approval unless policy escalates (e.g., “template T, low-risk topics, >20 clean approvals”) → still audit and notify.[6][5][3][4]

## 10) Metrics and Instrumentation

Product KPIs
- Time-to-first-approved-draft; approval rate without edits; engagement delta; weekly active automations; retention cohorts.

GTM/Revenue
- Trial-to-paid after first success moment; average time saved/week; case study lifts (screenshots, anonymized charts).[2]

Ops health
- Post success rate, retries, failed jobs, API quotas, moderation rejects, P95 latency.

Continuous improvement
- Evals on drafts and outcomes; bandit selection for topics/tone/cadence; release notes that show “what got smarter”.[3]

## 11) Roadmap (90 days)

- Weeks 1–2: Onboarding, OAuth, voice modeling, consultation scaffold, Notion quick-create.
- Weeks 3–4: X drafts, approval queue, scheduler, moderation, audit log.
- Weeks 5–6: Engagement ingestion, analytics card, feedback loop, A/B variants.
- Weeks 7–8: Content calendar, topic recommendations from performance, reliability hardening.
- Weeks 9–12: Concierge beta (25–50 users), iterate from feedback, publish case studies, consider calendar ingestion.

## 12) GTM Highlights

Positioning: “Your brand voice, done for you—approve great drafts in minutes and keep your Notion organized.”

Channels and proof
- Founder-led social with before/after posts and time saved.
- Partnerships with creator/consultant communities; in-app upgrade at success moments.
- Case studies and quantified lifts (conversion lift claims should reference engagement deltas and intent-driven outreach effectiveness).[2]

Pricing (test/iterate)
- Starter $19: 30 drafts/mo, Notion CRUD, approvals.
- Pro $49: 120 drafts, scheduler, analytics, voice tuner.
- Team $149: multi-user, multi-workspace, concierge onboarding.

Why this GTM: AI-powered GTM that uses intent, omnichannel proof, and automation drives faster conversion and lower CAC in 2025.[8][9][10][2]

***

Notes and rationale
- Feature selection matches what expert reviewers highlight as “must-have” assistant traits today: meeting/document summaries, calendar/task automation, integrations, workflow automation, and voice-consistent content.[11][12][13][1]
- Human-in-the-loop, state persistence, and auditability are emphasized as best practices for safe, reliable agents.[14][7][5][6][4][3]
- GTM leverages AI-era tactics that improve conversion and speed-to-market with personalization and intent signals.[9][10][8][2]

