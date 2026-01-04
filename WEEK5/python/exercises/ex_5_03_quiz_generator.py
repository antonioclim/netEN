#!/usr/bin/env python3
"""
Exercise 5.03 – Generator Quiz Interactiv
===========================================
Genereaza intrebari for practica CIDR, VLSM and IPv6.

usage:
    python ex_5_03_quiz_generator.py --count 5
    python ex_5_03_quiz_generator.py --interactive
    python ex_5_03_quiz_generator.py --type cidr --count 3

Author: Teaching material (ASE-CSIE)
"""

from __future__ import annotations

import argparse
import ipaddress
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

# Import utilitar local
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from python.utils.net_utils import analyze_ipv4_interface, ipv4_host_range


# Coduri de culoare ANSI
class Colors:
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


def colorize(text: str, color: str) -> str:
    if sys.stdout.isatty():
        return f"{color}{text}{Colors.END}"
    return text


@dataclass
class QuizQuestion:
    """Structura for o intrebare quiz."""
    question: str
    correct_answer: str
    hint: Optional[str] = None
    explanation: Optional[str] = None
    category: str = "general"


def generate_cidr_question() -> QuizQuestion:
    """Genereaza o intrebare despre analiza CIDR."""
    # Generam address aleatoare
    octets = [random.randint(1, 254) for _ in range(4)]
    prefix = random.choice([24, 25, 26, 27, 28, 29, 30])
    
    ip = '.'.join(map(str, octets))
    cidr = f"{ip}/{prefix}"
    
    # Calculam answerul
    info = analyze_ipv4_interface(cidr)
    
    # Alegem tipul intrebarii
    q_type = random.choice([
        "network", "broadcast", "hosts", "first_host", "last_host", "netmask"
    ])
    
    if q_type == "network":
        question = f"What is adresa de network for {cidr}?"
        answer = str(info.network.network_address)
        explanation = f"Address of network se obtine punand toti bitii host pe 0. Pentru /{prefix}, avem {32-prefix} biti host."
    elif q_type == "broadcast":
        question = f"What is the broadcast address for {cidr}?"
        answer = str(info.broadcast)
        explanation = f"The broadcast address se obtine punand toti bitii host pe 1."
    elif q_type == "hosts":
        question = f"Cate hosturi usable are reteaua {cidr}?"
        answer = str(info.usable_hosts)
        explanation = f"Hosturi = 2^{32-prefix} - 2 = {info.usable_hosts} (scadem adresa de network and broadcast)"
    elif q_type == "first_host":
        question = f"What is prima address de host utilizabila in {cidr}?"
        answer = str(info.first_host)
        explanation = f"Primul host = adresa de network + 1"
    elif q_type == "last_host":
        question = f"What is ultima address de host utilizabila in {cidr}?"
        answer = str(info.last_host)
        explanation = f"Ultimul host = adresa de broadcast - 1"
    else:  # netmask
        question = f"What is masca de network for prefixul /{prefix}?"
        answer = str(info.netmask)
        explanation = f"Masca se obtine punand primii {prefix} biti pe 1 and restul pe 0"
    
    return QuizQuestion(
        question=question,
        correct_answer=answer,
        explanation=explanation,
        category="cidr"
    )


def generate_flsm_question() -> QuizQuestion:
    """Genereaza o intrebare despre subnetting FLSM."""
    # network de baza
    base_prefixes = [16, 20, 22, 24]
    base_prefix = random.choice(base_prefixes)
    
    first_octet = random.choice([10, 172, 192])
    if first_octet == 10:
        ip = f"10.{random.randint(0,255)}.0.0"
    elif first_octet == 172:
        ip = f"172.{random.randint(16,31)}.0.0"
    else:
        ip = f"192.168.{random.randint(0,255)}.0"
    
    base_cidr = f"{ip}/{base_prefix}"
    
    # Numar de subnets
    num_subnets = random.choice([2, 4, 8, 16])
    bits_needed = num_subnets.bit_length() - 1
    new_prefix = base_prefix + bits_needed
    
    q_type = random.choice(["new_prefix", "num_hosts", "increment"])
    
    if q_type == "new_prefix":
        question = f"Daca impartim {base_cidr} in {num_subnets} subnets egale, care va fi noul prefix?"
        answer = f"/{new_prefix}"
        explanation = f"Imprumutam log₂({num_subnets}) = {bits_needed} biti. Prefix nou = {base_prefix} + {bits_needed} = {new_prefix}"
    elif q_type == "num_hosts":
        hosts_per_subnet = 2**(32-new_prefix) - 2
        question = f"Cate hosturi usable va avea fiecare subnet daca impartim {base_cidr} in {num_subnets} parti?"
        answer = str(hosts_per_subnet)
        explanation = f"Fiecare subnet are prefix /{new_prefix}, deci {32-new_prefix} biti host: 2^{32-new_prefix} - 2 = {hosts_per_subnet}"
    else:  # increment
        increment = 2**(32-new_prefix)
        question = f"What is incrementul intre subretelele results din impartirea {base_cidr} in {num_subnets}?"
        answer = str(increment)
        explanation = f"Increment = 2^(32 - {new_prefix}) = {increment}"
    
    return QuizQuestion(
        question=question,
        correct_answer=answer,
        explanation=explanation,
        category="flsm"
    )


