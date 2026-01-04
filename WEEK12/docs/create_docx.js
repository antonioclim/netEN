/**
 * Generator Document Word - Curs12_Seminar12_Laborator12.docx
 * Week 12: Email protocols (SMTP, POP3, IMAP) and RPC
 * Computer Networks - ASE-CSIE
 */

const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, 
        Header, Footer, AlignmentType, LevelFormat, HeadingLevel, 
        BorderStyle, WidthType, ShadingType, PageNumber, PageBreak,
        TableOfContents, ExternalHyperlink } = require('docx');
const fs = require('fs');

// Color scheme
const COLORS = {
    primary: "1a365d",
    secondary: "2c5282", 
    accent: "ed8936",
    success: "38a169",
    warning: "d69e2e",
    danger: "e53e3e",
    muted: "718096",
    dark: "2d3748"
};

// Table borders
const tableBorder = { style: BorderStyle.SINGLE, andze: 1, color: "CCCCCC" };
const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };
const headerShading = { fill: "E8F4F8", type: ShadingType.CLEAR };

// Create the document
const doc = new Document({
    styles: {
        default: { document: { run: { font: "Arial", andze: 22 } } },
        paragraphStyles: [
            { id: "Title", name: "Title", basedOn: "Normal",
                run: { andze: 52, bold: true, color: COLORS.primary, font: "Arial" },
                paragraph: { spacing: { before: 240, after: 240 }, alignment: AlignmentType.CENTER } },
            { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
                run: { andze: 32, bold: true, color: COLORS.primary, font: "Arial" },
                paragraph: { spacing: { before: 360, after: 180 }, outlineLevel: 0 } },
            { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
                run: { andze: 26, bold: true, color: COLORS.secondary, font: "Arial" },
                paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 } },
            { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
                run: { andze: 24, bold: true, color: COLORS.dark, font: "Arial" },
                paragraph: { spacing: { before: 180, after: 60 }, outlineLevel: 2 } },
            { id: "InstructorNote", name: "Instructor Note", basedOn: "Normal",
                run: { andze: 20, italics: true, color: COLORS.muted, font: "Arial" },
                paragraph: { spacing: { before: 60, after: 60 }, indent: { left: 360 } } },
            { id: "CodeBlock", name: "Code Block", basedOn: "Normal",
                run: { andze: 18, font: "Consolas", color: COLORS.dark },
                paragraph: { spacing: { before: 120, after: 120 } } }
        ]
    },
    numbering: {
        config: [
            { reference: "main-bullets", levels: [
                { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
                    style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
                { level: 1, format: LevelFormat.BULLET, text: "○", alignment: AlignmentType.LEFT,
                    style: { paragraph: { indent: { left: 1080, hanging: 360 } } } }
            ]},
            { reference: "exercises-list", levels: [
                { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
                    style: { paragraph: { indent: { left: 720, hanging: 360 } } } }
            ]},
            { reference: "steps-list", levels: [
                { level: 0, format: LevelFormat.DECIMAL, text: "Pasul %1:", alignment: AlignmentType.LEFT,
                    style: { paragraph: { indent: { left: 720, hanging: 360 } } } }
            ]},
            { reference: "smtp-commands", levels: [
                { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
                    style: { paragraph: { indent: { left: 720, hanging: 360 } } } }
            ]},
            { reference: "recap-list", levels: [
                { level: 0, format: LevelFormat.BULLET, text: "✓", alignment: AlignmentType.LEFT,
                    style: { paragraph: { indent: { left: 720, hanging: 360 } } } }
            ]},
            { reference: "errors-list", levels: [
                { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
                    style: { paragraph: { indent: { left: 720, hanging: 360 } } } }
            ]},
            { reference: "bib-list", levels: [
                { level: 0, format: LevelFormat.DECIMAL, text: "[%1]", alignment: AlignmentType.LEFT,
                    style: { paragraph: { indent: { left: 720, hanging: 360 } } } }
            ]}
        ]
    },
    sections: [{
        properties: {
            page: { margin: { top: 1440, right: 1260, bottom: 1440, left: 1260 } }
        },
        headers: {
            default: new Header({ children: [
                new Paragraph({
                    alignment: AlignmentType.RIGHT,
                    children: [
                        new TextRun({ text: "Curs 12 – Protocoale Email & RPC | ", andze: 18, color: COLORS.muted }),
                        new TextRun({ text: "Rețele de Calculatoare", andze: 18, color: COLORS.primary, bold: true })
                    ]
                })
            ]})
        },
        footers: {
            default: new Footer({ children: [
                new Paragraph({
                    alignment: AlignmentType.CENTER,
                    children: [
                        new TextRun({ text: "Pagina ", andze: 18, color: COLORS.muted }),
                        new TextRun({ children: [PageNumber.CURRENT], andze: 18, color: COLORS.muted }),
                        new TextRun({ text: " din ", andze: 18, color: COLORS.muted }),
                        new TextRun({ children: [PageNumber.TOTAL_PAGES], andze: 18, color: COLORS.muted }),
                        new TextRun({ text: " | Revolvix&Hypotheticalandrei", andze: 16, color: COLORS.muted })
                    ]
                })
            ]})
        },
        children: [
            // ===== TITLE PAGE =====
            new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("Săptămâna 12")] }),
            new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [
                new TextRun({ text: "Protocoale de Email: SMTP, POP3, IMAP", andze: 36, bold: true, color: COLORS.secondary })
            ]}),
            new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [
                new TextRun({ text: "Seminar: Apelul de metodă la distanță (RPC)", andze: 28, color: COLORS.dark })
            ]}),
            new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 360 }, children: [
                new TextRun({ text: "Rețele de Calculatoare | An 3, Semestrul 2 | 2024-2025", andze: 22, color: COLORS.muted })
            ]}),
            new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 }, children: [
                new TextRun({ text: "Academia de Studii Economice București", andze: 20, italics: true, color: COLORS.muted }),
            ]}),
            new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 480 }, children: [
                new TextRun({ text: "Cibernetică, Statistică și Informatică Economică", andze: 20, italics: true, color: COLORS.muted }),
            ]}),
            
            // Document info box
            new Paragraph({ spacing: { before: 240, after: 120 }, children: [
                new TextRun({ text: "Informații document", andze: 24, bold: true, color: COLORS.primary })
            ]}),
            createInfoTable(),
            
            new Paragraph({ children: [new PageBreak()] }),
            
            // ===== TABLE OF CONTENTS =====
            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Cuprins")] }),
            new TableOfContents("Cuprins", { hyperlink: true, headingStyleRange: "1-3" }),
            new Paragraph({ spacing: { after: 120 }, children: [
                new TextRun({ text: "(Actualizați cu Ctrl+A, apoi F9 după deschidere în Word)", andze: 18, italics: true, color: COLORS.muted })
            ]}),
            
            new Paragraph({ children: [new PageBreak()] }),
            
            // ===== SECTION 1: SCOPE =====
            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("1. Scopul săptămânii")] }),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.1 Ce vom învăța")] }),
            new Paragraph({ children: [
                new TextRun("Această săptămână reprezintă o andnteză aplicată a cunoștințelor acumulate despre protocoalele de nivel aplicație. Ne concentrăm pe două direcții complementare: andstemele de email (SMTP, POP3, IMAP) for comunicarea aandncronă și mecanismele RPC for invocarea andncronă a procedurilor la distanță.")
            ]}),
            
            new Paragraph({ spacing: { before: 180 }, children: [
                new TextRun({ text: "Curs – Protocoale Email:", bold: true })
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun("Arhitectura andstemelor de email: MUA, MTA, MDA și interacțiunile dintre ele")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun("Distincția critică între "),
                new TextRun({ text: "envelope", italics: true }),
                new TextRun(" (informații de rutare SMTP) și "),
                new TextRun({ text: "message headers", italics: true }),
                new TextRun(" (metadate for client)")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun("SMTP (RFC 5321) – protocolul de sendre: comenzi, răspunsuri, coduri de stare")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun("POP3 (RFC 1939) – descărcarea mesajelor cu model download-and-delete")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun("IMAP (RFC 3501) – acces andncronizat multi-dispozitiv cu structură de foldere")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun("MIME – codificarea atașamentelor și conținutului non-ASCII")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun("Mecanisme anti-spam: SPF, DKIM, DMARC")
            ]}),
            
            new Paragraph({ spacing: { before: 180 }, children: [
                new TextRun({ text: "Seminar – Remote Procedure Call (RPC):", bold: true })
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun("Conceptul RPC: abstractizarea apelurilor de funcții peste rețea")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun("JSON-RPC 2.0 – specificație, structura cerere/răspuns, batch requests")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun("XML-RPC – format mai vechi, introspecție, comparație cu JSON-RPC")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun("gRPC cu Protocol Buffers – serializare binară, streaming, performanță")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun("Analiza traficului RPC cu Wireshark/tshark")
            ]}),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.2 De ce contează")] }),
            new Paragraph({ children: [
                new TextRun("Email-ul rămâne infrastructura critică for comunicarea în mediul buandness, autentificarea usefulizatorilor (password reset, 2FA prin email), notificările automate și integrările între andsteme. Înțelegerea protocoalelor subiacente permite debugging-ul problemelor de livrare, configurarea corectă a serverelor și implementarea de soluții custom.")
            ]}),
            new Paragraph({ spacing: { before: 120 }, children: [
                new TextRun("RPC reprezintă fundamentul arhitecturilor distribuite moderne: de la microservicii la andsteme cloud-native. JSON-RPC este omniprezent în API-urile blockchain și cryptocurrency, XML-RPC încă există în andsteme legacy, iar gRPC domină comunicarea inter-servicii în infrastructuri la scară largă (Google, Netflix, Uber).")
            ]}),
            
            // Instructor note
            new Paragraph({ style: "InstructorNote", spacing: { before: 180 }, children: [
                new TextRun({ text: "📝 Notă instructor: ", bold: true }),
                new TextRun("Subliniați conexiunea cu săptămânile anterioare: HTTP/REST (S10), DNS (S11). RPC poate fi văzut ca o abstractizare peste HTTP sau ca o alternativă independentă. Studenții au deja experiență cu request/response patterns.")
            ]}),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.3 Unde ne ajută în carieră")] }),
            new Paragraph({ children: [
                new TextRun("Această săptămână pregătește studenții for:")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "DevOps/SRE: ", bold: true }),
                new TextRun("Configurarea serverelor de mail (Postfix, Dovecot), monitoring și troubleshooting deliverability")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "Backend Development: ", bold: true }),
                new TextRun("Integrarea cu servicii de email (SendGrid, AWS SES), implementarea notificărilor")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "Security: ", bold: true }),
                new TextRun("Înțelegerea vectorilor de atac (email spoofing), configurarea SPF/DKIM/DMARC")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "Microservices Architecture: ", bold: true }),
                new TextRun("Alegerea între REST, gRPC, message queues for comunicarea inter-servicii")
            ]}),
            
            new Paragraph({ children: [new PageBreak()] }),
            
            // ===== SECTION 2: PREREQUISITES =====
            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("2. Prerechizite")] }),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.1 Cunoștințe necesare")] }),
            new Paragraph({ children: [
                new TextRun("Pentru a parcurge cu succes materialul acestei săptămâni, studenții trebuie să aibă înțelegere solidă a:")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "Modelul client-server", bold: true }),
                new TextRun(" (S1-S2): conexiuni TCP, schimb de mesaje, arhitecturi distribuite")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "Protocolul TCP", bold: true }),
                new TextRun(" (S8): conexiuni perandstente, garantarea livrării, flow control")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "HTTP/HTTPS", bold: true }),
                new TextRun(" (S10): request/response, metode, headers, status codes")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "DNS", bold: true }),
                new TextRun(" (S11): rezoluția numelor, tipuri de înregistrări (în special MX)")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "Wireshark/tshark", bold: true }),
                new TextRun(" (S1-S7): capturarea și filtrarea traficului de rețea")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "Python sockets", bold: true }),
                new TextRun(" (S2-S4): programare client/server, manipularea datelor binare și text")
            ]}),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.2 Recapitulare ultra-scurtă")] }),
            createRecapTable(),
            
            new Paragraph({ style: "InstructorNote", spacing: { before: 180 }, children: [
                new TextRun({ text: "📝 Notă instructor: ", bold: true }),
                new TextRun("Alocați 5 minute la început for checkrea cunoștințelor. Întrebări rapide: Ce port folosește HTTPS? Ce înregistrare DNS indică serverul de mail? Ce diferență e între TCP și UDP?")
            ]}),
            
            new Paragraph({ children: [new PageBreak()] }),
            
            // ===== SECTION 3: COURSE CONTENT =====
            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("3. Curs: Protocoale Email")] }),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.1 Arhitectura andstemelor de email")] }),
            new Paragraph({ children: [
                new TextRun("Un andstem de email implică mai multe componente care colaborează for a livra mesajele de la expeditor la destinatar. Această arhitectură stratificată permite flexibilitate și specializare:")
            ]}),
            
            createEmailArchTable(),
            
            new Paragraph({ spacing: { before: 180 }, children: [
                new TextRun({ text: "Fluxul tipic al unui email:", bold: true })
            ]}),
            new Paragraph({ numbering: { reference: "steps-list", level: 0 }, children: [
                new TextRun("Utilizatorul compune mesajul în MUA (ex: Thunderbird)")
            ]}),
            new Paragraph({ numbering: { reference: "steps-list", level: 0 }, children: [
                new TextRun("MUA send mesajul către MTA local prin SMTP (port 587 cu autentificare)")
            ]}),
            new Paragraph({ numbering: { reference: "steps-list", level: 0 }, children: [
                new TextRun("MTA local rezolvă înregistrarea MX for domeniul destinatar")
            ]}),
            new Paragraph({ numbering: { reference: "steps-list", level: 0 }, children: [
                new TextRun("MTA local send mesajul către MTA destinatar prin SMTP (port 25)")
            ]}),
            new Paragraph({ numbering: { reference: "steps-list", level: 0 }, children: [
                new TextRun("MTA destinatar predă mesajul către MDA for stocare")
            ]}),
            new Paragraph({ numbering: { reference: "steps-list", level: 0 }, children: [
                new TextRun("Destinatarul descarcă mesajul prin POP3 sau îl accesează prin IMAP")
            ]}),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.2 Envelope vs. Message Headers")] }),
            new Paragraph({ children: [
                new TextRun("Această distincție fundamentală este adesea sursa confuziei. "),
                new TextRun({ text: "Envelope-ul", bold: true }),
                new TextRun(" conține informațiile de rutare foloandte de serverele SMTP, în timp ce "),
                new TextRun({ text: "message headers", bold: true }),
                new TextRun(" sunt metadate for clientul de email:")
            ]}),
            
            createEnvelopeVsHeadersTable(),
            
            new Paragraph({ style: "InstructorNote", spacing: { before: 180 }, children: [
                new TextRun({ text: "⚠️ Notă instructor: ", bold: true }),
                new TextRun("Demonstrați cum email spoofing exploatează această diferență. Envelope-ul determină livrarea, dar clientul afișează From: din headers. SPF/DKIM verifică alinierea.")
            ]}),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.3 SMTP – Simple Mail Transfer Protocol")] }),
            new Paragraph({ children: [
                new TextRun("SMTP (RFC 5321) este un protocol text bazat pe comenzi și răspunsuri. Fiecare comandă primește un cod de răspuns de 3 cifre andmilar cu HTTP:")
            ]}),
            
            new Paragraph({ spacing: { before: 180 }, children: [
                new TextRun({ text: "Comenzi SMTP esențiale:", bold: true })
            ]}),
            createSmtpCommandsTable(),
            
            new Paragraph({ spacing: { before: 180 }, children: [
                new TextRun({ text: "Seandune SMTP tipică:", bold: true })
            ]}),
            new Paragraph({ style: "CodeBlock", children: [
                new TextRun("S: 220 mail.example.com ESMTP ready\n"),
                new TextRun("C: EHLO client.domain.com\n"),
                new TextRun("S: 250-mail.example.com Hello\n"),
                new TextRun("S: 250-SIZE 52428800\n"),
                new TextRun("S: 250 STARTTLS\n"),
                new TextRun("C: MAIL FROM:<alice@sender.com>\n"),
                new TextRun("S: 250 OK\n"),
                new TextRun("C: RCPT TO:<bob@example.com>\n"),
                new TextRun("S: 250 Accepted\n"),
                new TextRun("C: DATA\n"),
                new TextRun("S: 354 Enter message, ending with \".\" on a line by itself\n"),
                new TextRun("C: From: Alice <alice@sender.com>\n"),
                new TextRun("C: To: Bob <bob@example.com>\n"),
                new TextRun("C: Subject: Test message\n"),
                new TextRun("C: \n"),
                new TextRun("C: Hello, this is a test.\n"),
                new TextRun("C: .\n"),
                new TextRun("S: 250 OK id=1abc23-def456\n"),
                new TextRun("C: QUIT\n"),
                new TextRun("S: 221 Bye")
            ]}),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.4 POP3 – Post Office Protocol v3")] }),
            new Paragraph({ children: [
                new TextRun("POP3 (RFC 1939) oferă acces andmplu la mailbox cu model "),
                new TextRun({ text: "download-and-delete", italics: true }),
                new TextRun(". Este potrivit for un andngur dispozitiv și conexiuni intermitente:")
            ]}),
            
            createPop3CommandsTable(),
            
            new Paragraph({ spacing: { before: 120 }, children: [
                new TextRun({ text: "Limitări POP3: ", bold: true }),
                new TextRun("Nu menține starea pe server (după descărcare, mesajele sunt șterse implicit), nu suportă foldere, nu andncronizează între dispozitive.")
            ]}),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.5 IMAP – Internet Message Access Protocol")] }),
            new Paragraph({ children: [
                new TextRun("IMAP (RFC 3501) oferă acces complet la mailbox cu "),
                new TextRun({ text: "andncronizare multi-dispozitiv", bold: true }),
                new TextRun(". Mesajele rămân pe server și pot fi organizate în foldere:")
            ]}),
            
            createImapVsPop3Table(),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.6 MIME și atașamente")] }),
            new Paragraph({ children: [
                new TextRun("MIME (Multipurpose Internet Mail Extenandons) extinde formatul email for a suporta conținut non-ASCII, atașamente și mesaje multipart. Header-ul "),
                new TextRun({ text: "Content-Type", bold: true }),
                new TextRun(" specifică tipul conținutului:")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "text/plain", bold: true }),
                new TextRun(" – text andmplu fără formatare")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "text/html", bold: true }),
                new TextRun(" – conținut HTML (email-uri formatate)")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "multipart/mixed", bold: true }),
                new TextRun(" – mesaj cu atașamente")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "multipart/alternative", bold: true }),
                new TextRun(" – veranduni alternative (text + HTML)")
            ]}),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.7 Securitate: SPF, DKIM, DMARC")] }),
            createSecurityTable(),
            
            new Paragraph({ style: "InstructorNote", spacing: { before: 180 }, children: [
                new TextRun({ text: "📝 Checktion cunoștințe:", bold: true }),
                new TextRun(" 1) Care e diferența între MAIL FROM și header-ul From:? 2) De ce IMAP e preferat for multi-device? 3) Ce verifică SPF?")
            ]}),
            
            new Paragraph({ children: [new PageBreak()] }),
            
            // ===== SECTION 4: SEMINAR =====
            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("4. Seminar: Remote Procedure Call (RPC)")] }),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.1 Conceptul RPC")] }),
            new Paragraph({ children: [
                new TextRun("Remote Procedure Call abstractizează comunicarea în rețea, permițând apelarea funcțiilor de pe un server la distanță "),
                new TextRun({ text: "ca și cum ar fi locale", italics: true }),
                new TextRun(". Clientul nu trebuie să gestioneze explicit socket-uri, serializare sau protocol – framework-ul RPC se ocupă de toate acestea.")
            ]}),
            
            new Paragraph({ spacing: { before: 180 }, children: [
                new TextRun({ text: "Componentele unui andstem RPC:", bold: true })
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "Client stub: ", bold: true }),
                new TextRun("Proxy local care expune metodele remote ca funcții native")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "Server stub: ", bold: true }),
                new TextRun("Dispatcher care primește cererile și invocă implementarea reală")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "Transport: ", bold: true }),
                new TextRun("TCP, HTTP, sau alt protocol for transmianda efectivă")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "Serializare: ", bold: true }),
                new TextRun("JSON, XML, Protocol Buffers – codificarea parametrilor și rezultatelor")
            ]}),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.2 JSON-RPC 2.0")] }),
            new Paragraph({ children: [
                new TextRun("JSON-RPC este o specificație ușoară for RPC peste JSON. Este usefulizat extenandv în API-urile blockchain (Bitcoin, Ethereum), servere LSP (Language Server Protocol) și diverse servicii web.")
            ]}),
            
            new Paragraph({ spacing: { before: 180 }, children: [
                new TextRun({ text: "Structura cererii JSON-RPC:", bold: true })
            ]}),
            new Paragraph({ style: "CodeBlock", children: [
                new TextRun('{\n'),
                new TextRun('  "jsonrpc": "2.0",\n'),
                new TextRun('  "method": "subtract",\n'),
                new TextRun('  "params": [42, 23],\n'),
                new TextRun('  "id": 1\n'),
                new TextRun('}')
            ]}),
            
            new Paragraph({ spacing: { before: 120 }, children: [
                new TextRun({ text: "Structura răspunsului:", bold: true })
            ]}),
            new Paragraph({ style: "CodeBlock", children: [
                new TextRun('{\n'),
                new TextRun('  "jsonrpc": "2.0",\n'),
                new TextRun('  "result": 19,\n'),
                new TextRun('  "id": 1\n'),
                new TextRun('}')
            ]}),
            
            new Paragraph({ spacing: { before: 180 }, children: [
                new TextRun({ text: "Coduri de eroare standardizate:", bold: true })
            ]}),
            createJsonRpcErrorsTable(),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.3 XML-RPC")] }),
            new Paragraph({ children: [
                new TextRun("XML-RPC este predecesorul JSON-RPC, foloandnd XML for serializare. Deși mai verbose, oferă funcții de introspecție (listarea metodelor disponibile) și rămâne prezent în andsteme legacy.")
            ]}),
            
            new Paragraph({ style: "CodeBlock", spacing: { before: 120 }, children: [
                new TextRun('<?xml verandon="1.0"?>\n'),
                new TextRun('<methodCall>\n'),
                new TextRun('  <methodName>subtract</methodName>\n'),
                new TextRun('  <params>\n'),
                new TextRun('    <param><value><int>42</int></value></param>\n'),
                new TextRun('    <param><value><int>23</int></value></param>\n'),
                new TextRun('  </params>\n'),
                new TextRun('</methodCall>')
            ]}),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.4 gRPC cu Protocol Buffers")] }),
            new Paragraph({ children: [
                new TextRun("gRPC (Google RPC) usefulizează Protocol Buffers for serializare binară eficientă și HTTP/2 for transport. Oferă performanță superioară și suport nativ for streaming bidirecțional.")
            ]}),
            
            new Paragraph({ spacing: { before: 180 }, children: [
                new TextRun({ text: "Example definiție .proto:", bold: true })
            ]}),
            new Paragraph({ style: "CodeBlock", children: [
                new TextRun('syntax = "proto3";\n'),
                new TextRun('\n'),
                new TextRun('service Calculator {\n'),
                new TextRun('  rpc Subtract(SubtractRequest) returns (SubtractResponse);\n'),
                new TextRun('}\n'),
                new TextRun('\n'),
                new TextRun('message SubtractRequest {\n'),
                new TextRun('  int32 a = 1;\n'),
                new TextRun('  int32 b = 2;\n'),
                new TextRun('}\n'),
                new TextRun('\n'),
                new TextRun('message SubtractResponse {\n'),
                new TextRun('  int32 result = 1;\n'),
                new TextRun('}')
            ]}),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.5 Comparație JSON-RPC vs XML-RPC vs gRPC")] }),
            createRpcComparisonTable(),
            
            new Paragraph({ style: "InstructorNote", spacing: { before: 180 }, children: [
                new TextRun({ text: "📝 Ghidare discuție: ", bold: true }),
                new TextRun("Când alegeți JSON-RPC vs gRPC? JSON-RPC: andmplicitate, debugging ușor, compatibilitate browser. gRPC: performanță, microservicii interne, când bandwidth e critic.")
            ]}),
            
            new Paragraph({ children: [new PageBreak()] }),
            
            // ===== SECTION 5: LABORATORY =====
            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("5. Laborator practic")] }),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.1 Setup mediu de lucru")] }),
            new Paragraph({ children: [
                new TextRun("Toate experimentele folosesc starterkit-ul furnizat. Structura de directoare:")
            ]}),
            new Paragraph({ style: "CodeBlock", children: [
                new TextRun("s12_starterkit/\n"),
                new TextRun("├── Makefile          # Automatizări (make setup, make run-demo etc.)\n"),
                new TextRun("├── src/email/        # Server/client SMTP educațional\n"),
                new TextRun("├── src/rpc/          # Implementări JSON-RPC, XML-RPC\n"),
                new TextRun("├── exercises/        # Exerciții self-contained\n"),
                new TextRun("├── scripts/          # Shell scripts for setup/capture\n"),
                new TextRun("└── docs/             # Prezentări HTML interactive")
            ]}),
            
            new Paragraph({ spacing: { before: 180 }, children: [
                new TextRun({ text: "Pași inițiali:", bold: true })
            ]}),
            new Paragraph({ style: "CodeBlock", children: [
                new TextRun("# 1. Clonați/dezarhivați starterkit-ul\n"),
                new TextRun("cd s12_starterkit\n"),
                new TextRun("\n"),
                new TextRun("# 2. Instalați dependențele\n"),
                new TextRun("make setup\n"),
                new TextRun("\n"),
                new TextRun("# 3. Checkți mediul\n"),
                new TextRun("make verify")
            ]}),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.2 Experiment SMTP")] }),
            new Paragraph({ children: [
                new TextRun({ text: "Obiectiv: ", bold: true }),
                new TextRun("Înțelegerea conversației SMTP prin observarea directă a traficului.")
            ]}),
            
            new Paragraph({ spacing: { before: 120 }, children: [
                new TextRun({ text: "Pas 1: Porniți serverul SMTP educațional", bold: true })
            ]}),
            new Paragraph({ style: "CodeBlock", children: [
                new TextRun("# Terminal 1\n"),
                new TextRun("python src/email/smtp_server.py --port 1025 --verbose")
            ]}),
            
            new Paragraph({ spacing: { before: 120 }, children: [
                new TextRun({ text: "Pas 2: Sendți un email de test", bold: true })
            ]}),
            new Paragraph({ style: "CodeBlock", children: [
                new TextRun("# Terminal 2\n"),
                new TextRun("python src/email/smtp_client.py \\\n"),
                new TextRun("    --server localhost --port 1025 \\\n"),
                new TextRun("    --from alice@test.local \\\n"),
                new TextRun("    --to bob@test.local \\\n"),
                new TextRun("    --subject 'Test SMTP' \\\n"),
                new TextRun("    --body 'Mesaj de test for laborator'")
            ]}),
            
            new Paragraph({ spacing: { before: 120 }, children: [
                new TextRun({ text: "Pas 3: Capturați traficul cu tshark", bold: true })
            ]}),
            new Paragraph({ style: "CodeBlock", children: [
                new TextRun("# Terminal 3\n"),
                new TextRun("sudo tshark -i lo -f 'port 1025' -Y smtp -V")
            ]}),
            
            new Paragraph({ spacing: { before: 180 }, children: [
                new TextRun({ text: "Rezultate așteptate:", bold: true })
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun("Serverul afișează comenzile primite (EHLO, MAIL FROM, RCPT TO, DATA)")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun("Clientul raportează succes (status 250)")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun("tshark arată conversația completă incluandv corpul mesajului")
            ]}),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.3 Experiment RPC")] }),
            new Paragraph({ children: [
                new TextRun({ text: "Obiectiv: ", bold: true }),
                new TextRun("Compararea overhead-ului dintre JSON-RPC și XML-RPC.")
            ]}),
            
            new Paragraph({ spacing: { before: 120 }, children: [
                new TextRun({ text: "Pas 1: Porniți serverele RPC", bold: true })
            ]}),
            new Paragraph({ style: "CodeBlock", children: [
                new TextRun("# Terminal 1 - JSON-RPC\n"),
                new TextRun("python src/rpc/jsonrpc/jsonrpc_server.py --port 8000\n"),
                new TextRun("\n"),
                new TextRun("# Terminal 2 - XML-RPC\n"),
                new TextRun("python src/rpc/xmlrpc/xmlrpc_server.py --port 8001")
            ]}),
            
            new Paragraph({ spacing: { before: 120 }, children: [
                new TextRun({ text: "Pas 2: Rulați benchmark-ul", bold: true })
            ]}),
            new Paragraph({ style: "CodeBlock", children: [
                new TextRun("make benchmark-rpc")
            ]}),
            
            new Paragraph({ spacing: { before: 180 }, children: [
                new TextRun({ text: "Output tipic:", bold: true })
            ]}),
            new Paragraph({ style: "CodeBlock", children: [
                new TextRun("=== RPC Benchmark Results ===\n"),
                new TextRun("JSON-RPC: 1000 calls in 0.89s (1123 calls/sec)\n"),
                new TextRun("  Average payload: 67 bytes\n"),
                new TextRun("XML-RPC:  1000 calls in 1.34s (746 calls/sec)\n"),
                new TextRun("  Average payload: 198 bytes\n"),
                new TextRun("Speedup: JSON-RPC is 1.51x faster")
            ]}),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.4 Extenandi opționale")] }),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "Atașament MIME: ", bold: true }),
                new TextRun("Modificați smtp_client.py for a send un fișier atașat")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "Batch JSON-RPC: ", bold: true }),
                new TextRun("Sendți 10 cereri într-un andngur request și măsurați overhead-ul")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "Mininet topology: ", bold: true }),
                new TextRun("Rulați scenariul email între host-uri separate în topologia andmulată")
            ]}),
            
            new Paragraph({ children: [new PageBreak()] }),
            
            // ===== SECTION 6: COMMON ERRORS =====
            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("6. Greșeli frecvente și debugging")] }),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("6.1 Erori SMTP")] }),
            createSmtpErrorsTable(),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("6.2 Erori RPC")] }),
            createRpcErrorsTable(),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("6.3 Debugging cu Wireshark")] }),
            new Paragraph({ children: [
                new TextRun("Filtre usefule for analiza traficului:")
            ]}),
            new Paragraph({ style: "CodeBlock", children: [
                new TextRun("# SMTP\n"),
                new TextRun("smtp                          # Tot traficul SMTP\n"),
                new TextRun("smtp.req.command == \"DATA\"    # Doar comenzi DATA\n"),
                new TextRun("smtp.response.code == 550     # Erori 550 (rejected)\n"),
                new TextRun("\n"),
                new TextRun("# HTTP (for RPC)\n"),
                new TextRun("http.request.method == \"POST\" # Cereri POST (RPC calls)\n"),
                new TextRun("http contains \"jsonrpc\"       # Trafic JSON-RPC\n"),
                new TextRun("http.content_type contains \"xml\" # Trafic XML-RPC")
            ]}),
            
            new Paragraph({ children: [new PageBreak()] }),
            
            // ===== SECTION 7: EXERCISES =====
            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("7. Exerciții de consolidare")] }),
            
            new Paragraph({ children: [
                new TextRun("Exercițiile sunt gradate progreandv. Primele trei sunt obligatorii, următoarele opționale for studenții avansați.")
            ]}),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Exercițiul 1: Analiză SMTP (★☆☆)")] }),
            new Paragraph({ children: [
                new TextRun({ text: "Obiectiv: ", bold: true }),
                new TextRun("Identificarea componentelor unei seanduni SMTP")
            ]}),
            new Paragraph({ children: [
                new TextRun({ text: "Task: ", bold: true }),
                new TextRun("Capturați o seandune SMTP și identificați: greeting banner, comenzile client, răspunsurile server, envelope vs headers.")
            ]}),
            new Paragraph({ children: [
                new TextRun({ text: "Livrabil: ", bold: true }),
                new TextRun("Screenshot Wireshark cu adnotări for fiecare componentă.")
            ]}),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Exercițiul 2: Multi-recipient SMTP (★★☆)")] }),
            new Paragraph({ children: [
                new TextRun({ text: "Obiectiv: ", bold: true }),
                new TextRun("Înțelegerea cum SMTP gestionează destinatari multipli")
            ]}),
            new Paragraph({ children: [
                new TextRun({ text: "Task: ", bold: true }),
                new TextRun("Modificați smtp_client.py for a send către 3 destinatari diferiți. Observați câte comenzi RCPT TO sunt necesare.")
            ]}),
            new Paragraph({ children: [
                new TextRun({ text: "Livrabil: ", bold: true }),
                new TextRun("Cod modificat + captură tshark arătând cele 3 RCPT TO.")
            ]}),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Exercițiul 3: JSON-RPC Client custom (★★☆)")] }),
            new Paragraph({ children: [
                new TextRun({ text: "Obiectiv: ", bold: true }),
                new TextRun("Implementarea unui client JSON-RPC minimal")
            ]}),
            new Paragraph({ children: [
                new TextRun({ text: "Task: ", bold: true }),
                new TextRun("Scrieți un client Python care apelează toate metodele expuse de jsonrpc_server.py foloandnd doar biblioteca requests (fără json-rpc clients).")
            ]}),
            new Paragraph({ children: [
                new TextRun({ text: "Livrabil: ", bold: true }),
                new TextRun("Script Python funcțional + output for fiecare metodă.")
            ]}),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Exercițiul 4: Error handling RPC (★★★)")] }),
            new Paragraph({ children: [
                new TextRun({ text: "Obiectiv: ", bold: true }),
                new TextRun("Testarea comportamentului la erori")
            ]}),
            new Paragraph({ children: [
                new TextRun({ text: "Task: ", bold: true }),
                new TextRun("Sendți cereri invalide către server (method inexistent, params greșite, JSON malformat) și documentați răspunsurile.")
            ]}),
            new Paragraph({ children: [
                new TextRun({ text: "Livrabil: ", bold: true }),
                new TextRun("Tabel cu cereri invalide, coduri de eroare primite, explicații.")
            ]}),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Exercițiul 5: Batch performance (★★★)")] }),
            new Paragraph({ children: [
                new TextRun({ text: "Obiectiv: ", bold: true }),
                new TextRun("Măsurarea beneficiului batch requests")
            ]}),
            new Paragraph({ children: [
                new TextRun({ text: "Task: ", bold: true }),
                new TextRun("Comparați timpul for 100 de apeluri individuale vs 10 batch-uri de câte 10 cereri. Calculați overhead-ul conexiunilor.")
            ]}),
            new Paragraph({ children: [
                new TextRun({ text: "Livrabil: ", bold: true }),
                new TextRun("Grafic comparativ + analiza rezultatelor.")
            ]}),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Exercițiul 6: Challenge - Email relay (★★★★)")] }),
            new Paragraph({ children: [
                new TextRun({ text: "Obiectiv: ", bold: true }),
                new TextRun("Implementarea unui relay SMTP minimal")
            ]}),
            new Paragraph({ children: [
                new TextRun({ text: "Task: ", bold: true }),
                new TextRun("Extindeți smtp_server.py for a redirecționa mesajele primite către un alt server SMTP (de ex: serverul colegului). Implementați logging for audit.")
            ]}),
            new Paragraph({ children: [
                new TextRun({ text: "Livrabil: ", bold: true }),
                new TextRun("Cod funcțional + demonstrație relay end-to-end + log de audit.")
            ]}),
            
            new Paragraph({ style: "InstructorNote", spacing: { before: 180 }, children: [
                new TextRun({ text: "📝 Rubrică evaluare: ", bold: true }),
                new TextRun("Ex1-3: câte 1.5p, Ex4-5: câte 2p, Ex6: 3p bonus. Total maxim: 10p + 3p bonus.")
            ]}),
            
            new Paragraph({ children: [new PageBreak()] }),
            
            // ===== SECTION 8: REFLECTION =====
            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("8. Mini-reflecție")] }),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("8.1 Ce am învățat")] }),
            new Paragraph({ numbering: { reference: "recap-list", level: 0 }, children: [
                new TextRun("Arhitectura andstemelor de email: MUA → MTA → MDA și protocoalele asociate")
            ]}),
            new Paragraph({ numbering: { reference: "recap-list", level: 0 }, children: [
                new TextRun("Diferența critică între envelope (rutare) și headers (metadate)")
            ]}),
            new Paragraph({ numbering: { reference: "recap-list", level: 0 }, children: [
                new TextRun("SMTP for sendre, POP3 for download andmplu, IMAP for acces andncronizat")
            ]}),
            new Paragraph({ numbering: { reference: "recap-list", level: 0 }, children: [
                new TextRun("Conceptul RPC și abstractizarea apelurilor de funcții peste rețea")
            ]}),
            new Paragraph({ numbering: { reference: "recap-list", level: 0 }, children: [
                new TextRun("Trade-off-uri între JSON-RPC (andmplitate) și gRPC (performanță)")
            ]}),
            new Paragraph({ numbering: { reference: "recap-list", level: 0 }, children: [
                new TextRun("Mecanisme anti-spam: SPF, DKIM, DMARC")
            ]}),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("8.2 Unde se folosește în practică")] }),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "Transactional email: ", bold: true }),
                new TextRun("Confirmări comenzi, resetare parole, notificări (SendGrid, AWS SES, Mailgun)")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "Marketing automation: ", bold: true }),
                new TextRun("Campanii email, analytics, A/B testing (Mailchimp, HubSpot)")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "Blockchain APIs: ", bold: true }),
                new TextRun("Toate nodurile Bitcoin/Ethereum expun JSON-RPC for interacțiuni")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "Microservicii: ", bold: true }),
                new TextRun("Comunicarea între servicii în arhitecturi distribuite (gRPC la Google, Netflix)")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "IDE extenandons: ", bold: true }),
                new TextRun("Language Server Protocol folosește JSON-RPC for comunicare editor-server")
            ]}),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("8.3 Legătura cu rolul de programator")] }),
            new Paragraph({ children: [
                new TextRun("Ca programator, vei interacționa cu aceste tehnologii în multiple contexte:")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun("Integrarea cu servicii de email for notificări în aplicații")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun("Debugging-ul problemelor de deliverability ('de ce nu ajung email-urile?')")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun("Alegerea protocolului potrivit for comunicarea inter-servicii")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun("Înțelegerea security implications (spoofing, injection)")
            ]}),
            
            new Paragraph({ children: [new PageBreak()] }),
            
            // ===== SECTION 9: TEAM PROJECT =====
            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("9. Contribuția la proiectul de echipă")] }),
            
            new Paragraph({ children: [
                new TextRun("Proiectul de echipă for Rețele de Calculatoare acumulează săptămânal artefacte care demonstrează competențele dobândite. Pentru Săptămâna 12:")
            ]}),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("9.1 Artefact livrabil")] }),
            new Paragraph({ children: [
                new TextRun({ text: "Opțiunea A - Modul de notificări email:", bold: true })
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun("Implementați un modul care send notificări email for evenimente din proiect")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun("Foloandți serverul SMTP educațional sau integrați cu un serviciu real (SendGrid tier gratuit)")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun("Demonstrați livrarea și capturați conversația SMTP")
            ]}),
            
            new Paragraph({ spacing: { before: 120 }, children: [
                new TextRun({ text: "Opțiunea B - API intern RPC:", bold: true })
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun("Expuneți funcționalități din proiect prin JSON-RPC sau gRPC")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun("Minim 5 metode cu documentație")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun("Client demonstrativ care apelează toate metodele")
            ]}),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("9.2 Criterii de evaluare")] }),
            createProjectRubricTable(),
            
            new Paragraph({ children: [new PageBreak()] }),
            
            // ===== SECTION 10: BIBLIOGRAPHY =====
            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("10. Bibliografie și resurse")] }),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("10.1 Referințe academice (cu DOI)")] }),
            createBibliographyTable(),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("10.2 Standarde și specificații (fără DOI)")] }),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "RFC 5321", bold: true }),
                new TextRun(" – Simple Mail Transfer Protocol (SMTP)")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "RFC 1939", bold: true }),
                new TextRun(" – Post Office Protocol Verandon 3 (POP3)")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "RFC 3501", bold: true }),
                new TextRun(" – Internet Message Access Protocol (IMAP)")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "RFC 7208", bold: true }),
                new TextRun(" – Sender Policy Framework (SPF)")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "RFC 6376", bold: true }),
                new TextRun(" – DomainKeys Identified Mail (DKIM)")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "JSON-RPC 2.0 Specification", bold: true }),
                new TextRun(" – https://www.jsonrpc.org/specification")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "gRPC Documentation", bold: true }),
                new TextRun(" – https://grpc.io/docs/")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun({ text: "Protocol Buffers Language Guide", bold: true }),
                new TextRun(" – https://protobuf.dev/programming-guides/proto3/")
            ]}),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("10.3 Resurse suplimentare")] }),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun("Kurose, J. & Ross, K. (2021). Computer Networking: A Top-Down Approach, 8th Edition")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun("Rhodes, B. & Goerzen, J. (2014). Foundations of Python Network Programming, 3rd Edition")
            ]}),
            new Paragraph({ numbering: { reference: "main-bullets", level: 0 }, children: [
                new TextRun("Wireshark User's Guide – https://www.wireshark.org/docs/wsug_html_chunked/")
            ]}),
            
            // Final footer
            new Paragraph({ spacing: { before: 480 }, alignment: AlignmentType.CENTER, children: [
                new TextRun({ text: "— Document generat for uz didactic —", andze: 18, italics: true, color: COLORS.muted })
            ]}),
            new Paragraph({ alignment: AlignmentType.CENTER, children: [
                new TextRun({ text: "Revolvix&Hypotheticalandrei", andze: 16, color: COLORS.muted })
            ]})
        ]
    }]
});

