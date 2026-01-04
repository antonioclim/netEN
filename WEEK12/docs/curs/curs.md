# Lecture 12: Email Protocols

> **Course:** Computer Networks  
> **Week:** 12 of 14  
> **Duration:** 2 hours  
> **Author:** Revolvix&Hypotheticalandrei

---

## What We Will Learn

This week we explore **email protocols**, the foundation of modern electronic communication. We will understand:

- Email systems architecture and their components
- The **SMTP** protocol for sending messages
- The **POP3** and **IMAP** protocols for reception
- The **MIME** format for attachments and multimedia content
- Security mechanisms: **SPF**, **DKIM**, **DMARC**

## Why It Matters

Email remains critical infrastructure for:
- Communication in business and institutional environments
- Authentication (password reset, account verification, 2FA)
- Automatic notifications from applications
- Integrations between systems (alerts, reports, workflows)

Understanding the underlying protocols enables:
- Debugging delivery issues ("why aren't emails arriving?")
- Correct server configuredion
- Implementing custom solutions for notifications

---

## 1. Email Systems Architecture

### 1.1 Main Components

| Component | Full Name | Role | Examples |
|-----------|-----------|------|----------|
| **MUA** | Mail User Agent | User interface for composing and reading | Thunderbird, Outlook, Gmail web |
| **MTA** | Mail Transfer Agent | Routes messages between servers | Postfix, Sendmail, Exchange |
| **MDA** | Mail Delivery Agent | Delivers message to local mailbox | Dovecot, Procmail, Cyrus |
| **MSA** | Mail Submission Agent | Receives messages from MUA (port 587) | Often integrated into MTA |

### 1.2 Email Flow

```
┌─────────┐    SMTP     ┌─────────┐    SMTP     ┌─────────┐
│   MUA   │───(587)────▶│   MTA   │───(25)────▶│   MTA   │
│ Sender  │             │ Sender  │             │ Receiver│
└─────────┘             └─────────┘             └────┬────┘
                                                     │
                              POP3/IMAP              │ Local
                        ┌─────────────────────────┐  │ delivery
                        │                         ▼  ▼
┌─────────┐    IMAP     │                    ┌─────────┐
│   MUA   │◀──(993)─────│                    │   MDA   │
│Receiver │             │                    │         │
└─────────┘             │                    └─────────┘
                        │                         │
                        └─────────────────────────┘
                              Mailbox storage
```

**Detailed steps:**

1. User composes the message in MUA (Thunderbird)
2. MUA sends to local MSA/MTA via SMTP (port 587 with authentication)
3. Local MTA resolves the **MX** record from DNS for the recipient domain
4. Local MTA sends to recipient MTA via SMTP (port 25)
5. Recipient MTA delivers the message to MDA for storage
6. Recipient accesses the message via POP3 or IMAP

---

## 2. Envelope vs. Message Headers

**The fundamental concept** that differentiates routing from display.

### 2.1 Envelope (SMTP)

**Routing** information used exclusively by SMTP servers:

```smtp
MAIL FROM:<alice@sender.com>
RCPT TO:<bob@recipient.com>
```

- Determines where the message is actually delivered
- Invisible to the end user
- Used for bounces and delivery reports

### 2.2 Message Headers

**Metadata** visible in the email client:

```
From: Alice Smith <alice@sender.com>
To: Bob Jones <bob@recipient.com>
Subject: Meeting Tomorrow
Date: Mon, 15 Jan 2025 10:30:00 +0200
```

### 2.3 Why Can They Differ?

| Situation | Envelope MAIL FROM | Header From: |
|-----------|-------------------|--------------|
| **Mailing list** | listserv@list.com | author@original.com |
| **Forward** | forwarder@domain.com | original@sender.com |
| **Spoofing** | attacker@evil.com | ceo@company.com |

⚠️ **Warning:** This difference is the basis of **email spoofing**. SPF, DKIM and DMARC verify alignment.

---

## 3. SMTP – Simple Mail Transfer Protocol

**RFC 5321** defines the standard protocol for sending emails.

### 3.1 Characteristics

- **Text-based** protocol (human-readable)
- **Command-response** model similar to HTTP
- Ports: **25** (server-to-server), **587** (submission with auth), **465** (legacy SMTPS)
- Persistent **TCP** connection per session

### 3.2 Main Commands

| Command | Parameters | Description | Successs Response |
|---------|------------|-------------|------------------|
| `EHLO` | hostname | Client identification, requests extensions | 250 |
| `MAIL FROM` | `<address>` | Specifies sender (envelope) | 250 |
| `RCPT TO` | `<address>` | Specifies recipient (can be repeated) | 250 |
| `DATA` | - | Begins body transmission | 354 |
| `QUIT` | - | Closes connection | 221 |
| `RSET` | - | Resets current session | 250 |
| `VRFY` | user | Verifies user existence | 250/550 |

