#!/usr/bin/env python3
"""
Data seeding script for Research Papers Manager
Creates 100 users and 1000 papers with random citations
"""

import os
import sys
import random
from datetime import datetime
from faker import Faker

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from app.factory import create_app
    from app.models.user import User
    from app.models.paper import Paper
    from app.utils.cache import CacheService
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure you're running this script from the project root or with proper PYTHONPATH")
    sys.exit(1)

# Initialize Faker for generating realistic data
fake = Faker()

def seed_users(app, count=100):
    """Create 100 random users"""
    print(f"Creating {count} users...")
    
    users = []
    with app.app_context():
        for i in range(count):
            # Generate user data
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f"{first_name.lower()}{last_name.lower()}_{random.randint(100, 999)}"
            email = fake.email()
            password = fake.password(length=random.randint(8, 12),
                                     special_chars=True, digits=True, upper_case=True, lower_case=True)
            department = fake.random_element(elements=[
                "Computer Engineering", "Electrical Engineering", "Computer Science",
                "Software Engineering", "Data Science", "Artificial Intelligence",
                "Machine Learning", "Cybersecurity", "Information Systems",
                "Signal Processing", "Communications Engineering", "Control Systems",
                "VLSI Design", "Power Electronics", "Quantum Computing"
            ])
            
            # Prepare user data for the User.create method
            user_data = {
                "username": username,
                "name": f"{first_name} {last_name}",
                "email": email,
                "password": password,
                "department": department
            }
            
            try:
                # Check if username is already taken using CacheService
                if CacheService.is_username_taken(username):
                    print(f"  Skipping duplicate username: {username}")
                    continue
                
                # Create user using the static method
                user_id = User.create(user_data)
                CacheService.add_username_to_cache(username)
                users.append(user_id)
                if (i + 1) % 20 == 0: print(f"  Created {i + 1} users...")
            
            except Exception as e:
                print(f"  Error creating user {username}: {e}")
                
    print(f"Successfully created {len(users)} users")
    return users