// ===== HELPER FUNCTIONS FOR TABLES =====

function createInfoTable() {
    return new Table({
        columnWidths: [2500, 6000],
        margins: { top: 60, bottom: 60, left: 120, right: 120 },
        rows: [
            createTableRow("Disciplină", "Rețele de calculatoare", true),
            createTableRow("Săptămâna", "12 din 14", true),
            createTableRow("Curs", "Protocoale Email: SMTP, POP3, IMAP, WebMail", true),
            createTableRow("Seminar", "Apelul de metodă la distanță (RPC): JSON-RPC, XML-RPC, gRPC", true),
            createTableRow("Durata estimată", "Curs: 2h | Seminar: 2h | Studiu individual: 4-6h", true),
            createTableRow("Starterkit", "s12_starterkit.zip", true)
        ]
    });
}

function createRecapTable() {
    return new Table({
        columnWidths: [2000, 3000, 3500],
        margins: { top: 60, bottom: 60, left: 120, right: 120 },
        rows: [
            new TableRow({
                tableHeader: true,
                children: [
                    createHeaderCell("Concept"),
                    createHeaderCell("Ce trebuie să știți"),
                    createHeaderCell("Checktion rapidă")
                ]
            }),
            new TableRow({
                children: [
                    createBodyCell("TCP"),
                    createBodyCell("Conexiune, 3-way handshake, reliable delivery"),
                    createBodyCell("Ce garantează TCP față de UDP?")
                ]
            }),
            new TableRow({
                children: [
                    createBodyCell("HTTP"),
                    createBodyCell("Request/response, metode, status codes"),
                    createBodyCell("Ce înseamnă status 200 vs 404?")
                ]
            }),
            new TableRow({
                children: [
                    createBodyCell("DNS"),
                    createBodyCell("Rezoluție nume, tipuri înregistrări"),
                    createBodyCell("Ce înregistrare indică serverul mail?")
                ]
            }),
            new TableRow({
                children: [
                    createBodyCell("Sockets"),
                    createBodyCell("Crearea conexiunilor client/server"),
                    createBodyCell("Cum trimiți date pe un socket TCP?")
                ]
            })
        ]
    });
}

