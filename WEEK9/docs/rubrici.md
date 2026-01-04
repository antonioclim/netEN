# Evaluation Rubrics – Week 9

## Individual Lab Evaluation

### Criterion 1: Setup and Configuration (15 points)

| Level | Points | Description |
|-------|--------|-------------|
| Excellent | 15 | Environment fully configured, `make verify` passes, setup documentation completed |
| Good | 12 | Functional setup with minor assistance, all components installed |
| Satisfactory | 9 | Partial setup, some components missing but core works |
| Insufficient | 5 | Incomplete setup, requires significant assistance |
| Not submitted | 0 | Did not configure environment |

### Criterion 2: Demo Execution (25 points)

| Level | Points | Description |
|-------|--------|-------------|
| Excellent | 25 | All demos executed and results correctly interpreted |
| Good | 20 | Demos executed, partial interpretation |
| Satisfactory | 15 | 2 out of 3 demos successful |
| Insufficient | 8 | 1 demo successful |
| Not submitted | 0 | Did not execute any demo |

### Criterion 3: Traffic Capture and Analysis (25 points)

| Level | Points | Description |
|-------|--------|-------------|
| Excellent | 25 | Complete capture, detailed analysis with identification of all protocol elements, clear report |
| Good | 20 | Correct capture and analysis, partial element identification |
| Satisfactory | 15 | Capture generated, superficial analysis |
| Insufficient | 8 | Capture generated but no analysis |
| Not submitted | 0 | Did not perform capture |

### Criterion 4: Docker Multi-Client (20 points)

| Level | Points | Description |
|-------|--------|-------------|
| Excellent | 20 | Complete orchestration, all clients functional, logs interpreted |
| Good | 16 | Docker compose functional, at least 2 clients connected |
| Satisfactory | 12 | Docker compose started, minor errors |
| Insufficient | 6 | Start attempt with major errors |
| Not submitted | 0 | Did not try Docker |

### Criterion 5: Reflective Note (15 points)

| Level | Points | Description |
|-------|--------|-------------|
| Excellent | 15 | Deep reflection, relevant connections, original observations |
| Good | 12 | Clear reflection, correct connections |
| Satisfactory | 9 | Basic reflection, answers guide questions |
| Insufficient | 5 | Minimal reflection, under 3 lines |
| Not submitted | 0 | Did not complete reflective note |

### Total score: 100 points

**Grade conversion:**
- 90-100: 10
- 80-89: 9
- 70-79: 8
- 60-69: 7
- 50-59: 6
- 40-49: 5
- < 40: 4 (requires redo)

---

## Seminar Exercises Evaluation (Bonus)

### Exercise 1: INFO Command (⭐) - 5 bonus points

| Criterion | Points |
|-----------|--------|
| Works correctly | 2 |
| Clean and commented code | 1 |
| Error handling | 1 |
| Output format according to specification | 1 |

### Exercise 2: LIST with Wildcard (⭐⭐) - 8 bonus points

| Criterion | Points |
|-----------|--------|
| Functional pattern matching | 3 |
| Correct parser integration | 2 |
| Edge cases handled | 2 |
| Usage documentation | 1 |

### Exercise 3: MKDIR (⭐⭐) - 8 bonus points

| Criterion | Points |
|-----------|--------|
| Functional directory creation | 3 |
| Correct name validation | 2 |
| Permission verification | 2 |
| Clear error messages | 1 |

### Exercise 4: Transfer Resumption (⭐⭐⭐) - 12 bonus points

| Criterion | Points |
|-----------|--------|
| Functional REST | 4 |
| Functional RETR with offset | 4 |
| Integrity after resumption | 2 |
| Test with large file | 2 |

### Exercise 5: Rate Limiting (⭐⭐⭐) - 12 bonus points

| Criterion | Points |
|-----------|--------|
| Functional limiting | 4 |
| Correct algorithm (token bucket or similar) | 3 |
| Configurability | 3 |
| Speed measurement and reporting | 2 |

### CHALLENGE Exercise: Multi-File Transfer (🏆) - 20 bonus points

| Criterion | Points |
|-----------|--------|
| Functional MGET | 5 |
| Functional MPUT | 5 |
| Progress report | 3 |
| Partial error handling | 4 |
| Complete documentation | 3 |

---

## Contribution to Team Project

### Weekly Artefact: File Transfer Module

**Requirement**: The team integrates into the project a file transfer mechanism between components (either custom protocol or wrapper over existing libraries).

### Team Evaluation Criteria (30 points of project grade)

| Criterion | Points | Description |
|-----------|--------|-------------|
| Functionality | 10 | Transfer works between at least 2 components |
| Integration | 8 | Code integrates cleanly into existing architecture |
| Testing | 6 | Automated tests for main scenarios |
| Documentation | 4 | README updated with transfer section |
| Code review | 2 | Pull request with review from teammate |

### Timeline

| data | Activity |
|------|----------|
| Week 9 + 2 days | Branch created, design documented |
| Week 9 + 5 days | Complete implementation, tests written |
| Week 10 | Demo in Seminar, merge into main |

---

## Recovery Criteria

### For passing grade (5)

The student must demonstrate:
1. Understanding of L5/L6 concepts (oral or written test)
2. Ability to run server and client (demonstration)
3. A minimal analysed capture (.pcap file + 5 observations)

### Recovery deadline

- Until exam session
- Scheduled individually with instructor

---

## Feedback and Calibration

### Student feedback rubric

After evaluation, each student receives:
- Detailed score for each criterion
- 2-3 identified strengths
- 2-3 improvement suggestions
- Recommended resources for deepening (if applicable)

### Calibration between evaluators

At the beginning and middle of semester:
- All evaluators grade the same 3 anonymised works
- Discussion for alignment
- Rubric adjustment if discrepancies > 10%

---

## Appendix: Forms

### Lab evaluation form

```
Student: ___________________ Group: _____ data: _______

CRITERIA                                    SCORE
─────────────────────────────────────────────────────
1. Setup and configuration         [   ] / 15
2. Demo execution                  [   ] / 25
3. Capture and analysis            [   ] / 25
4. Docker multi-client             [   ] / 20
5. Reflective note                 [   ] / 15
─────────────────────────────────────────────────────
TOTAL                              [   ] / 100

BONUS exercises:                   [   ] points

Observations:


Evaluator: ___________________
```

### Team feedback form

```
Team: ___________________  Week: 9

Artefact: File Transfer Module

CRITERIA                                    SCORE
─────────────────────────────────────────────────────
Functionality                      [   ] / 10
Integration                        [   ] / 8
Testing                            [   ] / 6
Documentation                      [   ] / 4
Code review                        [   ] / 2
─────────────────────────────────────────────────────
TOTAL                              [   ] / 30

Strengths:
1.
2.

To improve:
1.
2.

Evaluator: ___________________
```
