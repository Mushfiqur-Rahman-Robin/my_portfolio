// Removed `import React from 'react';`
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
            Hello! I'm [Your Name], a passionate Full-Stack Developer with
            expertise in building robust and scalable web applications. My
            journey in tech began with a curiosity for how things work, which
            quickly evolved into a love for crafting efficient and user-friendly
            software solutions.
          </p>
          <p>
            I specialize in the **Django** framework for the backend, leveraging
            its power and flexibility to create secure and performant APIs. On
            the frontend, I primarily work with **React** and **TypeScript**,
            building dynamic and responsive user interfaces that deliver
            excellent user experiences.
          </p>
          <p>
            Beyond coding, I'm deeply interested in **DevOps practices**,
            including **Docker** for containerization, **GitHub Actions** for CI/CD,
            and deploying applications on cloud platforms like Render and Vercel. I
            believe in writing clean, maintainable code and following best
            practices to ensure long-term project success.
          </p>
          <p>
            When I'm not coding, you can find me exploring new technologies,
            contributing to open source projects, or [mention a hobby or
            interest, e.g., reading sci-fi novels, hiking, playing chess]. I'm
            always eager to learn and grow, and I thrive in collaborative
            environments.
          </p>
        </div>
      </div>
    </div>
  );
};

export default About;
