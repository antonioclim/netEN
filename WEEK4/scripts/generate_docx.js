#!/usr/bin/env node
/**
 * DOCX generator for Week 4
 * Computer Networks (ASE-CSIE)
 * Custom TEXT and BINARY protocols over TCP and UDP
 */

const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, 
        Header, Footer, AlignmentType, LevelFormat, HeadingLevel, 
        BorderStyle, WidthType, ShadingType, PageNumber, PageBreak,
        ExternalHyperlink } = require('docx');
const fs = require('fs');

// Table border configuration
const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: "999999" };
const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };
const headerShading = { fill: "E8F4FD", type: ShadingType.CLEAR };

// Helper for paragraf simplu
const p = (text, options = {}) => new Paragraph({
    spacing: { after: 120 },
    ...options,
    children: [new TextRun({ text, size: 24, font: "Arial" })]
});

// Helper for paragraf bold
const pb = (text, options = {}) => new Paragraph({
    spacing: { after: 120 },
    ...options,
    children: [new TextRun({ text, size: 24, font: "Arial", bold: true })]
});

// Helper for paragraf cu text mixt
const pMix = (parts, options = {}) => new Paragraph({
    spacing: { after: 120 },
    ...options,
    children: parts.map(part => {
        if (typeof part === 'string') {
            return new TextRun({ text: part, size: 24, font: "Arial" });
        }
        return new TextRun({ size: 24, font: "Arial", ...part });
    })
});

// Helper for cod inline
const code = (text) => new TextRun({ 
    text, 
    size: 22, 
    font: "Consolas",
    shading: { fill: "F0F0F0", type: ShadingType.CLEAR }
});