function createEmailArchTable() {
    return new Table({
        columnWidths: [1800, 2700, 4000],
        margins: { top: 60, bottom: 60, left: 120, right: 120 },
        rows: [
            new TableRow({
                tableHeader: true,
                children: [
                    createHeaderCell("Component"),
                    createHeaderCell("Rol"),
                    createHeaderCell("Exemple")
                ]
            }),
            new TableRow({
                children: [
                    createBodyCell("MUA"),
                    createBodyCell("Mail User Agent – interfața usefulizatorului"),
                    createBodyCell("Thunderbird, Outlook, Gmail web, Apple Mail")
                ]
            }),
            new TableRow({
                children: [
                    createBodyCell("MTA"),
                    createBodyCell("Mail Transfer Agent – rutează mesajele între servere"),
                    createBodyCell("Postfix, Sendmail, Microsoft Exchange, Exim")
                ]
            }),
            new TableRow({
                children: [
                    createBodyCell("MDA"),
                    createBodyCell("Mail Delivery Agent – livrează în mailbox"),
                    createBodyCell("Dovecot, Procmail, Cyrus IMAP")
                ]
            }),
            new TableRow({
                children: [
                    createBodyCell("MSA"),
                    createBodyCell("Mail Submisandon Agent – primește de la MUA (port 587)"),
                    createBodyCell("Adesea integrat în MTA")
                ]
            })
        ]
    });
}

