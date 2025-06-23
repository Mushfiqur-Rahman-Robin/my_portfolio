import { useState } from 'react';
import axios from 'axios'; // Ensure axios is imported
import './Contact.css';

const Contact: React.FC = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: '',
  });
  const [status, setStatus] = useState<string | null>(null);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus('Sending message...');
    try {
      // Real API call to your backend
      const response = await axios.post(`${import.meta.env.VITE_API_URL}messages/`, formData);
      console.log('Message sent successfully:', response.data);
      setStatus('Message sent successfully!');
      setFormData({ name: '', email: '', message: '' }); // Clear form
    } catch (err) {
      console.error('Contact form submission error:', err);
      // More detailed error handling could check err.response.data for specific backend errors
      setStatus('Failed to send message. Please try again later.');
    }
  };

  return (
    <div className="contact-container">
      <h1>Contact Me</h1>
      <p className="contact-intro">
        Feel free to reach out to me for collaborations, inquiries, or just to
        say hello!
      </p>

      <div className="contact-methods">
        <div className="contact-item">
          <h3>Email</h3>
          <p>
            <a href="mailto:your.email@example.com">your.email@example.com</a>{' '}
            {/* Replace with your email */}
          </p>
        </div>
        <div className="contact-item">
          <h3>LinkedIn</h3>
          <p>
            <a
              href="https://linkedin.com/in/yourusername" // Replace with your LinkedIn
              target="_blank"
              rel="noopener noreferrer"
            >
              linkedin.com/in/yourusername
            </a>
          </p>
        </div>
        <div className="contact-item">
          <h3>GitHub</h3>
          <p>
            <a
              href="https://github.com/yourusername" // Replace with your GitHub
              target="_blank"
              rel="noopener noreferrer"
            >
              github.com/yourusername
            </a>
          </p>
        </div>
      </div>

      <h2 className="form-heading">Send me a message directly</h2>
      <form onSubmit={handleSubmit} className="contact-form">
        <div className="form-group">
          <label htmlFor="name">Name:</label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="email">Email:</label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="message">Message:</label>
          <textarea
            id="message"
            name="message"
            rows={6}
            value={formData.message}
            onChange={handleChange}
            required
          ></textarea>
        </div>
        <button type="submit" className="submit-btn">
          Send Message
        </button>
        {status && <p className="form-status">{status}</p>}
      </form>
    </div>
  );
};

export default Contact;
