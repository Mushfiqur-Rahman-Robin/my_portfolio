import './css/SkillsSection.css';

interface Skill {
  name: string;
  level: number; // Percentage 0-100
}

const skills: Skill[] = [
  { name: 'Python', level: 95 },
  // { name: 'JavaScript', level: 80 },
  { name: 'C / C++', level: 70 },
  { name: 'HTML / CSS / SQL', level: 90 },

  { name: 'TensorFlow', level: 90 },
  { name: 'PyTorch', level: 85 },
  { name: 'Keras', level: 85 },
  { name: 'Scikit-learn', level: 90 },
  { name: 'Flask / FastAPI / Streamlit', level: 80 },
  { name: 'Langchain', level: 75 },

  { name: 'Django', level: 90 },
  { name: 'Django REST Framework', level: 85 },
  { name: 'React', level: 80 },
  { name: 'PostgreSQL', level: 85 },
  { name: 'Docker', level: 80 },
  { name: 'Git & GitHub', level: 95 },
  { name: 'CI/CD (GitHub Actions, CircleCI)', level: 75 },
  { name: 'Nginx', level: 70 },
  { name: 'Monitoring (Prometheus, Grafana)', level: 60 },
  { name: 'Big Data (PySpark)', level: 65 },
  { name: 'Caching (Redis)', level: 70 },
  { name: 'Web-scrapping (BeautifulSoup, Selenium)', level: 85 },
  { name: 'Jira', level: 80 },
  { name: 'OCR', level: 75 },
  { name: 'Azure AI Document Intelligence', level: 60 },
  { name: 'Apify', level: 60 },

  { name: 'Exploratory Data Analysis', level: 90 },
  { name: 'Statistics', level: 85 },
  { name: 'Hypothesis Testing', level: 80 },
  { name: 'Supervised ML', level: 90 },
  { name: 'Unsupervised ML', level: 80 },
  { name: 'Computer Vision', level: 85 },
  { name: 'Natural Language Processing (NLP)', level: 85 },
  { name: 'Time-Series Forecasting', level: 75 },
  { name: 'Generative AI', level: 70 },
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