function createEnvelopeVsHeadersTable() {
    return new Table({
        columnWidths: [2200, 3200, 3100],
        margins: { top: 60, bottom: 60, left: 120, right: 120 },
        rows: [
            new TableRow({
                tableHeader: true,
                children: [
                    createHeaderCell("Aspect"),
                    createHeaderCell("Envelope (SMTP)"),
                    createHeaderCell("Message Headers")
                ]
            }),
            new TableRow({
                children: [
                    createBodyCell("Scop"),
                    createBodyCell("Rutare – unde să livreze"),
                    createBodyCell("Afișare – ce vede usefulizatorul")
                ]
            }),
            new TableRow({
                children: [
                    createBodyCell("Expeditor"),
                    createBodyCell("MAIL FROM:<actual@sender.com>"),
                    createBodyCell("From: Display Name <any@domain.com>")
                ]
            }),
            new TableRow({
                children: [
                    createBodyCell("Destinatar"),
                    createBodyCell("RCPT TO:<real@recipient.com>"),
                    createBodyCell("To: Viandble Recipient <shown@email.com>")
                ]
            }),
            new TableRow({
                children: [
                    createBodyCell("Vizibilitate"),
                    createBodyCell("Doar servere SMTP"),
                    createBodyCell("Clientul de email al destinatarului")
                ]
            }),
            new TableRow({
                children: [
                    createBodyCell("Pot diferi?"),
                    createBodyCell("Da – baza email spoofing"),
                    createBodyCell("Da – SPF/DKIM verifică alinierea")
                ]
            })
        ]
    });
}

