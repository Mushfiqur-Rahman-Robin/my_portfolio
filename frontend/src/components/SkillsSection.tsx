import './css/SkillsSection.css';

interface Skill {
  name: string;
  level: number; // Percentage 0-100
}

const skills: Skill[] = [
  { name: 'Python', level: 95 },
  { name: 'SQL', level: 80 },
  { name: 'Go', level: 65 },
  { name: 'HTML / CSS', level: 80 },
  { name: 'C / C++', level: 70 },
  { name: 'Flask / FastAPI / Streamlit', level: 85 },
  { name: 'Django', level: 70 },
  { name: 'React', level: 60 },
  { name: 'Supervised ML', level: 95 },
  { name: 'Scikit-learn', level: 90 },
  { name: 'TensorFlow', level: 90 },
  { name: 'EDA', level: 90 },
  { name: 'PyTorch', level: 85 },
  { name: 'Keras', level: 85 },
  { name: 'NLP', level: 85 },
  { name: 'Computer Vision', level: 85 },
  { name: 'Generative AI', level: 85 },
  { name: 'Agentic AI', level: 90 },
  { name: 'LangChain', level: 85 },
  { name: 'Unsupervised ML', level: 85 },
  { name: 'Statistics', level: 85 },
  { name: 'LangGraph', level: 80 },
  { name: 'Hypothesis Testing', level: 80 },
  { name: 'Time-Series Forecasting', level: 75 },
  { name: 'MLOps', level: 75 },
  { name: 'MLflow', level: 75 },
  { name: 'DVC', level: 70 },
  { name: 'Airflow', level: 70 },
  { name: 'AWS', level: 70 },
  { name: 'AWS SageMaker', level: 70 },
  { name: 'Git & GitHub', level: 90 },
  { name: 'Docker', level: 85 },
  { name: 'CI/CD (GitHub Actions, CircleCI)', level: 75 },
  { name: 'Nginx', level: 70 },
  { name: 'Caching (Redis)', level: 70 },
  { name: 'Monitoring (Prometheus, Grafana)', level: 60 },
  { name: 'Web Scraping (BS4, Selenium)', level: 85 },
  { name: 'n8n', level: 75 },
  { name: 'Claude Code', level: 70 },
];

const SkillsSection: React.FC = () => {
  return (
    <section className="skills-section">
      <h2>Technical Skills</h2>
      <div className="skills-panel">
        <div className="skill-list-grid">
          {skills.map((skill) => (
            <div className="skill-item" key={skill.name}>
              <div className="skill-head">
                <span className="skill-name">{skill.name}</span>
                <span className="skill-level">{skill.level}%</span>
              </div>
              <div className="skill-bar-container">
                <div
                  className="skill-bar-fill"
                  style={{ width: `${skill.level}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default SkillsSection;
