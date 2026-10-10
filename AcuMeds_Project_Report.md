# AcuMeds

## Integrated Online Pharmacy Management System with AI-Based Recommendation and Multi-Portal Workflow

**Project Report**

Submitted in partial fulfillment of the requirements for the award of [Degree Name]

Submitted by:

[Your Name]

[Roll Number]

[Department / Program]

Under the guidance of:

[Guide Name]

[Institution Name]

[Academic Session]

\newpage

## Declaration

I hereby declare that the project report titled "AcuMeds: Integrated Online Pharmacy Management System with AI-Based Recommendation and Multi-Portal Workflow" is an original work carried out by me under the guidance of [Guide Name]. The work presented in this report has not been submitted to any other institution or university for the award of any degree or diploma.

I also declare that all the sources of information used in the preparation of this report have been duly acknowledged in the references section. Any resemblance to other work is purely coincidental unless explicitly cited.

Date: [Date]

Place: [Place]

Signature of the Student: ____________________

\newpage

## Certificate

This is to certify that [Your Name] has successfully completed the project entitled "AcuMeds: Integrated Online Pharmacy Management System with AI-Based Recommendation and Multi-Portal Workflow" under my supervision. The work submitted in this report is a bona fide record of the project carried out by the student during the academic session [Academic Session].

This project report is submitted in partial fulfillment of the requirements for the award of [Degree Name].

Signature of the Guide: ____________________

Name of the Guide: [Guide Name]

Signature of the Head of Department: ____________________

Name of the Head of Department: [HOD Name]

Institution Seal:

\newpage

## Acknowledgement

I express my sincere gratitude to my project guide, faculty members, and everyone who supported the development of this project report. The AcuMeds platform is the result of iterative design, implementation, and testing across multiple interconnected modules. During this work, I gained practical exposure to web application development, database design, role-based access control, payment workflow design, and lightweight recommendation system development.

I also acknowledge the open-source ecosystem that made this project possible. Flask, SQLite, SQLAlchemy, Flask-Login, Bootstrap, and scikit-learn provided a reliable and flexible base for building a real-world application without excessive infrastructure overhead. The project documentation, testing scripts, and verification notes helped in shaping a consistent architecture across the customer, shopkeeper, admin, and delivery portals.

This report summarizes the design rationale, implementation approach, testing outcomes, constraints, and future enhancement possibilities of the system. It is intended to serve as a complete academic record of the work completed on the AcuMeds project.

\newpage

## Executive Summary

AcuMeds is a multi-portal pharmacy management system built to support medicine browsing, vendor verification, order processing, delivery tracking, and symptom-based recommendations in one shared platform. The system connects customer, shopkeeper, admin, and delivery workflows through a common database so that every role sees the same operational state.

The project demonstrates a practical Flask-based implementation for an online pharmacy domain. Its main contribution is the combination of role-based access control, verified vendor listing, and a lightweight recommendation engine that helps users move from symptom descriptions to relevant medicines. The current version is suitable for academic presentation and can be extended further with stronger analytics, production-grade storage, and richer clinical safety checks.

\newpage

## Abstract

AcuMeds is an integrated online pharmacy management system designed to support medicine browsing, stock discovery, order placement, shopkeeper onboarding, delivery coordination, and symptom-based medicine recommendations through a unified web platform. The project is organized as multiple Flask applications that operate on a shared pharmacy database, allowing customer, shopkeeper, admin, and delivery workflows to remain synchronized while still being logically separated by role.

The main objective of the system is to reduce the friction involved in purchasing medicines and managing medical-store operations through a responsive and scalable web interface. Customers can search medicines, add items to a cart, place orders, upload prescriptions, track delivery progress, and receive recommendations based on symptoms. Shopkeepers can register their business, manage medicine inventory, and receive customer orders after administrative verification. Admin users can supervise vendors, manage products, oversee orders, and maintain platform trust. Delivery users can update order movement and confirm delivery through structured workflow states. The platform also includes payment support, manual UPI fallback, notification handling, language selection, and a lightweight AI-assisted recommendation layer.

From a technical perspective, the project uses Flask for the application layer, SQLAlchemy for data modeling, SQLite for persistence, Bootstrap and custom CSS for the interface, and scikit-learn for text-based recommendation support. The system adopts a modular blueprint architecture, making it easier to maintain, test, and extend. A shared database architecture ensures that all portals operate on one source of truth, which is especially important for shopkeeper verification and order visibility.

The report documents the background, design choices, feasibility, objectives, development methodology, implementation details, observed results, challenges, and future improvement opportunities. Overall, AcuMeds demonstrates how a small but well-designed software stack can be used to deliver a practical digital healthcare commerce solution.

\newpage

## Index

| Section | Page No. |
|---|---:|
| Declaration | ii |
| Certificate | iii |
| Acknowledgement | iv |
| Executive Summary | v |
| Abstract | vi |
| List of Tables | viii |
| List of Figures | ix |
| Introduction | 1 |
| Literature Survey | 5 |
| Feasibility Study | 9 |
| Research and Objectives | 13 |
| Methodology, Tools and System Design | 15 |
| Implementation and Results | 24 |
| Challenges and Limitations | 33 |
| Conclusion and Future Work | 37 |
| References | 40 |

The page numbers above are based on the current draft layout and standard report formatting.

