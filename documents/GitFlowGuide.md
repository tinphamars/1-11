# Git Flow for Development Teams

Git Flow is a structured branching model that helps development teams
collaborate efficiently, maintain clean version history, and support
parallel development. This document outlines the typical Git Flow
process used by modern software teams.

------------------------------------------------------------------------

## 1. Main Branches

### **1.1 `main` (production branch)**

-   Contains **production-ready** code.
-   Every commit should be stable and deployable.
-   Only updated through **merge of release** or **hotfix** branches.

### **1.2 `develop` (integration branch)**

-   Contains the latest delivered development changes.
-   All features branch out from and merge back into `develop`.
-   Serves as the pre-release stage.

------------------------------------------------------------------------

## 2. Supporting Branch Types

### **2.1 Feature Branches**

-   Naming: `feature/<feature-name>`
-   Used to develop new features for upcoming releases.
-   Created from: `develop`
-   Merged back into: `develop`

**Flow:**

    git checkout develop
    git pull
    git checkout -b feature/login-page

After finishing:

    git checkout develop
    git merge feature/login-page
    git branch -d feature/login-page

------------------------------------------------------------------------

### **2.2 Release Branches**

-   Naming: `release/<version>`
-   Created when the next release is nearly ready.
-   Used for final testing, documentation, and minor bug fixes.
-   Created from: `develop`
-   Merged into: `main` and `develop`

**Flow:**

    git checkout develop
    git checkout -b release/1.2.0

After preparing the release:

    git checkout main
    git merge release/1.2.0
    git tag -a v1.2.0 -m "Release 1.2.0"

    git checkout develop
    git merge release/1.2.0
    git branch -d release/1.2.0

------------------------------------------------------------------------

### **2.3 Hotfix Branches**

-   Naming: `hotfix/<issue-name>`
-   Used to fix critical bugs in production.
-   Created from: `main`
-   Merged into: `main` and `develop`

**Flow:**

    git checkout main
    git checkout -b hotfix/fix-login-crash

After fixing:

    git checkout main
    git merge hotfix/fix-login-crash
    git tag -a v1.2.1 -m "Hotfix 1.2.1"

    git checkout develop
    git merge hotfix/fix-login-crash
    git branch -d hotfix/fix-login-crash

------------------------------------------------------------------------

## 3. Pull Request (PR) Workflow

Teams often require PRs for merging:

1.  Developer pushes branch.
2.  Creates a Pull Request (PR) to `develop` or `main`.
3.  CI runs automated tests.
4.  Reviewers approve the PR.
5.  Squash or merge commits (depending on team policy).

------------------------------------------------------------------------

## 4. Recommended Commit Message Format

Use semantic or conventional commits:

    feat: add login page
    fix: resolve crash on startup
    docs: update API documentation
    refactor: improve database layer

------------------------------------------------------------------------

## 5. Summary Diagram

               ┌──────────────┐
               │    main       │
               └───────▲──────┘
                       │
            ┌──────────┴───────────┐
            │        release        │
            └──────────▲───────────┘
                       │
         ┌─────────────┴──────────────┐
         │           develop           │
         └───────▲──────────┬─────────┘
                 │           │
            ┌────┴───┐   ┌──┴──────┐
            │ feature │   │ hotfix  │
            └─────────┘   └─────────┘

------------------------------------------------------------------------

## 6. Best Practices

-   Keep feature branches small and focused.
-   Always update branch from the latest `develop` before merging.
-   Use PR templates and require at least one reviewer.
-   Run automated tests before merging.
-   Tag every production release.

------------------------------------------------------------------------

## 7. Benefits of Git Flow

-   Clear separation between production, development, and features.
-   Supports multiple developers working simultaneously.
-   Reduces merge conflicts.
-   Makes releases predictable and manageable.

------------------------------------------------------------------------

End of document.
