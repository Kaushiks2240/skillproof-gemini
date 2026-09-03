````markdown
# SkillProof

> Prove what you built.

SkillProof is an AI-powered project evidence analysis platform that converts student project evidence into an evidence-backed skill profile.

The core idea is:

**CLAIM ↔ EVIDENCE**

SkillProof compares what a student claims to have built with the evidence they submit and identifies how strongly the evidence supports those claims.

## Problem

Students can claim experience with technologies or skills in their projects, but evaluating whether their submitted work actually supports those claims can be difficult and time-consuming.

## Solution

SkillProof analyzes student project evidence using Gemini and produces a structured result containing:

- Project information
- Technologies found in the evidence
- Student claims
- Supporting evidence
- Missing evidence
- Evidence-backed skills
- Personalized viva questions
- Portfolio information

## How It Works

```text
Student
   ↓
Project Evidence
   ↓
Gemini AI Analysis
   ↓
Claim ↔ Evidence Analysis
   ↓
Skills + Evidence Strength
   ↓
Personalized Viva Questions
   ↓
SkillProof Profile
   ↓
Public Portfolio + QR
````

## Evidence Strength

| Strength    | Meaning                               |
| ----------- | ------------------------------------- |
| STRONG      | Evidence directly supports the claim  |
| MODERATE    | Evidence partially supports the claim |
| WEAK        | Limited evidence supports the claim   |
| UNSUPPORTED | No meaningful supporting evidence     |

## Example

### Student Claim

```text
Built Java backend
```

### Supporting Evidence

```text
Java backend source code
REST controllers
```

### Result

```text
STRONG
```

### Personalized Viva Question

```text
Why did you choose a REST architecture?
```

## Core Output

SkillProof produces structured JSON containing:

```json
{
  "project": {},
  "technologies": [],
  "claims": [],
  "skills": [],
  "viva_questions": [],
  "portfolio": {}
}
```

## Public Portfolio

Each analyzed project can be associated with a unique Project ID.

Example:

```text
SP-A7K29
```

The Project ID can be used to access the project's public portfolio.

## QR Code

A QR code can be generated for the public portfolio so that the profile can be easily shared.

## Technology Stack

* **Frontend:** HTML / CSS / JavaScript
* **Backend:** Python
* **AI:** Gemini API
* **Database:** Firebase Firestore
* **QR Code:** QR code library

## API

```text
POST /api/analyze
POST /api/generate-viva
POST /api/generate-portfolio
GET  /api/project/<project_id>
GET  /p/<project_id>
```

## Project Flow

```text
SUBMIT
   ↓
ANALYZE
   ↓
COMPARE
   ↓
PROVE
   ↓
EXPLAIN
   ↓
SHARE
```

## Important Principle

SkillProof does **not** claim to prove whether a student is truthful or whether they personally wrote every submitted file.

It evaluates whether the **submitted evidence supports the submitted claims**.

```
```