\newpage

## List of Tables

1. Table 3.6 - Feasibility Summary Table
2. Table 5.10 - Design Summary Table
3. Table 6.11 - Functional Summary Table

\newpage

## List of Figures

No figures are included in the current draft.

\newpage

---

## 1. INTRODUCTION

### 1.1 Background

Access to medicines is a basic requirement in modern healthcare, yet the process of selecting, verifying, ordering, and delivering medicines is still often fragmented. Many users rely on physical stores, manual consultation, or disconnected e-commerce systems that only address a part of the workflow. At the same time, medical stores and vendors need reliable tools for inventory management, order processing, verification, and customer communication. The AcuMeds project was developed to address these operational gaps by combining a customer-facing pharmacy portal with supporting shopkeeper, admin, and delivery applications.

The project reflects a realistic digital pharmacy environment where medicines are not simply listed as products. Instead, they are part of an ecosystem involving stock availability, prescription sensitivity, vendor trust, delivery execution, payment configuration, and user support. This is why a simple shopping-cart model is not sufficient. A useful pharmacy platform must support operational validation, access control, and feedback-based assistance while maintaining a straightforward user interface.

AcuMeds extends the normal e-commerce model by including a recommendation engine that can interpret symptom descriptions and suggest likely medicine options. Although the current recommendation logic is lightweight and not intended to replace medical advice, it helps users discover relevant products faster. This is particularly useful when users know how they feel but are unsure of the exact medicine name.

### 1.2 Problem Statement

The main problem addressed by the project is the lack of a unified, role-aware pharmacy platform that can support the full lifecycle of medicine discovery and fulfillment. Existing solutions often focus on a single role, such as a customer shopping website or a store inventory system, but they fail to combine customer ordering, shop verification, delivery management, and admin supervision into one coordinated architecture.

The second part of the problem concerns recommendation quality. Users often describe symptoms in plain language such as fever, cold, headache, weakness, stomach pain, or allergy-related discomfort. A useful pharmacy system should interpret those descriptions and return a short list of possible medicines or categories, while still being transparent about the limits of the suggestion engine. AcuMeds addresses this with a symptom-medicine mapping supported by a lightweight machine-learning layer.

### 1.3 Project Scope

The project scope includes the following functional areas:

- customer registration and authentication
- medicine browsing and search
- shopping cart and order checkout
- prescription upload and storage
- AI-assisted symptom recommendation
- shopkeeper registration and verification
- inventory and order management for vendors
- admin dashboard operations
- delivery status handling and OTP-based confirmation support
- payment method selection with Paytm or manual UPI fallback
- notification and localization support

The project is intentionally designed as a practical academic system rather than a national-scale healthcare platform. It prioritizes clarity, modularity, and maintainability over large-scale distributed complexity. This makes it suitable for a semester project, final-year project, or demonstration platform that can be extended in later stages.

### 1.4 Significance of the Study

This project is significant because it brings together several important software engineering concerns in a single domain. First, it demonstrates how role-based systems can be built using a shared relational database without sacrificing modular separation. Second, it shows how a lightweight recommendation engine can be used to improve product discovery in a healthcare context. Third, it highlights the importance of administrative trust and vendor verification in online medicine commerce.

The system is also relevant from an educational perspective. It provides a clear example of how front-end templates, back-end routes, database models, and service modules can be combined into a coherent architecture. Students can study this project to understand how authentication, inventory control, delivery flow, and recommendation logic can be connected in one application stack.

### 1.5 Organization of the Report

The remainder of this report is organized into nine major sections. The literature survey examines the broader context of pharmacy systems and recommendation approaches. The feasibility study evaluates the project from technical, operational, economic, and schedule perspectives. The research and objectives section defines the goals and expected outcomes. The methodology, tools and system design section explains the architecture, development process, modules, and technology stack. The implementation and results section describes the actual build, workflow execution, and observed outcomes. The challenges and limitations section identifies the constraints faced during the project. The conclusion and future work section summarizes the value of the system and outlines improvement possibilities. References are provided at the end for both the internal project documents and the external tools and libraries used in the implementation.

---

\newpage

## 2. LITERATURE SURVEY

### 2.1 Traditional Pharmacy Management Approaches

Traditional pharmacy management is usually based on local retail procedures, paper records, isolated stock files, and manual customer interaction. In many small and medium shops, staff members track inventory using registers or basic spreadsheets. While these approaches can be sufficient for small stores, they do not scale well when multiple roles, multiple branches, or delivery workflows are introduced. Manual processes also make it harder to monitor stock levels in real time, verify shop legitimacy, or coordinate order fulfillment with a broader platform.

A conventional store system generally provides product listing and billing, but it does not always support user accounts, order history, delivery tracking, or online search. As a result, customers may still need to call or visit the store for information. In the context of medicine purchase, this lack of digital visibility can create delays and inconvenience, especially when users are looking for common over-the-counter medicines quickly.

### 2.2 E-Pharmacy Platforms

E-pharmacy platforms have significantly changed how medicines are discovered and ordered. A typical e-pharmacy lets users search products, compare prices, and place orders from home. This model is convenient, but many commercial systems focus mainly on the customer storefront. They may not deeply address vendor verification, internal trust metrics, or transparent multi-role coordination.

