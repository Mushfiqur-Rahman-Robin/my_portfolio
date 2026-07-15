import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Footer from '../components/Footer';

describe('<Footer />', () => {
  it('renders all primary social links with safe external attributes', () => {
    render(
      <MemoryRouter>
        <Footer />
      </MemoryRouter>,
    );

    const links = ['GitHub', 'LinkedIn', 'Facebook', 'Instagram', 'Hugging Face', 'Google Scholar'];
    for (const name of links) {
      const link = screen.getByRole('link', { name });
      expect(link).toHaveAttribute('target', '_blank');
      expect(link).toHaveAttribute('rel', 'noopener noreferrer');
      expect(link.getAttribute('href')).toMatch(/^https:\/\//);
    }
  });

  it('shows the copyright notice with the current year', () => {
    render(
      <MemoryRouter>
        <Footer />
      </MemoryRouter>,
    );
    const year = new Date().getFullYear();
    expect(
      screen.getByText(new RegExp(`${year} Md Mushfiqur Rahman`)),
    ).toBeInTheDocument();
  });
});