def seed_papers(app, user_ids, count=1000):
    """Create 1000 random papers with citations"""
    print(f"Creating {count} papers...")
    
    # ECE and AI/ML-focused research domains with distinct specializations
    domains = [
        "Theoretical Computer Science", "Algorithm Design", "Embedded Systems", 
        "Computer Architecture", "Deep Learning", "Cybersecurity",
        "Software Engineering", "Signal Processing", "Communications",
        "VLSI Design", "Control Systems", "Power Electronics",
        "Quantum Computing", "Computer Networks", "Database Systems",
        "Retrieval-Augmented Generation", "Convolutional Neural Networks", 
        "Explainable AI", "Natural Language Processing", "Computer Vision",
        "Reinforcement Learning", "Graph Neural Networks", "Federated Learning",
        "Transfer Learning", "Generative AI", "Knowledge Graphs",
        "Multi-Modal Learning", "Edge AI", "Neural Architecture Search"
    ]
    
    # Distinct keywords for each domain to reduce intersection
    domain_keywords = {
        "Theoretical Computer Science": ["complexity theory", "formal methods", "computational models", "proof systems"],
        "Algorithm Design": ["optimization algorithms", "graph algorithms", "sorting", "dynamic programming"],
        "Embedded Systems": ["microcontrollers", "real-time systems", "IoT", "firmware"],
        "Computer Architecture": ["processor design", "cache memory", "instruction sets", "parallel computing"],
        "Deep Learning": ["neural networks", "backpropagation", "CNN", "transformer models"],
        "Cybersecurity": ["cryptography", "intrusion detection", "authentication", "vulnerability analysis"],
        "Software Engineering": ["software testing", "design patterns", "agile development", "code quality"],
        "Signal Processing": ["digital filters", "FFT", "noise reduction", "signal analysis"],
        "Communications": ["wireless networks", "modulation", "channel coding", "antenna design"],
        "VLSI Design": ["circuit design", "logic synthesis", "layout optimization", "semiconductor"],
        "Control Systems": ["PID controllers", "state space", "stability analysis", "feedback systems"],
        "Power Electronics": ["power converters", "inverters", "power management", "energy efficiency"],
        "Quantum Computing": ["qubits", "quantum algorithms", "quantum gates", "entanglement"],
        "Computer Networks": ["network protocols", "routing algorithms", "QoS", "network security"],
        "Database Systems": ["query optimization", "indexing", "ACID properties", "distributed databases"],
        "Retrieval-Augmented Generation": ["document retrieval", "vector databases", "knowledge injection", "context augmentation"],
        "Convolutional Neural Networks": ["convolution layers", "pooling", "feature maps", "image classification"],
        "Explainable AI": ["interpretability", "model transparency", "LIME", "SHAP values"],
        "Natural Language Processing": ["tokenization", "language models", "sentiment analysis", "named entity recognition"],
        "Computer Vision": ["object detection", "image segmentation", "optical flow", "3D reconstruction"],
        "Reinforcement Learning": ["Q-learning", "policy gradients", "actor-critic", "reward functions"],
        "Graph Neural Networks": ["graph convolution", "node embeddings", "message passing", "graph attention"],
        "Federated Learning": ["decentralized training", "differential privacy", "client aggregation", "data locality"],
        "Transfer Learning": ["pre-trained models", "fine-tuning", "domain adaptation", "feature extraction"],
        "Generative AI": ["GANs", "VAEs", "diffusion models", "text generation"],
        "Knowledge Graphs": ["entity linking", "relation extraction", "ontologies", "semantic reasoning"],
        "Multi-Modal Learning": ["cross-modal fusion", "vision-language models", "audio-visual learning", "modality alignment"],
        "Edge AI": ["model compression", "quantization", "on-device inference", "latency optimization"],
        "Neural Architecture Search": ["AutoML", "architecture optimization", "evolutionary algorithms", "differentiable search"]
    }
    
    # ECE, AI/ML-focused venues and journals
    venues = [
        "IEEE Transactions on Computers", "ACM Transactions on Computer Systems",
        "IEEE Transactions on Signal Processing", "IEEE Communications Magazine",
        "IEEE Transactions on VLSI Systems", "IEEE Control Systems Magazine",
        "IEEE Transactions on Power Electronics", "ACM Computing Surveys",
        "IEEE Transactions on Embedded Computing Systems", "IEEE Computer Architecture Letters",
        "IEEE Transactions on Information Theory", "ACM Transactions on Algorithms",
        "IEEE Security & Privacy", "IEEE Software",
        "IEEE Transactions on Quantum Engineering", "Computer Networks Journal",
        "Neural Information Processing Systems", "International Conference on Machine Learning",
        "Association for Computational Linguistics", "IEEE Conference on Computer Vision and Pattern Recognition",
        "International Conference on Learning Representations", "Conference on Empirical Methods in Natural Language Processing",
        "IEEE Transactions on Pattern Analysis and Machine Intelligence", "Nature Machine Intelligence",
        "Journal of Machine Learning Research", "IEEE Transactions on Neural Networks and Learning Systems",
        "ACM Transactions on Knowledge Discovery from Data", "Artificial Intelligence Journal",
        "IEEE Transactions on Artificial Intelligence", "Machine Learning Journal"
    ]
    
    papers = []
    with app.app_context():
        for i in range(count):
            # Select random domain and author
            domain = random.choice(domains)
            author_id = random.choice(user_ids)
            
            # Get domain-specific keywords (no intersection with other domains)
            domain_keywords_list = domain_keywords[domain]
            keywords = random.sample(domain_keywords_list, k=min(len(domain_keywords_list), random.randint(2, 4)))
            
            title = generate_paper_title(domain, fake)
            abstract = generate_paper_abstract(domain, keywords, fake)
            
            num_authors = random.randint(1, 4)
            authors = []
            for _ in range(num_authors):
                authors.append(f"{fake.first_name()} {fake.last_name()}")
            pub_date = fake.date_between(start_date=datetime(2015, 6, 5), end_date=datetime(2025, 6, 5))
            
            # Prepare paper data for Paper.create method
            paper_data = {
                "title": title,
                "authors": authors,
                "abstract": abstract,
                "keywords": keywords,
                "publication_date": pub_date.isoformat(),
                "journal_conference": random.choice(venues),
                "citations": []  # Will be added later
            }
            
            try:
                paper_id = Paper.create(paper_data, author_id)
                papers.append(paper_id)
                if (i + 1) % 100 == 0: print(f"  Created {i + 1} papers...")
            except Exception as e:
                print(f"  Error creating paper: {e}")
                
    print(f"Successfully created {len(papers)} papers")
    return papers