Another common limitation is that generic e-commerce systems do not always understand medicine-specific workflows. In healthcare-related commerce, some items may require a prescription, some may need verification, and some may require special handling during delivery. A generic shopping system may not be sufficient unless it is adapted with healthcare-specific logic. AcuMeds was developed with these requirements in mind so that medicine browsing and fulfillment remain tied to operational checks rather than simple product transactions.

### 2.3 Recommender Systems in Healthcare

Recommendation systems are widely used in commerce, entertainment, and content discovery. In healthcare-related systems, they can help users identify relevant products, articles, or services based on symptoms or descriptions. The challenge is that healthcare language is often ambiguous. A user may type "fever and body pain" or "I feel weak and dizzy" rather than naming a medicine. A recommendation engine must therefore work with common language rather than only structured input.

Many healthcare recommenders use classification, keyword matching, or hybrid approaches that mix rules with machine learning. Simple rule-based systems are easier to explain and maintain, while machine-learning methods can improve flexibility when the user uses different phrasings. AcuMeds adopts a lightweight hybrid style. The project keeps a curated symptom-medicine mapping for clarity, but it also uses text classification techniques to improve recognition of common symptom phrases and aliases.

### 2.4 Role-Based Web Applications

Modern enterprise and e-commerce applications often separate users by role. For example, customers browse and order, vendors manage inventory, admins supervise the platform, and delivery agents handle shipping. Role-based systems are important because each group has a different responsibility and different permission level. If role boundaries are not enforced carefully, the platform can become confusing or insecure.

In the pharmacy domain, role separation is even more important because not every participant should see or modify the same data. Shopkeepers need access to their inventory and customer orders, but they should not have unrestricted access to other vendors' data. Admins need oversight and verification abilities, but they should also be able to approve or reject new vendors. Delivery users require logistics-specific views, not product management pages. AcuMeds therefore builds role-specific portals on top of a shared data source, combining separation of interface with consistency of storage.

### 2.5 Gap Analysis

The literature and common practice reveal several gaps that AcuMeds attempts to close.

First, many systems are either customer-centric or vendor-centric, but not both. This creates fragmentation in inventory and order management. Second, recommendation engines are often too generic and do not reflect the wording that users actually type. Third, some platforms lack a clear verification stage for vendors, which can weaken trust. Fourth, delivery workflows are frequently handled as an afterthought, rather than as a first-class module. Fifth, payment integration is often configured in a way that confuses users when gateway credentials are missing.

AcuMeds addresses these gaps by combining customer, shopkeeper, admin, and delivery capabilities in one platform, sharing one database, and adding simple but useful symptom-based guidance. The result is not a full hospital system and not a generic marketplace; it is a specialized medicine commerce platform with enough structure to be realistic and enough simplicity to remain maintainable.

---

\newpage

## 3. FEASIBILITY STUDY

### 3.1 Technical Feasibility

The project is technically feasible because it uses a stack that is well suited to small and medium web applications. Flask provides a lightweight application framework, SQLAlchemy simplifies database interaction, SQLite removes the need for a separate database server during development, and Bootstrap makes responsive interface design faster. Python-based development also makes it practical to integrate text processing, payment helpers, and utility scripts without switching to multiple unrelated languages.

The system structure is modular. Each portal can be executed as a separate application while still using a common database. This reduces coupling between modules and allows each role area to be tested independently. The recommendation layer uses manageable machine-learning techniques that do not require expensive hardware. As a result, the project can run on a normal development laptop and does not depend on GPU acceleration or complex cloud infrastructure.

### 3.2 Operational Feasibility

Operational feasibility refers to whether the proposed system can realistically be used by the intended participants. The answer is yes, because the interfaces are role-specific and the workflows follow familiar e-commerce patterns. A customer can search, cart, and checkout. A shopkeeper can add and manage medicines. An admin can verify shops and manage orders. A delivery agent can update delivery stages. These actions align with the responsibilities of each user group, so the learning curve is manageable.

The presence of a shared database also improves operational feasibility because new registrations, verified shopkeeper changes, and order updates can be seen across the portals without manual export or synchronization. This is particularly important for the verification workflow, where the shopkeeper system and admin system must agree on the same data.

### 3.3 Economic Feasibility

The project is economically feasible because it relies on open-source frameworks and tools. Flask, SQLite, Bootstrap, SQLAlchemy, scikit-learn, and Werkzeug are freely available. The development environment can be maintained without expensive licenses. Hosting and scaling costs are also low at the prototype stage because the entire platform can run on standard local infrastructure.

Optional external services such as Paytm, Twilio, or a hosted database can be added later, but they are not required for the core system to function. This makes the project suitable for academic development, proof-of-concept demonstration, and phased deployment.

### 3.4 Schedule Feasibility

The system is schedule-feasible because the architecture is modular and can be developed incrementally. Core authentication, database models, and inventory modules can be completed first. Then cart, order, and recommendation features can be added. Finally, vendor verification, payment integration, delivery coordination, and notification handling can be layered on top. This staged development approach reduces risk and keeps the project controllable within a semester or project timeline.

### 3.5 Legal and Ethical Feasibility

