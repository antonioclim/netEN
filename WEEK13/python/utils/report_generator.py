#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Report Generator - Generator of Rapoarte for Security
==========================================================

Week 13 - IoT and Security in Computer Networks
Academia of Studii Economice - CSIE

Scopul modulului:
    Generationa of professional reports from exercise results
    of security (scanari, checkri vulnerabilities, captures traffic).

Formate suportate:
    - Markdown (.md) - for documentatie
    - HTML (.html) - for prezentare
    - JSON (.json) - for processing automatizata
    - Text (.txt) - for console/log

Author: Teaching Staff ASE-CSIE
Data: 2025
"""

import json 
import os 
from datetime import datetime 
from typing import Dict ,List ,Any ,Optional 
from dataclasses import dataclass ,field 
from enum import Enum 
import html 


# ============================================================================
# ENUMERARI SI DATA STRUCTURES
# ============================================================================

class ReportFormat (Enum ):
    """Available formats for reports."""
    MARKDOWN ="md"
    HTML ="html"
    JSON ="json"
    TEXT ="txt"


class Severity (Enum ):
    """Niveluri of severitate for vulnerabilities."""
    CRITICAL =(4 ,"🔴","#dc3545")
    HIGH =(3 ,"🟠","#fd7e14")
    MEDIUM =(2 ,"🟡","#ffc107")
    LOW =(1 ,"🟢","#28a745")
    INFO =(0 ,"🔵","#17a2b8")

    def __init__ (self ,level :int ,emoji :str ,color :str ):
        self .level =level 
        self .emoji =emoji 
        self .color =color 


@dataclass 
class Finding :
    """
    Represent o discovery (vulnerability, port open, etc.).
    
    Attributes:
        title: Titlul descriptiv
        severity: Nivelul of severitate
        description: Dewritere detaliata
        target: Tinta afectata (IP:port, service, etc.)
        remediation: Recommandri for remediere
        references: Link-uri catre documentatie
        evidence: Dovezi (output, screenshot path, etc.)
    """
    title :str 
    severity :Severity 
    description :str 
    target :str =""
    remediation :str =""
    references :List [str ]=field (default_factory =list )
    evidence :str =""
    cvss_score :Optional [float ]=None 
    cve_id :Optional [str ]=None 


@dataclass 
class ScanResult :
    """
    Resultul unei scanari of ports or services.
    
    Attributes:
        host: IP address or hostname
        port: Port number
        state: Starea (open, closed, filtered)
        service: Servicel detectat
        version: Versiunea servicelui
        banner: Banner-ul raw
    """
    host :str 
    port :int 
    state :str 
    service :str =""
    version :str =""
    banner :str =""


@dataclass 
class ReportMetadata :
    """
    Metadate for report.
    
    Attributes:
        title: Titlul raportului
        author: Autorul/echipa
        date: Data generarii
        target_scope: Scopul testarii
        methodology: Metodologia utilizata
    """
    title :str 
    author :str ="Student ASE-CSIE"
    date :str =field (default_factory =lambda :datetime .now ().strftime ("%Y-%m-%d %H:%M"))
    target_scope :str =""
    methodology :str ="Network Security Assessment"
    executive_summary :str =""


    # ============================================================================
    # CLASA PRINCIPALA - REPORT GENERATOR
    # ============================================================================

class ReportGenerator :
    """
    Security activities report generator.
    
    Arhitectura:
        - Colectare date (findings, scan results, statistici)
        - Template engine simple for formatare
        - Export in multiple formate
    
    Usage:
        >>> gen = ReportGenerator("Report Security S13")
        >>> gen.add_finding(Finding(...))
        >>> gen.add_scan_result(ScanResult(...))
        >>> gen.generate("report.html", ReportFormat.HTML)
    """

    def __init__ (self ,title :str ,author :str ="Student ASE-CSIE"):
        """
        Initialize the report generator.
        
        Args:
            title: Titlul raportului
            author: Numele autorului or echipei
        """
        self .metadata =ReportMetadata (title =title ,author =author )
        self .findings :List [Finding ]=[]
        self .scan_results :List [ScanResult ]=[]
        self .raw_data :Dict [str ,Any ]={}
        self .sections :List [Dict [str ,str ]]=[]

        # ========================================================================
        # ADAUGARE CONTINUT
        # ========================================================================

    def set_executive_summary (self ,summary :str ):
        """Set rezumatul executiv."""
        self .metadata .executive_summary =summary 

    def set_scope (self ,scope :str ):
        """Set scopul evaluarii."""
        self .metadata .target_scope =scope 

    def add_finding (self ,finding :Finding ):
        """
        Add o discovery/vulnerability at report.
        
        Args:
            finding: Obiect Finding with detalii
        """
        self .findings .append (finding )

    def add_scan_result (self ,result :ScanResult ):
        """
        Add resultul unei scanari.
        
        Args:
            result: Obiect ScanResult
        """
        self .scan_results .append (result )

    def add_scan_results_bulk (self ,results :List [Dict ]):
        """
        Add results of scanning in bulk from format dict.
        
        Args:
            results: Lista of dictionare with results
        """
        for r in results :
            self .scan_results .append (ScanResult (
            host =r .get ("host",""),
            port =r .get ("port",0 ),
            state =r .get ("state","unknown"),
            service =r .get ("service",""),
            version =r .get ("version",""),
            banner =r .get ("banner","")
            ))

    def add_section (self ,title :str ,content :str ):
        """
        Add o sectiune personalizata.
        
        Args:
            title: Titlul sectiunii
            content: Contentul (suporta Markdown)
        """
        self .sections .append ({"title":title ,"content":content })

    def add_raw_data (self ,key :str ,data :Any ):
        """
        Add date raw for export JSON.
        
        Args:
            key: Identificator date
            data: Datele (must sa fie JSON serializabile)
        """
        self .raw_data [key ]=data 

    def load_from_json (self ,filepath :str ):
        """
        Load date dintr-un file JSON (output of at alte exercises).
        
        Args:
            filepath: Calea catre fisierul JSON
        """
        try :
            with open (filepath ,'r',encoding ='utf-8')as f :
                data =json .load (f )

                # Processing automata on baza structurii
            if "scan_results"in data :
                self .add_scan_results_bulk (data ["scan_results"])

            if "vulnerabilities"in data :
                for v in data ["vulnerabilities"]:
                    self .add_finding (Finding (
                    title =v .get ("name","Unknown"),
                    severity =Severity [v .get ("severity","INFO").upper ()],
                    description =v .get ("description",""),
                    target =v .get ("target",""),
                    remediation =v .get ("remediation",""),
                    cvss_score =v .get ("cvss_score"),
                    cve_id =v .get ("cve_id")
                    ))

                    # Stocare raw for referinta
            self .raw_data ["imported"]=data 

        except Exception as e :
            print (f"[!] Error at incarcarea JSON: {e}")

            # ========================================================================
            # GENERATION RAPOARTE
            # ========================================================================

    def generate (self ,output_path :str ,format :ReportFormat =ReportFormat .HTML ):
        """
        Generate raportul in formatul specificat.
        
        Args:
            output_path: Calea for fisierul output
            format: Formatul dorit (HTML, Markdown, JSON, Text)
        """
        generators ={
        ReportFormat .HTML :self ._generate_html ,
        ReportFormat .MARKDOWN :self ._generate_markdown ,
        ReportFormat .JSON :self ._generate_json ,
        ReportFormat .TEXT :self ._generate_text ,
        }

        content =generators [format ]()

        with open (output_path ,'w',encoding ='utf-8')as f :
            f .write (content )

        print (f"[✓] Report generated: {output_path}")
        return output_path 

        # ========================================================================
        # GENERATION HTML
        # ========================================================================

    def _generate_html (self )->str :
        """Generate report HTML complete with styling."""

        # Calculare statistici
        stats =self ._calculate_statistics ()

        html_content =f"""<!DOCTYPE html>
