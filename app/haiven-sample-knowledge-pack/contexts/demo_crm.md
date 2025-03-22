---
key: context
title: CRM System Demo
---

You're part of a team developing a sophisticated web application designed to streamline the workflow for Sales Managers managing relationships with their portfolio of clients in the hospitality, restaurant, catering, and trading sectors. This tool is aimed at enhancing personal customer relationships and boosting revenue streams through effective client management.

**Target Users:**
- Sales Managers responsible for maintaining and growing client relationships.
- Users often working remotely or traveling, needing seamless accessibility.

**Functional and Technical Requirements:**
- Mobile-first design ensuring responsive usability on smartphones and tablets.
- Robust offline functionality to accommodate users operating in regions with unreliable or intermittent internet connections.
- Internationalization (i18n) and localization (l10n) capabilities to support diverse linguistic and regional user bases.

**Domain-Specific Terminology:**
- **Contact/Activity:** Any interaction with customers including visits, phone calls, or emails. Sales Managers log detailed notes on these activities for ongoing customer relationship management.

**Application Architecture:**
- **Frontend:** TypeScript, ReactJS, Redux, KonvaJS, React-Konva for dynamic and interactive visual components.
- **Backend:** Java (with Gradle, Guice, Jersey) providing scalable RESTful APIs.
- **Database and Search:** PostgreSQL for data persistence, Solr utilized for advanced search indexing capabilities.
- **Deployment and Infrastructure:** Docker containers orchestrated by Kubernetes for scalable and reliable deployments.

**Integration Points with External Systems:**
1. **CRM Data Exchange:** Integration with existing CRM system via CSV flat-file exchanges. Data includes:
   - Customer master data (export)
   - Contacts and Activities (bi-directional: export and import)
   - Address data (export)

2. **Authentication Integration:** Employee Active Directory integration to manage secure login functionality.

**MVVM React Component Architecture:**
- Clearly separated responsibilities through Model-View-ViewModel (MVVM) architecture.
- Two distinct view models:
  - **Shared View Model:** State shared across remote and local users, managed via Redux slices, fully tested with Vitest.
  - **Local View Model:** State specific to a single user's session, managed via React props or useState hooks, with global local view models implemented via Redux slices, tested using Vitest.
- React hooks (useSelector, createSelector) employed for optimized state access and performance.
- Encapsulated ViewModel interfaces for interacting with Redux stores, ensuring abstraction and maintainability.
- React-Konva used extensively for rendering interactive graphic elements, ensuring component responsiveness and user engagement.

**Testing Standards and Patterns:**
- Unit and integration tests for view models implemented using Vitest.
- React component views tested through Cypress component tests employing fake view models via view model interfaces to ensure accurate, isolated testing scenarios.
- Testing patterns adhere to:
  - Use of `describe` blocks over individual `test` declarations.
  - Preference for data-driven testing approaches.
  - Clear separation between testing of shared and local view model logic.

This structured and robust approach ensures a highly usable, performant, and scalable CRM tool tailored specifically to the dynamic and diverse requirements of Sales Managers in various operational contexts.

