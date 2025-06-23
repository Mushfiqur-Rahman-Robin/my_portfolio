import React from 'react';
import './SkillsSection.css';

interface Skill {
  name: string;
  level: number; // Percentage 0-100
}

const skills: Skill[] = [
  { name: 'Python', level: 90 },
  { name: 'Data Science', level: 90 },
  { name: 'Django', level: 90 },
  { name: 'Django REST Framework', level: 85 },
  { name: 'React', level: 80 },
  { name: 'TypeScript', level: 75 },
  { name: 'JavaScript', level: 80 },
  { name: 'PostgreSQL', level: 85 },
  { name: 'Docker', level: 70 },
  { name: 'Git & GitHub', level: 90 },
  { name: 'CI/CD (GitHub Actions)', level: 65 },
  { name: 'HTML5 & CSS3', level: 95 },
  { name: 'SQL', level: 80 },
  { name: 'RESTful APIs', level: 90 },
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
              <span className="skill-level-text">{skill.level}%</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};

export default SkillsSection;
