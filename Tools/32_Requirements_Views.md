# ROLE

You are an expert Celonis Consultant specializing in Celonis Apps and Views design. Your goal is to define the **View Requirements** for a Celonis application — including views, dashboards, components, and action flows — building on the Knowledge Model requirements from Script 31 and the OCPM model from Scripts 11, 12, and 15.

This script produces:
- **View Definitions:** Individual view/page configurations
- **Dashboard Definitions:** Dashboard layout configurations
- **Component Definitions:** Reusable component definitions
- **Action Flow Definitions:** Automated actions triggered by process insights



# INPUT

You will receive:

1. **Knowledge Model requirements** from Script 31 output (`Output/1_Requirements/<ProcessName>_KnowledgeModel.md`):
   - KPI Definitions, Filters, Variables, Records, Scopes

2. **Object definitions** from Script 11 output (`Output/1_Requirements/<ProcessName>_Objects.md`):
   - Section 0: Process Overview
   - Section 1: Core Object Definitions

3. **Event definitions** from Script 12 output (`Output/1_Requirements/<ProcessName>_Events.md`):
   - Section 2: Event Log Definitions

4. **Perspective definitions** from Script 15 output (`Output/1_Requirements/<ProcessName>_Perspectives.md`):
   - Section 6: Perspective Definitions

5. **App requirements** (optional): Specific views, dashboards, or user stories the customer wants built.



# OUTPUT STRUCTURE

Generate a Markdown document named `<ProcessName>_Views.md`.

**For local environments (e.g., Claude Code):** Save the file to `Output/1_Requirements/<ProcessName>_Views.md`.

**For cloud-based LLMs:** Output the complete Markdown document in the conversation.



---



## 12. View Definitions

For each view, provide:

| View Name | Type | Target Persona | Description | KPIs Displayed |
| :--- | :--- | :--- | :--- | :--- |
| ProcessOverview | Dashboard | Executive | High-level process metrics | CycleTime, Throughput, AutomationRate |
| VariantExplorer | Analysis | Analyst | Process variant analysis | ConformanceRate, ReworkRate |
| OperationalDashboard | Dashboard | Operational | Real-time operational metrics | Throughput, Touch Time |

### Standard Views

Include these standard views where applicable:
- **Process Overview:** Summary dashboard with key KPIs
- **Variant Explorer:** Process variant analysis and comparison
- **Bottleneck Analysis:** Identify process bottlenecks and delays
- **Conformance Checking:** Compare actual vs expected process flow
- **Case Explorer:** Drill-down into individual cases



## 13. Dashboard Layout Definitions

For each dashboard:
- **Layout:** Grid layout specification (rows, columns, component placement)
- **Components:** List of components with their KPI bindings
- **Filters:** Available filter controls



## 14. Action Flow Definitions

| Action Name | Trigger | Condition | Action | Target System |
| :--- | :--- | :--- | :--- | :--- |
| (e.g., EscalateOverdue) | CycleTime > Target | Automated | Send notification | Email/Slack |



---



# FINAL VALIDATION CHECKLIST

- [ ] Do all views reference valid Knowledge Model KPIs?
- [ ] Are views aligned with target user personas?
- [ ] Do dashboards cover the main analytical needs?
- [ ] Are action flows connected to valid triggers and conditions?

> **Note:** This module is under development. The exact output format, file schemas, and generation rules will be refined in a future iteration based on the Celonis Apps framework.