### 3.3 Response Codes

| Code | Category | Description |
|------|----------|-------------|
| 2xx | Successs | Command accepted |
| 3xx | Intermediate | Awaiting continuation (e.g. DATA) |
| 4xx | Temporary failure | Retry later |
| 5xx | Permanent failure | Fatal error |

**Common examples:**
- `220` – Server ready
- `250` – OK
- `354` – Start mail input
- `421` – Service unavailable (try later)
- `550` – Mailbox unavailable (rejected)
- `554` – Transaction failed

### 3.4 Completee SMTP Session

```smtp
S: 220 mail.example.com ESMTP Postfix
C: EHLO client.domain.com
S: 250-mail.example.com
S: 250-SIZE 52428800
S: 250-STARTTLS
S: 250-AUTH PLAIN LOGIN
S: 250 8BITMIME
C: MAIL FROM:<alice@client.domain.com>
S: 250 2.1.0 Ok
C: RCPT TO:<bob@example.com>
S: 250 2.1.5 Ok
C: DATA
S: 354 End data with <CR><LF>.<CR><LF>
C: From: Alice <alice@client.domain.com>
C: To: Bob <bob@example.com>
C: Subject: Test message
C: Date: Mon, 15 Jan 2025 10:30:00 +0200
C: Content-Type: text/plain; charset=utf-8
C: 
C: Hello Bob,
C: This is a test message.
C: 
C: Best regards,
C: Alice
C: .
S: 250 2.0.0 Ok: queued as ABC123
C: QUIT
S: 221 2.0.0 Bye
```

### 3.5 Extensions (ESMTP)

Extensions announced in the EHLO response:

| Extension | Description |
|-----------|-------------|
| `SIZE` | Limits message size |
| `STARTTLS` | Upgrade to encrypted connection |
| `AUTH` | Authentication mechanisms |
| `8BITMIME` | Support for 8-bit characters |
| `PIPELINING` | Multiple commands without waiting for response |

---

## 4. POP3 – Post Office Protocol v3

**RFC 1939** – Simple protocol for downloading messages.

### 4.1 Characteristics

- Model: **download-and-delete** (default)
- Port: **110** (plaintext), **995** (TLS)
- Suitable for: single device, intermittent connections
- Does **not** maintain state on server after download

### 4.2 Main Commands

| Command | Description | Response |
|---------|-------------|----------|
| `USER` | Specifies username | +OK |
| `PASS` | Specifies password | +OK logged in |
| `STAT` | Number and total size of messages | +OK n size |
| `LIST` | Lists messages | +OK (multi-line) |
| `RETR n` | Downloads message n | +OK (content) |
| `DELE n` | Marks for deletion | +OK |
| `QUIT` | Applies deletions, closes | +OK |
| `RSET` | Cancels marked deletions | +OK |
| `NOOP` | Keep-alive | +OK |

### 4.3 POP3 Session

```pop3
S: +OK POP3 server ready
C: USER bob
S: +OK
C: PASS secret123
S: +OK Logged in
C: STAT
S: +OK 3 12500
C: LIST
S: +OK 3 messages
S: 1 4200
S: 2 3800
S: 3 4500
S: .
C: RETR 1
S: +OK 4200 octets
S: From: alice@example.com
S: Subject: Hello
S: ...message content...
S: .
C: DELE 1
S: +OK Marked for deletion
C: QUIT
S: +OK Bye
```

### 4.4 POP3 Limitations

- Does **not** support folders (only INBOX)
- Does **not** synchronise between devices
- Does **not** allow server-side search
- Messages deleted from server cannot be recovered

---

## 5. IMAP – Internet Message Access Protocol

**RFC 3501** – Full mailbox access with synchronisation.

### 5.1 Characteristics

- Model: **server-side storage** (messages remain on server)
- Port: **143** (plaintext), **993** (TLS)
- Supports: folders, flags, search, partial fetch
- Ideal for: multi-device, webmail

### 5.2 POP3 vs IMAP Comparison

| Aspect | POP3 | IMAP |
|--------|------|------|
| **Model** | Download-and-delete | Server-side storage |
| **Multi-device** | No | Yes, synchronised |
| **Folders** | No | Yes, full hierarchy |
| **Search** | Client-side | Server-side |
| **Bandwidth** | Full download | Selective FETCH |
| **Offline** | After download | Requires sync |
| **Complexity** | Simple | Complex |

### 5.3 Essential IMAP Commands

