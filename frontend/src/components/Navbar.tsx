import { Link } from 'react-router-dom';
import './Navbar.css';

const Navbar: React.FC = () => {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          My Portfolio
        </Link>
        <ul className="nav-menu">
          <li className="nav-item">
            <Link to="/" className="nav-links">
              Home
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/about" className="nav-links">
              About
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/projects" className="nav-links">
              Projects
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/certifications" className="nav-links">
              Certifications
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/publications" className="nav-links">
              Publications
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/achievements" className="nav-links">
              Achievements
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/experience" className="nav-links">
              Experience
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/resume" className="nav-links">
              Resume
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/contact" className="nav-links">
              Contact
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;
