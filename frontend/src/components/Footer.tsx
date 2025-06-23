import './Footer.css';

const Footer: React.FC = () => {
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="social-links">
          <a
            href="https://github.com/yourusername" // Replace with your GitHub URL
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub
          </a>
          <a
            href="https://linkedin.com/in/yourusername" // Replace with your LinkedIn URL
            target="_blank"
            rel="noopener noreferrer"
          >
            LinkedIn
          </a>
          <a
            href="https://twitter.com/yourusername" // Replace with your Twitter URL
            target="_blank"
            rel="noopener noreferrer"
          >
            Twitter
          </a>
          {/* Add more social media links as needed */}
        </div>
        <p>&copy; {new Date().getFullYear()} Your Name. All rights reserved.</p>
      </div>
    </footer>
  );
};

export default Footer;
