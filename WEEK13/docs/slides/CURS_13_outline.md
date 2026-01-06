# Week 13 Lecture Outline
## IoT and Security in Computer Networks

### Learning outcomes
By the end of this lecture, students should be able to:
- Describe typical IoT communication patterns and threat surfaces
- Explain MQTT basics (publish, subscribe, QoS, retained messages and TLS)
- Distinguish between network-level, transport-level and application-level controls
- Recognise common misconfigurations (anonymous brokers, weak segmentation and exposed services)
- Relate basic reconnaissance outputs (banners and headers) to risk assessment

### Agenda
1. IoT landscape and constraints
   - Device limitations, update mechanisms and supply chain risks
2. Communication protocols used in IoT
   - MQTT as a case study (topics, brokers, QoS and session state)
3. Threat model for IoT deployments
   - Assets, adversaries and realistic attack paths
4. Defence-in-depth for IoT networks
   - Segmentation, least privilege, secure defaults and monitoring
5. Practical mapping to the laboratory kit
   - Docker-based lab services (DVWA, Mosquitto, vsftpd stub backdoor)
   - How the demos connect to the theory

### Suggested reading
- OASIS. (2019). *MQTT Version 5.0* (standard).  
- ISO/IEC. (2022). *ISO/IEC 27400:2022 Cybersecurity — IoT security and privacy*.

(Standards are referenced for context. The laboratory focuses on practical mechanics and does not require full standard coverage.)