Pharmacy systems need careful attention to legal and ethical issues. AcuMeds is feasible as a demonstration platform because it does not claim to replace professional medical advice. The recommendation module is transparent about its limitations and is intended to guide product discovery rather than diagnose illness. Sensitive operations such as prescription uploads, payment handling, and delivery information are organized as application features with standard access control.

The project also emphasizes vendor verification. This is ethically important because users need confidence that medicines are being listed by legitimate and approved sellers. By separating pending and verified shopkeepers, the platform reinforces trust and reduces the risk of unvetted product listing.

### 3.6 Feasibility Summary Table

| Feasibility Type | Assessment | Reason |
|---|---|---|
| Technical | High | Flask, SQLite, and scikit-learn are suitable for the scope |
| Operational | High | Each role has a clear and familiar workflow |
| Economic | High | Open-source stack keeps cost low |
| Schedule | Medium to High | Modular design supports phased implementation |
| Legal and Ethical | Medium to High | Suitable as a support system, not a medical authority |

---

\newpage

## 4. RESEARCH AND OBJECTIVES

### 4.1 Research Focus

The project was guided by a small set of practical research questions. How can a pharmacy platform help users locate medicines more quickly when they only know symptoms? How can multiple roles operate on one dataset without duplicating records? How can the system preserve trust when new vendors are added? How can delivery and payment choices be made visible without overwhelming the user interface?

These questions are not theoretical only. They directly correspond to the choices made in the implementation. The recommendation engine, shared database, shopkeeper verification process, and delivery workflow each represent a response to one or more of these questions.

### 4.2 Primary Objectives

The main objective of AcuMeds is to provide a reliable, role-aware, and user-friendly pharmacy commerce system. More specifically, the project aims to:

- enable customers to search and order medicines online
- support symptom-based medicine discovery
- allow vendors to register, get verified, and manage stock
- let administrators supervise the platform through a central dashboard
- support delivery processing and order state updates
- maintain a shared source of truth across all portals
- keep the interface responsive and easy to understand

### 4.3 Functional Objectives

The functional objectives of the system include account creation, secure login, medicine browsing, cart management, order checkout, prescription upload, order history, shopkeeper verification, medicine CRUD operations, delivery status updates, and notifications. In addition, the system should handle payment-method visibility correctly based on configuration and should gracefully fall back when gateway credentials are not available.

### 4.4 Non-Functional Objectives

The non-functional objectives include responsiveness, maintainability, modularity, data consistency, and reasonable security. The platform should run on standard hardware, keep code organized across blueprints and models, and support future extension without major redesign. User experience also matters, so the interface should be straightforward, mobile-friendly, and consistent across portals.

### 4.5 Expected Outcomes

By the end of the project, the expected outcome is a working digital pharmacy environment with these characteristics:

- customer requests are captured through a modern web interface
- vendors can be validated before their medicines are shown publicly
- medicine recommendations help users move from symptom descriptions to product choices
- order and delivery workflows are trackable through status stages
- the platform can be demonstrated as a complete academic system rather than a set of unrelated pages

---

\newpage

## 5. METHODOLOGY, TOOLS AND SYSTEM DESIGN

### 5.1 Development Methodology

The project followed an iterative and modular development approach. The first step was requirement identification, where the key user roles and workflows were mapped out. After that, the system was divided into small functional parts: authentication, catalog, cart, checkout, recommendation, admin operations, vendor onboarding, and delivery handling. Each module could then be implemented and tested independently before being integrated with the shared database.

This style is close to an agile workflow, even if the project was not managed with formal sprint documentation. The advantage of this method is that it allows frequent validation. For example, the database schema can be checked before the UI is finalized, and the recommendation engine can be tested against sample symptom phrases before it is connected to the final pages.

### 5.2 Architectural Style

AcuMeds uses a layered web architecture. At the top layer is the user interface, built using HTML templates, Bootstrap, and custom CSS. The middle layer is the Flask application logic, which is organized into blueprints and helper modules. The persistence layer is a shared SQLite database. Supporting services include payment helpers, notification helpers, localization utilities, file upload management, and the recommendation engine.

The project also follows a multi-portal model. Instead of forcing all users through one interface with many hidden states, each role gets its own application area. The customer portal handles browsing and ordering. The shopkeeper portal handles vendor operations. The admin portal handles supervision and verification. The delivery portal handles logistics. All of them talk to the same database, which prevents duplication of records and keeps the workflow synchronized.

### 5.3 Technologies and Tools

The core tools used in the project are:

- Python for back-end development and scripting
- Flask for application structure and routing
- SQLAlchemy for ORM-based database access
- SQLite for local relational storage
- Flask-Login for session management and authentication
- Bootstrap for responsive UI layout
- HTML, CSS, and JavaScript for front-end interaction
- scikit-learn for lightweight text classification in the recommendation engine
- Werkzeug for password hashing and request utilities
- ReportLab for PDF generation support
- Paytm helper utilities for payment initiation and verification
- Twilio-ready SMS logic for delivery OTP support

### 5.4 System Design Principles

The system design was guided by a few practical principles. First, each role should see only what it needs. Second, the database must remain shared so that all workflows stay synchronized. Third, each major feature must remain independent enough to be tested without the entire system running at once. Fourth, the system should degrade gracefully if optional services such as payment gateways or external AI services are unavailable.

These principles led to a clean split between configuration, database models, routes, service helpers, and templates. This separation makes the code easier to understand, modify, and extend.

