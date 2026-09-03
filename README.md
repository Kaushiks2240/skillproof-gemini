
# SkillProof

> Prove what you built.

SkillProof is an AI-powered project evidence analysis platform that connects student project claims to concrete repository evidence.

Instead of simply accepting claims such as:

> "I built a machine learning model."

SkillProof asks:

> **What evidence in the submitted project actually supports that claim?**

The core idea is:

**CLAIM ↔ EVIDENCE**

SkillProof analyzes submitted project evidence using Google Gemini and produces a structured, evidence-grounded assessment of the student's technical claims.

---

## Problem

Students often describe technologies and skills in resumes, project reports, and portfolios, but evaluating whether those claims are supported by their actual project work can be difficult and time-consuming.

Evaluators may need to manually inspect:

- Source code
- Dependencies
- Controllers and services
- Database schemas
- Configuration files
- Tests
- Other project artifacts

Traditional viva questions also tend to test generic textbook knowledge instead of the student's actual implementation.

---

## Solution

SkillProof creates an evidence pipeline that connects:

**Student Claims → Project Evidence → Gemini Reasoning → Evidence Assessment → Personalized Viva → Public Portfolio**

For every claim, SkillProof evaluates how strongly the submitted evidence supports it.

The system uses four support levels:

- **STRONG** — Direct implementation evidence supports the claim.
- **MODERATE** — Supporting evidence exists, but implementation is incomplete.
- **WEAK** — Limited or indirect evidence exists.
- **UNSUPPORTED** — No meaningful submitted evidence supports the claim.

---

# How It Works

```text
                    STUDENT
                       │
                       ▼
              ┌─────────────────┐
              │   SUBMIT SCREEN  │
              │                 │
              │ Problem         │
              │ Claims          │
              │ Contributions   │
              │ Project Evidence│
              └────────┬────────┘
                       │
                       │ POST /api/analyze
                       ▼
              ┌─────────────────┐
              │ Flask Backend   │
              │ Python REST API │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Gemini 2.5 Flash│
              │                 │
              │ Evidence        │
              │ Reasoning       │
              │ Gap Analysis    │
              │ Viva Generation │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Structured      │
              │ Analysis Result │
              └────────┬────────┘
                       │
              ┌────────┴────────┐
              ▼                 ▼
       Firebase Firestore   Frontend Analysis
              │
              ▼
       Public Portfolio
              │
              ▼
          QR Code
````

---

# Core Evidence Pipeline

## 1. Candidate Input

The student provides:

* Problem narrative
* Solution description
* Technical/project claims
* Contribution breakdown
* Project evidence
* Repository files or GitHub repository information

---

## 2. Evidence Analysis

The Flask backend sends the project information and submitted evidence to Gemini 2.5 Flash.

Gemini analyzes the evidence against the student's claims.

For example:

```text
Claim:
"Built Java Spring Boot backend and MySQL schema"

Evidence:
- pom.xml
- AttendanceController.java
- AttendanceRepository.java
- db/schema.sql
```

Gemini can identify:

```text
pom.xml
    ↓
Spring Boot + JPA dependencies

AttendanceController.java
    ↓
REST endpoints

AttendanceRepository.java
    ↓
Database queries

db/schema.sql
    ↓