def add_citations(app, paper_ids, min_citations=0, max_citations=5):
    """Add random citations between papers by updating existing papers"""
    print("Adding citations between papers...")
    
    citation_count = 0
    papers_with_citations = 0
    
    with app.app_context():
        for paper_id in paper_ids:
            # Random number of citations for this paper
            num_citations = random.randint(min_citations, max_citations)
            
            if num_citations > 0:
                # Select random papers to cite (excluding self)
                available_papers = [p for p in paper_ids if p != paper_id]
                if len(available_papers) >= num_citations:
                    cited_papers = random.sample(available_papers, num_citations)
                    
                    try:
                        # Use Paper model to create citations
                        Paper._create_citations(paper_id, cited_papers)
                        citation_count += len(cited_papers)
                        papers_with_citations += 1
                        
                        if papers_with_citations % 100 == 0:
                            print(f"  Added citations to {papers_with_citations} papers...")
                            
                    except Exception as e:
                        print(f"  Error adding citations to paper {paper_id}: {e}")
                        
    print(f"Successfully added {citation_count} citations to {papers_with_citations} papers")

def generate_paper_title(domain, fake_instance):
    """Generate realistic paper title based on specific ECE domain"""
    
    # Domain-specific title templates
    domain_templates = {
        "Theoretical Computer Science": [
            "On the Computational Complexity of {topic}",
            "A Formal Analysis of {topic} in Computational Models",
            "Theoretical Foundations of {topic}: A Complexity Perspective",
            "Decidability and Complexity of {topic} Problems"
        ],
        "Algorithm Design": [
            "Efficient {topic} Algorithms for Large-Scale Applications",
            "Approximation Algorithms for {topic} Optimization",
            "A Fast {topic} Algorithm with Improved Time Complexity",
            "Parallel {topic} Algorithms for Multi-Core Systems"
        ],
        "Embedded Systems": [
            "Real-Time {topic} Implementation on {hardware} Platforms",
            "Low-Power {topic} Design for IoT Applications",
            "Hardware-Software Co-design for {topic} Systems",
            "Embedded {topic} Optimization for Resource-Constrained Devices"
        ],
        "Computer Architecture": [
            "High-Performance {topic} Architecture for Modern Processors",
            "Cache-Efficient {topic} Design in Multi-Core Systems",
            "Novel {topic} Microarchitecture with Enhanced Throughput",
            "FPGA-Based {topic} Acceleration Techniques"
        ],
        "Deep Learning": [
            "Deep Neural Networks for {topic} Recognition",
            "Transformer-Based {topic} Models with Attention Mechanisms",
            "Convolutional Architectures for {topic} Classification",
            "Federated Learning Approaches for {topic} Applications"
        ],
        "Cybersecurity": [
            "Advanced {topic} Techniques for Network Security",
            "Cryptographic Protocols for Secure {topic}",
            "Machine Learning-Based {topic} Threat Detection",
            "Zero-Trust Architecture for {topic} Protection"
        ],
        "Software Engineering": [
            "Automated {topic} Testing Frameworks and Methodologies",
            "DevOps Integration for {topic} Development Lifecycle",
            "Microservices Architecture for Scalable {topic}",
            "Continuous Integration Strategies for {topic} Projects"
        ],
        "Signal Processing": [
            "Digital {topic} Filtering with Adaptive Algorithms",
            "Spectral Analysis Techniques for {topic} Signals",
            "Noise Reduction in {topic} Using Advanced DSP",
            "Real-Time {topic} Processing on Embedded Platforms"
        ],
        "Communications": [
            "5G/6G {topic} for Next-Generation Wireless Networks",
            "MIMO {topic} Techniques for High-Speed Communication",
            "Software-Defined Radio Implementation of {topic}",
            "Millimeter-Wave {topic} for Ultra-High Bandwidth"
        ],
        "VLSI Design": [
            "Low-Power {topic} Circuit Design in Nanometer Technologies",
            "Physical Design Optimization for {topic} ASIC Implementation",
            "High-Speed {topic} Logic Synthesis and Layout",
            "Radiation-Hardened {topic} Circuits for Space Applications"
        ],
        "Control Systems": [
            "Adaptive {topic} Control for Nonlinear Dynamic Systems",
            "Model Predictive Control Strategies for {topic}",
            "Robust {topic} Controller Design Under Uncertainty",
            "Distributed Control Algorithms for {topic} Networks"
        ],
        "Power Electronics": [
            "High-Efficiency {topic} Converter Topologies",
            "Wide-Bandgap Semiconductor {topic} Applications",
            "Grid-Tied {topic} Systems with Power Quality Enhancement",
            "Thermal Management in High-Power {topic} Devices"
        ],
        "Quantum Computing": [
            "Quantum {topic} Algorithms for NISQ Era Devices",
            "Error Correction Schemes for {topic} Quantum Circuits",
            "Variational Quantum {topic} for Optimization Problems",
            "Quantum Advantage in {topic} Computational Tasks"
        ],
        "Computer Networks": [
            "Software-Defined Networking for {topic} Management",
            "Edge Computing Architectures for {topic} Services",
            "Network Function Virtualization in {topic} Infrastructure",
            "QoS-Aware {topic} Routing in Multi-Tier Networks"
        ],
        "Database Systems": [
            "Distributed {topic} Management in Cloud Environments",
            "NoSQL Database Optimization for {topic} Workloads",
            "Blockchain-Based {topic} Integrity and Provenance",
            "In-Memory {topic} Processing for Real-Time Analytics"
        ],
        "Retrieval-Augmented Generation": [
            "Enhanced {topic} with Large-Scale Knowledge Retrieval",
            "Multi-Modal RAG Systems for {topic} Applications",
            "Efficient {topic} Retrieval in Vector Databases",
            "Context-Aware {topic} Generation with Dynamic Retrieval"
        ],
        "Convolutional Neural Networks": [
            "Advanced {topic} Architectures for Visual Recognition",
            "Lightweight CNN Models for {topic} on Mobile Devices",
            "Attention-Enhanced CNNs for {topic} Classification",
            "3D Convolutional Networks for {topic} Analysis"
        ],
        "Explainable AI": [
            "Interpretable {topic} Models for Critical Decision Making",
            "Post-Hoc Explanations for {topic} Deep Learning Systems",
            "Inherently Explainable {topic} Architectures",
            "Human-Centered XAI for {topic} Applications"
        ],
        "Natural Language Processing": [
            "Transformer-Based {topic} Models for Multilingual Text",
            "Few-Shot Learning Approaches for {topic} Tasks",
            "Large Language Models for {topic} Understanding",
            "Cross-Lingual {topic} Transfer with Minimal Supervision"
        ],
        "Computer Vision": [
            "Self-Supervised Learning for {topic} Recognition",
            "Multi-Scale {topic} Detection in Complex Scenes",
            "3D Vision Systems for {topic} Reconstruction",
            "Real-Time {topic} Processing with Edge Computing"
        ],
        "Reinforcement Learning": [
            "Deep RL Algorithms for {topic} Optimization",
            "Multi-Agent {topic} Learning in Dynamic Environments",
            "Sample-Efficient {topic} Learning with Curiosity-Driven Exploration",
            "Offline RL for {topic} Policy Learning from Historical Data"
        ],
        "Graph Neural Networks": [
            "Scalable {topic} Learning on Large-Scale Graphs",
            "Heterogeneous Graph Neural Networks for {topic}",
            "Temporal {topic} Modeling with Dynamic Graph Networks",
            "Graph Attention Mechanisms for {topic} Prediction"
        ],
        "Federated Learning": [
            "Privacy-Preserving {topic} Learning Across Distributed Clients",
            "Communication-Efficient {topic} Aggregation Strategies",
            "Personalized Federated Learning for {topic} Applications",
            "Robust FL Systems Against {topic} Adversarial Attacks"
        ],
        "Transfer Learning": [
            "Cross-Domain {topic} Transfer with Deep Feature Adaptation",
            "Few-Shot {topic} Learning via Meta-Learning Approaches",
            "Domain-Adversarial {topic} Transfer for Robust Models",
            "Progressive {topic} Transfer Learning with Incremental Adaptation"
        ],
        "Generative AI": [
            "Diffusion Models for High-Quality {topic} Generation",
            "Controllable {topic} Generation with Latent Space Manipulation",
            "GAN-Based {topic} Synthesis with Style Transfer",
            "Autoregressive Models for Sequential {topic} Generation"
        ],
        "Knowledge Graphs": [
            "Automated {topic} Construction from Unstructured Text",
            "Neural-Symbolic {topic} Reasoning for Question Answering",
            "Dynamic {topic} Embedding for Temporal Knowledge Graphs",
            "Multi-Modal Knowledge Graphs for {topic} Integration"
        ],
        "Multi-Modal Learning": [
            "Cross-Modal {topic} Fusion for Enhanced Understanding",
            "Self-Supervised Multi-Modal {topic} Representation Learning",
            "Vision-Language Models for {topic} Comprehension",
            "Audio-Visual {topic} Learning with Temporal Alignment"
        ],
        "Edge AI": [
            "Ultra-Low Latency {topic} Inference on Edge Devices",
            "Distributed {topic} Processing Across Edge-Cloud Continuum",
            "Energy-Efficient {topic} Acceleration for IoT Systems",
            "Adaptive {topic} Models for Resource-Constrained Environments"
        ],
        "Neural Architecture Search": [
            "Evolutionary {topic} Architecture Optimization",
            "Differentiable NAS for {topic} Model Discovery",
            "Hardware-Aware {topic} Architecture Search",
            "Progressive {topic} Architecture Growing with Performance Prediction"
        ]
    }
    
    # Domain-specific topics
    domain_topics = {
        "Theoretical Computer Science": ["P vs NP", "automata theory", "formal verification", "lambda calculus"],
        "Algorithm Design": ["graph traversal", "sorting networks", "approximation schemes", "online algorithms"],
        "Embedded Systems": ["RTOS scheduling", "sensor fusion", "power management", "fault tolerance"],
        "Computer Architecture": ["branch prediction", "memory hierarchy", "instruction pipelining", "cache coherence"],
        "Deep Learning": ["attention mechanisms", "generative models", "transfer learning", "model compression"],
        "Cybersecurity": ["blockchain security", "homomorphic encryption", "side-channel attacks", "privacy preservation"],
        "Software Engineering": ["static analysis", "automated testing", "refactoring tools", "dependency management"],
        "Signal Processing": ["wavelet transforms", "adaptive filtering", "compressed sensing", "multirate systems"],
        "Communications": ["channel estimation", "OFDM systems", "beamforming", "error correction codes"],
        "VLSI Design": ["clock distribution", "power gating", "DFT insertion", "timing closure"],
        "Control Systems": ["state estimation", "optimal control", "system identification", "fault detection"],
        "Power Electronics": ["power factor correction", "DC-DC conversion", "motor drives", "renewable integration"],
        "Quantum Computing": ["quantum supremacy", "variational circuits", "quantum annealing", "quantum error correction"],
        "Computer Networks": ["traffic engineering", "network monitoring", "load balancing", "security protocols"],
        "Database Systems": ["transaction processing", "query execution", "data warehousing", "stream processing"],
        "Retrieval-Augmented Generation": ["dense retrieval", "passage ranking", "knowledge injection", "retrieval quality"],
        "Convolutional Neural Networks": ["feature extraction", "spatial pooling", "receptive fields", "depth-wise convolution"],
        "Explainable AI": ["saliency maps", "counterfactual explanations", "feature attribution", "model introspection"],
        "Natural Language Processing": ["language modeling", "syntactic parsing", "semantic role labeling", "coreference resolution"],
        "Computer Vision": ["object tracking", "pose estimation", "scene understanding", "visual reasoning"],
        "Reinforcement Learning": ["exploration strategies", "value function approximation", "policy optimization", "reward shaping"],
        "Graph Neural Networks": ["graph classification", "link prediction", "node centrality", "community detection"],
        "Federated Learning": ["client selection", "model aggregation", "communication compression", "Byzantine robustness"],
        "Transfer Learning": ["domain shift", "negative transfer", "catastrophic forgetting", "continual learning"],
        "Generative AI": ["latent space interpolation", "mode collapse", "style control", "conditional generation"],
        "Knowledge Graphs": ["triple extraction", "entity resolution", "knowledge completion", "graph embedding"],
        "Multi-Modal Learning": ["modality fusion", "cross-modal retrieval", "representation alignment", "missing modality"],
        "Edge AI": ["model pruning", "neural compression", "hardware acceleration", "distributed inference"],
        "Neural Architecture Search": ["search space design", "performance estimation", "architecture encoding", "evolutionary search"]
    }
    
    templates = domain_templates.get(domain, [
        "Novel Approaches to {topic} in {domain}",
        "Advanced {topic} Techniques for {domain}",
        "Efficient {topic} Implementation in {domain}",
        "Optimization Strategies for {topic} in {domain}"
    ])
    
    topics = domain_topics.get(domain, ["system optimization", "performance analysis"])
    
    template = random.choice(templates)
    topic = random.choice(topics)
    
    # For templates that need hardware specification
    if "{hardware}" in template:
        hardware_options = ["ARM Cortex-M", "RISC-V", "ESP32", "STM32", "Arduino"]
        return template.format(topic=topic, hardware=random.choice(hardware_options))
    
    return template.format(topic=topic, domain=domain)

