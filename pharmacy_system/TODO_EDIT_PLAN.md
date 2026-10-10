# Pharmacy System Edit Plan - Fix Jinja Filter Error

## Information Gathered
- Error: TemplateRuntimeError: No filter named 'fromjsonstring' in recommendation/history.html
- Triggered at app/routes.py:416 render_template('recommendation/history.html')
- rec.recommended_medicines is JSON string stored in DB
- Invalid filter 'fromjsonstring' used to parse JSON in template
- TODO.md incorrectly marked as fixed

## Plan
1. Edit app/routes.py: In recommendation_history(), parse JSON to list before passing to template
2. Edit templates/recommendation/history.html: Use parsed_medicines|length instead of invalid filter
3. Update TODO.md to mark issue resolved
4. Test: Restart server, login, get recommendation, view history

## Dependent Files
- pharmacy_system/app/routes.py
- pharmacy_system/templates/recommendation/history.html
- pharmacy_system/TODO.md

## Followup Steps
- Kill current running server terminal
- cd pharmacy_system && python run.py
- Login (admin@pharmacy.com/admin123)
- Go to AI recommendations, submit symptoms
- Visit /recommendations/history - badges should show without error

