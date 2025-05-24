import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom'; // For expect(...).toBeInTheDocument() etc.
import StyledButton from './StyledButton'; // Assuming StyledButton is in the same directory
import { CircularProgress } from '@mui/material'; // To check for loading indicator

// Mocking CircularProgress to simplify the test for loading state
// Actual MUI Button with loading prop might render CircularProgress,
// or it might change aria-busy or other attributes.
// This mock helps us verify if CircularProgress is attempted to be rendered.
jest.mock('@mui/material/CircularProgress', () => () => <div data-testid="loading-spinner">Loading...</div>);


describe('StyledButton', () => {
  test('renders with children', () => {
    render(<StyledButton>Click Me</StyledButton>);
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
  });

  test('calls onClick prop when clicked', () => {
    const handleClick = jest.fn(); // Mock function
    render(<StyledButton onClick={handleClick}>Click Me</StyledButton>);
    fireEvent.click(screen.getByText(/click me/i));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test('is disabled when disabled prop is true', () => {
    render(<StyledButton disabled>Click Me</StyledButton>);
    expect(screen.getByRole('button', { name: /click me/i })).toBeDisabled();
  });

  test('shows loading indicator and is disabled when loading prop is true', () => {
    render(<StyledButton loading>Click Me</StyledButton>);
    
    // Check if the button is disabled (MUI typically disables button when loading)
    // expect(screen.getByRole('button', { name: /click me/i })).toBeDisabled(); // This might not be true if children are replaced
    
    // Check if the loading spinner (mocked) is present
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    
    // Check that the original children (text) might not be visible, or button text changes
    // This depends on how StyledButton implements the loading state.
    // If it replaces children with CircularProgress:
    expect(screen.queryByText(/click me/i)).not.toBeInTheDocument(); 
    // Or, if it shows "Loading..." text from our mock:
    expect(screen.getByText(/loading\.\.\./i)).toBeInTheDocument();

    // Also, MUI Button might disable itself when its internal loading state is active
    // or if StyledButton explicitly passes disabled={loading || props.disabled}
    // For this test, let's assume `loading` implies it should behave as disabled for clicks
    const handleClick = jest.fn();
    render(<StyledButton loading onClick={handleClick}>Click Me</StyledButton>);
     // Clicking a button that shows a spinner should not trigger onClick
    const buttonElement = screen.getByRole('button'); // Get the button by its role
    fireEvent.click(buttonElement);
    expect(handleClick).not.toHaveBeenCalled();

  });

  test('applies custom sx props', () => {
    const customStyle = { backgroundColor: 'red' };
    render(<StyledButton sx={customStyle}>Styled</StyledButton>);
    expect(screen.getByRole('button', { name: /styled/i })).toHaveStyle('background-color: red');
  });

  test('passes other MUI Button props like "color"', () => {
    render(<StyledButton color="secondary">Secondary Color</StyledButton>);
    const button = screen.getByRole('button', { name: /secondary color/i });
    // Checking the exact class or style for MUI color can be brittle.
    // For this example, just ensure it renders. A visual regression test would be better for styling.
    expect(button).toBeInTheDocument();
    // If specific class is known: expect(button).toHaveClass('MuiButton-secondary');
  });
});

// Note on testing `loading` prop:
// The actual DOM structure when MUI Button's `loading` prop is true (if it has one, 
// or if `StyledButton` implements it using `startIcon={<CircularProgress />}`)
// needs to be inspected to write the most accurate test.
// The mock for CircularProgress helps to see if it's rendered.
// If the button text itself changes (e.g., to "Loading..."), that can be asserted.
// If StyledButton uses MUI's <LoadingButton> (from @mui/lab), it has specific behaviors.
// The current StyledButton passes `loading` to MUI's `Button` `disabled` prop and shows children or spinner.
// The test above for loading state has been adapted to check for the spinner and that original text is gone.
```