| Command | Description |
|---------|-------------|
| `LOGIN user pass` | Authentication |
| `LIST "" "*"` | Lists all folders |
| `SELECT folder` | Opens a folder |
| `FETCH n:m (BODY[])` | Downloads messages |
| `SEARCH criteria` | Searches messages |
| `STORE n +FLAGS (\Seen)` | Sets flags |
| `CREATE folder` | Creates folder |
| `LOGOUT` | Disconnection |

### 5.4 IMAP Flags

| Flag | Meaning |
|------|---------|
| `\Seen` | Message read |
| `\Answered` | Replied to |
| `\Flagged` | Marked important |
| `\Deleted` | Marked for deletion |
| `\Draft` | Draft |

---

## 6. MIME – Multipurpose Internet Mail Extensions

Extends email format for non-ASCII content and attachments.

### 6.1 MIME Headers

```
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="----=_Part_123"
Content-Transfer-Encoding: base64
```

### 6.2 Common Content-Types

| Type | Description |
|------|-------------|
| `text/plain` | Plain text |
| `text/html` | HTML content |
| `multipart/mixed` | Message with attachments |
| `multipart/alternative` | Alternative versions (text + HTML) |
| `application/pdf` | PDF document |
| `image/png` | PNG image |

### 6.3 Multipart Structure

```mime
From: alice@example.com
To: bob@example.com
Subject: Document attached
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="----=_Boundary"

------=_Boundary
Content-Type: text/plain; charset=utf-8

Please find attached the document.

------=_Boundary
Content-Type: application/pdf; name="document.pdf"
Content-Disposition: attachment; filename="document.pdf"
Content-Transfer-Encoding: base64

JVBERi0xLjQKJcOkw7zDtsOfCjIgMCBvYmoKPDwvTGVu...
------=_Boundary--
```

---

## 7. Security: SPF, DKIM, DMARC

### 7.1 SPF – Sender Policy Framework

**What it verifies:** The sender's IP is authorised to send for the domain.

**How it works:**
1. Receiving server extracts domain from envelope MAIL FROM
2. Queries DNS TXT record for domain
3. Checks if sender's IP is in the list

**SPF record example:**
```dns
example.com. IN TXT "v=spf1 ip4:192.0.2.0/24 include:_spf.google.com -all"
```

### 7.2 DKIM – DomainKeys Identified Mail

**What it verifies:** The message was not modified in transit.

**How it works:**
1. Sender server digitally signs headers and body
2. Signature is added as `DKIM-Signature` header
3. Public key is published in DNS
4. Receiving server verifies signature

**DKIM Header:**
```
DKIM-Signature: v=1; a=rsa-sha256; d=example.com; s=selector1;
  h=from:to:subject:date; bh=47DEQpj8HBSa...;
  b=dzdVyOfAKCdLX...
```

### 7.3 DMARC – Domain-based Message Authentication

**What it verifies:** SPF/DKIM alignment and specifies policy on failure.

**Policies:**
- `none` – Monitoring, no action
- `quarantine` – Mark as spam
- `reject` – Reject the message

**Example:**
```dns
_dmarc.example.com. IN TXT "v=DMARC1; p=quarantine; rua=mailto:reports@example.com"
```

---

## 8. WebMail and Modern APIs

### 8.1 WebMail

The email client runs in the browser, communicating with the backend via:
- **IMAP** (traditional) for mailbox access
- **Proprietary APIs** (Gmail API, Outlook REST API)

### 8.2 Transactional Email Services

For programmatic notifications:
- **SendGrid**, **Mailgun**, **AWS SES**, **Postmark**
- REST API for sending
- Webhooks for tracking (delivery, open, click)

---

## What We Learned

- Email architecture: **MUA → MTA → MDA** and the role of each component
- The critical **envelope** vs **headers** difference and security implications
- **SMTP** for sending: commands, responses, completee session
- **POP3** for simple download, **IMAP** for synchronised access
- **MIME** for multimedia content and attachments
- **SPF/DKIM/DMARC** for authentication and anti-spoofing

---

## How It Helps Us

| Role | Applicability |
|------|---------------|
| **Backend Developer** | Email notification integration, deliverability debugging |
| **DevOps/SRE** | Mail server configuredion, monitoring, SPF/DKIM setup |
| **Security** | Understanding attack vectors, DMARC configuredion |
| **Product** | Authentication flow design, onboarding |

---

## Bibliography

1. Kurose, J. & Ross, K. (2021). *Computer Networking: A Top-Down Approach*, 8th Edition.
2. RFC 5321 – Simple Mail Transfer Protocol
3. RFC 1939 – Post Office Protocol Version 3
4. RFC 3501 – Internet Message Access Protocol
5. RFC 7208 – Sender Policy Framework (SPF)
6. RFC 6376 – DomainKeys Identified Mail (DKIM)

---

*Document generated for educational use | Revolvix&Hypotheticalandrei*
