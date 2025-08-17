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
                "Computer Science", "Information Systems", "Software Engineering",
                "Data Science", "Artificial Intelligence", "Cybersecurity"
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
    
    # Research domains for realistic papers
    domains = [
        "Computer Science", "Machine Learning", "Artificial Intelligence",
        "Data Science", "Software Engineering", "Cybersecurity",
        "Database Systems", "Distributed Systems", "Computer Vision",
        "Natural Language Processing", "Robotics", "Human-Computer Interaction"
    ]
    
    # Keywords for each domain
    domain_keywords = {
        "Computer Science": ["algorithm", "computation", "programming", "software"],
        "Machine Learning": ["neural networks", "deep learning", "classification", "regression"],
        "Artificial Intelligence": ["AI", "intelligent systems", "automation", "reasoning"],
        "Data Science": ["big data", "analytics", "mining", "visualization"],
        "Software Engineering": ["development", "testing", "architecture", "methodology"],
        "Cybersecurity": ["security", "encryption", "privacy", "vulnerability"],
        "Database Systems": ["SQL", "NoSQL", "indexing", "transactions"],
        "Distributed Systems": ["scalability", "fault tolerance", "consistency", "microservices"],
        "Computer Vision": ["image processing", "object detection", "recognition", "segmentation"],
        "Natural Language Processing": ["text analysis", "language models", "sentiment", "parsing"],
        "Robotics": ["automation", "sensors", "control systems", "navigation"],
        "Human-Computer Interaction": ["usability", "interface design", "user experience", "accessibility"]
    }
    
    # Journal/Conference names
    venues = [
        "IEEE Transactions on Software Engineering",
        "ACM Computing Surveys", "Nature Machine Intelligence",
        "Journal of Machine Learning Research", "International Conference on Machine Learning",
        "Conference on Neural Information Processing Systems", "ACM SIGMOD",
        "IEEE Computer Vision and Pattern Recognition", "International Joint Conference on Artificial Intelligence"
    ]
    
    papers = []
    with app.app_context():
        for i in range(count):
            # Select random domain and author
            domain = random.choice(domains)
            author_id = random.choice(user_ids)            
            title = generate_paper_title(domain, fake)
            abstract = generate_paper_abstract(domain, domain_keywords[domain], fake)
            keywords = random.sample(domain_keywords[domain], k=random.randint(2, 4))            
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
    """Generate realistic paper title based on domain"""
    templates = [
        "A Novel Approach to {topic} in {domain}",
        "Efficient {method} for {topic}: A {domain} Perspective", 
        "Deep Learning Techniques for {topic} in {domain}",
        "Optimizing {method} Performance in {domain} Applications",
        "Machine Learning-Based {topic} Analysis for {domain}",
        "Scalable {method} Architecture for {domain} Systems",
        "Comparative Study of {topic} Methods in {domain}",
        "Real-time {topic} Processing Using {method}",
        "Advanced {topic} Algorithms for {domain} Applications",
        "Secure {method} Implementation in {domain} Environments"
    ]
    
    domain_topics = {
        "Computer Science": ["algorithm design", "data structures", "computational complexity"],
        "Machine Learning": ["feature selection", "model optimization", "pattern recognition"],
        "Artificial Intelligence": ["knowledge representation", "decision making", "cognitive modeling"],
        "Data Science": ["predictive analytics", "data mining", "statistical modeling"],
        "Software Engineering": ["code quality", "software testing", "design patterns"],
        "Cybersecurity": ["threat detection", "access control", "vulnerability assessment"],
        "Database Systems": ["query optimization", "data indexing", "transaction processing"],
        "Distributed Systems": ["load balancing", "consensus algorithms", "distributed computing"],
        "Computer Vision": ["image recognition", "object tracking", "feature extraction"],
        "Natural Language Processing": ["text classification", "language understanding", "semantic analysis"],
        "Robotics": ["path planning", "sensor fusion", "autonomous navigation"],
        "Human-Computer Interaction": ["user interface design", "interaction modeling", "accessibility features"]
    }
    
    domain_methods = [
        "neural networks", "genetic algorithms", "reinforcement learning",
        "blockchain technology", "cloud computing", "edge computing",
        "microservices", "containerization", "API design"
    ]
    
    template = random.choice(templates)
    topic = random.choice(domain_topics.get(domain, ["system design"]))
    method = random.choice(domain_methods)
    
    return template.format(topic=topic, method=method, domain=domain)

def generate_paper_abstract(domain, keywords, fake_instance):
    """Generate realistic paper abstract"""
    # Abstract templates
    intro_templates = [
        "This paper presents a comprehensive study of {topic} in the context of {domain}.",
        "We propose a novel approach to address the challenges of {topic} in {domain} applications.",
        "Recent advances in {domain} have highlighted the importance of {topic} research.",
        "The increasing complexity of {domain} systems requires innovative solutions for {topic}."
    ]
    
    method_templates = [
        "Our methodology combines {method1} with {method2} to achieve improved performance.",
        "We implement a {method1}-based framework that leverages {method2} techniques.",
        "The proposed solution utilizes {method1} algorithms enhanced with {method2} capabilities.",
        "Our approach integrates {method1} and {method2} methodologies for optimal results."
    ]
    
    result_templates = [
        "Experimental results demonstrate significant improvements in accuracy and efficiency.",
        "Performance evaluation shows our method outperforms existing approaches by {improvement}%.",
        "The proposed system achieves {metric} improvements compared to baseline methods.",
        "Comprehensive testing validates the effectiveness of our approach across multiple datasets."
    ]
    
    conclusion_templates = [
        "These findings contribute to the advancement of {domain} research and practice.",
        "The results have important implications for future {domain} system design.",
        "This work opens new avenues for research in {domain} and related fields.",
        "The proposed method provides a foundation for next-generation {domain} applications."
    ]
    
    # Generate abstract components
    intro = random.choice(intro_templates).format(
        topic=random.choice(keywords),
        domain=domain
    )
    
    method = random.choice(method_templates).format(
        method1=random.choice(keywords),
        method2=random.choice(keywords)
    )
    
    results = random.choice(result_templates).format(
        improvement=random.randint(10, 50),
        metric=random.choice(["performance", "accuracy", "efficiency", "scalability"])
    )
    
    conclusion = random.choice(conclusion_templates).format(domain=domain)
    
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