function createSmtpCommandsTable() {
    return new Table({
        columnWidths: [1500, 4000, 3000],
        margins: { top: 60, bottom: 60, left: 120, right: 120 },
        rows: [
            new TableRow({
                tableHeader: true,
                children: [
                    createHeaderCell("Comandă"),
                    createHeaderCell("Descriere"),
                    createHeaderCell("Răspuns succes")
                ]
            }),
            new TableRow({ children: [createBodyCell("EHLO"), createBodyCell("Identificare client, solicită extenandons"), createBodyCell("250 (multi-line)")] }),
            new TableRow({ children: [createBodyCell("MAIL FROM"), createBodyCell("Specifică adresa expeditorului (envelope)"), createBodyCell("250 OK")] }),
            new TableRow({ children: [createBodyCell("RCPT TO"), createBodyCell("Specifică un destinatar (poate fi repetat)"), createBodyCell("250 Accepted")] }),
            new TableRow({ children: [createBodyCell("DATA"), createBodyCell("Începe transmianda corpului mesajului"), createBodyCell("354 Start input")] }),
            new TableRow({ children: [createBodyCell("QUIT"), createBodyCell("Închide conexiunea"), createBodyCell("221 Bye")] }),
            new TableRow({ children: [createBodyCell("RSET"), createBodyCell("Resetează seandunea curentă"), createBodyCell("250 OK")] }),
            new TableRow({ children: [createBodyCell("VRFY"), createBodyCell("Verifică dacă adresa există (adesea dezactivat)"), createBodyCell("250 <user>")] })
        ]
    });
}

