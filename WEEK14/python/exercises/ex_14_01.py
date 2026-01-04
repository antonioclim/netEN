#!/usr/bin/env python3
"""ex_14_01.py — Review drills for Week 14.

Features:
  - Interactive self-test with multiple choice questions
  - Generate quiz with N random questions
  - Export results in JSON

Usage:
  python3 ex_14_01.py --selftest          # interactive test
  python3 ex_14_01.py --quiz 10           # 10 random questions
  python3 ex_14_01.py --quiz 10 --out q.json  # export JSON
"""

from __future__ import annotations

import argparse
import json
import random
from typing import Dict, List, Tuple

# Question bank (format: (question, [options], correct_answer_index, explanation))
QUESTIONS: List[Tuple[str, List[str], int, str]] = [
    # Layers and encapsulation
    (
        "Which OSI layer is responsible for logical addressing (IP)?",
        ["Link (2)", "Network (3)", "Transport (4)", "Application (7)"],
        1,
        "The Network layer (3) manages IP addressing and routing."
    ),
    (
        "What PDU does the Transport layer use for TCP?",
        ["Frame", "Packet", "Segment", "Message"],
        2,
        "TCP uses segments; UDP uses datagrams."
    ),
    (
        "Encapsulation adds headers when data...",
        ["Goes up the stack", "Goes down the stack", "Is processed by application", "Reaches destination"],
        1,
        "During transmission, data goes down and receives headers at each layer."
    ),
    
    # Addressing
    (
        "A MAC address has...",
        ["32 bits", "48 bits", "64 bits", "128 bits"],
        1,
        "MAC addresses (Ethernet) have 48 bits (6 bytes), e.g.: 00:1A:2B:3C:4D:5E."
    ),
    (
        "What protocol resolves IP → MAC in local networks?",
        ["DNS", "DHCP", "ARP", "ICMP"],
        2,
        "ARP (Address Resolution Protocol) maps IPs to MAC addresses."
    ),
    (
        "Which of the following is a private IP address?",
        ["8.8.8.8", "192.168.1.1", "172.32.0.1", "11.0.0.1"],
        1,
        "192.168.0.0/16 is a private block (RFC 1918)."
    ),
    
    # TCP/UDP
    (
        "Which TCP flag initiates a new connection?",
        ["ACK", "FIN", "SYN", "RST"],
        2,
        "SYN (Synchronize) starts the 3-way TCP handshake."
    ),
    (
        "UDP is a protocol that is...",
        ["Connection-oriented, reliable", "Connection-oriented, unreliable", 
         "Connectionless, reliable", "Connectionless, unreliable"],
        3,
        "UDP does not guarantee delivery and does not establish connection."
    ),
    (
        "What does a TCP packet with RST flag mean?",
        ["Retransmission request", "Connection reset", "Acknowledgement received", "Synchronisation request"],
        1,
        "RST (Reset) abruptly closes the connection, usually on error."
    ),
    (
        "Which TCP mechanism prevents network congestion?",
        ["Flow Control", "Congestion Control", "Error Control", "Sequence Control"],
        1,
        "Congestion Control (e.g.: AIMD, slow start) adjusts rate during congestion."
    ),
    
    # Ports
    (
        "On which standard port does HTTP listen?",
        ["22", "53", "80", "443"],
        2,
        "HTTP uses port 80; HTTPS uses 443."
    ),
    (
        "On which standard port does DNS listen?",
        ["22", "53", "80", "443"],
        1,
        "DNS uses port 53 (UDP and TCP)."
    ),
    (
        "An ephemeral port is usually in the range...",
        ["0-1023", "1024-49151", "49152-65535", "80-443"],
        2,
        "Ephemeral ports (client) are in 49152-65535 (or 32768+ on Linux)."
    ),
    
    # Routing
    (
        "What Linux command displays the routing table?",
        ["ip addr", "ip route", "ip link", "ip neigh"],
        1,
        "`ip route` or `ip r` displays routes; `netstat -rn` is the old variant."
    ),
    (
        "Default gateway is used when...",
        ["Destination is in the same subnet", "Destination is in another subnet", 
         "Packet is broadcast", "No specific route exists"],
        3,
        "Default gateway is used when no more specific route exists (0.0.0.0/0)."
    ),
    
    # HTTP
    (
        "What HTTP code indicates success?",
        ["200", "301", "404", "500"],
        0,
        "200 OK = success; 301 = redirect; 404 = not found; 500 = server error."
    ),
    (
        "Which HTTP method is idempotent and safe?",
        ["GET", "POST", "PUT", "DELETE"],
        0,
        "GET does not modify state; POST is not idempotent."
    ),
    
    # Diagnostics
    (
        "What does 'Connection refused' mean on a TCP connection?",
        ["Network timeout", "Port not listening", "Firewall blocking", "DNS failed"],
        1,
        "Immediate RST = port not listening; timeout = filtered/blocked."
    ),
    (
        "What command checks which ports are listening on host?",
        ["ping localhost", "ss -lntp", "ip addr", "tcpdump -i lo"],
        1,
        "`ss -lntp` shows TCP sockets in LISTEN; `netstat -tlnp` is equivalent."
    ),
    (
        "Which tool captures packets for analysis?",
        ["ping", "traceroute", "tcpdump", "ss"],
        2,
        "tcpdump/tshark/Wireshark capture and analyse packets."
    ),
    
    # CIDR
    (
        "How many usable IP addresses does a /24 network have?",
        ["254", "255", "256", "512"],
        0,
        "/24 = 256 addresses, but 2 are reserved (network and broadcast) → 254 usable."
    ),
    (
        "What is the subnet mask for /16?",
        ["255.0.0.0", "255.255.0.0", "255.255.255.0", "255.255.255.128"],
        1,
        "/16 = 16 bits for network → 255.255.0.0."
    ),
]


