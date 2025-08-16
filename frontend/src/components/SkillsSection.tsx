import './css/SkillsSection.css';

interface Skill {
  name: string;
  level: number; // Percentage 0-100
}

const skills: Skill[] = [
  // Programming Languages & Frameworks (prioritized)
  { name: 'Python', level: 95 },
  { name: 'SQL', level: 80 },
  { name: 'Go', level: 65 },
  { name: 'HTML / CSS', level: 80 },
  { name: 'C / C++', level: 70 },
  { name: 'Flask / FastAPI / Streamlit', level: 85 },
  { name: 'Django', level: 70 },
  // { name: 'Django REST Framework', level: 70 },
  { name: 'React', level: 60 },

  // AI/ML & Data Science Tools
  { name: 'Scikit-learn', level: 90 },
  { name: 'TensorFlow', level: 90 },
  { name: 'PyTorch', level: 85 },
  { name: 'Keras', level: 85 },
  { name: 'Langchain', level: 85 },
  { name: 'LangGraph', level: 80 },
  { name: 'Exploratory Data Analysis', level: 90 },
  { name: 'Natural Language Processing (NLP)', level: 85 },
  { name: 'Computer Vision', level: 85 },
  { name: 'Statistics', level: 85 },
  { name: 'Supervised ML', level: 95 },
  { name: 'Unsupervised ML', level: 85 },
  { name: 'Generative AI', level: 85 },
  { name: 'Time-Series Forecasting', level: 75 },
  // { name: 'Hypothesis Testing', level: 80 },

  // DevOps, Infra, Deployment
  { name: 'Docker', level: 80 },
  { name: 'Git & GitHub', level: 90 },
  { name: 'CI/CD (GitHub Actions, CircleCI)', level: 75 },
  { name: 'Nginx', level: 70 },
  { name: 'Monitoring (Prometheus, Grafana)', level: 60 },
  { name: 'Caching (Redis)', level: 70 },

  // Other Technical/Support Skills
  // { name: 'MySQL', level: 80 },
  // { name: 'PostgreSQL', level: 80 },
  { name: 'MLOps', level: 75 },
  { name: 'Web-scrapping (BeautifulSoup, Selenium)', level: 85 },
];


const SkillsSection: React.FC = () => {
  return (
    <section className="skills-section">
      <h2>My Skills</h2>
      <div className="skills-grid">
        {skills.map((skill, index) => (
          <div className="skill-item" key={index}>
            <span className="skill-name">{skill.name}</span>
            <div className="skill-bar-container">
              <div
                className="skill-bar-fill"
                style={{ width: `${skill.level}%` }}
              ></div>
              {/* Removed skill level text span */}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};

export default SkillsSection;
