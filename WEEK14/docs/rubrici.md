# Evaluation Rubrics — Week 14: Final Project

## Contents

1. [Team Project Evaluation Rubric](#1-team-project-evaluation-rubric)
2. [Detailed Criteria](#2-detailed-criteria)
3. [Grading Scale](#3-grading-scale)
4. [Defence Questions](#4-defence-questions)
5. [Originality Indicators](#5-originality-indicators)

---

## 1. Team Project Evaluation Rubric

### Criterion A: Technical Complexity (40 points)

| Score | Descriptor | Indicators |
|-------|------------|------------|
| 36-40 | Exceptional | Multi-tier architecture, custom protocol or significant extension, functional load balancing, data persistence, advanced logging |
| 30-35 | Very Good | TCP/UDP client-server with multiple functionalities, data validation, error handling, at least 3 message types |
| 24-29 | Good | Functional client-server with 2 message types, basic error handling, structured code |
| 16-23 | Satisfactory | Echo client-server with minor modifications, functional but minimal code |
| 0-15  | Insufficient | Non-functional or copied code without understanding |

### Criterion B: Functionality and Demonstration (30 points)

| Score | Descriptor | Indicators |
|-------|------------|------------|
| 27-30 | Exceptional | Impeccable live demonstration, multiple scenarios, error recovery demonstrated |
| 22-26 | Very Good | Fluent demonstration, at least 2 scenarios, Wireshark capture correctly interpreted |
| 16-21 | Good | Functional demonstration with minor issues, capture presented |
| 10-15 | Satisfactory | Partial demonstration, requires help to run |
| 0-9   | Insufficient | Project does not start or demonstration failed |

### Criterion C: Presentation and Communication (20 points)

| Score | Descriptor | Indicators |
|-------|------------|------------|
| 18-20 | Exceptional | Clear structure, timing respected, precise and complete answers to questions |
| 14-17 | Very Good | Organised presentation, correct answers to most questions |
| 10-13 | Good | Acceptable presentation, some hesitation at questions |
| 6-9   | Satisfactory | Disorganised presentation or incomplete answers |
| 0-5   | Insufficient | Poor communication or inability to explain own code |

### Criterion D: Documentation and Reproducibility (10 points)

| Score | Descriptor | Indicators |
|-------|------------|------------|
| 9-10  | Exceptional | Complete README, clear steps, diagrams, example captures, Makefile/scripts |
| 7-8   | Very Good | README with functional instructions, dependencies listed |
| 5-6   | Good | Minimal README but sufficient for running |
| 3-4   | Satisfactory | Incomplete or erroneous instructions |
| 0-2   | Insufficient | No documentation or unusable |

---

## 2. Detailed Criteria

### 2.1 What "Technical Complexity" Means

Complexity levels are evaluated as follows:

**Level 1 (Basic)**: Simple TCP or UDP echo
- Single message type (text → echo)
- No validation or error handling

**Level 2 (Intermediate)**: Protocol with commands
- At least 3 different commands (e.g.: GET, PUT, LIST)
- Input validation, error codes
- Clear client/server separation

**Level 3 (Advanced)**: Complete application
- Persistence (files or simple database)
- Authentication or sessions
- Structured logging

**Level 4 (Expert)**: Distributed architecture
- Load balancing or failover
- Binary protocol or compression
- Metrics and monitoring

### 2.2 Requirements for Live Demonstration

The demonstration must include:

1. **Starting components** (in correct order)
2. **Main scenario** (basic functionality)
3. **Error scenario** (what happens when something fails)
4. **Wireshark/tshark capture** (with packet explanation)

Time allocated: 7-10 minutes presentation + 3-5 minutes questions.

---

## 3. Grading Scale

| Total Points | Grade | Qualifier |
|--------------|-------|-----------|
| 95-100       | 10    | Exceptional |
| 85-94        | 9     | Very Good  |
| 75-84        | 8     | Good       |
| 65-74        | 7     | Satisfactory |
| 55-64        | 6     | Acceptable |
| 45-54        | 5     | Minimum    |
| 0-44         | 4     | Insufficient |

### Bonuses (maximum +10 points)

- **+3**: Functional Docker containerisation
- **+2**: Automated tests (pytest or similar)
- **+2**: CI/CD configuration (GitHub Actions)
- **+2**: Documentation in professional format (generated PDF)
- **+1**: Architecture diagrams (draw.io, Mermaid)

### Penalties

- **-5**: Late presentation without reason
- **-10**: Plagiarised code (detected through similarity)
- **-15**: Team member absent without justification
- **-20**: Identical project to another team

---

## 4. Defence Questions

Questions are structured by cognitive levels:

### Level 1: Knowledge

- What transport protocol do you use?
- What port does the server listen on?
- What Python library do you use for sockets?

### Level 2: Comprehension

- Why did you choose TCP instead of UDP (or vice versa)?
- What do the three times in the TCP handshake represent?
- What is the difference between `bind()` and `connect()`?

### Level 3: Application

- How would you modify the server to accept multiple connections?
- What happens if the client sends data larger than the buffer?
- How would you add timeout to network operations?

### Level 4: Analysis

- Where is the bottleneck in your architecture?
- What would happen if the server crashes mid-transfer?
- How does network latency affect application performance?

### Level 5: Evaluation

- What would you do differently if you started the project again?
- What are the limitations of the chosen architecture?
- How does your solution compare to commercial alternatives?

---

## 5. Originality Indicators

### Positive Signs

- Code organised in functions/classes with descriptive names
- Comments that explain "why", not "what"
- Error handling specific to the project
- Natural integration between components
- Prompt answers to questions about any part of the code

### Negative Signs (possible plagiarism)

- Code copied from a tutorial without adaptation
- Generic variables (x, y, data1, data2)
- Comments in English when the project is in Romanian (or vice versa)
- Inability to explain code sections
- Inconsistent style (mixing tabs/spaces, different conventions)

---

## Annex: Grading Form

```
Team: __________________ Date: __________

Members present:
□ __________________ □ __________________
□ __________________ □ __________________

EVALUATION:
                           Score awarded
A. Technical complexity    _____ / 40
B. Functionality           _____ / 30
C. Presentation            _____ / 20
D. Documentation           _____ / 10
                           -----------
   SUBTOTAL                _____ / 100

Bonuses:                   + _____
Penalties:                 - _____
                           -----------
   FINAL TOTAL             _____

Observations:
_________________________________________________
_________________________________________________

Evaluator signature: _________________
```

---

*Document generated for the course "Computer Networks", Week 14.*