def run_selftest() -> Tuple[int, int]:
    """Runs interactive self-test."""
    print("\n" + "=" * 60)
    print("  Self-Test Review W14")
    print("=" * 60 + "\n")
    
    questions = QUESTIONS.copy()
    random.shuffle(questions)
    
    correct = 0
    total = len(questions)
    
    for i, (question, options, answer_idx, explanation) in enumerate(questions, 1):
        print(f"\nQuestion {i}/{total}:")
        print(f"  {question}\n")
        
        for j, opt in enumerate(options):
            print(f"    {j + 1}. {opt}")
        
        while True:
            try:
                user_input = input("\nAnswer (1-4, or 'q' to quit): ").strip()
                if user_input.lower() == 'q':
                    print(f"\nTest interrupted. Partial score: {correct}/{i-1}")
                    return correct, i - 1
                
                user_answer = int(user_input) - 1
                if 0 <= user_answer < len(options):
                    break
                print("Enter a number between 1 and 4.")
            except ValueError:
                print("Enter a valid number.")
        
        if user_answer == answer_idx:
            print("✓ Correct!")
            correct += 1
        else:
            print(f"✗ Wrong. Correct answer: {answer_idx + 1}. {options[answer_idx]}")
        
        print(f"  Explanation: {explanation}")
    
    return correct, total


def generate_quiz(n: int) -> List[Dict]:
    """Generates a quiz with N random questions."""
    questions = random.sample(QUESTIONS, min(n, len(QUESTIONS)))
    
    quiz = []
    for q, opts, ans_idx, expl in questions:
        quiz.append({
            "question": q,
            "options": opts,
            "correct_index": ans_idx,
            "correct_answer": opts[ans_idx],
            "explanation": expl,
        })
    
    return quiz


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Review drills W14")
    parser.add_argument("--selftest", action="store_true", help="Run interactive self-test")
    parser.add_argument("--quiz", type=int, help="Generate quiz with N questions")
    parser.add_argument("--out", help="Output file for quiz (JSON)")
    parser.add_argument("--list", action="store_true", help="List all questions")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    
    if args.selftest:
        correct, total = run_selftest()
        print("\n" + "=" * 60)
        print(f"  Final score: {correct}/{total} ({100 * correct // total}%)")
        print("=" * 60 + "\n")
        return 0 if correct == total else 1
    
    elif args.quiz:
        quiz = generate_quiz(args.quiz)
        
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(quiz, f, indent=2, ensure_ascii=False)
            print(f"Quiz saved to: {args.out}")
        else:
            print(json.dumps(quiz, indent=2, ensure_ascii=False))
        return 0
    
    elif args.list:
        print(f"\nTotal questions: {len(QUESTIONS)}\n")
        for i, (q, opts, ans_idx, _) in enumerate(QUESTIONS, 1):
            print(f"{i}. {q}")
            print(f"   Answer: {opts[ans_idx]}\n")
        return 0
    
    else:
        print("Usage:")
        print("  python3 ex_14_01.py --selftest       # interactive test")
        print("  python3 ex_14_01.py --quiz 10        # 10 random questions")
        print("  python3 ex_14_01.py --quiz 10 --out q.json")
        print("  python3 ex_14_01.py --list           # list questions")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