<html lang="ro">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(self.metadata.title)}</title>
    <style>
        :root {{
            --primary: #2c3e50;
            --secondary: #3498db;
            --success: #28a745;
            --warning: #ffc107;
            --danger: #dc3545;
            --info: #17a2b8;
            --light: #f8f9fa;
            --dark: #343a40;
        }}
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: var(--dark);
            background: var(--light);
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: 30px;
        }}
        
        .header h1 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        
        .header .meta {{
            opacity: 0.9;
            font-size: 0.95em;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        section {{
            margin-bottom: 30px;
        }}
        
        h2 {{
            color: var(--primary);
            border-bottom: 2px solid var(--secondary);
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        
        h3 {{
            color: var(--secondary);
            margin: 15px 0 10px;
        }}
        
        /* Stats Cards */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: var(--light);
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid var(--secondary);
        }}
        
        .stat-card.critical {{ border-left-color: var(--danger); }}
        .stat-card.high {{ border-left-color: #fd7e14; }}
        .stat-card.medium {{ border-left-color: var(--warning); }}
        .stat-card.low {{ border-left-color: var(--success); }}
        
        .stat-card .number {{
            font-size: 2.5em;
            font-weight: bold;
            color: var(--primary);
        }}
        
        .stat-card .label {{
            color: #666;
            font-size: 0.9em;
        }}
        
        /* Findings */
        .finding {{
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            margin-bottom: 15px;
            overflow: hidden;
        }}
        
        .finding-header {{
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
        }}
        
        .finding-header:hover {{
            background: var(--light);
        }}
        
        .finding.critical .finding-header {{ border-left: 4px solid var(--danger); }}
        .finding.high .finding-header {{ border-left: 4px solid #fd7e14; }}
        .finding.medium .finding-header {{ border-left: 4px solid var(--warning); }}
        .finding.low .finding-header {{ border-left: 4px solid var(--success); }}
        .finding.info .finding-header {{ border-left: 4px solid var(--info); }}
        
        .severity-badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            color: white;
        }}
        
        .severity-badge.critical {{ background: var(--danger); }}
        .severity-badge.high {{ background: #fd7e14; }}
        .severity-badge.medium {{ background: var(--warning); color: var(--dark); }}
        .severity-badge.low {{ background: var(--success); }}
        .severity-badge.info {{ background: var(--info); }}
        
        .finding-body {{
            padding: 0 20px 20px;
            display: none;
        }}
        
        .finding.expanded .finding-body {{
            display: block;
        }}
        
        .finding-body p {{
            margin-bottom: 10px;
        }}
        
        .finding-body .label {{
            font-weight: bold;
            color: var(--primary);
        }}
        
        .evidence {{
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 4px;
            font-family: 'Consolas', monospace;
            font-size: 0.9em;
            overflow-x: auto;
            white-space: pre-wrap;
        }}
        
        /* Scan Results Table */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        
        th {{
            background: var(--primary);
            color: white;
            font-weight: 600;
        }}
        
        tr:hover {{
            background: var(--light);
        }}
        
        .state-open {{
            color: var(--success);
            font-weight: bold;
        }}
        
        .state-closed {{
            color: var(--danger);
        }}
        
        .state-filtered {{
            color: var(--warning);
        }}
        
        /* Footer */
        .footer {{
            background: var(--dark);
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 0.9em;
        }}
        
        /* Print styles */
        @media print {{
            body {{ background: white; }}
            .container {{ box-shadow: none; }}
            .finding-body {{ display: block !important; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{html.escape(self.metadata.title)}</h1>
            <div class="meta">
                <span>Author: {html.escape(self.metadata.author)}</span> |
                <span>Data: {html.escape(self.metadata.date)}</span> |
                <span>Metodologie: {html.escape(self.metadata.methodology)}</span>
            </div>
        </div>
        
        <div class="content">
            <!-- Executive Summary -->
            {self._html_executive_summary()}
            
            <!-- Statistics -->
            {self._html_statistics(stats)}
            
            <!-- Findings -->
            {self._html_findings()}
            
            <!-- Scan Results -->
            {self._html_scan_results()}
            
            <!-- Custom Sections -->
            {self._html_custom_sections()}
        </div>
        
        <div class="footer">
            <p>Generat automat of Report Generator - ASE-CSIE Week 13</p>
            <p>© {datetime.now().year} Academia of Studii Economice Bucuresti</p>
        </div>
    </div>
    
    <script>
        // Toggle finding details
        document.querySelectorAll('.finding-header').forEach(header => {{
            header.addEventListener('click', () => {{
                header.parentElement.classList.toggle('expanded');
            }});
        }});
    </script>
</body>
</html>"""

        return html_content 

    def _html_executive_summary (self )->str :
        """Generate sectiunea Executive Summary."""
        if not self .metadata .executive_summary :
            return ""

        return f"""
            <section>
                <h2>Rezumat Executiv</h2>
                <p>{html.escape(self.metadata.executive_summary)}</p>
                {f'<p><strong>Scop:</strong> {html.escape(self.metadata.target_scope)}</p>' if self.metadata.target_scope else ''}
            </section>
        """

    def _html_statistics (self ,stats :Dict )->str :
        """Generate cardurile with statistici."""
        return f"""
            <section>
                <h2>Statistici</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="number">{stats['total_findings']}</div>
                        <div class="label">Total Descoperiri</div>
                    </div>
                    <div class="stat-card critical">
                        <div class="number">{stats['by_severity'].get('CRITICAL', 0)}</div>
                        <div class="label">Critical</div>
                    </div>
                    <div class="stat-card high">
                        <div class="number">{stats['by_severity'].get('HIGH', 0)}</div>
                        <div class="label">High</div>
                    </div>
                    <div class="stat-card medium">
                        <div class="number">{stats['by_severity'].get('MEDIUM', 0)}</div>
                        <div class="label">Medium</div>
                    </div>
                    <div class="stat-card low">
                        <div class="number">{stats['by_severity'].get('LOW', 0)}</div>
                        <div class="label">Low</div>
                    </div>
                    <div class="stat-card">
                        <div class="number">{stats['open_ports']}</div>
                        <div class="label">Ports Opene</div>
                    </div>
                </div>
            </section>
        """

    def _html_findings (self )->str :
        """Generate sectiunea with descoperiri/vulnerabilities."""
        if not self .findings :
            return ""

            # Sorting after severitate (descrescator)
        sorted_findings =sorted (
        self .findings ,
        key =lambda f :f .severity .level ,
        reverse =True 
        )

        findings_html =""
        for f in sorted_findings :
            sev =f .severity .name .lower ()
            findings_html +=f"""
                <div class="finding {sev}">
                    <div class="finding-header">
                        <div>
                            <strong>{html.escape(f.title)}</strong>
                            {f' <small>({f.cve_id})</small>' if f.cve_id else ''}
                        </div>
                        <span class="severity-badge {sev}">{f.severity.name}</span>
                    </div>
                    <div class="finding-body">
                        <p><span class="label">Target:</span> {html.escape(f.target)}</p>
                        <p><span class="label">Dewritere:</span> {html.escape(f.description)}</p>
                        {f'<p><span class="label">CVSS Score:</span> {f.cvss_score}</p>' if f.cvss_score else ''}
                        {f'<p><span class="label">Remediere:</span> {html.escape(f.remediation)}</p>' if f.remediation else ''}
                        {f'<div class="label">Dovezi:</div><div class="evidence">{html.escape(f.evidence)}</div>' if f.evidence else ''}
                    </div>
                </div>
            """

        return f"""
            <section>
                <h2>Descoperiri ({len(self.findings)})</h2>
                {findings_html}
            </section>
        """

    def _html_scan_results (self )->str :
        """Generate tabelul with results scanning."""
        if not self .scan_results :
            return ""

        rows =""
        for r in self .scan_results :
            state_class =f"state-{r.state}"
            rows +=f"""
                <tr>
                    <td>{html.escape(r.host)}</td>
                    <td>{r.port}</td>
                    <td class="{state_class}">{r.state.upper()}</td>
                    <td>{html.escape(r.service)}</td>
                    <td>{html.escape(r.version)}</td>
                    <td><code>{html.escape(r.banner[:50]) if r.banner else '-'}</code></td>
                </tr>
            """

        return f"""
            <section>
                <h2>Results Scanning ({len(self.scan_results)})</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Host</th>
                            <th>Port</th>
                            <th>State</th>
                            <th>Service</th>
                            <th>Version</th>
                            <th>Banner</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </section>
        """

    def _html_custom_sections (self )->str :
        """Generate sectiuni personalizate."""
        if not self .sections :
            return ""

        sections_html =""
        for sec in self .sections :
        # Conversie simpla Markdown -> HTML for content
            content =html .escape (sec ["content"])
            content =content .replace ("\n\n","</p><p>")
            content =content .replace ("**","<strong>").replace ("**","</strong>")
            content =content .replace ("`","<code>").replace ("`","</code>")

            sections_html +=f"""
                <section>
                    <h2>{html.escape(sec['title'])}</h2>
                    <p>{content}</p>
                </section>
            """

        return sections_html 

        # ========================================================================
        # GENERATION MARKDOWN
        # ========================================================================

    def _generate_markdown (self )->str :
        """Generate report Markdown."""
        stats =self ._calculate_statistics ()

        md =f"""# {self.metadata.title}

**Author:** {self.metadata.author}  
**Data:** {self.metadata.date}  
**Metodologie:** {self.metadata.methodology}

---

## Rezumat Executiv

{self.metadata.executive_summary if self.metadata.executive_summary else '_Nu a fost furnizat un rezumat executiv._'}

{f'**Scop:** {self.metadata.target_scope}' if self.metadata.target_scope else ''}

---

## Statistici

| Metric | Value |
|--------|---------|
| Total Descoperiri | {stats['total_findings']} |
| Critical | {stats['by_severity'].get('CRITICAL', 0)} |
| High | {stats['by_severity'].get('HIGH', 0)} |
| Medium | {stats['by_severity'].get('MEDIUM', 0)} |
| Low | {stats['by_severity'].get('LOW', 0)} |
| Ports Opene | {stats['open_ports']} |

---

## Descoperiri

"""

        # Findings sortate
        for f in sorted (self .findings ,key =lambda x :x .severity .level ,reverse =True ):
            md +=f"""
### {f.severity.emoji} [{f.severity.name}] {f.title}

- **Target:** {f.target}
- **Dewritere:** {f.description}
{f'- **CVE:** {f.cve_id}' if f.cve_id else ''}
{f'- **CVSS Score:** {f.cvss_score}' if f.cvss_score else ''}
{f'- **Remediere:** {f.remediation}' if f.remediation else ''}

{f'**Dovezi:**' + chr(10) + '```' + chr(10) + f.evidence + chr(10) + '```' if f.evidence else ''}

"""

            # Scan results
        if self .scan_results :
            md +="""
---

## Results Scanning

| Host | Port | State | Service | Version |
|------|------|-------|----------|----------|
"""
            for r in self .scan_results :
                md +=f"| {r.host} | {r.port} | {r.state} | {r.service} | {r.version} |\n"

                # Custom sections
        for sec in self .sections :
            md +=f"""
---

## {sec['title']}

{sec['content']}

"""

        md +=f"""
---

_Raport generated automat of Report Generator - ASE-CSIE Week 13_  
_© {datetime.now().year} Academia of Studii Economice Bucuresti_
"""

        return md 

        # ========================================================================
        # GENERATION JSON
        # ========================================================================

    def _generate_json (self )->str :
        """Generate export JSON structurat."""
        data ={
        "metadata":{
        "title":self .metadata .title ,
        "author":self .metadata .author ,
        "date":self .metadata .date ,
        "methodology":self .metadata .methodology ,
        "scope":self .metadata .target_scope ,
        "executive_summary":self .metadata .executive_summary ,
        },
        "statistics":self ._calculate_statistics (),
        "findings":[
        {
        "title":f .title ,
        "severity":f .severity .name ,
        "severity_level":f .severity .level ,
        "description":f .description ,
        "target":f .target ,
        "remediation":f .remediation ,
        "cve_id":f .cve_id ,
        "cvss_score":f .cvss_score ,
        "evidence":f .evidence ,
        "references":f .references ,
        }
        for f in self .findings 
        ],
        "scan_results":[
        {
        "host":r .host ,
        "port":r .port ,
        "state":r .state ,
        "service":r .service ,
        "version":r .version ,
        "banner":r .banner ,
        }
        for r in self .scan_results 
        ],
        "custom_sections":self .sections ,
        "raw_data":self .raw_data ,
        }

        return json .dumps (data ,indent =2 ,ensure_ascii =False )

        # ========================================================================
        # GENERATION TEXT
        # ========================================================================

    def _generate_text (self )->str :
        """Generate report text simple for console."""
        stats =self ._calculate_statistics ()

        sep ="="*70 

        txt =f"""
{sep}
  {self.metadata.title.upper()}
{sep}

Author:       {self.metadata.author}
Data:        {self.metadata.date}
Metodologie: {self.metadata.methodology}

{sep}
  STATISTICI
{sep}

Total Descoperiri:  {stats['total_findings']}
  - Critical:       {stats['by_severity'].get('CRITICAL', 0)}
  - High:           {stats['by_severity'].get('HIGH', 0)}
  - Medium:         {stats['by_severity'].get('MEDIUM', 0)}
  - Low:            {stats['by_severity'].get('LOW', 0)}
Ports Opene:   {stats['open_ports']}

{sep}
  DESCOPERIRI
{sep}
"""

        for f in sorted (self .findings ,key =lambda x :x .severity .level ,reverse =True ):
            txt +=f"""
[{f.severity.name}] {f.title}
  Target:      {f.target}
  Dewritere:  {f.description}
  {f'CVE:        {f.cve_id}' if f.cve_id else ''}
  {f'Remediere:  {f.remediation}' if f.remediation else ''}
"""

        if self .scan_results :
            txt +=f"""
{sep}
  REZULTATE SCANARE
{sep}

{'Host':<20} {'Port':<8} {'State':<10} {'Service':<15} {'Version':<20}
{'-'*70}
"""
            for r in self .scan_results :
                txt +=f"{r.host:<20} {r.port:<8} {r.state:<10} {r.service:<15} {r.version:<20}\n"

        txt +=f"""
{sep}
  Generat of Report Generator - ASE-CSIE
{sep}
"""

        return txt 

        # ========================================================================
        # UTILITATI
        # ========================================================================

    def _calculate_statistics (self )->Dict [str ,Any ]:
        """Calculeaza statistici agregate."""
        by_severity ={}
        for f in self .findings :
            sev =f .severity .name 
            by_severity [sev ]=by_severity .get (sev ,0 )+1 

        open_ports =sum (1 for r in self .scan_results if r .state =="open")

        return {
        "total_findings":len (self .findings ),
        "by_severity":by_severity ,
        "open_ports":open_ports ,
        "total_hosts":len (set (r .host for r in self .scan_results )),
        }


        # ============================================================================
        # HELPER FUNCTIONS
        # ============================================================================

def quick_report_from_scan (
scan_json :str ,
output_path :str ,
title :str ="Report Scanning",
format :ReportFormat =ReportFormat .HTML 
)->str :
    """
    Generate quick un report from output-ul unui scan JSON.
    
    Args:
        scan_json: Calea catre fisierul JSON with results
        output_path: Calea for raportul output
        title: Titlul raportului
        format: Formatul dorit
    
    Returns:
        Calea catre raportul generated
    """
    gen =ReportGenerator (title )
    gen .load_from_json (scan_json )
    gen .set_executive_summary (
    f"Report generated automat from scanninga efectuata. "
    f"S-au identificat {len(gen.findings)} vulnerabilities and "
    f"{len(gen.scan_results)} results of scanning."
    )
    return gen .generate (output_path ,format )


    # ============================================================================
    # DEMO / TEST
    # ============================================================================

def demo ():
    """Demonstration generation report."""

    print ("=== Demo Report Generator ===\n")

    # Create generator
    gen =ReportGenerator (
    title ="Report Evaluare Security - Infrastructura IoT",
    author ="Echipa Security S13"
    )

    # Setting metadata
    gen .set_executive_summary (
    "Evaluarea of security a infrastructurii IoT a identificat "
    "more multe vulnerabilities critice, inclusiv backdoor in servicel FTP "
    "and comunicatii MQTT neencryptede. Se recommand remedierea imediata."
    )
    gen .set_scope ("172.20.0.0/24 - Docker network pentest")

    # Addition findings
    gen .add_finding (Finding (
    title ="vsftpd 2.3.4 Backdoor",
    severity =Severity .CRITICAL ,
    description ="Servicel FTP contains un backdoor which allow acces neauthorised on portul 6200.",
    target ="172.20.0.12:21",
    remediation ="Update imediata at versiunea 3.x or dezactiveare service.",
    cve_id ="CVE-2011-2523",
    cvss_score =9.8 ,
    evidence ="220 (vsFTPd 2.3.4)\nUSER test:)\n331 Please specify password\nPASS x\n[Shell open on 6200]"
    ))

    gen .add_finding (Finding (
    title ="MQTT without TLS",
    severity =Severity .HIGH ,
    description ="Broker-ul MQTT accept connections neencryptede on portul 1883.",
    target ="172.20.0.100:1883",
    remediation ="Configuration TLS mandatory, dezactiveare port 1883.",
    references =["https://mosquitto.org/documentation/tls/"]
    ))

    gen .add_finding (Finding (
    title ="MQTT Authentication Anonima",
    severity =Severity .MEDIUM ,
    description ="Broker-ul allow conectare without credentiale.",
    target ="172.20.0.100:1883",
    remediation ="Setting allow_anonymous false in mosquitto.conf"
    ))

    # Addition scan results
    gen .add_scan_result (ScanResult ("172.20.0.10",80 ,"open","HTTP","Apache/2.4","Apache/2.4.7"))
    gen .add_scan_result (ScanResult ("172.20.0.10",443 ,"closed","HTTPS"))
    gen .add_scan_result (ScanResult ("172.20.0.12",21 ,"open","FTP","vsftpd 2.3.4"))
    gen .add_scan_result (ScanResult ("172.20.0.12",6200 ,"open","Shell","Backdoor"))
    gen .add_scan_result (ScanResult ("172.20.0.100",1883 ,"open","MQTT","Mosquitto"))
    gen .add_scan_result (ScanResult ("172.20.0.100",8883 ,"open","MQTT-TLS","Mosquitto"))

    # Generate reports in all formats
    output_dir ="/tmp"

    gen .generate (f"{output_dir}/raport_demo.html",ReportFormat .HTML )
    gen .generate (f"{output_dir}/raport_demo.md",ReportFormat .MARKDOWN )
    gen .generate (f"{output_dir}/raport_demo.json",ReportFormat .JSON )
    gen .generate (f"{output_dir}/raport_demo.txt",ReportFormat .TEXT )

    print ("\n[✓] Demo complete! Rapoarte generate in /tmp/")


if __name__ =="__main__":
    demo ()
