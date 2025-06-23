// Removed `import React from 'react';`
import './Home.css';

const Home: React.FC = () => {
  return (
    <div className="home-container">
      <section className="hero-section">
        <h1>Welcome to My Personal Portfolio!</h1>
        <p>
          Showcasing my journey in software development, including projects,
          publications, and certifications.
        </p>
        <div className="cta-buttons">
          <a href="/projects" className="btn primary">
            View Projects
          </a>
          <a href="/contact" className="btn secondary">
            Get in Touch
          </a>
        </div>
      </section>

      <section className="highlights-section">
        <h2>What I Do</h2>
        <div className="highlights-grid">
          <div className="highlight-card">
            <h3>Full-Stack Development</h3>
            <p>
              Building robust and scalable web applications with Django, React,
              and modern architectural patterns.
            </p>
          </div>
          <div className="highlight-card">
            <h3>DevOps & Cloud</h3>
            <p>
              Automating deployments, managing infrastructure, and deploying
              applications on cloud platforms using Docker and CI/CD.
            </p>
          </div>
          <div className="highlight-card">
            <h3>Problem Solving</h3>
            <p>
              Passionate about tackling complex challenges and delivering
              efficient, elegant solutions.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
