import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BetaWarningDialog } from '../components/common/BetaWarningDialog';

describe('BetaWarningDialog', () => {
  it('renders dialog when open', () => {
    render(
      <BetaWarningDialog
        open={true}
        onClose={vi.fn()}
        onDismissForever={vi.fn()}
      />,
    );

    expect(screen.getByText(/Compte Beta - Phase de Test/i)).toBeTruthy();
    expect(screen.getByText(/Aucune limitation d'usage/i)).toBeTruthy();
    expect(screen.getByText(/freelansign@gmail.com/i)).toBeTruthy();
  });

  it('calls onClose when close button clicked', () => {
    const onClose = vi.fn();
    render(
      <BetaWarningDialog
        open={true}
        onClose={onClose}
        onDismissForever={vi.fn()}
      />,
    );

    fireEvent.click(screen.getByText(/J'ai compris/i));
    expect(onClose).toHaveBeenCalled();
  });

  it('calls onDismissForever when checkbox is checked', () => {
    const onDismissForever = vi.fn();
    render(
      <BetaWarningDialog
        open={true}
        onClose={vi.fn()}
        onDismissForever={onDismissForever}
      />,
    );

    const checkbox = screen.getByRole('checkbox');
    fireEvent.click(checkbox);
    fireEvent.click(screen.getByText(/J'ai compris/i));

    expect(onDismissForever).toHaveBeenCalled();
  });

  it('does not render when open is false', () => {
    render(
      <BetaWarningDialog
        open={false}
        onClose={vi.fn()}
        onDismissForever={vi.fn()}
      />,
    );

    expect(screen.queryByText(/Compte Beta/i)).toBeNull();
  });

  it('does not call onDismissForever when checkbox is unchecked', () => {
    const onDismissForever = vi.fn();
    render(
      <BetaWarningDialog
        open={true}
        onClose={vi.fn()}
        onDismissForever={onDismissForever}
      />,
    );

    fireEvent.click(screen.getByText(/J'ai compris/i));

    expect(onDismissForever).not.toHaveBeenCalled();
  });
});