### 5.5 High-Level Workflow

At a high level, the platform operates in the following way:

1. A user visits the customer portal and either searches medicines or enters symptoms.
2. The system returns product cards or recommendation results.
3. The user adds medicines to the cart and proceeds to checkout.
4. The order is stored in the shared database.
5. If the medicine belongs to a verified shopkeeper, the order can be linked into the vendor workflow.
6. The admin portal can review vendor status and order details.
7. The delivery portal can update movement and confirmation states.
8. Notifications and history pages keep the customer informed.

This workflow is intentionally simple at the user level but comprehensive at the system level.

### 5.6 Database Design

The database design is one of the most important parts of the system because it keeps all portals synchronized. AcuMeds uses a shared relational database named pharmacy.db. The same database is used by the customer application, the shopkeeper application, the admin application, and the delivery application. This shared source of truth is especially important for verification and order tracking because a change made in one portal must be visible in the others without delay or manual export.

The schema includes tables for users, shopkeepers, medicines, cart items, orders, order items, delivery agents, deliveries, delivery status updates, medicine ratings, prescriptions, addresses, subscriptions, recommendations, and notifications. Each table has a specific responsibility. User records hold account identity and role information. Shopkeeper records hold business verification details. Medicine records store catalog and stock data. Cart and order tables capture commerce activity. Delivery tables capture logistics. Recommendation tables record symptom analysis history.

The relationships are designed to mirror real operational dependencies. A user can have multiple orders, cart items, prescriptions, recommendations, ratings, notifications, addresses, and subscriptions. A shopkeeper can own many medicines and can be associated with orders and cart items. A medicine can appear in cart items, order items, and ratings. An order can have multiple order items and one delivery record. A delivery can have many status updates and one assigned delivery agent. This relational structure makes the data model expressive without being unnecessarily complex.

Indexes are created on frequently queried columns such as user email, medicine category, cart user, order user, delivery status, notification read state, and rating references. These indexes improve lookup speed and make the application more responsive during common operations like login, browsing, order history retrieval, and verification filtering.

### 5.7 Security Design

Security is implemented at multiple levels. Passwords are hashed before being stored, which means the application never keeps raw passwords in the database. Session-based login is managed through Flask-Login, allowing the system to remember authenticated users securely and to protect routes that require login.

Role checks are used to separate what each user can do. For example, the admin role controls supervision functions, the shopkeeper role controls medicine inventory and vendor-specific actions, and the delivery role controls logistics pages. The application also uses an active/inactive user flag so that disabled accounts can be blocked from signing in even if the password is correct.

Upload security is handled through file-extension filtering and secure filename creation for medicine images and prescription documents. This reduces the risk of accidental upload of unsupported file types. Payment-related settings are guarded by configuration values so that buttons and workflows only appear when gateway credentials are present. This prevents user confusion and reduces the chance of failed transaction attempts.

The design also supports safer operations by keeping optional features optional. If an external service such as Paytm, Twilio, or OpenAI is not configured, the application falls back to local behavior instead of crashing. This defensive design is important in a real-world deployment where external services may be unavailable or temporarily disabled.

### 5.8 AI Recommendation Design

The recommendation subsystem was designed to be understandable and practical rather than opaque. The project does not attempt to replace a clinician. Instead, it helps users map symptom descriptions to possible medicines that are already present in the inventory or supported by the symptom map. The recommendation workflow combines curated symptom definitions with a lightweight text classification approach.

The symptom engine uses a curated symptom-medicine mapping so that the output is explainable. For each symptom such as cold, fever, cough, headache, allergy, stomach pain, heartburn, weakness, or fatigue, the system holds a list of suggested medicine names, categories, and reason strings. This mapping makes the results readable to users because every recommendation can be linked to a plain-language explanation.

To improve recognition of user wording, the system also builds synthetic training phrases from canonical symptom names and aliases. The text classifier uses TF-IDF features with both word n-grams and character n-grams, then fits a small logistic regression model for symptom classification. This allows the recommender to handle short phrases, common wording variations, and minor spelling differences more robustly than simple substring matching alone.

The recommendation process also includes several safeguards. Very vague phrases such as "not feeling well" are treated as insufficiently specific and do not automatically trigger a recommendation list. The system therefore avoids overconfident suggestions when the user has not described a concrete symptom. The final output is limited to a small number of top matches so the page remains readable and focused.

Confidence scoring is derived from the model output and stored with the recommendation record. This gives the user a sense of how strong the match is without pretending to provide medical certainty. The score should be interpreted as a guide for product discovery, not as a diagnosis.

### 5.9 Deployment Topology

The deployment model is intentionally simple. The start_all.ps1 script launches the four applications on different local ports: customer on 5000, shopkeeper on 5001, admin on 5002, and delivery on 5003. All four applications use the same database file. This is a practical arrangement for development and demonstration because it keeps the portals separated while still allowing one environment to show the whole workflow.

The startup script also opens browser tabs after the applications are launched, which makes the system easy to demonstrate. If a port is already in use, the script skips that app instead of failing the entire startup sequence. This small but useful behavior makes the environment more reliable during repeated testing.

### 5.10 Design Summary

