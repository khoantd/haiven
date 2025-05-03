// Global test setup for Vitest/jsdom

if (!window.getComputedStyle) {
  window.getComputedStyle = () => ({
    getPropertyValue: () => '',
  });
} 