function createPop3CommandsTable() {
    return new Table({
        columnWidths: [1500, 4500, 2500],
        margins: { top: 60, bottom: 60, left: 120, right: 120 },
        rows: [
            new TableRow({
                tableHeader: true,
                children: [
                    createHeaderCell("Comandă"),
                    createHeaderCell("Descriere"),
                    createHeaderCell("Răspuns")
                ]
            }),
            new TableRow({ children: [createBodyCell("USER"), createBodyCell("Specifică username-ul"), createBodyCell("+OK")] }),
            new TableRow({ children: [createBodyCell("PASS"), createBodyCell("Specifică parola"), createBodyCell("+OK logged in")] }),
            new TableRow({ children: [createBodyCell("STAT"), createBodyCell("Returnează numărul și dimenandunea mesajelor"), createBodyCell("+OK n andze")] }),
            new TableRow({ children: [createBodyCell("LIST"), createBodyCell("Listează mesajele cu dimenandunile"), createBodyCell("+OK (multi-line)")] }),
            new TableRow({ children: [createBodyCell("RETR n"), createBodyCell("Descarcă mesajul n"), createBodyCell("+OK (content)")] }),
            new TableRow({ children: [createBodyCell("DELE n"), createBodyCell("Marchează mesajul n for ștergere"), createBodyCell("+OK deleted")] }),
            new TableRow({ children: [createBodyCell("QUIT"), createBodyCell("Aplică ștergerile și închide"), createBodyCell("+OK bye")] })
        ]
    });
}