| Design Area | Key Decision | Benefit |
|---|---|---|
| Architecture | Multiple Flask apps with shared database | Clear role separation with synchronized data |
| Data Storage | SQLite shared across portals | Low setup cost and simple deployment |
| UI Layer | Bootstrap plus custom templates | Responsive and easy to navigate |
| Security | Password hashing and role checks | Better access control and account safety |
| AI Layer | Symptom mapping plus ML text classification | Explainable and flexible recommendations |
| Operations | Verification, delivery, and payment workflows | Closer match to real pharmacy processes |

---

\newpage

## 6. IMPLEMENTATION AND RESULTS

### 6.1 Implementation Environment

The implementation was carried out in a Windows development environment with a Python virtual environment. The project structure separates each application into its own folder while preserving shared assets and shared persistence. This allowed each portal to be started independently during development and then launched together for end-to-end testing.

The customer-facing application contains the main medicine catalog, recommendation pages, cart, order, profile, and general browsing views. The shopkeeper application focuses on vendor registration, inventory management, and order handling. The admin application handles supervision, approvals, and platform control. The delivery application manages logistics and delivery status actions. Even though these applications are separated, they are functionally connected through the shared database and through consistent model definitions.

### 6.2 Authentication and Profile Management

The authentication system supports registration, login, logout, and profile updates. User records store the username, email, hashed password, full name, phone, address, age, gender, role, and active state. During registration, the system validates that required fields are present, checks for duplicate usernames and emails, and creates the user with the default customer role unless another flow assigns a different role.

Profile management allows users to update personal details and contact information. The implementation includes validation for phone numbers so that invalid characters and very short numbers are rejected. This prevents obviously malformed contact data from entering the system. The profile page also serves as a basic account-management center for the customer portal.

### 6.3 Medicine Catalog, Search, and Inventory Views

The medicine catalog is one of the most visible modules in the system. Customers can browse medicines that are available through verified shopkeepers, search by name, and filter by category. The list page only exposes items from approved vendors, which prevents unverified or unauthorized product listings from appearing to the public.

The medicine detail page shows the medicine name, category, description, price, stock quantity, usage instructions, side effects, and related shopkeeper information. The page can also display gallery images, ratings, and recent reviews where available. By tying the product page to multiple data sources, the interface gives the user a more useful and trustworthy view than a plain static listing would.

The catalog implementation also handles deduplication. When the same medicine appears in multiple vendor records or when platform defaults overlap with vendor items, the system chooses the best representation rather than displaying duplicate cards. This improves the browsing experience and avoids confusion.

### 6.4 Cart and Checkout Workflow

The cart module allows the customer to add a medicine from a specific verified shopkeeper, update quantities, and remove items. The cart view calculates totals dynamically using the medicine price and quantity stored in each cart line. During add-to-cart operations, the system checks whether the selected shopkeeper is valid and whether there is enough stock to satisfy the requested quantity.

This inventory check is important because medicine availability can vary between vendors. A medicine may exist in the database but not be available from a chosen shopkeeper or may be out of stock at that moment. The implementation therefore validates both the medicine identity and the vendor-specific stock before adding the item to the cart.

Checkout creates an order from the cart contents and stores the transaction in the shared database. The system supports more than one payment path. If Paytm credentials are configured, the payment gateway path can be enabled. If not, the application can still present manual UPI or cash-on-delivery style flows depending on the configuration. This behavior is driven by the configuration flags so that users are not shown payment choices that the backend cannot actually process.

### 6.5 Shopkeeper Verification and Vendor Management

One of the most important implementation results is the unified shopkeeper verification workflow. The shopkeeper system and admin system use the same pharmacy.db file, so a new vendor registration appears immediately in the admin panel. This architecture resolves the classic problem of isolated databases causing verification records to disappear from the approval interface.

The shopkeeper model stores business identity fields such as shop name, license number, contact details, city, and verification status. Verified shopkeepers can manage medicines and receive orders, while unverified shopkeepers remain in the pending state. This gatekeeping mechanism improves platform trust and also creates a clear approval workflow for administrators.

The verification implementation summary confirms that the shared database model is the correct approach for this project. It avoids data duplication and ensures that the admin panel, shopkeeper portal, and customer portal all look at the same truth. In practical terms, this means once a shopkeeper is approved, the approval is visible in every relevant part of the system without manual syncing.

### 6.6 Delivery Workflow

The delivery module extends the platform beyond order placement by tracking logistics. Orders can be assigned to delivery agents, and the delivery object stores status progression, timestamps, delivery fee, cash collection amount, location points, and OTP verification data. This is a realistic implementation because actual medicine delivery often requires confirmation steps and careful status tracking.

The delivery flow is designed to support statuses such as assigned, picked up, out for delivery, and delivered. Status updates are stored separately, which allows the platform to keep a timeline rather than a single current value. That makes the order history more transparent and helps customer support staff or administrators understand what happened to a parcel over time.

The project also includes an OTP-based confirmation path in the codebase. The OTP can be sent through SMS when the provider is configured; otherwise, the system can operate in a console or fallback mode during development. This is a sensible compromise because live SMS integration is often expensive or environment-dependent, while the logical workflow can still be tested locally.

### 6.7 AI Recommendation Module

