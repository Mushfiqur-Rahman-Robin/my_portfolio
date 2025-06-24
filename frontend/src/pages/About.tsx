import './About.css';

const About: React.FC = () => {
  return (
    <div className="about-container">
      <h1>About Me</h1>
      <div className="about-content">
        <div className="about-image">
          {/* You can replace this with your actual profile picture */}
          <img src="/src/assets/profile.jpg" alt="Profile Picture" />
        </div>
        <div className="about-text">
          <p>
            Hello! I'm **Md Mushfiqur Rahman**, a passionate **AI/ML Engineer** and Full-Stack Developer
            with expertise in building robust, scalable, and intelligent software solutions.
            My journey in tech is driven by a deep curiosity for solving complex problems and
            transforming ideas into practical applications.
          </p>
          <p>
            My core strength lies in **Artificial Intelligence** and **Machine Learning**, where
            I leverage frameworks like **TensorFlow**, **PyTorch**, and **Scikit-learn** to develop
            cutting-edge solutions in areas such as **Computer Vision**, **Natural Language Processing (NLP)**,
            and **Time-Series Forecasting**. I have significant experience crafting AI-powered agents,
            developing end-to-end data pipelines, and optimizing models for real-world performance.
          </p>
          <p>
            On the full-stack side, I build powerful backends with **Django** and **Django REST Framework**,
            and dynamic, responsive frontends with **React** and **TypeScript**. My work extends to
            **DevOps practices**, including **Docker** for containerization, and establishing robust **CI/CD pipelines**
            with **GitHub Actions** for seamless deployments.
          </p>
          <p>
            I thrive in collaborative environments, always eager to learn new technologies and contribute
            to impactful projects. When I'm not coding, you can find me engaged in continuous learning,
            exploring new research papers, or contributing to open-source initiatives.
          </p>
        </div>
      </div>
    </div>
  );
};

export default About;
