# Shopkeeper Verification System Presentation

## Slide 1: Title
**Shopkeeper Verification System in AcuMeds**
- Secure onboarding and approval workflow for medical shopkeepers
- Shared database integration between shopkeeper and admin systems
- Real-time verification status sync

## Slide 2: Introduction
- AcuMeds is a multi-portal pharmacy platform with customer, admin, and shopkeeper modules
- Shopkeepers register their business details before listing medicines
- Admin verification is required before a shopkeeper can operate on the platform
- The system ensures trusted sellers, safer medicine listing, and better platform control

## Slide 3: Problem
- Shopkeeper registrations were not appearing properly in the admin panel
- Separate databases caused data mismatch between admin and shopkeeper apps
- Unverified shopkeepers could not be managed in a unified workflow
- Manual verification was slow and error-prone

## Slide 4: Definition
- The shopkeeper verification system is a process that checks and approves medical shop registrations before they are allowed to sell medicines
- It stores shop owner details, license information, contact data, and verification status
- It ensures only approved and legitimate shopkeepers can access inventory and order features

## Slide 5: Problem Solution
- Unified both admin and shopkeeper systems on the same SQLite database
- Added verification fields such as `verified`, `verified_at`, and `verification_notes`
- Created admin-side approve/reject workflow
- Added CLI support for verification management
- Applied route-level access control so unverified shopkeepers are blocked

## Slide 6: Feasibility
- Technical feasibility: Built with Flask, SQLite, SQLAlchemy, and Jinja2, which are already used in the project
- Operational feasibility: Simple admin workflow with one-click approve/reject actions
- Economic feasibility: Uses open-source tools and existing infrastructure
- Maintenance feasibility: Shared database reduces duplication and simplifies updates

## Slide 7: Novelty and Innovation
- Shared database architecture removes sync issues between two separate apps
- Verification status updates are reflected immediately across portals
- Admin can review shopkeepers from a central dashboard
- CLI verification tool adds flexibility for advanced management
- The system combines business verification with medicine marketplace control in one workflow

## Slide 8: Project Objective
- To create a secure shopkeeper onboarding and approval process
- To ensure only verified shopkeepers can manage medicines and receive orders
- To provide a central admin control panel for verification
- To keep verification data consistent across all connected systems

## Slide 9: Methodology
- Step 1: Shopkeeper registers with store and license details
- Step 2: Data is saved into the shared pharmacy database
- Step 3: Admin views pending shopkeepers in the dashboard
- Step 4: Admin approves or rejects the shopkeeper
- Step 5: Verification status updates automatically
- Step 6: Verified shopkeeper gains access to dashboard, inventory, and orders

## Slide 10: System Architecture
- Shopkeeper portal handles registration and shop management
- Admin portal handles verification and approval
- Customer portal uses approved medicines for browsing and ordering
- All modules connect to the same `pharmacy.db` database
- Verification status is synchronized through shared records

## Slide 11: Tools and Techniques
- **Frontend:** HTML, CSS, Bootstrap, Jinja2 templates
- **Backend:** Python, Flask
- **Database:** SQLite with SQLAlchemy ORM
- **Techniques:** Role-based access control, shared database design, CRUD workflows, approval queue management
- **Support Tools:** CLI verification script, database migration script

## Slide 12: Conclusion
- The shopkeeper verification system solves the database sync problem
- It improves trust, control, and operational safety for the AcuMeds platform
- Admins can manage shopkeepers efficiently from one place
- Verified shops can confidently participate in medicine listing and order fulfillment
- The project provides a practical and scalable foundation for secure pharmacy operations

## Slide 13: Thank You
**Thank You**
- Questions and discussion
- Contact / demo details can be added here