def generate_paper_abstract(domain, keywords, fake_instance):
    """Generate realistic paper abstract based on specific ECE domain"""
    
    # Domain-specific abstract templates
    domain_intros = {
        "Theoretical Computer Science": [
            "This paper investigates the theoretical foundations of {topic}, focusing on computational complexity and formal analysis.",
            "We present a rigorous mathematical framework for {topic} with emphasis on algorithmic decidability.",
            "The computational complexity of {topic} is analyzed through formal methods and complexity theory.",
        ],
        "Algorithm Design": [
            "We propose an efficient algorithm for {topic} with improved time and space complexity bounds.",
            "This work presents a novel algorithmic approach to {topic} optimization with provable performance guarantees.",
            "An innovative {topic} algorithm is developed with logarithmic complexity improvements over existing methods.",
        ],
        "Embedded Systems": [
            "This paper presents a real-time embedded implementation of {topic} for resource-constrained IoT devices.",
            "We develop a low-power {topic} solution optimized for microcontroller-based embedded systems.",
            "A hardware-software co-design approach for {topic} is proposed for embedded applications.",
        ],
        "Computer Architecture": [
            "We present a novel microarchitectural design for {topic} with enhanced performance and energy efficiency.",
            "This work introduces cache-aware {topic} optimization techniques for modern multi-core processors.",
            "A high-throughput {topic} architecture is proposed with improved instruction-level parallelism.",
        ],
        "Deep Learning": [
            "This paper introduces a novel deep neural network architecture for {topic} with attention mechanisms.",
            "We propose a transformer-based model for {topic} that achieves state-of-the-art performance.",
            "A federated learning framework for {topic} is developed to address privacy and scalability concerns.",
        ],
        "Cybersecurity": [
            "This work presents advanced cryptographic techniques for secure {topic} in distributed environments.",
            "We develop a machine learning-based approach for {topic} threat detection and mitigation.",
            "A zero-trust security framework for {topic} is proposed with end-to-end encryption.",
        ],
        "Software Engineering": [
            "This paper introduces automated testing methodologies for {topic} in agile development environments.",
            "We present a DevOps-integrated framework for {topic} with continuous integration and deployment.",
            "A microservices architecture for scalable {topic} applications is developed and evaluated.",
        ],
        "Signal Processing": [
            "This work presents advanced digital signal processing techniques for {topic} with real-time constraints.",
            "We develop adaptive filtering algorithms for {topic} noise reduction in challenging environments.",
            "A spectral analysis framework for {topic} is proposed using wavelet transforms and FFT optimization.",
        ],
        "Communications": [
            "This paper introduces novel {topic} techniques for next-generation 5G/6G wireless networks.",
            "We present MIMO-based {topic} algorithms for high-speed millimeter-wave communications.",
            "A software-defined radio implementation of {topic} is developed for cognitive radio systems.",
        ],
        "VLSI Design": [
            "This work presents low-power {topic} circuit designs optimized for nanometer CMOS technologies.",
            "We develop radiation-hardened {topic} circuits for space and aerospace applications.",
            "A high-speed {topic} ASIC implementation is proposed with advanced physical design optimization.",
        ],
        "Control Systems": [
            "This paper presents adaptive control strategies for {topic} in nonlinear dynamic systems.",
            "We develop model predictive control algorithms for {topic} with uncertainty quantification.",
            "A distributed control framework for {topic} networks is proposed with consensus algorithms.",
        ],
        "Power Electronics": [
            "This work introduces high-efficiency {topic} converter topologies using wide-bandgap semiconductors.",
            "We present grid-tied {topic} systems with advanced power quality enhancement techniques.",
            "A thermal management solution for high-power {topic} devices is developed and validated.",
        ],
        "Quantum Computing": [
            "This paper presents quantum {topic} algorithms optimized for near-term quantum devices.",
            "We develop variational quantum circuits for {topic} with improved noise resilience.",
            "A quantum error correction scheme for {topic} is proposed using surface codes.",
        ],
        "Computer Networks": [
            "This work presents software-defined networking solutions for {topic} in edge computing environments.",
            "We develop QoS-aware {topic} routing algorithms for multi-tier network architectures.",
            "A network function virtualization framework for {topic} is proposed with service chaining.",
        ],
        "Database Systems": [
            "This paper introduces distributed {topic} management techniques for cloud-native applications.",
            "We present NoSQL optimization strategies for {topic} workloads with improved scalability.",
            "A blockchain-based {topic} integrity framework is developed for decentralized systems.",
        ]
    }
    
    # Domain-specific methodology descriptions
    domain_methods = {
        "Theoretical Computer Science": [
            "Our approach employs formal verification techniques and complexity analysis to establish theoretical bounds.",
            "The methodology combines automata theory with algebraic structures for rigorous mathematical proofs.",
        ],
        "Algorithm Design": [
            "The algorithm utilizes advanced data structures and dynamic programming for optimal time complexity.",
            "Our approach leverages graph-theoretic properties and approximation schemes for efficient computation.",
        ],
        "Embedded Systems": [
            "The implementation uses real-time operating system scheduling with interrupt-driven architectures.",
            "Our design employs power management techniques and sensor fusion for optimal resource utilization.",
        ],
        "Computer Architecture": [
            "The architecture incorporates branch prediction mechanisms and cache optimization for performance enhancement.",
            "Our design utilizes instruction pipelining and memory hierarchy optimization for throughput improvement.",
        ],
        "Deep Learning": [
            "The model architecture employs multi-head attention and residual connections for improved learning.",
            "Our approach utilizes transfer learning and data augmentation for enhanced generalization.",
        ],
        "Cybersecurity": [
            "The framework implements homomorphic encryption and secure multi-party computation protocols.",
            "Our approach employs adversarial training and differential privacy for robust security.",
        ],
        "Software Engineering": [
            "The methodology incorporates static analysis tools and automated code generation techniques.",
            "Our framework utilizes continuous integration pipelines and containerization for deployment.",
        ],
        "Signal Processing": [
            "The algorithm employs adaptive filtering and multirate signal processing for optimal performance.",
            "Our approach utilizes compressed sensing and sparse reconstruction for efficient signal recovery.",
        ],
        "Communications": [
            "The system implements advanced modulation schemes and channel coding for reliable transmission.",
            "Our approach employs beamforming and interference cancellation for improved signal quality.",
        ],
        "VLSI Design": [
            "The design utilizes clock tree synthesis and power gating for energy-efficient operation.",
            "Our approach employs design-for-test methodologies and timing closure optimization.",
        ],
        "Control Systems": [
            "The controller implements state estimation and optimal control theory for system stability.",
            "Our approach utilizes fault detection algorithms and robust control design principles.",
        ],
        "Power Electronics": [
            "The converter employs pulse-width modulation and power factor correction for efficient operation.",
            "Our design utilizes soft-switching techniques and magnetic component optimization.",
        ],
        "Quantum Computing": [
            "The algorithm employs quantum gate synthesis and circuit optimization for NISQ devices.",
            "Our approach utilizes variational principles and parameter optimization for quantum advantage.",
        ],
        "Computer Networks": [
            "The framework implements traffic engineering and load balancing for network optimization.",
            "Our approach employs machine learning and network monitoring for intelligent routing.",
        ],
        "Database Systems": [
            "The system utilizes query optimization and indexing strategies for improved performance.",
            "Our approach employs distributed consensus and transaction processing for data consistency.",
        ]
    }
    
    # Domain-specific results
    domain_results = {
        "Theoretical Computer Science": [
            "Theoretical analysis proves polynomial-time complexity with logarithmic space bounds.",
            "The formal verification establishes correctness guarantees and computational limits.",
        ],
        "Algorithm Design": [
            "Performance evaluation demonstrates O(n log n) time complexity with constant space overhead.",
            "Experimental results show 40-60% improvement over state-of-the-art algorithms.",
        ],
        "Embedded Systems": [
            "Hardware testing validates real-time performance with microsecond response times.",
            "Power consumption analysis shows 30-50% energy savings compared to existing solutions.",
        ],
        "Computer Architecture": [
            "Synthesis results demonstrate 25% improvement in instructions per cycle with reduced power.",
            "FPGA implementation achieves clock frequencies exceeding 500 MHz with optimal resource utilization.",
        ],
        "Deep Learning": [
            "Experimental validation achieves 95%+ accuracy with 20% reduction in computational overhead.",
            "Cross-validation results demonstrate superior generalization across multiple benchmark datasets.",
        ],
        "Cybersecurity": [
            "Security analysis proves resilience against advanced persistent threats and side-channel attacks.",
            "Performance evaluation shows minimal overhead while maintaining cryptographic strength.",
        ],
        "Software Engineering": [
            "Testing results demonstrate 90% code coverage with automated bug detection capabilities.",
            "Deployment metrics show 50% reduction in development time with improved software quality.",
        ],
        "Signal Processing": [
            "Signal-to-noise ratio improvements of 15-25 dB are achieved across frequency bands.",
            "Real-time processing capabilities are validated with sampling rates up to 1 GSPS.",
        ],
        "Communications": [
            "Channel capacity analysis demonstrates throughput improvements of 2-3x over existing systems.",
            "Bit error rate measurements show performance within 1 dB of theoretical Shannon limits.",
        ],
        "VLSI Design": [
            "Post-layout simulation confirms timing closure with setup/hold margin improvements.",
            "Power analysis shows 40% reduction in dynamic power with maintained performance targets.",
        ],
        "Control Systems": [
            "Stability analysis confirms robust performance under parameter variations and disturbances.",
            "Simulation results demonstrate convergence within specified settling time constraints.",
        ],
        "Power Electronics": [
            "Efficiency measurements exceed 95% across wide load ranges with improved thermal performance.",
            "Harmonic distortion analysis shows compliance with grid codes and power quality standards.",
        ],
        "Quantum Computing": [
            "Quantum advantage is demonstrated for specific problem instances with exponential speedup.",
            "Error rate analysis shows improvement in quantum gate fidelity and coherence times.",
        ],
        "Computer Networks": [
            "Network performance analysis shows latency reduction and throughput improvements of 30-40%.",
            "Scalability testing validates operation across thousands of network nodes.",
        ],
        "Database Systems": [
            "Query performance evaluation demonstrates 2-5x speedup for complex analytical workloads.",
            "Consistency analysis confirms ACID properties under high-concurrency scenarios.",
        ]
    }
    
    # Generate domain-specific abstract
    intro_options = domain_intros.get(domain, [
        f"This paper addresses key challenges in {domain} through innovative approaches."
    ])
    
    method_options = domain_methods.get(domain, [
        f"Our methodology combines theoretical analysis with practical {random.choice(keywords)} implementation."
    ])
    
    result_options = domain_results.get(domain, [
        f"Experimental results validate the effectiveness of our {random.choice(keywords)} approach."
    ])
    
    # Select components
    intro = random.choice(intro_options).format(topic=random.choice(keywords))
    method = random.choice(method_options)
    results = random.choice(result_options)
    
    conclusion_templates = [
        f"These findings advance the state-of-the-art in {domain} research and provide practical insights for system designers.",
        f"The proposed approach opens new research directions in {domain} with significant implications for industry applications.",
        f"This work contributes to the theoretical understanding and practical implementation of {domain} systems.",
    ]
    
    conclusion = random.choice(conclusion_templates)
    
    return f"{intro} {method} {results} {conclusion}"

def main():
    """Main seeding function"""
    print("Starting data seeding process...")
    print("=" * 50)
    
    # Create Flask app
    app = create_app()
    
    try:
        # Seed users (100 users)
        user_ids = seed_users(app, count=100)
        
        if not user_ids:
            print("Error: No users were created. Stopping seeding process.")
            return
        
        # Seed papers (1000 papers)
        paper_ids = seed_papers(app, user_ids, count=1000)
        
        if not paper_ids:
            print("Error: No papers were created. Stopping seeding process.")
            return
            
        # Add citations between papers
        add_citations(app, paper_ids, min_citations=0, max_citations=10)
        
        print("=" * 50)
        print("Data seeding completed successfully!")
        print(f"Created: {len(user_ids)} users, {len(paper_ids)} papers")
        
        # Optional: Print some statistics
        with app.app_context():
            db = app.mongo_db  # type: ignore
            
            # Count total citations in the citations collection
            total_citations = db.citations.count_documents({})
            
            # Count users and papers
            total_users = db.users.count_documents({})
            total_papers = db.papers.count_documents({})
            
            print(f"Total citations: {total_citations}")
            print(f"Database totals: {total_users} users, {total_papers} papers")
        
    except Exception as e:
        print(f"Error during seeding: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