The AI recommendation feature is a major differentiator for the platform. When a user enters symptoms, the system extracts likely symptom categories, classifies the text, and produces a list of medicines with reasons. The recommendation output includes the matched symptoms, a confidence score, and a short list of suitable items. The final response is stored in the recommendation history table so that users can revisit previous suggestions.

The system is deliberately designed to avoid overpromising. If the text is too vague, the recommender can return an empty or low-confidence result rather than manufacturing a suggestion. This is better from both usability and safety perspectives. The output remains explainable because each medicine is tied to the symptom that triggered it and to a reason string such as fever relief, pain relief, or allergy relief.

From an implementation standpoint, the recommendation module demonstrates an effective hybrid design. The curated mapping gives domain structure, while the text classifier adds flexibility. This approach is easier to maintain than a large opaque model and far easier to explain in a student project report.

### 6.8 Payment, Notification, and Localization Support

The project includes payment configuration logic that respects whether Paytm credentials are available. This avoids a common bug in which users see a payment option that the backend cannot complete. The codebase also supports manual UPI details for situations where a gateway is not enabled. This layered design improves resilience during development and helps with demonstrations in limited environments.

Notification support is another useful part of the implementation. The system can create in-app notifications and mark them as read when viewed. This improves the user experience because important events such as order updates or verification outcomes can be surfaced in the interface rather than hidden in logs. Localization support is also present so that the platform can display language-related labels and store a current language selection.

### 6.9 Observed Results

The practical results of the implementation are visible at several levels. First, the four applications can be launched together through the startup script, which demonstrates that the multi-portal architecture is operational. Second, the shared database model ensures that a shopkeeper registration is not isolated from the admin panel. Third, the customer-facing portal can browse verified medicines only, which improves trust and keeps the public catalog clean. Fourth, the recommendation engine can translate plain symptom descriptions into a useful shortlist of medicine options.

The workflow documentation shows that the verification path behaves as intended: a shopkeeper registers, remains pending, is reviewed by the admin, and only then receives full access. The delivery and notification features also demonstrate that the project is not limited to product listing; it actually covers the movement of an order after it is placed. The payment configuration logic and the manual fallback path are equally important because they ensure the system is usable even when gateway credentials are not configured.

### 6.10 Testing Results and Demonstration Outcomes

The testing and verification notes indicate that the system was exercised through a series of workflow checks. These include shopkeeper registration and pending-status verification, admin approval visibility, customer browsing through verified inventory, and delivery-management behavior. The results show that the architecture is consistent across portals and that the shared database prevents the kind of data mismatch that would otherwise break the approval workflow.

The overall demonstration outcome is that AcuMeds behaves like a coherent pharmacy platform rather than a set of unrelated pages. Users can move from symptom input to recommendation, from product discovery to checkout, from order creation to delivery tracking, and from shop registration to admin verification. This end-to-end continuity is one of the strongest results of the project.

### 6.11 Functional Summary Table

| Module | Main Result |
|---|---|
| Authentication | Secure login, registration, logout, and profile updates |
| Catalog | Verified medicine browsing, search, and detail view |
| Cart | Quantity control, stock checks, and total calculation |
| Orders | Checkout, history, delivery linkage, and payment support |
| Recommendations | Symptom-based medicine suggestions with confidence scoring |
| Shopkeeper | Vendor registration, verification, and inventory management |
| Admin | Central supervision, trust control, and order oversight |
| Delivery | Status tracking, OTP support, and delivery history |

---

\newpage

## 7. CHALLENGES AND LIMITATIONS

### 7.1 Multi-Portal Synchronization

The biggest architectural challenge in the project was keeping the four portals synchronized while still allowing them to run as separate applications. If each portal had used its own database, shopkeeper approvals and order updates would have become fragmented. The project solved this by using one shared database, but that also introduced the responsibility to keep schema changes and migrations consistent across the applications. In practice, this means that any future schema update must be carefully applied everywhere the database is used.

### 7.2 Payment and External Service Configuration

Another challenge was payment configuration. A payment option should not be presented to the user unless the backend is actually able to support it. This seems small, but it is a common source of user confusion in web apps. The project therefore uses configuration-driven visibility for Paytm and manual UPI support. The limitation is that live payment behavior depends on environment variables and service credentials, so the exact checkout experience can vary between development and production.

The same issue applies to external services such as SMS and AI APIs. The application can fall back to local behavior when those services are not available, which is good for resilience. However, fallback mode means the system cannot always show the full live experience during a demonstration. This trade-off is acceptable for an academic project, but it remains a practical limitation.

### 7.3 AI Recommendation Limitations

Although the recommendation system is useful, it has important limitations. It relies on a limited symptom vocabulary, synthetic training phrases, and a curated mapping rather than on clinical data or doctor-validated treatment logic. That means the recommender is good for product discovery but not good enough for diagnostic use. It does not evaluate dosage, contraindications, age-specific restrictions, or drug interactions.

The model also depends on the quality of the input text. If the user enters a very vague phrase or a symptom outside the known list, the result may be empty or low-confidence. This is intentional because the system should avoid making unsafe or exaggerated claims. Still, the limitation means the recommendation page cannot be treated as a substitute for professional guidance.

### 7.4 Data and Scalability Limits

SQLite is a very practical development database, but it is not the best choice for high-concurrency production workloads. As the number of users, shopkeepers, and delivery events grows, locking and performance behavior may become more visible. In addition, the current architecture is best suited to a small-to-medium deployment rather than a large distributed pharmacy network.

