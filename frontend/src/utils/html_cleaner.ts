// frontend/src/utils/html_cleaner.ts

/**
 * Strips HTML tags from a string using DOMParser, and normalizes whitespace.
 * This is the frontend equivalent of the backend's `clean_html` for displaying plain text.
 * @param htmlString The string containing HTML content.
 * @returns The string with all HTML tags removed and whitespace normalized.
 */
export const stripHtmlTags = (htmlString: string): string => {
  if (!htmlString) {
    return "";
  }
  try {
    const doc = new DOMParser().parseFromString(htmlString, 'text/html');
    let text = doc.body.textContent || "";

    // Normalize whitespace: replace multiple newlines/spaces with a single space, then trim.
    text = text.replace(/(\r\n|\n|\r)/gm, " "); // Replace all newline variations with a space
    text = text.replace(/\s+/g, " ").trim();    // Replace multiple spaces with a single space and trim

    return text;
  } catch (e) {
    console.error("Error parsing HTML string for stripping tags:", e);
    return htmlString; // Fallback: return original string if parsing fails, to avoid breaking the display
  }
};