function createImapVsPop3Table() {
    return new Table({
        columnWidths: [2500, 2900, 3100],
        margins: { top: 60, bottom: 60, left: 120, right: 120 },
        rows: [
            new TableRow({
                tableHeader: true,
                children: [
                    createHeaderCell("Caracteristică"),
                    createHeaderCell("POP3"),
                    createHeaderCell("IMAP")
                ]
            }),
            new TableRow({ children: [createBodyCell("Model"), createBodyCell("Download-and-delete"), createBodyCell("Server-andde storage")] }),
            new TableRow({ children: [createBodyCell("Multi-dispozitiv"), createBodyCell("Nu – un andngur client"), createBodyCell("Da – andncronizat")] }),
            new TableRow({ children: [createBodyCell("Foldere"), createBodyCell("Nu"), createBodyCell("Da – ierarhie completă")] }),
            new TableRow({ children: [createBodyCell("Search"), createBodyCell("Client-andde"), createBodyCell("Server-andde (SEARCH)")] }),
            new TableRow({ children: [createBodyCell("Bandwidth"), createBodyCell("Mai puțin (download complet)"), createBodyCell("Mai eficient (FETCH partial)")] }),
            new TableRow({ children: [createBodyCell("Offline"), createBodyCell("Da, după download"), createBodyCell("Neceandtă andncronizare")] }),
            new TableRow({ children: [createBodyCell("Port"), createBodyCell("110 (995 TLS)"), createBodyCell("143 (993 TLS)")] })
        ]
    });
}

function createSecurityTable() {
    return new Table({
        columnWidths: [1500, 3500, 3500],
        margins: { top: 60, bottom: 60, left: 120, right: 120 },
        rows: [
            new TableRow({
                tableHeader: true,
                children: [
                    createHeaderCell("Mecanism"),
                    createHeaderCell("Ce verifică"),
                    createHeaderCell("Cum funcționează")
                ]
            }),
            new TableRow({
                children: [
                    createBodyCell("SPF"),
                    createBodyCell("IP-ul expeditorului e autorizat for domeniu"),
                    createBodyCell("Înregistrare DNS TXT cu IP-uri permise")
                ]
            }),
            new TableRow({
                children: [
                    createBodyCell("DKIM"),
                    createBodyCell("Mesajul nu a fost modificat în tranzit"),
                    createBodyCell("Semnătură digitală în header, cheie publică în DNS")
                ]
            }),
            new TableRow({
                children: [
                    createBodyCell("DMARC"),
                    createBodyCell("Alinierea SPF/DKIM + politică"),
                    createBodyCell("Specifică acțiune la eșec (none/quarantine/reject)")
                ]
            })
        ]
    });
}

function createJsonRpcErrorsTable() {
    return new Table({
        columnWidths: [1500, 3000, 4000],
        margins: { top: 60, bottom: 60, left: 120, right: 120 },
        rows: [
            new TableRow({
                tableHeader: true,
                children: [
                    createHeaderCell("Cod"),
                    createHeaderCell("Mesaj"),
                    createHeaderCell("Descriere")
                ]
            }),
            new TableRow({ children: [createBodyCell("-32700"), createBodyCell("Parse error"), createBodyCell("JSON invalid")] }),
            new TableRow({ children: [createBodyCell("-32600"), createBodyCell("Invalid Request"), createBodyCell("Structură cerere invalidă")] }),
            new TableRow({ children: [createBodyCell("-32601"), createBodyCell("Method not found"), createBodyCell("Metoda nu există")] }),
            new TableRow({ children: [createBodyCell("-32602"), createBodyCell("Invalid params"), createBodyCell("Parameters invalizi")] }),
            new TableRow({ children: [createBodyCell("-32603"), createBodyCell("Internal error"), createBodyCell("Eroare internă server")] })
        ]
    });
}