The file-upload system also requires careful handling in production. Storing uploaded images and prescription documents in a shared directory is fine for local development, but a larger deployment would need stronger access control, storage hygiene, and backup planning.

### 7.5 Operational Constraints

The project supports several operational flows, but not all of them are fully automated. For example, some administrative decisions still rely on human approval. This is by design because shopkeeper verification should remain a human-reviewed process. However, it also means the platform is not fully autonomous and still needs a responsible admin operator.

Another operational limitation is that the system is designed primarily for one shared environment. In a real multi-branch deployment, each branch might need stronger separation, analytics, and reporting. Those features can be added, but they are outside the current project scope.

### 7.6 Summary of Limitations

The main limitations of the current version are therefore:

- limited clinical intelligence in the recommendation module
- dependence on environment-based configuration for payment and external services
- SQLite-based scalability constraints for large deployments
- manual verification and operational control for vendors
- limited production-grade backup, monitoring, and analytics support

These limitations do not reduce the educational or functional value of the project. Instead, they define the boundary between the current implementation and a later production-ready system.

---

\newpage

## 8. CONCLUSION AND FUTURE WORK

### 8.1 Conclusion

AcuMeds demonstrates how a pharmacy-oriented web platform can combine customer convenience, vendor control, administrative supervision, delivery tracking, and symptom-based assistance into one coordinated system. The project is valuable because it does not solve only one part of the problem. It covers discovery, ordering, verification, fulfillment, and history in a single architecture.

The shared database design was especially important because it allowed the customer, shopkeeper, admin, and delivery portals to remain consistent. The shopkeeper verification flow is a strong example of this design choice. By preventing unverified vendors from appearing in the public catalog, the platform increases trust and improves the quality of the shopping experience.

The recommendation engine also contributes real value. Even though it is lightweight and intentionally conservative, it helps users move from symptom descriptions to possible medicines without forcing them to know the exact product name in advance. This makes the system more usable for common healthcare shopping scenarios.

Overall, the project shows that a carefully designed Flask application can support meaningful multi-role workflows without requiring a heavy enterprise stack. The system is practical for academic use, demonstration, and incremental expansion.

### 8.2 Future Work

The current system can be improved in several ways. One major area is recommendation quality. The symptom model can be expanded with larger datasets, multilingual phrasing, better ranking logic, and interaction checks. A future version could combine rule-based filtering with a stronger language model or a medical knowledge base to improve relevance while still keeping safety controls.

Another important area is medication safety. Future work could add drug-interaction warnings, allergy flags, prescription validation rules, and age-specific restrictions. These features would move the platform closer to a production-grade pharmacy assistant while maintaining the educational structure of the current project.

On the operational side, the platform could benefit from stronger analytics dashboards, branch-level reporting, stock forecasting, and automatic reorder suggestions. Delivery management could be enhanced with route mapping, live GPS tracking, and richer status notifications. Customer communication could also be improved with email alerts, SMS messages, and push notifications.

The architecture could further evolve by replacing SQLite with PostgreSQL or MySQL, adding centralized logging, and deploying the applications with Docker or a cloud orchestration platform. This would improve scalability and reliability for a real-world environment. Finally, a mobile application could be introduced so that customers and delivery agents can interact with the platform on smartphones more naturally.

### 8.3 Future Enhancement Roadmap

1. Add stronger medical intelligence for symptom interpretation.
2. Introduce drug interaction and allergy validation.
3. Add OCR-based prescription extraction for faster uploads.
4. Expand vendor analytics, order analytics, and stock forecasting.
5. Replace local SQLite storage with a production database.
6. Add push notifications, email alerts, and richer SMS flows.
7. Create a mobile client for customers and delivery agents.
8. Deploy the system in containers with automated backups and monitoring.

---

\newpage

## 9. REFERENCES

1. AcuMeds project source code, including app/__init__.py, app/models.py, app/routes.py, app/ml_recommendation.py, config.py, and start_all.ps1.
2. AcuMeds README.md and related project documentation in the pharmacy_system folder.
3. AI_SYSTEM.md, describing the medicine recommendation architecture and workflow.
4. VERIFICATION_IMPLEMENTATION_SUMMARY.md, documenting the shared database verification model.
5. SHOPKEEPER_VERIFICATION_GUIDE.md, describing the vendor approval workflow.
6. Flask Documentation. https://flask.palletsprojects.com/
7. Flask-SQLAlchemy Documentation. https://flask-sqlalchemy.palletsprojects.com/
8. Flask-Login Documentation. https://flask-login.readthedocs.io/
9. SQLite Documentation. https://www.sqlite.org/docs.html
10. scikit-learn User Guide. https://scikit-learn.org/stable/user_guide.html
11. Werkzeug Documentation. https://werkzeug.palletsprojects.com/
12. Bootstrap Documentation. https://getbootstrap.com/docs/
13. ReportLab User Guide. https://www.reportlab.com/docs/reportlab-userguide.pdf
14. Paytm Developer Documentation. https://developer.paytm.com/
15. Twilio SMS Documentation. https://www.twilio.com/docs/sms
16. OWASP Top Ten Web Application Security Risks. https://owasp.org/www-project-top-ten/



