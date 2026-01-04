const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, 
        Header, Footer, AlignmentType, LevelFormat, HeadingLevel, BorderStyle, 
        WidthType, ShadingType, PageNumber, PageBreak } = require('docx');
const fs = require('fs');

// Color scheme
const COLORS = {
  primary: "1B4F72",
  secondary: "2874A6",
  accent: "E67E22",
  text: "2C3E50",
  lightBg: "EBF5FB",
  instructorBg: "FEF9E7",
  warningBg: "FDEDEC"
};

// Table border style
const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: "BDC3C7" };
const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Calibri", size: 22 } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal",
        run: { size: 56, bold: true, color: COLORS.primary, font: "Calibri Light" },
        paragraph: { spacing: { before: 120, after: 240 }, alignment: AlignmentType.CENTER } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, color: COLORS.primary, font: "Calibri Light" },
        paragraph: { spacing: { before: 360, after: 120 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, color: COLORS.secondary, font: "Calibri" },
        paragraph: { spacing: { before: 240, after: 80 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, color: COLORS.text, font: "Calibri" },
        paragraph: { spacing: { before: 200, after: 60 }, outlineLevel: 2 } },
      { id: "InstructorNote", name: "Instructor Note", basedOn: "Normal",
        run: { size: 20, italics: true, color: "7B7D7D" },
        paragraph: { spacing: { before: 60, after: 60 }, indent: { left: 360 } } },
      { id: "CodeBlock", name: "Code Block", basedOn: "Normal",
        run: { size: 18, font: "Consolas", color: "2E4053" },
        paragraph: { spacing: { before: 80, after: 80 } } }
    ]
  },
  numbering: {
    config: [
      { reference: "bullet-list",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-1",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-2",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-3",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-4",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-5",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-6",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }
    ]
  },
  sections: [{
    properties: {
      page: { margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 } }
    },
    headers: {
      default: new Header({ children: [new Paragraph({ 
        alignment: AlignmentType.RIGHT,
        children: [
          new TextRun({ text: "Computer Networks — Week 5", size: 18, color: "7B7D7D" })
        ]
      })] })
    },
    footers: {
      default: new Footer({ children: [new Paragraph({ 
        alignment: AlignmentType.CENTER,
        children: [
          new TextRun({ text: "Pagina ", size: 18 }), 
          new TextRun({ children: [PageNumber.CURRENT], size: 18 }),
          new TextRun({ text: " din ", size: 18 }), 
          new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 18 }),
          new TextRun({ text: " | ASE CSIE — Informatica Economica", size: 18, color: "7B7D7D" })
        ]
      })] })
    },
    children: [
      // ═══════════════════════════════════════════════════════════════════
      // COVER PAGE
      // ═══════════════════════════════════════════════════════════════════
      new Paragraph({ spacing: { before: 2400 } }),
      new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("RETELE DE CALCULATOARE")] }),
      new Paragraph({ 
        alignment: AlignmentType.CENTER, spacing: { before: 240 },
        children: [new TextRun({ text: "Lectureul 5 | Seminar 5 | Laboratory 5", size: 32, color: COLORS.secondary })]
      }),
      new Paragraph({ spacing: { before: 480 } }),
      new Paragraph({ 
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Nivelul Retea: IP Addressingv4/IPv6, Subnetting, VLSM", size: 28, bold: true, color: COLORS.text })]
      }),
      new Paragraph({ spacing: { before: 960 } }),
      new Paragraph({ 
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Anul universitar 2024–2025, Semestrul 2", size: 22, color: "7B7D7D" })]
      }),
      new Paragraph({ 
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Academia de Studii Economice Bucuresti", size: 22, color: "7B7D7D" })]
      }),
      new Paragraph({ 
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Facultatea de Cibernetica, Statistica si Informatica Economica", size: 22, color: "7B7D7D" })]
      }),
      new Paragraph({ spacing: { before: 1440 } }),
      new Paragraph({ 
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "📘 Notes for cadre didactice si studenti", size: 20, italics: true, color: "7B7D7D" })]
      }),
      
      new Paragraph({ children: [new PageBreak()] }),
      
      // ═══════════════════════════════════════════════════════════════════
      // SECTION 1: SCOPUL SAPTAMANII
      // ═══════════════════════════════════════════════════════════════════
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("1. Scopul Saptamanii")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Ce vom invata")] }),
      new Paragraph({ children: [new TextRun("Aceasta saptamana marcheaza tranzitia de la nivelurile inferioare ale stivei TCP/IP catre nivelul care asigura conectivitatea globala: nivelul retea. Vom explora mecanismele prin care pachetele de date pot traversa granitele retelelor locale si ajunge la destinatii aflate oriunde pe Internet.")] }),
      new Paragraph({ spacing: { before: 120 } }),
      
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Structura adreselor IPv4 si IPv6: format, clase istorice, notatie CIDR")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Calculul parametrilor retelei: adresa de retea, broadcast, interval de gazde valide")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Tehnici de partitionare: FLSM (subretele egale) si VLSM (alocare optimizata)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Header-ul IPv4 vs IPv6: campuri esentiale si diferente arhitecturale")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Simularea rutarii intr-un mediu virtual (Mininet): configurare, verificare, debugging")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("De ce conteaza")] }),
      new Paragraph({ children: [new TextRun("Adresarea IP reprezinta fundatia oricarei comunicatii pe Internet. Un programator care stapaneste aceste concepte poate:")] }),
      
      new Paragraph({ numbering: { reference: "numbered-1", level: 0 }, children: [new TextRun({ text: "Diagnostica probleme de conectivitate ", bold: true }), new TextRun("— intelegerea subnetting-ului ajuta la identificarea rapida a problemelor de rutare sau izolare a traficului")] }),
      new Paragraph({ numbering: { reference: "numbered-1", level: 0 }, children: [new TextRun({ text: "Proiecta infrastructuri scalabile ", bold: true }), new TextRun("— planificarea corecta a spatiului de adrese previne epuizarea si conflictele")] }),
      new Paragraph({ numbering: { reference: "numbered-1", level: 0 }, children: [new TextRun({ text: "Automatiza deployment-uri cloud ", bold: true }), new TextRun("— VPC-urile AWS, Azure, GCP necesita configurarea explicita a CIDR-urilor")] }),
      new Paragraph({ numbering: { reference: "numbered-1", level: 0 }, children: [new TextRun({ text: "Securiza aplicatiile ", bold: true }), new TextRun("— segmentarea retelei prin subretele izolate reduce suprafata de atac")] }),
      
      new Paragraph({ spacing: { before: 200 }, style: "InstructorNote", children: [
        new TextRun({ text: "💡 Nota for cadru didactic: ", bold: true }),
        new TextRun("Subliniati conexiunea cu realitatea profesionala — studentii vor intalni aceste concepte la interviuri tehnice si in primele saptamani de lucru. Pregatiti 2-3 exemple concrete din proiecte reale (e.g., configurarea unui VPC in AWS, debugging CIDR mismatch).")
      ] }),
      
      new Paragraph({ children: [new PageBreak()] }),
      
      // ═══════════════════════════════════════════════════════════════════
      // SECTION 2: PRERECHIZITE SI RECAPITULARE
      // ═══════════════════════════════════════════════════════════════════
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("2. Prerechizite si Recapitulare")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Din saptamanile anterioare")] }),
      
      new Table({
        columnWidths: [2500, 6500],
        rows: [
          new TableRow({
            tableHeader: true,
            children: [
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ children: [new TextRun({ text: "Saptamana", bold: true })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ children: [new TextRun({ text: "Concepte relevante for S5", bold: true })] })] })
            ]
          }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("S1–S2")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Modelele OSI si TCP/IP, incapsulare, PDU-uri")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("S3")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Programare socket: structuri sockaddr, AF_INET, bind()")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("S4")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Nivelul legatura de date: cadre Ethernet, adrese MAC")] })] })
          ] })
        ]
      }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 360 }, children: [new TextRun("Recapitulare expresa: operatii pe biti")] }),
      new Paragraph({ children: [new TextRun("Calculele CIDR se bazeaza pe operatii pe biti. Asigurati-va ca stapaniti:")] }),
      
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [
        new TextRun({ text: "AND (&): ", bold: true }), new TextRun("extrage partea de retea (IP & Mask = Network)")
      ] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [
        new TextRun({ text: "OR (|): ", bold: true }), new TextRun("calculeaza broadcast-ul (Network | Wildcard = Broadcast)")
      ] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [
        new TextRun({ text: "NOT (~): ", bold: true }), new TextRun("inverseaza masca for a obtine wildcard mask")
      ] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 240 }, children: [new TextRun("Tabel de conversie rapida")] }),
      
      new Table({
        columnWidths: [1500, 2500, 2500, 2500],
        rows: [
          new TableRow({
            tableHeader: true,
            children: [
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Zecimal", bold: true })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Binar", bold: true })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Ca masca", bold: true })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Prefix", bold: true })] })] })
            ]
          }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("255")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("11111111")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("8 biti retea")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("/8 per octet")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("128")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("10000000")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("1 bit retea")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("Imparte in 2")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("192")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("11000000")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("2 biti retea")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("Imparte in 4")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("240")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("11110000")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("4 biti retea")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("Imparte in 16")] })] })
          ] })
        ]
      }),
      
      new Paragraph({ spacing: { before: 240 }, style: "InstructorNote", children: [
        new TextRun({ text: "⏱️ Timing: ", bold: true }),
        new TextRun("Alocati maxim 10 minute for recapitulare. Daca studentii au dificultati cu conversiile, recomandati exercitii suplimentare acasa si continuati cu materia.")
      ] }),
      
      new Paragraph({ children: [new PageBreak()] }),
      
      // ═══════════════════════════════════════════════════════════════════
      // SECTION 3: CURS
      // ═══════════════════════════════════════════════════════════════════
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("3. Lecture: Nivelul Retea")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.1 Rolul nivelului retea")] }),
      new Paragraph({ children: [new TextRun("Nivelul retea (Layer 3) asigura doua functii fundamentale:")] }),
      
      new Paragraph({ numbering: { reference: "numbered-2", level: 0 }, children: [
        new TextRun({ text: "Adresarea logica ", bold: true }), 
        new TextRun("— identificarea unica a fiecarui dispozitiv conectat la retea prin adrese IP")
      ] }),
      new Paragraph({ numbering: { reference: "numbered-2", level: 0 }, children: [
        new TextRun({ text: "Rutarea ", bold: true }), 
        new TextRun("— determinarea caii optime for transmiterea pachetelor intre retele diferite")
      ] }),
      
      new Paragraph({ spacing: { before: 160 }, children: [
        new TextRun({ text: "Analogie: ", italics: true }),
        new TextRun("Daca adresa MAC este numarul de serie al unui telefon, adresa IP este numarul de telefon - poate fi schimbat, portat intre operatori si permite rutare ierarhica (prefix tara, prefix oras, numar local).")
      ] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.2 Structura adreselor IPv4")] }),
      new Paragraph({ children: [new TextRun("O adresa IPv4 consta din 32 de biti, reprezentati in format \"dotted-decimal\" — patru numere zecimale (0–255) separate prin puncte.")] }),
      
      new Paragraph({ style: "CodeBlock", spacing: { before: 120 }, children: [new TextRun("Exemplu: 192.168.1.10 = 11000000.10101000.00000001.00001010")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Adrese speciale")] }),
      
      new Table({
        columnWidths: [2500, 4500, 2000],
        rows: [
          new TableRow({
            tableHeader: true,
            children: [
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ children: [new TextRun({ text: "Interval", bold: true })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ children: [new TextRun({ text: "Scop", bold: true })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ children: [new TextRun({ text: "RFC", bold: true })] })] })
            ]
          }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("10.0.0.0/8")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Adrese private (retele mari)")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("RFC 1918")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("172.16.0.0/12")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Adrese private (retele medii)")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("RFC 1918")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("192.168.0.0/16")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Adrese private (retele mici)")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("RFC 1918")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("127.0.0.0/8")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Loopback (localhost)")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("RFC 1122")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("169.254.0.0/16")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Link-local (APIPA)")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("RFC 3927")] })] })
          ] })
        ]
      }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.3 CIDR si Subnetting")] }),
      new Paragraph({ children: [new TextRun("CIDR (Classless Inter-Domain Routing) a inlocuit sistemul claselor, permitand prefixe de lungime variabila.")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Formule esentiale")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("Total adrese = 2^(32 - prefix)")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("Hosturi valizi = 2^(32 - prefix) - 2")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("Network address = IP AND subnet_mask")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("Broadcast = IP OR wildcard_mask")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Exemplu rezolvat")] }),
      new Paragraph({ children: [new TextRun({ text: "Problema: ", bold: true }), new TextRun("Analizati 172.16.50.12/21")] }),
      
      new Paragraph({ style: "CodeBlock", spacing: { before: 80 }, children: [new TextRun("Prefix /21 → Masca: 255.255.248.0")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("172.16.50.12 AND 255.255.248.0 = 172.16.48.0 (Network)")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("Broadcast: 172.16.55.255")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("Hosturi: 172.16.48.1 — 172.16.55.254 (2046 adrese)")] }),
      
      new Paragraph({ spacing: { before: 200 }, style: "InstructorNote", children: [
        new TextRun({ text: "🎯 Mini-demo la curs: ", bold: true }),
        new TextRun("Rulati python/apps/subnet_calc.py cu adresa 172.16.50.12/21 si proiectati rezultatul. Explicati pas cu pas conversia binara.")
      ] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.4 FLSM vs VLSM")] }),
      
      new Table({
        columnWidths: [1500, 3750, 3750],
        rows: [
          new TableRow({
            tableHeader: true,
            children: [
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Aspect", bold: true })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "FLSM", bold: true })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "VLSM", bold: true })] })] })
            ]
          }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Descriere")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Toate subretelele au acelasi prefix")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Prefixe diferite, adaptate necesitatilor")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Eficienta")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Scazuta — risipa de adrese")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Ridicata — alocare optimizata")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Complexitate")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Simpla, usor de planificat")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Necesita planificare atenta")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Utilizare")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Retele uniforme, simple")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Retele enterprise, cloud VPC")] })] })
          ] })
        ]
      }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.5 IPv6: De ce si cum")] }),
      new Paragraph({ children: [new TextRun("IPv6 rezolva limitarile IPv4 prin:")] }),
      
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Spatiu extins: ", bold: true }), new TextRun("128 biti = 3.4 × 10³⁸ adrese")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Header simplificat: ", bold: true }), new TextRun("mai putine campuri, procesare mai rapida")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Auto-configurare (SLAAC): ", bold: true }), new TextRun("nu necesita DHCP for adresare")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Reguli de comprimare IPv6")] }),
      new Paragraph({ numbering: { reference: "numbered-3", level: 0 }, children: [new TextRun("Eliminarea zerourilor de inceput din fiecare grup")] }),
      new Paragraph({ numbering: { reference: "numbered-3", level: 0 }, children: [new TextRun("Inlocuirea unei secvente continue de grupuri 0000 cu ::")] }),
      new Paragraph({ numbering: { reference: "numbered-3", level: 0 }, children: [new TextRun(":: poate fi folosit o singura data per adresa")] }),
      
      new Paragraph({ style: "CodeBlock", spacing: { before: 120 }, children: [new TextRun("2001:0db8:0000:0000:0000:0000:0000:0001 → 2001:db8::1")] }),
      
      new Paragraph({ children: [new PageBreak()] }),
      
      // ═══════════════════════════════════════════════════════════════════
      // SECTION 4: SEMINAR
      // ═══════════════════════════════════════════════════════════════════
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("4. Seminar: Ghid Practic")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.1 Parcurs pas cu pas")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Partea A: Analiza CIDR cu Python")] }),
      new Paragraph({ children: [new TextRun({ text: "Timp estimat: ", italics: true }), new TextRun("15 minute")] }),
      
      new Paragraph({ spacing: { before: 120 }, children: [new TextRun({ text: "Pas 1: ", bold: true }), new TextRun("Navigati in directorul exercitiilor")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("cd python/exercises")] }),
      
      new Paragraph({ spacing: { before: 100 }, children: [new TextRun({ text: "Pas 2: ", bold: true }), new TextRun("Analizati o adresa CIDR")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("python ex_5_01_cidr_flsm.py analyze 172.16.50.12/21")] }),
      
      new Paragraph({ spacing: { before: 100 }, children: [new TextRun({ text: "Rezultat asteptat: ", bold: true })] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("Network: 172.16.48.0/21")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("Netmask: 255.255.248.0")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("Broadcast: 172.16.55.255")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("Host range: 172.16.48.1 - 172.16.55.254")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("Valid hosts: 2046")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Partea B: Partitionare FLSM")] }),
      new Paragraph({ children: [new TextRun({ text: "Timp estimat: ", italics: true }), new TextRun("15 minute")] }),
      
      new Paragraph({ spacing: { before: 120 }, children: [new TextRun({ text: "Scenariu: ", bold: true }), new TextRun("Impartiti 10.0.0.0/8 in 4 subretele egale")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("python ex_5_01_cidr_flsm.py flsm 10.0.0.0/8 4")] }),
      
      new Paragraph({ spacing: { before: 100 }, children: [new TextRun({ text: "Interpretare: ", bold: true }), new TextRun("Fiecare subretea primeste 2³⁰ - 2 = 1.073.741.822 gazde. Prefixul creste de la /8 la /10 (adaugam 2 biti for a distinge 4 subretele).")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Partea C: Planificare VLSM")] }),
      new Paragraph({ children: [new TextRun({ text: "Timp estimat: ", italics: true }), new TextRun("20 minute")] }),
      
      new Paragraph({ spacing: { before: 120 }, children: [new TextRun({ text: "Scenariu: ", bold: true }), new TextRun("Alocati 192.168.1.0/24 for departamente cu nevoi diferite: IT (50), HR (20), Finance (10), Management (5), legaturi WAN (2×2)")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("python ex_5_02_vlsm_ipv6.py vlsm 192.168.1.0/24 50 20 10 5 2 2")] }),
      
      new Paragraph({ spacing: { before: 100 }, children: [new TextRun({ text: "Principiu VLSM: ", bold: true }), new TextRun("Sortam descrescator dupa numarul de gazde si alocam de la cel mai mare la cel mai mic.")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.2 Interpretarea rezultatelor")] }),
      new Paragraph({ children: [new TextRun("La fiecare pas, verificati:")] }),
      
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Adresa de retea sa fie corect calculata (biti de host = 0)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Broadcast-ul sa fie ultimul din bloc")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Subretelele sa nu se suprapuna")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Eficienta alocarii (adrese utilizate vs disponibile)")] }),
      
      new Paragraph({ spacing: { before: 200 }, style: "InstructorNote", children: [
        new TextRun({ text: "⚠️ Greseala frecventa: ", bold: true }),
        new TextRun("Studentii uita sa scada 2 din total for adresele de retea si broadcast. Subliniati de ce prima si ultima adresa nu pot fi atribuite gazdelor.")
      ] }),
      
      new Paragraph({ children: [new PageBreak()] }),
      
      // ═══════════════════════════════════════════════════════════════════
      // SECTION 5: LABORATOR
      // ═══════════════════════════════════════════════════════════════════
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("5. Laboratory Practic")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.1 Experiment: Topologie Mininet cu rutare")] }),
      
      new Paragraph({ children: [new TextRun({ text: "Obiectiv: ", bold: true }), new TextRun("Construiti o retea cu 2 subretele si un router, apoi verificati conectivitatea.")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Pas 0: Verificare mediu")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("make verify")] }),
      new Paragraph({ children: [new TextRun("Toate testele trebuie sa treaca inainte de a continua.")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Pas 1: Pornirea topologiei de baza")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("cd mininet")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("sudo python3 topo_5_base.py")] }),
      
      new Paragraph({ spacing: { before: 100 }, children: [new TextRun({ text: "Topologie: ", bold: true })] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("h1 (10.0.1.10/24) -- [s1] -- r1 -- [s2] -- h2 (10.0.2.10/24)")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Pas 2: Testare conectivitate")] }),
      new Paragraph({ children: [new TextRun("Din CLI-ul Mininet:")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("mininet> h1 ping -c 3 h2")] }),
      
      new Paragraph({ spacing: { before: 100 }, children: [new TextRun({ text: "Rezultat asteptat: ", bold: true }), new TextRun("0% packet loss")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Pas 3: Analiza rutelor")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("mininet> h1 ip route")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("mininet> r1 ip route")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.2 Experiment: VLSM cu topologie extinsa")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("sudo python3 topo_5_extended.py")] }),
      new Paragraph({ children: [new TextRun("Aceasta topologie include 3 subretele cu prefixe diferite, demonstrand VLSM in practica.")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.3 Extensii optionale")] }),
      
      new Paragraph({ numbering: { reference: "numbered-4", level: 0 }, children: [new TextRun({ text: "Captura pachete: ", bold: true }), new TextRun("mininet> h1 tcpdump -i h1-eth0 -c 10 -w /tmp/h1_capture.pcap &")] }),
      new Paragraph({ numbering: { reference: "numbered-4", level: 0 }, children: [new TextRun({ text: "Test debit: ", bold: true }), new TextRun("Rulati iperf intre h1 si h2")] }),
      new Paragraph({ numbering: { reference: "numbered-4", level: 0 }, children: [new TextRun({ text: "IPv6 dual-stack: ", bold: true }), new TextRun("Adaugati adrese IPv6 si testati conectivitatea")] }),
      
      new Paragraph({ children: [new PageBreak()] }),
      
      // ═══════════════════════════════════════════════════════════════════
      // SECTION 6: GRESELI FRECVENTE
      // ═══════════════════════════════════════════════════════════════════
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("6. Greseli Frecvente si Debugging")] }),
      
      new Table({
        columnWidths: [3000, 3000, 3000],
        rows: [
          new TableRow({
            tableHeader: true,
            children: [
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.warningBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ children: [new TextRun({ text: "Simptom", bold: true })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.warningBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ children: [new TextRun({ text: "Cauza probabila", bold: true })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.warningBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ children: [new TextRun({ text: "Solutie", bold: true })] })] })
            ]
          }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("ping: Network unreachable")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Lipsa ruta catre destinatie sau gateway incorect")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Verificati ip route si default gateway")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Subretele se suprapun")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Greseala la calculul prefixului sau alocarii")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Recalculati de la zero, verificati suprapunerea")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("IP forwarding dezactivat")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Routerul nu transmite pachete intre interfete")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("sysctl net.ipv4.ip_forward=1")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Mininet nu porneste")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Resurse blocate de sesiune anterioara")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("make clean sau sudo mn -c")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Numar incorect de gazde")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Nu s-au scazut adresele de retea/broadcast")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Hosturi = 2^(32-prefix) - 2")] })] })
          ] })
        ]
      }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 360 }, children: [new TextRun("Comenzi utile for debugging")] }),
      
      new Paragraph({ style: "CodeBlock", children: [new TextRun("# Verificare configuratie IP")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("ip addr show")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("# Afisare tabel de rutare")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("ip route")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("# Captura live pachete ICMP")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("sudo tcpdump -i any icmp -n")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("# Verificare IP forwarding")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("sysctl net.ipv4.ip_forward")] }),
      
      new Paragraph({ children: [new PageBreak()] }),
      
      // ═══════════════════════════════════════════════════════════════════
      // SECTION 7: EXERCITII
      // ═══════════════════════════════════════════════════════════════════
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("7. Exercitii de Consolidare")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Exercitiul S5.1: Analiza CIDR (10 puncte)")] }),
      new Paragraph({ children: [new TextRun({ text: "Cerinta: ", bold: true }), new TextRun("Pentru adresa 10.45.128.200/18, determinati:")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Adresa de retea si masca in format dotted-decimal")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Adresa de broadcast")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Intervalul de gazde valide si numarul lor")] }),
      new Paragraph({ children: [new TextRun({ text: "Verificare: ", italics: true }), new TextRun("python ex_5_01_cidr_flsm.py analyze 10.45.128.200/18")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Exercitiul S5.2: Partitionare FLSM (10 puncte)")] }),
      new Paragraph({ children: [new TextRun({ text: "Cerinta: ", bold: true }), new TextRun("Impartiti 172.30.0.0/20 in 32 de subretele egale. Listati primele 5 subretele cu adresa de retea, broadcast si interval gazde.")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Exercitiul S5.3: Planificare VLSM (15 puncte)")] }),
      new Paragraph({ children: [new TextRun({ text: "Scenariu: ", bold: true }), new TextRun("Compania TechCorp are sediu cu 4 departamente:")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Development: 100 statii")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Sales: 45 statii")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("HR: 15 statii")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Server Room: 10 servere")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("2 legaturi WAN (cate 2 adrese fiecare)")] }),
      new Paragraph({ children: [new TextRun({ text: "Cerinta: ", bold: true }), new TextRun("Proiectati schema VLSM pornind de la 192.168.50.0/24. Calculati eficienta alocarii.")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Exercitiul S5.4: Comprimare IPv6 (10 puncte)")] }),
      new Paragraph({ children: [new TextRun({ text: "Cerinta: ", bold: true }), new TextRun("Comprimati la forma minimala:")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("a) 2001:0db8:0000:0042:0000:0000:0000:8a2e")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("b) fe80:0000:0000:0000:0000:0000:0000:0001")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("c) 0000:0000:0000:0000:0000:ffff:c0a8:0164")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Exercitiul S5.5: Expandare IPv6 (10 puncte)")] }),
      new Paragraph({ children: [new TextRun({ text: "Cerinta: ", bold: true }), new TextRun("Expandati la forma completa:")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("a) 2001:db8::1")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("b) fe80::1")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("c) ::ffff:192.168.1.100")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Exercitiul S5.6 — Challenge (15 puncte)")] }),
      new Paragraph({ children: [new TextRun({ text: "Scenariu avansat: ", bold: true }), new TextRun("O universitate primeste blocul IPv6 2001:db8:acad::/48. Proiectati o schema de adresare care sa aloce:")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Cate un /64 for fiecare din cele 8 facultati")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("4 subretele /64 for infrastructura (servere, management)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Rezervati 4 subretele /64 for extindere viitoare")] }),
      new Paragraph({ children: [new TextRun({ text: "Cerinta: ", bold: true }), new TextRun("Prezentati planul de alocare si justificati conventiile de numerotare.")] }),
      
      new Paragraph({ children: [new PageBreak()] }),
      
      // ═══════════════════════════════════════════════════════════════════
      // SECTION 8: REFLECTIE
      // ═══════════════════════════════════════════════════════════════════
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("8. Mini-Reflectie")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Ce am invatat")] }),
      new Paragraph({ children: [new TextRun("Dupa parcurgerea acestei saptamani, ar trebui sa puteti raspunde la:")] }),
      
      new Paragraph({ numbering: { reference: "numbered-5", level: 0 }, children: [new TextRun("Care este diferenta fundamentala dintre o adresa MAC si o adresa IP?")] }),
      new Paragraph({ numbering: { reference: "numbered-5", level: 0 }, children: [new TextRun("De ce folosim CIDR in loc de sistemul claselor?")] }),
      new Paragraph({ numbering: { reference: "numbered-5", level: 0 }, children: [new TextRun("Cand este preferabil VLSM fata de FLSM?")] }),
      new Paragraph({ numbering: { reference: "numbered-5", level: 0 }, children: [new TextRun("Care sunt principalele avantaje ale IPv6?")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Unde se foloseste in practica")] }),
      
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Cloud computing: ", bold: true }), new TextRun("VPC design in AWS/Azure/GCP necesita planificare CIDR")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Containerizare: ", bold: true }), new TextRun("Kubernetes foloseste subretele for Pods si Services")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Securitate: ", bold: true }), new TextRun("Firewalls si ACL-uri opereaza pe prefixe CIDR")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "DevOps/IaC: ", bold: true }), new TextRun("Terraform, Ansible gestioneaza adrese IP programatic")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Legatura cu rolul de programator")] }),
      new Paragraph({ children: [new TextRun("Programarea de retea moderna presupune configurarea corecta a bind addresses, intelegerea NAT traversal si debugging-ul problemelor de conectivitate. Cunoasterea temeinica a adresarii IP transforma un programator competent intr-unul care poate lucra eficient cu infrastructura distribuita.")] }),
      
      new Paragraph({ children: [new PageBreak()] }),
      
      // ═══════════════════════════════════════════════════════════════════
      // SECTION 9: CONTRIBUTIA LA PROIECT
      // ═══════════════════════════════════════════════════════════════════
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("9. Contributia Saptamanii la Proiect")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Artefact livrabil")] }),
      new Paragraph({ children: [new TextRun({ text: "Deadline: ", bold: true }), new TextRun("Pana la inceputul saptamanii 6")] }),
      
      new Paragraph({ spacing: { before: 160 }, children: [new TextRun({ text: "Cerinta for echipa: ", bold: true }), new TextRun("Adaugati la proiect o schema de adresare care include:")] }),
      
      new Paragraph({ numbering: { reference: "numbered-6", level: 0 }, children: [new TextRun("Minimum 3 subretele distincte (pot fi FLSM sau VLSM)")] }),
      new Paragraph({ numbering: { reference: "numbered-6", level: 0 }, children: [new TextRun("Justificarea alegerii prefixelor (de ce aceste marimi?)")] }),
      new Paragraph({ numbering: { reference: "numbered-6", level: 0 }, children: [new TextRun("O diagrama de topologie (poate fi ASCII art sau imagine)")] }),
      new Paragraph({ numbering: { reference: "numbered-6", level: 0 }, children: [new TextRun("Optional: script Mininet functional care demonstreaza conectivitatea")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Criterii de evaluare")] }),
      
      new Table({
        columnWidths: [5000, 2000, 2000],
        rows: [
          new TableRow({
            tableHeader: true,
            children: [
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ children: [new TextRun({ text: "Criteriu", bold: true })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Punctaj", bold: true })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Bonus", bold: true })] })] })
            ]
          }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Schema contine minim 3 subretele fara suprapunere")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("30%")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("—")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Justificarea alegerilor este coerenta")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("25%")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("—")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Topologia este clara si completa")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("25%")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("—")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Script Mininet functional")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("20%")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("+10%")] })] })
          ] })
        ]
      }),
      
      new Paragraph({ children: [new PageBreak()] }),
      
      // ═══════════════════════════════════════════════════════════════════
      // SECTION 10: BIBLIOGRAFIE
      // ═══════════════════════════════════════════════════════════════════
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("10. Bibliografie si Resurse")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Lucrari cu DOI")] }),
      
      new Table({
        columnWidths: [500, 5500, 3000],
        rows: [
          new TableRow({
            tableHeader: true,
            children: [
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "#", bold: true })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ children: [new TextRun({ text: "Referinta", bold: true })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ children: [new TextRun({ text: "DOI", bold: true })] })] })
            ]
          }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("1")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Kurose, J. F., & Ross, K. W. (2017). Computer Networking: A Top-Down Approach (7th ed.). Pearson.")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "—", italics: true })] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("2")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Rhodes, B., & Goetzen, J. (2014). Foundations of Python Network Programming (3rd ed.). Apress.")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("10.1007/978-1-4302-5855-1")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("3")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Lantz, B., et al. (2010). A Network in a Laptop: Rapid Prototyping for SDN. HotNets.")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("10.1145/1868447.1868466")] })] })
          ] })
        ]
      }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 360 }, children: [new TextRun("Standarde si specificatii")] }),
      
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "RFC 791 ", bold: true }), new TextRun("— Internet Protocol (IPv4)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "RFC 1918 ", bold: true }), new TextRun("— Address Allocation for Private Internets")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "RFC 4291 ", bold: true }), new TextRun("— IP Version 6 Addressing Architecture")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "RFC 4632 ", bold: true }), new TextRun("— Classless Inter-Domain Routing (CIDR)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "RFC 8200 ", bold: true }), new TextRun("— Internet Protocol, Version 6 (IPv6)")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 360 }, children: [new TextRun("Resurse online recomandate")] }),
      
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Mininet Walkthrough: http://mininet.org/walkthrough/")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Python ipaddress module: https://docs.python.org/3/library/ipaddress.html")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("IANA IPv4 Special-Purpose Registry: https://www.iana.org/assignments/iana-ipv4-special-registry")] }),
      
      new Paragraph({ spacing: { before: 720 } }),
      new Paragraph({ 
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "— Sfarsit document —", size: 20, color: "7B7D7D", italics: true })]
      }),
      new Paragraph({ 
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Revolvix&Hypotheticalandrei", size: 16, color: "BDC3C7" })]
      })
    ]
  }]
});

// Save the document
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/home/claude/starterkit_s5/docs/Lecture5_Seminar5_Laboratory5.docx", buffer);
  console.log("✓ Document saved: Lecture5_Seminar5_Laboratory5.docx");
});