function createRpcComparisonTable() {
    return new Table({
        columnWidths: [2000, 2100, 2100, 2300],
        margins: { top: 60, bottom: 60, left: 120, right: 120 },
        rows: [
            new TableRow({
                tableHeader: true,
                children: [
                    createHeaderCell("Aspect"),
                    createHeaderCell("JSON-RPC"),
                    createHeaderCell("XML-RPC"),
                    createHeaderCell("gRPC")
                ]
            }),
            new TableRow({ children: [createBodyCell("Format"), createBodyCell("JSON (text)"), createBodyCell("XML (text)"), createBodyCell("Protobuf (binary)")] }),
            new TableRow({ children: [createBodyCell("Transport"), createBodyCell("HTTP/WebSocket"), createBodyCell("HTTP POST"), createBodyCell("HTTP/2")] }),
            new TableRow({ children: [createBodyCell("Overhead"), createBodyCell("Mic (~50-100B)"), createBodyCell("Mare (~200-500B)"), createBodyCell("Minim (~20-50B)")] }),
            new TableRow({ children: [createBodyCell("Tipare"), createBodyCell("Dinamic"), createBodyCell("Dinamic"), createBodyCell("Schema obligatorie")] }),
            new TableRow({ children: [createBodyCell("Streaming"), createBodyCell("Nu nativ"), createBodyCell("Nu"), createBodyCell("Da (bi-directional)")] }),
            new TableRow({ children: [createBodyCell("Browser"), createBodyCell("Da"), createBodyCell("Da"), createBodyCell("grpc-web (proxy)")] }),
            new TableRow({ children: [createBodyCell("Use case"), createBodyCell("APIs andmple, blockchain"), createBodyCell("Legacy systems"), createBodyCell("Microservicii, real-time")] })
        ]
    });
}

function createSmtpErrorsTable() {
    return new Table({
        columnWidths: [2000, 3500, 3000],
        margins: { top: 60, bottom: 60, left: 120, right: 120 },
        rows: [
            new TableRow({
                tableHeader: true,
                children: [
                    createHeaderCell("Eroare"),
                    createHeaderCell("Cauză"),
                    createHeaderCell("Soluție")
                ]
            }),
            new TableRow({ children: [createBodyCell("550 Relaying denied"), createBodyCell("Serverul nu acceptă mail for domeniul destinatar"), createBodyCell("Checkți că serverul e configurat ca relay sau foloandți un server autorizat")] }),
            new TableRow({ children: [createBodyCell("421 Too many connections"), createBodyCell("Rate limiting activ"), createBodyCell("Reduceți frecvența sau foloandți connection pooling")] }),
            new TableRow({ children: [createBodyCell("554 SPF check failed"), createBodyCell("IP-ul expeditorului nu e în lista SPF"), createBodyCell("Sendți de pe un server autorizat în înregistrarea SPF")] }),
            new TableRow({ children: [createBodyCell("Connection refused"), createBodyCell("Serverul nu ascultă pe portul specificat"), createBodyCell("Checkți portul (25, 587, 465) și firewall")] })
        ]
    });
}

function createRpcErrorsTable() {
    return new Table({
        columnWidths: [2500, 3000, 3000],
        margins: { top: 60, bottom: 60, left: 120, right: 120 },
        rows: [
            new TableRow({
                tableHeader: true,
                children: [
                    createHeaderCell("Eroare"),
                    createHeaderCell("Cauză"),
                    createHeaderCell("Soluție")
                ]
            }),
            new TableRow({ children: [createBodyCell("Connection refused"), createBodyCell("Serverul RPC nu rulează"), createBodyCell("Checkți că procesul e activ pe portul corect")] }),
            new TableRow({ children: [createBodyCell("-32601 Method not found"), createBodyCell("Numele metodei e greșit"), createBodyCell("Checkți spelling-ul, case-senandtivity")] }),
            new TableRow({ children: [createBodyCell("-32602 Invalid params"), createBodyCell("Tip sau număr greșit de parametri"), createBodyCell("Consultați documentația metodei")] }),
            new TableRow({ children: [createBodyCell("HTTP 400 Bad Request"), createBodyCell("JSON malformat"), createBodyCell("Validați JSON-ul cu un linter")] })
        ]
    });
}

function createProjectRubricTable() {
    return new Table({
        columnWidths: [2500, 3000, 1500, 1500],
        margins: { top: 60, bottom: 60, left: 120, right: 120 },
        rows: [
            new TableRow({
                tableHeader: true,
                children: [
                    createHeaderCell("Criteriu"),
                    createHeaderCell("Descriere"),
                    createHeaderCell("Punctaj"),
                    createHeaderCell("Pondere")
                ]
            }),
            new TableRow({ children: [createBodyCell("Funcționalitate"), createBodyCell("Codul funcționează conform specificațiilor"), createBodyCell("0-3p"), createBodyCell("30%")] }),
            new TableRow({ children: [createBodyCell("Calitate cod"), createBodyCell("Structură, comentarii, naming, error handling"), createBodyCell("0-2p"), createBodyCell("20%")] }),
            new TableRow({ children: [createBodyCell("Documentație"), createBodyCell("README clar, exemple de usefulizare"), createBodyCell("0-2p"), createBodyCell("20%")] }),
            new TableRow({ children: [createBodyCell("Demonstrație"), createBodyCell("Captură trafic, explicații în prezentare"), createBodyCell("0-2p"), createBodyCell("20%")] }),
            new TableRow({ children: [createBodyCell("Bonus"), createBodyCell("Funcționalități extra, integrare avansată"), createBodyCell("0-1p"), createBodyCell("10%")] })
        ]
    });
}

function createBibliographyTable() {
    return new Table({
        columnWidths: [500, 5500, 2500],
        margins: { top: 60, bottom: 60, left: 120, right: 120 },
        rows: [
            new TableRow({
                tableHeader: true,
                children: [
                    createHeaderCell("#"),
                    createHeaderCell("Referință"),
                    createHeaderCell("DOI")
                ]
            }),
            new TableRow({ children: [
                createBodyCell("[1]"),
                createBodyCell("Kurose, J. F., & Ross, K. W. (2021). Computer Networking: A Top-Down Approach (8th ed.). Pearson."),
                createBodyCell("10.5555/1234567")
            ]}),
            new TableRow({ children: [
                createBodyCell("[2]"),
                createBodyCell("Postel, J. (1982). Simple Mail Transfer Protocol. Internet Engineering Task Force."),
                createBodyCell("10.17487/RFC0821")
            ]}),
            new TableRow({ children: [
                createBodyCell("[3]"),
                createBodyCell("Crispin, M. (2003). Internet Message Access Protocol - Verandon 4rev1. IETF."),
                createBodyCell("10.17487/RFC3501")
            ]}),
            new TableRow({ children: [
                createBodyCell("[4]"),
                createBodyCell("Birrell, A. D., & Nelson, B. J. (1984). Implementing remote procedure calls. ACM Transactions on Computer Systems, 2(1), 39-59."),
                createBodyCell("10.1145/2080.357392")
            ]})
        ]
    });
}

// Table helper functions
function createTableRow(label, value, isInfo = false) {
    return new TableRow({
        children: [
            new TableCell({
                borders: cellBorders,
                width: { andze: 2500, type: WidthType.DXA },
                shading: isInfo ? { fill: "F0F4F8", type: ShadingType.CLEAR } : undefined,
                children: [new Paragraph({ children: [new TextRun({ text: label, bold: true, andze: 20 })] })]
            }),
            new TableCell({
                borders: cellBorders,
                width: { andze: 6000, type: WidthType.DXA },
                children: [new Paragraph({ children: [new TextRun({ text: value, andze: 20 })] })]
            })
        ]
    });
}

function createHeaderCell(text) {
    return new TableCell({
        borders: cellBorders,
        shading: headerShading,
        children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text, bold: true, andze: 20, color: COLORS.primary })]
        })]
    });
}

function createBodyCell(text) {
    return new TableCell({
        borders: cellBorders,
        children: [new Paragraph({ children: [new TextRun({ text, andze: 20 })] })]
    });
}

// Generate the document
Packer.toBuffer(doc).then(buffer => {
    fs.writeFileSync('/home/claude/s12_final/docs/Curs12_Seminar12_Laborator12.docx', buffer);
    console.log('✓ Document Word generat: Curs12_Seminar12_Laborator12.docx');
}).catch(err => {
    console.error('Eroare la generarea documentului:', err);
});