Tables + foreign keys + enums
```

The claim can therefore receive:

```text
STRONG
```

---

# Negative-Claim Detection

A major feature of SkillProof is identifying claims that do not have corresponding implementation evidence.

Example:

```text
Claim:
"Built an ML model predicting low student attendance"
```

But the repository contains:

```text
No ML libraries
No Python scripts
No notebooks
No model weights
No predictive service
No controller invoking ML logic
```

SkillProof can classify the claim as:

```text
UNSUPPORTED
```

and explain what evidence is missing.

The system does not invent evidence to make a claim appear stronger.

---

# Strict Support-Level Classification

SkillProof uses four fixed support levels:

| Level           | Meaning                                             |
| --------------- | --------------------------------------------------- |
| **STRONG**      | Direct implementation evidence supports the claim   |
| **MODERATE**    | Evidence exists but implementation is incomplete    |
| **WEAK**        | Limited or indirect evidence exists                 |
| **UNSUPPORTED** | No meaningful submitted evidence supports the claim |

This structured classification makes the Gemini response predictable and easier for the frontend to display.

---

# Personalized Viva Generation

SkillProof does not rely only on generic technical questions.

Instead, viva questions are generated from the student's actual project evidence.

For example, if the repository contains an endpoint that performs multiple database queries, SkillProof may generate a question such as:

```text
How would you optimize this endpoint into a
single aggregate JPQL query?
```

This allows evaluators to test whether the student understands the implementation decisions behind their project.

---

# Evidence-Grounded Project Story

After analyzing the evidence, SkillProof can synthesize the project into an evidence-backed technical profile.

The resulting profile can contain:

* Project information
* Technologies
* Supported claims
* Evidence
* Missing evidence
* Support levels
* Skills
* Personalized viva questions
* Portfolio information

---

# Structured AI Output

Gemini produces a structured response rather than relying only on free-form text.

Conceptually:

```json
{
  "project": {},
  "technologies": [],
  "claims": [
    {
      "claim": "",
      "support_level": "",
      "evidence": [],
      "reason": ""
    }
  ],
  "skills": [],
  "viva_questions": [],
  "portfolio": {}
}
```

The support level is constrained to:

```text
STRONG
MODERATE
WEAK
UNSUPPORTED
```

This allows the frontend to reliably render the analysis.

---

# Application Screens

SkillProof currently uses three primary screens:

### 1. Submit

`submit.html`

Collects:

* Problem narrative
* Solution claims
* Contribution information
* Repository/project evidence

### 2. Analysis

`analysis.html`

Displays:

* Claim ↔ Evidence matrix
* Support levels
* Missing evidence
* Evidence reasoning
* Personalized viva questions

### 3. Portfolio

`portfolio.html`

Displays:

* Evidence-backed project story
* Project information
* Supported skills
* Public portfolio information
* QR code

---

# Backend

SkillProof uses a lightweight Flask REST backend.

Main analysis endpoint:

```text
POST /api/analyze
```

The backend is responsible for:

1. Receiving project information
2. Preparing the Gemini request
3. Calling the Gemini API
4. Processing the structured response
5. Returning the analysis to the frontend
6. Connecting the analysis to persistence

The Gemini API key is kept server-side using:

```text
GEMINI_API_KEY
```

rather than exposing it in frontend code.

---

# Cloud Persistence

SkillProof uses Firebase Firestore to persist assessments.

Projects are associated with unique identifiers such as:

```text
SP-A7K29
```

Conceptually:

```text
projects/
   SP-A7K29
```

The application also supports a localStorage fallback for situations where cloud persistence is unavailable.

---

# Public Portfolio

Each analyzed project can be associated with a public portfolio route:

```text
/p/SP-A7K29
```

This allows an evaluator or recruiter to access the evidence-backed project profile without going through the submission flow again.

---

# QR Code

SkillProof can generate a QR code pointing to the project's public portfolio.

```text
QR Code
   ↓
/p/SP-A7K29
   ↓
Evidence-backed Portfolio
```

The QR code acts as a simple sharing and distribution mechanism for the portfolio.

---

# Technology Stack

| Layer           | Technology                 |
| --------------- | -------------------------- |
| Frontend        | HTML, CSS, JavaScript      |
| UI Design       | Google Stitch / Material 3 |
| Styling         | Tailwind CSS               |
| Backend         | Python + Flask             |
| AI              | Google Gemini 2.5 Flash    |
| AI SDK          | Google GenAI SDK           |
| Database        | Firebase Firestore         |
| Client Fallback | Browser localStorage       |
| Distribution    | QR Code                    |

---

# API

### Analyze Project

```text
POST /api/analyze
```

Receives the student's project information and evidence and returns the Gemini-powered assessment.

### Public Portfolio

```text
GET /p/<project_id>
```

Example:

```text
/p/SP-A7K29
```

---

# Project Flow

```text
SUBMIT
   ↓
ANALYZE
   ↓
COMPARE CLAIMS ↔ EVIDENCE
   ↓
CLASSIFY SUPPORT
   ↓
IDENTIFY GAPS
   ↓
GENERATE VIVA
   ↓
STORE RESULT
   ↓
BUILD PORTFOLIO
   ↓
SHARE WITH QR
```

---

# Team Architecture

SkillProof was developed using four specialized tracks:

### Backend + Gemini API

* Flask REST API
* Gemini integration
* API key isolation
* CORS
* Backend verification

### Frontend + UI

* Three-screen application
* Google Stitch / Material 3 design
* Responsive interface
* Candidate/session handling

### AI Reasoning + Schema

* Structured Gemini response schema
* Support-level classification
* Negative-claim detection
* Evidence gap analysis
* Code-grounded viva generation
* Evidence-grounded project storytelling

### Firebase + Product

* Firestore persistence
* Project IDs
* Public portfolio routing
* QR generation
* localStorage fallback

---

# Important Principle

SkillProof does **not** claim to prove whether a student is truthful or whether they personally wrote every submitted file.

It evaluates whether the:

**submitted evidence supports the submitted claims.**

```text
CLAIM
  ↓
EVIDENCE
  ↓
GEMINI ANALYSIS
  ↓
SUPPORT LEVEL
  ↓
EXPLANATION
```
```
```
