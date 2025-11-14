# Jira Ticket Flow & Usage Conventions

This document defines the standard Jira workflow and conventions used by
the development team to ensure consistency, clarity, and efficient
collaboration.

------------------------------------------------------------------------

## 1. Jira Ticket Types

### **1.1 Story**

-   Represents a feature or user requirement.
-   Should follow user story format: \> As a `<role>`{=html}, I want
    `<function>`{=html}, so that `<benefit>`{=html}

### **1.2 Task**

-   General work item that does not fit into Story or Bug.
-   Often technical tasks.

### **1.3 Bug**

-   Represents an issue that breaks expected behavior.
-   Requires reproduction steps and environment details.

### **1.4 Sub-task**

-   A smaller unit of work that belongs to a parent Story, Task, or Bug.

------------------------------------------------------------------------

## 2. Standard Workflow

### **2.1 Ticket Statuses**

  Status                         Meaning
  ------------------------------ ----------------------------------------
  **Backlog**                    Ticket created but not yet prioritized
  **Selected for Development**   Approved for upcoming sprint
  **In Progress**                Developer is currently working on it
  **In Review**                  Code submitted, pending code review
  **QA Testing**                 QA team is verifying the work
  **Ready for Release**          Passed QA and ready for deployment
  **Done**                       Deployed and verified

------------------------------------------------------------------------

## 3. Ticket Lifecycle

### **3.1 Creating a Ticket**

Every ticket must include: - **Title**: Clear and descriptive -
**Description**: The problem or feature details - **Acceptance
Criteria** (for Story) - **Steps to Reproduce** (for Bug) -
**Screenshots or logs** (if applicable) - **Priority Level**: Low /
Medium / High / Critical

------------------------------------------------------------------------

### **3.2 Moving a Ticket Through Workflow**

#### **Start work**

    Move ticket → In Progress
    Assign to yourself
    Create a branch: feature/JIRA-123-description

#### **Submit for review**

    Move ticket → In Review
    Create Pull Request
    Link PR to Jira ticket
    Request reviewers

#### **QA phase**

    Move ticket → QA Testing
    QA tests based on acceptance criteria

#### **Before release**

    Move ticket → Ready for Release
    Ticket included in release notes

#### **After deployment**

    Move ticket → Done
    Ensure no regression issues

------------------------------------------------------------------------

## 4. Branch and Commit Naming Conventions

### **4.1 Branch Naming**

    feature/JIRA-123-login-page
    bugfix/JIRA-210-crash-on-load
    hotfix/JIRA-099-payment-error

### **4.2 Commit Message Format**

Use the Jira ticket ID:

    JIRA-123: implement login page UI
    JIRA-210: fix crash when loading profile

------------------------------------------------------------------------

## 5. Commenting & Communication Rules

### **5.1 Use Jira Comments, Not DM**

-   All technical updates must be logged in Jira.
-   No important information hidden in Slack or private messages.

### **5.2 Mention People When Needed**

    @john please review this part
    @anna need clarification on API spec

### **5.3 Keep comments professional and concise**

------------------------------------------------------------------------

## 6. Attachments & Documentation Rules

-   Include screenshots for UI changes.
-   Attach logs and error messages for bugs.
-   Add diagrams when describing flows or architecture.
-   Link Jira tickets to Confluence pages if documentation is needed.

------------------------------------------------------------------------

## 7. Sprint & Release Integration

### **7.1 Sprint Planning**

-   Tickets must be well-defined before being pulled into a sprint.
-   Story points estimated using Fibonacci scale.

### **7.2 Release Notes**

Each release must include: - Jira list of completed tickets - Feature
highlights - Bug fixes - Known issues (if any)

------------------------------------------------------------------------

## 8. Best Practices

-   Keep tickets small and focused (1--3 days of work).
-   Avoid "giant tasks" without clear breakdowns.
-   Always update status immediately after changes.
-   Never leave a ticket in **In Review** for more than 24 hours.
-   Ensure all acceptance criteria are met before moving to QA.

------------------------------------------------------------------------

## 9. Benefits of Following Jira Conventions

-   Clear visibility across team members
-   Faster onboarding for new developers
-   Improved traceability during audits
-   Better communication with QA and PM
-   Predictable and reliable delivery process

------------------------------------------------------------------------

End of document.
