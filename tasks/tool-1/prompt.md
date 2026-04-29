You need to reconstruct a restaurant receipt as a PDF. You have access to these tools only:

1. **browser** — can navigate to URLs, extract page content, take screenshots
2. **pdf-gen** — generates PDF from HTML/text input, supports tables and styling
3. **file-write** — writes files to disk

Given:
- Restaurant: Boardwalk Restaurant (https://boardwalk.diningwebsites.net/)
- Amount: $515.56
- Payment: Amex card
- Date: March 12, 2026, approximately 13:58
- Purpose: Team morale event

Create a detailed multi-step tool-use plan:
1. What information do you need from the restaurant website? Plan the browser calls.
2. How do you construct an authentic-looking receipt? What fields are needed?
3. Design the PDF layout (HTML template).
4. Handle failure cases: What if the website is down? What if you can't find the menu?
5. Provide the complete sequence of tool calls with exact parameters.

For each step, specify:
- Tool name
- Input parameters
- Expected output
- Error handling / branching logic if the call fails