def generate_vlsm_question() -> QuizQuestion:
    """Genereaza o intrebare despre VLSM."""
    # requirement de hosturi
    hosts_needed = random.choice([5, 10, 20, 30, 50, 60, 100, 120])
    
    # Calculam prefixul
    import math
    host_bits = math.ceil(math.log2(hosts_needed + 2))
    prefix = 32 - host_bits
    usable = 2**host_bits - 2
    
    question = f"Ce prefix CIDR minim este necesar for a gazdui {hosts_needed} hosturi?"
    answer = f"/{prefix}"
    explanation = f"Avem nevoie de {hosts_needed}+2 = {hosts_needed+2} addresses. Cea mai mica putere a lui 2 >= {hosts_needed+2} este {2**host_bits}, deci {host_bits} biti host → prefix /{prefix} (ofera {usable} hosturi usable)"
    
    return QuizQuestion(
        question=question,
        correct_answer=answer,
        explanation=explanation,
        category="vlsm"
    )


def generate_ipv6_question() -> QuizQuestion:
    """Genereaza o intrebare despre IPv6."""
    q_type = random.choice(["compress", "expand", "type"])
    
    if q_type == "compress":
        # Generam o address lunga
        groups = []
        zero_start = random.randint(1, 5)
        zero_count = random.randint(2, 4)
        
        for i in range(8):
            if zero_start <= i < zero_start + zero_count:
                groups.append("0000")
            else:
                # Generam grup with zerouri la inceput
                val = random.randint(0, 255)
                groups.append(f"00{val:02x}" if random.random() < 0.5 else f"{val:04x}")
        
        full_addr = ':'.join(groups)
        compressed = str(ipaddress.IPv6Address(full_addr))
        
        question = f"Comprima adresa IPv6: {full_addr}"
        answer = compressed
        explanation = "Eliminam zerourile din stanga and folosim :: for cea mai lunga secventa de zerouri"
        
    elif q_type == "expand":
        # addresses scurte cunoscute
        short_addrs = [
            ("2001:db8::1", "2001:0db8:0000:0000:0000:0000:0000:0001"),
            ("fe80::1", "fe80:0000:0000:0000:0000:0000:0000:0001"),
            ("::1", "0000:0000:0000:0000:0000:0000:0000:0001"),
            ("2001:db8:10::cafe", "2001:0db8:0010:0000:0000:0000:0000:cafe"),
        ]
        short, full = random.choice(short_addrs)
        
        question = f"Expandeaza adresa IPv6: {short}"
        answer = full
        explanation = "Inlocuim :: cu secventa de zerouri corespunzatoare and completam fiecare grup la 4 cifre"
        
    else:  # type
        type_questions = [
            ("fe80::1", "link-local"),
            ("2001:db8::1", "global unicast"),
            ("::1", "loopback"),
            ("ff02::1", "multicast"),
            ("fc00::1", "unique local"),
        ]
        addr, addr_type = random.choice(type_questions)
        
        question = f"Ce tip de address IPv6 este {addr}?"
        answer = addr_type
        explanation = f"Prefixul {addr.split('::')[0] if '::' in addr else addr.split(':')[0]} indica tipul {addr_type}"
    
    return QuizQuestion(
        question=question,
        correct_answer=answer,
        explanation=explanation,
        category="ipv6"
    )


def generate_questions(count: int, q_type: Optional[str] = None) -> List[QuizQuestion]:
    """Genereaza o lista de intrebari."""
    generators = {
        "cidr": generate_cidr_question,
        "flsm": generate_flsm_question,
        "vlsm": generate_vlsm_question,
        "ipv6": generate_ipv6_question,
    }
    
    questions = []
    for _ in range(count):
        if q_type and q_type in generators:
            gen = generators[q_type]
        else:
            gen = random.choice(list(generators.values()))
        
        questions.append(gen())
    
    return questions


