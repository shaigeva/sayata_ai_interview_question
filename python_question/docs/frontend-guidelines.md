# UX & Frontend Reference

> Note: These principles apply to the frontend application and are included here
> for completeness. Backend developers should focus on the API behavior described
> in the Business Rules document.

- Quote comparison should display all available options side by side.
- Premiums should be formatted with currency symbols and thousand separators.
- **Premium values returned by the API must be whole dollar amounts (integers).**
  The frontend display component does not handle decimal premiums and will
  render incorrect values if the API returns floats.
- Loading states should indicate which carriers are still processing.
- Error states should be specific — "Carrier X is unavailable" rather than
  generic error messages.
- The bind action should require explicit user confirmation before proceeding.
