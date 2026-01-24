// frontend/src/pages/About.tsx
import './css/About.css';

const About: React.FC = () => {
  return (
    <div className="about-container">
      <h1>About Me</h1>
      {/* The main content area where image and text will interact */}
      <div className="about-content-wrapper"> {/* NEW Wrapper for overall content block */}
        <div className="about-text">
          {/* IMAGE IS NOW INSIDE THE ABOUT-TEXT DIV */}
          <div className="about-image">
            <img src="/website_about.png" alt="Profile Picture" />
          </div>

          <p>
            Hello! I'm Md Mushfiqur Rahman, a full-stack data scientist with more than 3 years of professional experience. I strive to tackle real-world challenges using my technical expertise in Data Science. I thrive in environments where research work is valued alongside routine tasks, constantly motivated to learn and stay updated with the latest tools and technologies in the ever-evolving data-driven world.
          </p>
          <p>
            Currently, I serve as an AI/ML Team Lead, focusing on designing and
            implementing advanced Machine Learning and Generative AI systems. My
            work involves leading the development of innovative AI solutions,
            including architecting and deploying complex agentic AI systems
            and solutions built upon Large Language Models (LLMs). I contribute
            to system design and ensure the smooth execution and deployment of AI-
            powered projects. My core areas of interest include Statistics, Data
            Science, Machine Learning, Deep Learning, Generative AI, and
            Cryptocurrency. I possess a solid understanding of various machine
            learning and deep learning algorithms, always making an effort to
            keep pace with new tools and technologies in the AI domain.
          </p>
          <p>
            I believe in "Learning is Surviving!" – a philosophy that guides my
            approach to continuous professional development. As an active
            learner, I constantly keep myself updated with AI trends and
            innovations by reading LinkedIn posts from top AI figures. I
            participate in Kaggle contests and maintain a strong presence on
            LinkedIn and GitHub, alongside conducting research work utilizing my
            knowledge in machine learning and deep learning. I think like a
            Software Engineer and work like a Data Scientist, with a particular
            passion for collecting and analyzing datasets. I am very passionate
            about my work, adhering strictly to schedules to ensure projects are
            completed before deadlines. I believe in ultimate professionalism in
            my work ethic.
          </p>
          <div className="clearfix"></div> {/* Used to clear the float */}
        </div>
      </div>
    </div>
  );
};

export default About;