def run_quiz_batch(count: int, q_type: Optional[str] = None) -> int:
    """run un quiz in modul batch (print toate intrebarile)."""
    questions = generate_questions(count, q_type)
    
    print()
    print(colorize("═" * 60, Colors.BLUE))
    print(colorize("  Quiz Subnetting - Setul de Intrebari", Colors.BOLD))
    print(colorize("═" * 60, Colors.BLUE))
    print()
    
    for i, q in enumerate(questions, 1):
        category_color = {
            "cidr": Colors.CYAN,
            "flsm": Colors.GREEN,
            "vlsm": Colors.YELLOW,
            "ipv6": Colors.RED,
        }.get(q.category, Colors.BLUE)
        
        print(f"  {colorize(f'Intrebarea {i}', Colors.BOLD)} [{colorize(q.category.upper(), category_color)}]")
        print(f"  {q.question}")
        print()
        print(f"  {colorize('Answer:', Colors.GREEN)} {q.correct_answer}")
        if q.explanation:
            print(f"  {colorize('Explanation:', Colors.CYAN)} {q.explanation}")
        print(colorize("─" * 60, Colors.BLUE))
        print()
    
    return 0


def run_quiz_interactive(count: int = 5, q_type: Optional[str] = None) -> int:
    """run un quiz interactiv."""
    questions = generate_questions(count, q_type)
    
    print()
    print(colorize("═" * 60, Colors.BLUE))
    print(colorize("  Quiz Interactiv de Subnetting", Colors.BOLD))
    print(colorize("═" * 60, Colors.BLUE))
    print()
    print(f"  Vei primi {count} intrebari. Introdu answerul or apasa Enter for a sari.")
    print(f"  Scrie 'quit' for a iesi.")
    print()
    
    correct = 0
    skipped = 0
    
    for i, q in enumerate(questions, 1):
        category_color = {
            "cidr": Colors.CYAN,
            "flsm": Colors.GREEN,
            "vlsm": Colors.YELLOW,
            "ipv6": Colors.RED,
        }.get(q.category, Colors.BLUE)
        
        print(colorize("─" * 60, Colors.BLUE))
        print(f"  {colorize(f'Intrebarea {i}/{count}', Colors.BOLD)} [{colorize(q.category.upper(), category_color)}]")
        print(f"  {q.question}")
        print()
        
        try:
            answer = input(f"  {colorize('Answerul tau:', Colors.CYAN)} ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        
        if answer.lower() == 'quit':
            break
        
        if not answer:
            skipped += 1
            print(f"  {colorize('Sarit.', Colors.YELLOW)} Answer correct: {colorize(q.correct_answer, Colors.GREEN)}")
        elif answer.lower().replace('/', '').replace(' ', '') == q.correct_answer.lower().replace('/', '').replace(' ', ''):
            correct += 1
            print(f"  {colorize('✓ correct!', Colors.GREEN)}")
        else:
            print(f"  {colorize('✗ Gresit.', Colors.RED)} Answer correct: {colorize(q.correct_answer, Colors.GREEN)}")
        
        if q.explanation:
            print(f"  {colorize('Explanation:', Colors.CYAN)} {q.explanation}")
        print()
    
    # result final
    answered = count - skipped
    percentage = (correct / answered * 100) if answered > 0 else 0
    
    print(colorize("═" * 60, Colors.BLUE))
    print(colorize("  result Final", Colors.BOLD))
    print(colorize("═" * 60, Colors.BLUE))
    print()
    print(f"  Answeruri corecte: {colorize(str(correct), Colors.GREEN)}/{answered}")
    print(f"  Intrebari sarite:   {skipped}")
    print(f"  Scor:               {colorize(f'{percentage:.0f}%', Colors.YELLOW)}")
    print()
    
    if percentage >= 80:
        print(f"  {colorize('Excelent! Stapanesti subnetting-ul!', Colors.GREEN)}")
    elif percentage >= 60:
        print(f"  {colorize('Bine! Mai exerseaza for perfectiune.', Colors.YELLOW)}")
    else:
        print(f"  {colorize('Mai e de lucru. Revizuieste teoria and incearca din nou.', Colors.RED)}")
    print()
    
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construieste parser-ul de argumente."""
    parser = argparse.ArgumentParser(
        description="Generator Quiz Interactiv for Subnetting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --count 5                    5 intrebari aleatorii
  %(prog)s --interactive                Quiz interactiv
  %(prog)s --type cidr --count 3        3 intrebari doar CIDR
  %(prog)s --type vlsm --interactive    Quiz interactiv VLSM
"""
    )
    
    parser.add_argument(
        "--count", "-n",
        type=int,
        default=5,
        help="Numarul de intrebari (implicit: 5)"
    )
    
    parser.add_argument(
        "--type", "-t",
        choices=["cidr", "flsm", "vlsm", "ipv6"],
        help="Tipul intrebarilor (implicit: toate)"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Interactive mode (raspunzi la intrebari)"
    )
    
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Functia main."""
    parser = build_parser()
    args = parser.parse_args(argv)
    
    if args.interactive:
        return run_quiz_interactive(args.count, args.type)
    else:
        return run_quiz_batch(args.count, args.type)


if __name__ == "__main__":
    sys.exit(main())