// Create document
const doc = new Document({
    styles: {
        default: { 
            document: { 
                run: { font: "Arial", size: 24 } 
            } 
        },
        paragraphStyles: [
            { 
                id: "Title", name: "Title", basedOn: "Normal",
                run: { size: 56, bold: true, color: "1a365d", font: "Arial" },
                paragraph: { spacing: { before: 240, after: 240 }, alignment: AlignmentType.CENTER }
            },
            { 
                id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
                run: { size: 36, bold: true, color: "1a365d", font: "Arial" },
                paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 }
            },
            { 
                id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
                run: { size: 30, bold: true, color: "2c5282", font: "Arial" },
                paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 }
            },
            { 
                id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
                run: { size: 26, bold: true, color: "3182ce", font: "Arial" },
                paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 }
            },
            {
                id: "InstructorNote", name: "Instructor Note", basedOn: "Normal",
                run: { size: 22, italics: true, color: "666666", font: "Arial" },
                paragraph: { 
                    spacing: { before: 100, after: 100 },
                    indent: { left: 720 },
                    shading: { fill: "FFF8E1", type: ShadingType.CLEAR }
                }
            }
        ]
    },
    numbering: {
        config: [
            {
                reference: "bullet-list",
                levels: [{
                    level: 0,
                    format: LevelFormat.BULLET,
                    text: "•",
                    alignment: AlignmentType.LEFT,
                    style: { paragraph: { indent: { left: 720, hanging: 360 } } }
                }]
            },
            {
                reference: "numbered-list-1",
                levels: [{
                    level: 0,
                    format: LevelFormat.DECIMAL,
                    text: "%1.",
                    alignment: AlignmentType.LEFT,
                    style: { paragraph: { indent: { left: 720, hanging: 360 } } }
                }]
            },
            {
                reference: "numbered-list-2",
                levels: [{
                    level: 0,
                    format: LevelFormat.DECIMAL,
                    text: "%1.",
                    alignment: AlignmentType.LEFT,
                    style: { paragraph: { indent: { left: 720, hanging: 360 } } }
                }]
            },
            {
                reference: "numbered-list-3",
                levels: [{
                    level: 0,
                    format: LevelFormat.DECIMAL,
                    text: "%1.",
                    alignment: AlignmentType.LEFT,
                    style: { paragraph: { indent: { left: 720, hanging: 360 } } }
                }]
            },
            {
                reference: "numbered-list-ex",
                levels: [{
                    level: 0,
                    format: LevelFormat.DECIMAL,
                    text: "%1.",
                    alignment: AlignmentType.LEFT,
                    style: { paragraph: { indent: { left: 720, hanging: 360 } } }
                }]
            }
        ]
    },
    sections: [{
        properties: {
            page: {
                margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
            }
        },
        headers: {
            default: new Header({
                children: [new Paragraph({
                    alignment: AlignmentType.RIGHT,
                    children: [
                        new TextRun({ text: "Retele de Calculatoare | Saptamana 4", size: 20, font: "Arial", color: "666666" })
                    ]
                })]
            })
        },
        footers: {
            default: new Footer({
                children: [new Paragraph({
                    alignment: AlignmentType.CENTER,
                    children: [
                        new TextRun({ text: "Pagina ", size: 20, font: "Arial" }),
                        new TextRun({ children: [PageNumber.CURRENT], size: 20, font: "Arial" }),
                        new TextRun({ text: " din ", size: 20, font: "Arial" }),
                        new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 20, font: "Arial" }),
                        new TextRun({ text: " | Revolvix&Hypotheticalandrei", size: 18, font: "Arial", color: "999999" })
                    ]
                })]
            })
        },
        children: [
            // TITLU
            new Paragraph({
                heading: HeadingLevel.TITLE,
                children: [new TextRun({ text: "Saptamana 4", size: 56, bold: true, font: "Arial", color: "1a365d" })]
            }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { after: 480 },
                children: [new TextRun({ 
                    text: "Protocoale Text and Binare Custom peste TCP and UDP", 
                    size: 36, font: "Arial", color: "2c5282" 
                })]
            }),
            
            // Info disciplina
            new Table({
                columnWidths: [4680, 4680],
                rows: [
                    new TableRow({
                        children: [
                            new TableCell({
                                borders: cellBorders,
                                width: { size: 4680, type: WidthType.DXA },
                                children: [pMix([{ text: "Disciplina: ", bold: true }, "Retele de Calculatoare"])]
                            }),
                            new TableCell({
                                borders: cellBorders,
                                width: { size: 4680, type: WidthType.DXA },
                                children: [pMix([{ text: "Program: ", bold: true }, "Informatica Economica"])]
                            })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({
                                borders: cellBorders,
                                width: { size: 4680, type: WidthType.DXA },
                                children: [pMix([{ text: "An: ", bold: true }, "3, Semestrul 2"])]
                            }),
                            new TableCell({
                                borders: cellBorders,
                                width: { size: 4680, type: WidthType.DXA },
                                children: [pMix([{ text: "Durata: ", bold: true }, "2h curs + 2h seminar"])]
                            })
                        ]
                    })
                ]
            }),
            
            // ========== SECTIUNEA 1 ==========
            new Paragraph({ children: [new PageBreak()] }),
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun({ text: "1. Scopul saptamanii", size: 36, bold: true, font: "Arial", color: "1a365d" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "1.1 Ce vom invata", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            p("This saptamana marcheaza tranzitia de la utilizarea protocoalelor standard (HTTP, FTP) la proiectarea and implementarea protocoalelor proprii. Studentii vor dobandi competentele necesare for a specifica, implementa and testa protocols de comunicare adaptate nevoilor specifice ale aplicatiilor."),
            
            pb("Obiective de invatare:"),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Proiectarea protocoalelor text cu format human-readable", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Proiectarea protocoalelor binare cu header fix and payload variabil", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Rezolvarea problemei de framing in TCP streams", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Serializare and deserializare binara cu struct.pack/unpack", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Validarea integritatii datelor cu CRC32", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Implementare pattern fire-and-forget for UDP", size: 24, font: "Arial" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "1.2 De ce conteaza", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            p("In practica profesionala, programatorii se confrunta frecvent cu situatii in care protocoalele standard nu are optimale. Aplicatiile de gaming, IoT, streaming and trading financiar necesita protocols custom for a minimiza latenta and overhead-ul. Intelegerea principiilor de proiectare a protocoalelor permite:"),
            
            new Paragraph({
                numbering: { reference: "numbered-list-1", level: 0 },
                children: [new TextRun({ text: "Optimizarea performantei: reducerea overhead-ului de la sute de bytes (HTTP) la zeci de bytes", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "numbered-list-1", level: 0 },
                children: [new TextRun({ text: "Control granular: specificarea exacta a comportamentului in cazuri de eroare", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "numbered-list-1", level: 0 },
                children: [new TextRun({ text: "Debugging avansat: capacitatea de a analiza and depana traffic la nivel de bytes", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "numbered-list-1", level: 0 },
                children: [new TextRun({ text: "Interoperabilitate: comunicarea cu sisteme embedded and legacy", size: 24, font: "Arial" })]
            }),
            
            // Nota instructor
            new Paragraph({
                style: "InstructorNote",
                spacing: { before: 200, after: 200 },
                shading: { fill: "FFF8E1", type: ShadingType.CLEAR },
                children: [new TextRun({ 
                    text: "📋 Nota instructor: This saptamana is fundamentala for proiectul de echipa. Asigurati-va ca studentii inteleg ca vor trebui sa implementeze un protocol custom for aplicatia lor. Alocati timp for intrebari despre cerintele proiectului.", 
                    size: 22, italics: true, font: "Arial", color: "666666" 
                })]
            }),
            
            // ========== SECTIUNEA 2 ==========
            new Paragraph({ children: [new PageBreak()] }),
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun({ text: "2. Prerechizite and recapitulare", size: 36, bold: true, font: "Arial", color: "1a365d" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "2.1 Cunostinte necesare din S1-S3", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            
            new Table({
                columnWidths: [3120, 3120, 3120],
                rows: [
                    new TableRow({
                        tableHeader: true,
                        children: [
                            new TableCell({
                                borders: cellBorders,
                                shading: headerShading,
                                width: { size: 3120, type: WidthType.DXA },
                                children: [pb("Saptamana", { alignment: AlignmentType.CENTER })]
                            }),
                            new TableCell({
                                borders: cellBorders,
                                shading: headerShading,
                                width: { size: 3120, type: WidthType.DXA },
                                children: [pb("Concept", { alignment: AlignmentType.CENTER })]
                            }),
                            new TableCell({
                                borders: cellBorders,
                                shading: headerShading,
                                width: { size: 3120, type: WidthType.DXA },
                                children: [pb("Relevanta for S4", { alignment: AlignmentType.CENTER })]
                            })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("S1")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("Wireshark, tshark, netcat")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("Analiza traficului custom")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("S2")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("Sockets TCP/UDP de baza")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("Fundament for protocols")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("S3")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("Server concurent, threading")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("Handler clienti multipli")] })
                        ]
                    })
                ]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                spacing: { before: 300 },
                children: [new TextRun({ text: "2.2 Recapitulare TCP vs UDP", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            
            new Table({
                columnWidths: [4680, 4680],
                rows: [
                    new TableRow({
                        tableHeader: true,
                        children: [
                            new TableCell({
                                borders: cellBorders,
                                shading: headerShading,
                                width: { size: 4680, type: WidthType.DXA },
                                children: [pb("TCP (Transmission Control Protocol)", { alignment: AlignmentType.CENTER })]
                            }),
                            new TableCell({
                                borders: cellBorders,
                                shading: headerShading,
                                width: { size: 4680, type: WidthType.DXA },
                                children: [pb("UDP (User Datagram Protocol)", { alignment: AlignmentType.CENTER })]
                            })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [p("Connection-oriented (necesita connect())")] }),
                            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [p("Connectionless (sendto() directly)")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [p("Reliable: ACK, retransmisie automata")] }),
                            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [p("Best-effort: fara garantii de livrare")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [p("Ordered delivery garantata")] }),
                            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [p("Fara garantie de ordine")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [p("Stream-based (bytes continui)")] }),
                            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [p("Message-based (datagrame discrete)")] })
                        ]
                    })
                ]
            }),
            
            // ========== SECTIUNEA 3 ==========
            new Paragraph({ children: [new PageBreak()] }),
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun({ text: "3. Curs: Protocoale Custom", size: 36, bold: true, font: "Arial", color: "1a365d" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "3.1 Motivatia protocoalelor custom", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            p("Protocoalele standard precum HTTP, FTP or SMTP are proiectate for versatilitate and interoperabilitate larga. This generalitate vine cu un cost: overhead semnificativ for cazuri simple. Un request HTTP minimal for a obtine o value can depasi 500 bytes, in timp ce un protocol binary custom can realiza acelasi lucru in 14-20 bytes."),
            
            pb("Cazuri de utilizare for protocols custom:"),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Gaming: latenta minima, update-uri de stare frecvente", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "IoT/Senzori: dispozitive cu resurse limitate, banda ingusta", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Trading financiar: microsecunde conteaza", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Sisteme embedded: memorie and procesor limitate", size: 24, font: "Arial" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "3.2 Protocoale TEXT", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            
            p("Protocoalele text use characters ASCII/UTF-8 human-readable. Avantajul principal is debugging-ul facil - traffic can fi inspectat directly cu netcat or telnet."),
            
            pb("Format protocol TEXT for S4:"),
            p("Mesajele urmeaza formatul: \"<LUNGIME> <PAYLOAD>\\n\" unde LUNGIME is un numar zecimal reprezentand lungimea payload-ului in bytes, urmat de un spatiu separator and payload-ul propriu-zis, terminat cu newline."),
            
            pMix([{ text: "Exemplu: ", bold: true }, "Clientul trimite \"5 Hello\\n\" - serverul primeste and parseaza payload-ul \"Hello\"."]),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_3,
                children: [new TextRun({ text: "Problema Framing-ului in TCP", size: 26, bold: true, font: "Arial", color: "3182ce" })]
            }),
            p("TCP is un protocol stream-based, ceea ce inseamna ca datele trimise in apeluri send() separate pot fi primite concatenate intr-un singur recv(), or fragmentate in multiple recv()-uri. This caracteristica impune necesitatea unui mechanism de delimitation a messages (framing)."),
            
            pb("Solutii de framing:"),
            new Paragraph({
                numbering: { reference: "numbered-list-2", level: 0 },
                children: [new TextRun({ text: "Delimitator fix (newline, null byte) - simplu dar payload-ul nu can contine delimitatorul", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "numbered-list-2", level: 0 },
                children: [new TextRun({ text: "Lungime prefixata - payload-ul e precedat de lungimea sa", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "numbered-list-2", level: 0 },
                children: [new TextRun({ text: "Header fix - structura cunoscuta la inceput, include lungimea", size: 24, font: "Arial" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "3.3 Protocoale BINARE", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            p("Protocoalele binare encodeaza datele in format binary compact. Principalele avantaje are eficienta (overhead minim) and performanta (parsing rapid). Dezavantajul is ca debugging-ul necesita instrumente specializate (Wireshark, hex dump)."),
            
            pb("Structura header-ului BINAR for S4 (14 bytes):"),
            
            new Table({
                columnWidths: [1500, 1200, 2000, 4660],
                rows: [
                    new TableRow({
                        tableHeader: true,
                        children: [
                            new TableCell({ borders: cellBorders, shading: headerShading, width: { size: 1500, type: WidthType.DXA }, children: [pb("Offset", { alignment: AlignmentType.CENTER })] }),
                            new TableCell({ borders: cellBorders, shading: headerShading, width: { size: 1200, type: WidthType.DXA }, children: [pb("Bytes", { alignment: AlignmentType.CENTER })] }),
                            new TableCell({ borders: cellBorders, shading: headerShading, width: { size: 2000, type: WidthType.DXA }, children: [pb("Camp", { alignment: AlignmentType.CENTER })] }),
                            new TableCell({ borders: cellBorders, shading: headerShading, width: { size: 4660, type: WidthType.DXA }, children: [pb("Descriere", { alignment: AlignmentType.CENTER })] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 1500, type: WidthType.DXA }, children: [p("0")] }),
                            new TableCell({ borders: cellBorders, width: { size: 1200, type: WidthType.DXA }, children: [p("2")] }),
                            new TableCell({ borders: cellBorders, width: { size: 2000, type: WidthType.DXA }, children: [p("MAGIC")] }),
                            new TableCell({ borders: cellBorders, width: { size: 4660, type: WidthType.DXA }, children: [p("\"NP\" (0x4E50) - identificator protocol")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 1500, type: WidthType.DXA }, children: [p("2")] }),
                            new TableCell({ borders: cellBorders, width: { size: 1200, type: WidthType.DXA }, children: [p("1")] }),
                            new TableCell({ borders: cellBorders, width: { size: 2000, type: WidthType.DXA }, children: [p("VERSION")] }),
                            new TableCell({ borders: cellBorders, width: { size: 4660, type: WidthType.DXA }, children: [p("Versiune protocol (0x01)")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 1500, type: WidthType.DXA }, children: [p("3")] }),
                            new TableCell({ borders: cellBorders, width: { size: 1200, type: WidthType.DXA }, children: [p("1")] }),
                            new TableCell({ borders: cellBorders, width: { size: 2000, type: WidthType.DXA }, children: [p("TYPE")] }),
                            new TableCell({ borders: cellBorders, width: { size: 4660, type: WidthType.DXA }, children: [p("Tip message (0=req, 1=resp, 2=error)")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 1500, type: WidthType.DXA }, children: [p("4")] }),
                            new TableCell({ borders: cellBorders, width: { size: 1200, type: WidthType.DXA }, children: [p("4")] }),
                            new TableCell({ borders: cellBorders, width: { size: 2000, type: WidthType.DXA }, children: [p("PAYLOAD_LEN")] }),
                            new TableCell({ borders: cellBorders, width: { size: 4660, type: WidthType.DXA }, children: [p("Lungime payload (big-endian, uint32)")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 1500, type: WidthType.DXA }, children: [p("8")] }),
                            new TableCell({ borders: cellBorders, width: { size: 1200, type: WidthType.DXA }, children: [p("2")] }),
                            new TableCell({ borders: cellBorders, width: { size: 2000, type: WidthType.DXA }, children: [p("SEQUENCE")] }),
                            new TableCell({ borders: cellBorders, width: { size: 4660, type: WidthType.DXA }, children: [p("Numar secventa (big-endian, uint16)")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 1500, type: WidthType.DXA }, children: [p("10")] }),
                            new TableCell({ borders: cellBorders, width: { size: 1200, type: WidthType.DXA }, children: [p("4")] }),
                            new TableCell({ borders: cellBorders, width: { size: 2000, type: WidthType.DXA }, children: [p("CRC32")] }),
                            new TableCell({ borders: cellBorders, width: { size: 4660, type: WidthType.DXA }, children: [p("Checksum payload (big-endian, uint32)")] })
                        ]
                    })
                ]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_3,
                spacing: { before: 300 },
                children: [new TextRun({ text: "Serializare cu struct in Python", size: 26, bold: true, font: "Arial", color: "3182ce" })]
            }),
            p("Modulul struct din Python permite conversia intre valori Python and reprezentari binare. Formatul '>2sBBIHI' specifica: big-endian (>), 2 bytes string (2s), doua unsigned char (BB), unsigned int (I), unsigned short (H), unsigned int (I)."),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "3.4 Protocol UDP for senzori", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            p("UDP is ideal for aplicatii care necesita latenta minima and tolereaza pierderi ocazionale. Un senzor IoT care trimite citiri la fiecare 2 secunde can tolera pierderea unei citiri - urmatoarea oricum vine curand."),
            
            pb("Format datagrama senzor (23 bytes fix):"),
            p("Versiune (1B) + SensorID (4B) + Temperatura float (4B) + Locatie ASCII padded (10B) + CRC32 (4B)"),
            
            // Note instructor
            new Paragraph({
                style: "InstructorNote",
                spacing: { before: 200, after: 200 },
                shading: { fill: "FFF8E1", type: ShadingType.CLEAR },
                children: [new TextRun({ 
                    text: "📋 Nota instructor: La acest punct, demonstrati live diferenta dintre TEXT and BINAR capturand trafic cu tshark. Aratati payload-ul TEXT directly in ASCII vs hex dump for BINAR. Timing estimat: 5-7 minute.", 
                    size: 22, italics: true, font: "Arial", color: "666666" 
                })]
            }),
            
            // ========== SECTIUNEA 4 ==========
            new Paragraph({ children: [new PageBreak()] }),
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun({ text: "4. Seminar: Implementare ghidata", size: 36, bold: true, font: "Arial", color: "1a365d" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "4.1 Pregatire mediu de lucru", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            p("Inainte de a incepe implementarea, verificati ca aveti toate instrumentele necesare instalate and functionale."),
            
            pb("Comenzi de verificare:"),
            p("python3 --version (necesita 3.8+)"),
            p("pip3 --version"),
            p("tshark --version"),
            p("nc -h (netcat)"),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "4.2 Implementare Protocol TEXT - pas cu pas", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_3,
                children: [new TextRun({ text: "Pasul 1: Functia recv_until()", size: 26, bold: true, font: "Arial", color: "3182ce" })]
            }),
            p("This function reads bytes din socket pana intalneste delimitatorul specificat. Este esentiala for protocols text care use newline or other caracter ca terminator de message."),
            
            pb("Pseudocod:"),
            p("1. Initializeaza buffer gol"),
            p("2. Repeta: reads 1 byte, adauga la buffer"),
            p("3. Daca delimitatorul e in buffer, returneaza buffer"),
            p("4. Daca conexiunea s-a inchis (recv returneaza empty), ridica exceptie"),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_3,
                children: [new TextRun({ text: "Pasul 2: Functia parse_message()", size: 26, bold: true, font: "Arial", color: "3182ce" })]
            }),
            p("Extrage lungimea declarata and payload-ul din formatul '<LEN> <PAYLOAD>'. Valideaza ca lungimea declarata corespunde cu lungimea reala a payload-ului."),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_3,
                children: [new TextRun({ text: "Pasul 3: Handler client", size: 26, bold: true, font: "Arial", color: "3182ce" })]
            }),
            p("Functia handle_client primeste conexiunea acceptata and proceseaza mesaje in bucla pana la deconectare. Fiecare message primit e parsat, procesat (ecou in exemplul nostru) and raspunsul e trimis inapoi."),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "4.3 Implementare Protocol BINAR - pas cu pas", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_3,
                children: [new TextRun({ text: "Pasul 1: Functia recv_exact()", size: 26, bold: true, font: "Arial", color: "3182ce" })]
            }),
            p("Spre deosebire de recv_until(), this function reads exact N bytes, acumuland in buffer pana ajunge la lungimea ceruta. Este necesara deoarece recv(n) can returna mai putin de n bytes."),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_3,
                children: [new TextRun({ text: "Pasul 2: Pack and Unpack header", size: 26, bold: true, font: "Arial", color: "3182ce" })]
            }),
            p("Utilizati struct.pack for a crea header-ul and struct.unpack for a-l citi. Formatul '>2sBBIHI' corespunde structurii definite (14 bytes total)."),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_3,
                children: [new TextRun({ text: "Pasul 3: Calcul and validare CRC32", size: 26, bold: true, font: "Arial", color: "3182ce" })]
            }),
            p("CRC32 se calculeaza peste payload cu zlib.crc32(data) & 0xFFFFFFFF. Masca & 0xFFFFFFFF asigura rezultat unsigned pe 32 biti. La receptie, comparati CRC-ul din header cu cel calculat local."),
            
            // Note instructor
            new Paragraph({
                style: "InstructorNote",
                spacing: { before: 200, after: 200 },
                shading: { fill: "FFF8E1", type: ShadingType.CLEAR },
                children: [new TextRun({ 
                    text: "📋 Nota instructor: Lasati studentii sa implementeze singuri recv_exact() (5 min), apoi discutati solutiile. Greseli comune: nu verifica daca recv() returneaza empty bytes (conexiune inchisa).", 
                    size: 22, italics: true, font: "Arial", color: "666666" 
                })]
            }),
            
            // ========== SECTIUNEA 5 ==========
            new Paragraph({ children: [new PageBreak()] }),
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun({ text: "5. Laborator: Experimente practice", size: 36, bold: true, font: "Arial", color: "1a365d" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "5.1 Experiment 1: Protocol TEXT functional", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            
            pb("Obiectiv: Rularea and testarea serverului and clientului TEXT."),
            
            pb("Pasi:"),
            new Paragraph({
                numbering: { reference: "numbered-list-3", level: 0 },
                children: [new TextRun({ text: "Deschideti Terminal 1, navigati la /python/apps/", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "numbered-list-3", level: 0 },
                children: [new TextRun({ text: "Porniti serverul: python3 text_proto_server.py", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "numbered-list-3", level: 0 },
                children: [new TextRun({ text: "Deschideti Terminal 2, testati cu netcat: echo '5 Hello' | nc localhost 3333", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "numbered-list-3", level: 0 },
                children: [new TextRun({ text: "Rulati clientul Python: python3 text_proto_client.py", size: 24, font: "Arial" })]
            }),
            
            pb("Rezultat asteptat:"),
            p("Serverul afiseaza mesajele primite and trimite ecou inapoi. Clientul primeste raspunsurile and le afiseaza."),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "5.2 Experiment 2: Captura and analiza trafic", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            
            pb("Obiectiv: Capturarea and analiza traficului TEXT and BINAR cu tshark."),
            
            pb("Comenzi for captura TEXT:"),
            p("sudo tshark -i lo -f 'tcp port 3333' -Y 'tcp.payload' -T fields -e frame.number -e tcp.payload"),
            
            pb("Comenzi for captura BINAR:"),
            p("sudo tshark -i lo -f 'tcp port 4444' -Y 'tcp.payload' -x"),
            
            pb("Intrebari de analiza:"),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Ce observati in payload-ul TEXT vs BINAR?", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Puteti identifica header-ul de 14 bytes in traffic BINAR?", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Care is overhead-ul for un message 'Hello' in fiecare protocol?", size: 24, font: "Arial" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "5.3 Experiment 3: Simulare senzori UDP in Mininet", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            
            pb("Obiectiv: Testarea protocolului UDP sensor intr-o topologie izolata."),
            
            p("Utilizati scenariul Mininet din /mininet/scenario_udp_demo.py care creeaza o topologie cu 2 senzori and un colector, incluzand simulare de pierderi pe una din legaturi."),
            
            // ========== SECTIUNEA 6 ==========
            new Paragraph({ children: [new PageBreak()] }),
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun({ text: "6. Greseli frecvente and debugging", size: 36, bold: true, font: "Arial", color: "1a365d" })]
            }),
            
            new Table({
                columnWidths: [3000, 3000, 3360],
                rows: [
                    new TableRow({
                        tableHeader: true,
                        children: [
                            new TableCell({ borders: cellBorders, shading: headerShading, width: { size: 3000, type: WidthType.DXA }, children: [pb("Simptom", { alignment: AlignmentType.CENTER })] }),
                            new TableCell({ borders: cellBorders, shading: headerShading, width: { size: 3000, type: WidthType.DXA }, children: [pb("Cauza probabila", { alignment: AlignmentType.CENTER })] }),
                            new TableCell({ borders: cellBorders, shading: headerShading, width: { size: 3360, type: WidthType.DXA }, children: [pb("Diagnostic", { alignment: AlignmentType.CENTER })] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 3000, type: WidthType.DXA }, children: [p("recv() blocheaza indefinit")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3000, type: WidthType.DXA }, children: [p("Nu s-a trimis suficient")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3360, type: WidthType.DXA }, children: [p("Verifica daca \\n e trimis")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 3000, type: WidthType.DXA }, children: [p("Date trunchiare")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3000, type: WidthType.DXA }, children: [p("recv() < bytes asteptati")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3360, type: WidthType.DXA }, children: [p("Foloseste recv_exact()")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 3000, type: WidthType.DXA }, children: [p("CRC mismatch constant")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3000, type: WidthType.DXA }, children: [p("Endianness gresit")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3360, type: WidthType.DXA }, children: [p("Verifica > vs < in format")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 3000, type: WidthType.DXA }, children: [p("Magic invalid")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3000, type: WidthType.DXA }, children: [p("Offset gresit in unpack")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3360, type: WidthType.DXA }, children: [p("Verifica HEADER_SIZE")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 3000, type: WidthType.DXA }, children: [p("Conexiune refuzata")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3000, type: WidthType.DXA }, children: [p("Server nu asculta")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3360, type: WidthType.DXA }, children: [p("netstat -tlnp | grep PORT")] })
                        ]
                    })
                ]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                spacing: { before: 300 },
                children: [new TextRun({ text: "6.1 Comenzi utile de debugging", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            
            pb("Verificare port activ:"),
            p("netstat -tlnp | grep 3333"),
            
            pb("Test conexiune rapida:"),
            p("nc -v localhost 3333"),
            
            pb("Captura raw pe interfata:"),
            p("sudo tcpdump -i lo port 3333 -XX"),
            
            pb("Verificare procese Python:"),
            p("ps aux | grep python"),
            
            // ========== SECTIUNEA 7 ==========
            new Paragraph({ children: [new PageBreak()] }),
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun({ text: "7. Exercitii de consolidare", size: 36, bold: true, font: "Arial", color: "1a365d" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "Exercitiu 1: Protocol TEXT cu comenzi (Intelegere)", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            p("Extindeti protocolul TEXT for a suporta comenzi multiple: ECHO, UPPER, LOWER, REVERSE, COUNT. Formatul devine \"<CMD> <LEN> <PAYLOAD>\\n\". Serverul trebuie sa proceseze comanda and sa returneze rezultatul corespunzator."),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "Exercitiu 2: Analiza overhead (Aplicare)", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            p("Capturati 10 mesaje TEXT and 10 BINAR. Calculati overhead-ul total (bytes protocol / bytes payload) for fiecare. Raspundeti: care protocol e mai eficient for payload de 5 bytes? Dar for 500 bytes?"),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "Exercitiu 3: Protocol BINAR cu tipuri (Aplicare)", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            p("Extindeti header-ul BINAR cu un camp CONTENT_TYPE: 0=text UTF-8, 1=JSON, 2=bytes raw. Serverul trebuie sa proceseze diferit fiecare tip (for JSON: deserializare and extragere camp specific)."),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "Exercitiu 4: Agregator UDP (Analiza)", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            p("Creati un agregator care primeste date de la multipli senzori and: (a) calculeaza media temperaturii per locatie, (b) detecteaza senzori care nu au trimis in ultimele 30 secunde, (c) genereaza raport JSON periodic."),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "Exercitiu 5: Testare in Mininet (Sinteza)", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            p("Implementati o topologie Mininet cu 3 hosturi and testati protocolul BINAR. Adaugati delay de 50ms pe o legatura cu 'tc netem' and masurati impactul asupra throughput-ului."),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "Exercitiu 6 - Challenge: Protocol hibrid (Creatie)", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            p("Proiectati and implementati un protocol hibrid care: (1) uses handshake TEXT for negociere capabilitati, (2) trece la mod BINAR for transfer date, (3) suporta compresie optionala zlib, (4) include timestamp in fiecare message. Livrati specificatie documentata, implementare server+client, and captura tshark demonstrativa."),
            
            // ========== SECTIUNEA 8 ==========
            new Paragraph({ children: [new PageBreak()] }),
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun({ text: "8. Mini-reflectie", size: 36, bold: true, font: "Arial", color: "1a365d" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "8.1 Ce am invatat", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            
            pb("Concepte fundamentale:"),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Diferenta fundamentala intre protocols text (human-readable) and binare (compact, eficient)", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Problema framing-ului in TCP and solutii: delimitatori, lungime prefixata, header fix", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Tehnici de read: recv_until() for text, recv_exact() for binary", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Serializare binara cu struct.pack/unpack and conventii endianness", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Validarea integritatii cu CRC32 - detectare erori, nu securitate", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Caracteristicile UDP for aplicatii fire-and-forget", size: 24, font: "Arial" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "8.2 Unde se uses in practica", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            
            new Table({
                columnWidths: [3120, 3120, 3120],
                rows: [
                    new TableRow({
                        tableHeader: true,
                        children: [
                            new TableCell({ borders: cellBorders, shading: headerShading, width: { size: 3120, type: WidthType.DXA }, children: [pb("Domeniu", { alignment: AlignmentType.CENTER })] }),
                            new TableCell({ borders: cellBorders, shading: headerShading, width: { size: 3120, type: WidthType.DXA }, children: [pb("Exemplu protocol", { alignment: AlignmentType.CENTER })] }),
                            new TableCell({ borders: cellBorders, shading: headerShading, width: { size: 3120, type: WidthType.DXA }, children: [pb("Caracteristici", { alignment: AlignmentType.CENTER })] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("Cache/DB")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("Redis RESP, Memcached")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("Text simplu, high throughput")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("Gaming")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("Protocol custom UDP")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("Latenta minima, toleranta pierderi")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("IoT")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("MQTT, CoAP")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("Overhead minim, dispozitive limitate")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("RPC")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("gRPC (Protocol Buffers)")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("Binar eficient, schema-based")] })
                        ]
                    })
                ]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                spacing: { before: 300 },
                children: [new TextRun({ text: "8.3 Legatura cu rolul de programator", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            p("Competentele dobandite in this saptamana are directly aplicabile in roluri precum: Backend Developer (design API-uri eficiente), Systems Programmer (comunicare inter-proces), Embedded Developer (protocols for microcontrolere), Game Developer (networking multiplayer), IoT Engineer (protocols senzori)."),
            
            // ========== SECTIUNEA 9 ==========
            new Paragraph({ children: [new PageBreak()] }),
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun({ text: "9. Contributia la proiectul de echipa", size: 36, bold: true, font: "Arial", color: "1a365d" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "9.1 Artefact S4: Protocol custom for aplicatie", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            
            pb("Cerinte minime:"),
            new Paragraph({
                numbering: { reference: "numbered-list-ex", level: 0 },
                children: [new TextRun({ text: "Specificatie documentata: format header, tipuri mesaje, diagrame", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "numbered-list-ex", level: 0 },
                children: [new TextRun({ text: "Implementare server and client functionale", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "numbered-list-ex", level: 0 },
                children: [new TextRun({ text: "Minim 3 tipuri de mesaje/comenzi diferite", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "numbered-list-ex", level: 0 },
                children: [new TextRun({ text: "Validare integritate (CRC or other mechanism)", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "numbered-list-ex", level: 0 },
                children: [new TextRun({ text: "Captura tshark demonstrativa cu interpretare", size: 24, font: "Arial" })]
            }),
            
            pb("Criterii bonus:"),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Protocol hibrid (negociere TEXT → transfer BINAR)", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Compresie payload optionala", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Suport for multiple versiuni protocol", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Teste automate for protocol", size: 24, font: "Arial" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "9.2 Integrare in arhitectura proiectului", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            p("Protocolul dezvoltat trebuie sa se integreze in arhitectura generala a aplicatiei de echipa. Documentati in README cum se pozitioneaza protocolul: ce componente il use, ce date transporta, and de ce ati ales this abordare (TEXT vs BINAR)."),
            
            // ========== SECTIUNEA 10 ==========
            new Paragraph({ children: [new PageBreak()] }),
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun({ text: "10. Bibliografie and resurse", size: 36, bold: true, font: "Arial", color: "1a365d" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "10.1 Bibliografie academica cu DOI", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            
            new Table({
                columnWidths: [5000, 4360],
                rows: [
                    new TableRow({
                        tableHeader: true,
                        children: [
                            new TableCell({ borders: cellBorders, shading: headerShading, width: { size: 5000, type: WidthType.DXA }, children: [pb("Referinta", { alignment: AlignmentType.CENTER })] }),
                            new TableCell({ borders: cellBorders, shading: headerShading, width: { size: 4360, type: WidthType.DXA }, children: [pb("DOI / Link", { alignment: AlignmentType.CENTER })] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 5000, type: WidthType.DXA }, children: [p("Kurose, J. & Ross, K. (2021). Computer Networking: A Top-Down Approach (8th ed.). Pearson.")] }),
                            new TableCell({ borders: cellBorders, width: { size: 4360, type: WidthType.DXA }, children: [p("ISBN: 978-0135928615")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 5000, type: WidthType.DXA }, children: [p("Stevens, W.R. (1993). TCP/IP Illustrated, Vol. 1: The Protocols. Addison-Wesley.")] }),
                            new TableCell({ borders: cellBorders, width: { size: 4360, type: WidthType.DXA }, children: [p("ISBN: 978-0201633467")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 5000, type: WidthType.DXA }, children: [p("Rhodes, B. & Goerzen, J. (2014). Foundations of Python Network Programming (3rd ed.). Apress.")] }),
                            new TableCell({ borders: cellBorders, width: { size: 4360, type: WidthType.DXA }, children: [p("DOI: 10.1007/978-1-4302-5855-1")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 5000, type: WidthType.DXA }, children: [p("Postel, J. (1981). Transmission Control Protocol. RFC 793.")] }),
                            new TableCell({ borders: cellBorders, width: { size: 4360, type: WidthType.DXA }, children: [p("DOI: 10.17487/RFC0793")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 5000, type: WidthType.DXA }, children: [p("Postel, J. (1980). User Datagram Protocol. RFC 768.")] }),
                            new TableCell({ borders: cellBorders, width: { size: 4360, type: WidthType.DXA }, children: [p("DOI: 10.17487/RFC0768")] })
                        ]
                    })
                ]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                spacing: { before: 300 },
                children: [new TextRun({ text: "10.2 Standarde and specificatii (fara DOI)", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Python struct module documentation: https://docs.python.org/3/library/struct.html", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Python zlib module documentation: https://docs.python.org/3/library/zlib.html", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Wireshark User's Guide: https://www.wireshark.org/docs/wsug_html/", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Mininet Documentation: http://mininet.org/walkthrough/", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Redis Protocol Specification (RESP): https://redis.io/docs/reference/protocol-spec/", size: 24, font: "Arial" })]
            }),
            
            // Footer final
            new Paragraph({
                spacing: { before: 600 },
                alignment: AlignmentType.CENTER,
                children: [new TextRun({ 
                    text: "─── Revolvix&Hypotheticalandrei ───", 
                    size: 20, font: "Arial", color: "999999", italics: true 
                })]
            })
        ]
    }]
});

// Generare and salvare
Packer.toBuffer(doc).then(buffer => {
    fs.writeFileSync('/home/claude/output/starterkit_s4/Curs4_Seminar4_Laborator4.docx', buffer);
    console.log('✓ Document DOCX generat: Curs4_Seminar4_Laborator4.docx');
}).catch(err => {
    console.error('Eroare la generare DOCX:', err);
    process.exit(1);
});
